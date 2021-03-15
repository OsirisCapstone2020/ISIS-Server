from boto3 import client as s3_client, set_stream_logger as set_boto3_logger
from tempfile import NamedTemporaryFile
from logging import getLogger, StreamHandler, WARN
from sys import stdout
from os import path
from .config import Config

set_boto3_logger("", level=WARN)
s3_logger = getLogger("s3")
s3_logger.addHandler(StreamHandler(stream=stdout))
s3_logger.setLevel(Config.app.log_level)


class S3Client:
    def __init__(self):
        self.s3 = s3_client(
            "s3",
            endpoint_url=Config.s3.server,
            aws_access_key_id=Config.s3.access_key,
            aws_secret_access_key=Config.s3.secret_key
        )
        # s3_logger.info(self.s3.list_objects(Bucket=Config.s3.bucket))

    def download(self, object_name: str) -> str:
        """
        Downloads a file with object_name from S3. Returns the name of
        a temporary file on the local system that the file was downloaded to.
        """
        try:
            s3_logger.info("Downloading {}...".format(object_name))
            with NamedTemporaryFile(delete=False, mode='wb') as temp_file:
                self.s3.download_fileobj(
                    Config.s3.bucket,
                    object_name,
                    temp_file
                )
                temp_file_name = temp_file.name

            s3_logger.info(
                "Download complete. Stored at {}.\n".format(temp_file_name)
            )
        except Exception as e:
            s3_logger.error("Download failed: {}".format(str(e)))
            raise e

        return temp_file_name

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
            s3_logger.info("Upload of {} complete.\n".format(file_path))
        except Exception as e:
            s3_logger.error("Upload failed: {}".format(str(e)))
            raise e

        return object_name
