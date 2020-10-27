from boto3 import client as s3_client, set_stream_logger as set_boto3_logger
from tempfile import NamedTemporaryFile
from logging import getLogger, DEBUG, ERROR, StreamHandler
from sys import stdout
from os import path

# TODO: Make this configurable outside the code
S3_SERVER = "http://127.0.0.1:9000"
CLIENT_KEY = "abc"
CLIENT_SECRET = "12345678"

set_boto3_logger("", level=ERROR)
s3_logger = getLogger("s3")
s3_logger.addHandler(StreamHandler(stream=stdout))
s3_logger.setLevel(DEBUG)

s3 = s3_client(
    "s3",
    endpoint_url=S3_SERVER,
    aws_access_key_id=CLIENT_KEY,
    aws_secret_access_key=CLIENT_SECRET
)


def s3_download(bucket_name, object_name):
    s3_logger.info(
        "Downloading {}/{} from {}...".format(
            bucket_name,
            object_name,
            S3_SERVER
        )
    )

    with NamedTemporaryFile(delete=False) as temp_file:
        s3.download_fileobj(bucket_name, object_name, temp_file)
        temp_file_name = temp_file.name

    s3_logger.info("Download complete. Stored at {}.\n".format(temp_file_name))
    return temp_file_name


def s3_upload(bucket_name, file_path):
    object_name = path.basename(file_path)

    s3_logger.info(
        "Uploading {}/{} to {}...".format(
            bucket_name,
            object_name,
            S3_SERVER
        )
    )

    result = s3.upload_file(file_path, bucket_name, object_name)

    s3_logger.info("Upload of {} complete.\n".format(file_path))

    return result
