from flask_expects_json import expects_json
from flask import request, jsonify, current_app
from os import remove as remove_file
from os.path import splitext, exists as path_exists, basename
from requests import get as req_get
from urllib.parse import urlparse

from ..config import Config
from ..input_validation import get_json_schema
from ..logger import get_logger

READ_CHUNK_SZ = 8192

logger = get_logger("start")


def download(url):
    """
    Downloads the file at url to a temporary file & returns the temporary file
    """
    input_path = urlparse(url).path
    orig_file = basename(input_path)
    output_file = Config.get_tmp_file(orig_file)
    _, ext = splitext(output_file)

    with req_get(url, stream=True) as req, open(output_file, mode='wb') as temp_file:
        req.raise_for_status()
        for req_chunk in req.iter_content(READ_CHUNK_SZ):
            temp_file.write(req_chunk)

    return output_file


@expects_json(get_json_schema())
def post_start():
    input_files = request.json["from"]

    # Make sure we're dealing with an array no matter what
    if isinstance(input_files, str):
        input_files = [input_files]

    # Either err or output_file will be set, but not both
    err = None
    output_files = list()
    temp_files = list()

    try:
        # Download the file to a temp file, upload it to S3, delete the
        # temp file
        for file in input_files:
            logger.debug("Downloading {}...".format(file))
            temp_file = download(file)
            logger.debug("{} downloaded to {}".format(file, temp_file))

            output_file = current_app.s3_client.upload(temp_file)

            temp_files.append(temp_file)
            output_files.append(output_file)

    except Exception as e:
        err = str(e)

    for temp_file in temp_files:
        if path_exists(temp_file):
            remove_file(temp_file)

    return jsonify({
        "to": output_files,
        "err": err
    })
