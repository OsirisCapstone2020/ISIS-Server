from os.path import splitext
from typing import List

from boto3 import client as s3_client, set_stream_logger as set_boto3_logger
from botocore.config import Config as S3Config
from logging import getLogger, StreamHandler, WARN
from sys import stdout
from os import path

from .config import Config
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlencode

from .utils import Utils

set_boto3_logger("", level=WARN)
s3_logger = getLogger("s3")
s3_logger.addHandler(StreamHandler(stream=stdout))
s3_logger.setLevel(Config.app.log_level)


class S3File:
    def __init__(self, temp_path: str, tags: dict):
        self.path = temp_path
        self.tags = tags


class S3Client:
    def __init__(self):
        self.s3 = s3_client(
            "s3",
            endpoint_url=Config.s3.server,
            aws_access_key_id=Config.s3.access_key,
            aws_secret_access_key=Config.s3.secret_key,
            config=S3Config(connect_timeout=300, read_timeout=300)
        )

    def download(self, object_name: str) -> S3File:
        """
        Downloads a file with object_name from S3. Returns the name of
        a temporary file on the local system that the file was downloaded to.
        """
        try:
            s3_logger.info("Downloading {}...".format(object_name))
            _, ext = splitext(object_name)
            temp_file_name = Utils.get_tmp_file(ext)
            tags = self.get_tags(object_name)

            with open(temp_file_name, mode='wb') as temp_file:
                self.s3.download_fileobj(
                    Config.s3.bucket,
                    object_name,
                    temp_file
                )

            s3_logger.info(
                "Download complete. Stored at {}.".format(temp_file_name)
            )
        except Exception as e:
            s3_logger.error("Download failed: {}".format(str(e)))
            raise e

        return S3File(temp_file_name, tags)

    def multi_download(self, object_names: List[str]) -> List[S3File]:
        threads = list()
        with ThreadPoolExecutor() as thread_pool:
            for object_name in object_names:
                threads.append(thread_pool.submit(self.download, object_name))
        return [t.result() for t in threads]

    def upload(self, s3_file: S3File) -> str:
        """
        Uploads the file at file_path to s3
        """
        object_name = path.basename(s3_file.path)
        s3_logger.info(
            "Uploading {} to {}...".format(object_name, Config.s3.server)
        )

        try:
            self.s3.upload_file(
                s3_file.path,
                Config.s3.bucket,
                object_name
            )

            if len(s3_file.tags.keys()) > 0:
                self.set_tags(object_name, s3_file.tags)

            s3_logger.info("Upload of {} complete.".format(s3_file.path))
        except Exception as e:
            s3_logger.error("Upload failed: {}".format(str(e)))
            raise e

        return object_name

    def multi_upload(self, s3_files: List[S3File]) -> List[str]:
        threads = list()
        with ThreadPoolExecutor() as thread_pool:
            for s3_file in s3_files:
                threads.append(thread_pool.submit(self.upload, s3_file))
        return [t.result() for t in threads]

    def copy(self, src_obj: str, dst_obj: str, public=False) -> str:
        dst_obj = "{}_{}".format(
            datetime.now().strftime("%F_%H-%M-%S"),
            dst_obj
        )

        s3_logger.info("Copying {} to {}...".format(src_obj, dst_obj))

        try:
            copy_args = {
                "Bucket": Config.s3.bucket,
                "CopySource": {
                    "Bucket": Config.s3.bucket,
                    "Key": src_obj
                },
                "Key": dst_obj
            }

            if public:
                copy_args["TaggingDirective"] = "REPLACE"
                copy_args["Tagging"] = urlencode(dict(public="true"))

            self.s3.copy_object(**copy_args)
            s3_logger.info("Copy complete")

            return "{}/{}".format(
                Config.s3.server,
                dst_obj
            )

        except Exception as e:
            s3_logger.error("Copy failed: {}".format(str(e)))
            raise e

    def get_tags(self, object_name) -> dict:
        tag_response = self.s3.get_object_tagging(
            Bucket=Config.s3.bucket,
            Key=object_name
        )

        tags = dict()
        for tag in tag_response["TagSet"]:
            tags[tag["Key"]] = tag["Value"]

        return tags

    def set_tags(self, object_name: str, tags: dict):
        old_tags = self.get_tags(object_name)
        tags = {**old_tags, **tags}
        tag_set = list()

        for k, v in tags.items():
            tag_set.append({"Key": k, "Value": v})

        self.s3.put_object_tagging(
            Bucket=Config.s3.bucket,
            Key=object_name,
            Tagging={"TagSet": tag_set}
        )
