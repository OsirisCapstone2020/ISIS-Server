from flask_expects_json import expects_json
from flask import request, jsonify
from os import remove as remove_file
from requests import get as req_get
from tempfile import NamedTemporaryFile

from ..app import app
from ..logger import get_logger

CMD_NAME = "start"
READ_CHUNK_SZ = 8192

START_SCHEMA = {
    "type": "object",
    "properties": {
        "from": {"type": "string"},
        "args": {
            "type": "object",
            "properties": {}
        },
    },
    "required": ["args", "from"],
    "additionalProperties": False
}

logger = get_logger(CMD_NAME)


def download(url):
    """
    Downloads the file at url to a temporary file & returns the temporary file
    """
    with req_get(url, stream=True) as req, NamedTemporaryFile(mode='wb', delete=False) as temp_file:
        req.raise_for_status()
        for req_chunk in req.iter_content(READ_CHUNK_SZ):
            temp_file.write(req_chunk)

        return temp_file.name


@app.route(["/{}".format(CMD_NAME)], methods=["POST"])
@expects_json(START_SCHEMA)
def post_start():
    input_file = request.json["from"]

    # Either err or output_file will be set, but not both
    err = None
    output_file = None

    try:
        # Download the file to a temp file, upload it to S3, delete the
        # temp file
        temp_file = download(input_file)
        output_file = app.s3.upload(temp_file)
        remove_file(temp_file)

    except Exception as e:
        err = str(e)

    return jsonify({
        "to": output_file,
        "err": err
    })
