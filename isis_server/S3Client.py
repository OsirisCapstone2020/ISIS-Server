from os.path import splitext
from typing import List

from boto3 import client as s3_client, set_stream_logger as set_boto3_logger
from logging import getLogger, StreamHandler, WARN
from sys import stdout
from os import path, extsep

from .ISISRequest import ISISInputFile
from .config import Config
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

set_boto3_logger("", level=WARN)
s3_logger = getLogger("s3")
s3_logger.addHandler(StreamHandler(stream=stdout))
s3_logger.setLevel(Config.app.log_level)

# 30 days
PUBLIC_EXPIRES_IN = 86400 * 30


class S3Client:
    def __init__(self):
        self.s3 = s3_client(
            "s3",
            endpoint_url=Config.s3.server,
            aws_access_key_id=Config.s3.access_key,
            aws_secret_access_key=Config.s3.secret_key
        )

    def download(self, object_name: str) -> str:
        """
        Downloads a file with object_name from S3. Returns the name of
        a temporary file on the local system that the file was downloaded to.
        """
        try:
            s3_logger.info("Downloading {}...".format(object_name))
            _, ext = splitext(object_name)
            temp_file_name = ISISInputFile.get_tmp_file(ext)

            with open(temp_file_name, mode='wb') as temp_file:
                self.s3.download_fileobj(
                    Config.s3.bucket,
                    object_name,
                    temp_file
                )

            s3_logger.info(
                "Download complete. Stored at {}.\n".format(temp_file_name)
            )
        except Exception as e:
            s3_logger.error("Download failed: {}".format(str(e)))
            raise e

        return temp_file_name

    def multi_download(self, object_names: List[str]) -> List[str]:
        threads = list()
        with ThreadPoolExecutor() as thread_pool:
            for object_name in object_names:
                threads.append(thread_pool.submit(self.download, object_name))
        return [t.result() for t in threads]

    def upload(self, file_path: str) -> str:
        """
        Uploads the file at file_path to s3
        """
        object_name = path.basename(file_path)
        s3_logger.info(
            "Uploading {} to {}...".format(object_name, Config.s3.server)
        )

        try:
            self.s3.upload_file(
                file_path,
                Config.s3.bucket,
                object_name
            )
            s3_logger.info("Upload of {} complete.".format(file_path))
        except Exception as e:
            s3_logger.error("Upload failed: {}".format(str(e)))
            raise e

        return object_name

    def multi_upload(self, file_paths: List[str]) -> List[str]:
        threads = list()
        with ThreadPoolExecutor() as thread_pool:
            for file_path in file_paths:
                threads.append(thread_pool.submit(self.upload, file_path))
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

            self.s3.copy_object(**copy_args)

            if public:
                return self.s3.generate_presigned_url(
                    "get_object",
                    Params={
                        "Bucket": Config.s3.bucket,
                        "Key": dst_obj
                    },
                    ExpiresIn=PUBLIC_EXPIRES_IN
                )
            else:
                return "{}/{}/{}".format(
                    Config.s3.server,
                    Config.s3.bucket,
                    dst_obj
                )

        except Exception as e:
            s3_logger.error("Copy failed: {}".format(str(e)))
            raise e
