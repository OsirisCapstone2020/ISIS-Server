from flask_expects_json import expects_json
from flask import request, jsonify, current_app
from os import remove as remove_file
from requests import get as req_get
from tempfile import NamedTemporaryFile

from ..input_validation import get_json_schema
from ..logger import get_logger

READ_CHUNK_SZ = 8192

logger = get_logger("start")


def download(url):
    """
    Downloads the file at url to a temporary file & returns the temporary file
    """
    with req_get(url, stream=True) as req, NamedTemporaryFile(mode='wb', delete=False) as temp_file:
        req.raise_for_status()
        for req_chunk in req.iter_content(READ_CHUNK_SZ):
            temp_file.write(req_chunk)

        return temp_file.name


@expects_json(get_json_schema())
def post_start():
    input_file = request.json["from"]

    # Either err or output_file will be set, but not both
    err = None
    output_file = None

    try:
        # Download the file to a temp file, upload it to S3, delete the
        # temp file
        logger.debug("Downloading {}...".format(input_file))
        temp_file = download(input_file)
        logger.debug("{} downloaded to {}".format(input_file, temp_file))

        output_file = current_app.s3_client.upload(temp_file)
        remove_file(temp_file)

    except Exception as e:
        err = str(e)

    return jsonify({
        "to": output_file,
        "err": err
    })
