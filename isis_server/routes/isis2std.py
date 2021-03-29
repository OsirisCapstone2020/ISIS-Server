from flask_expects_json import expects_json
from flask import request, jsonify, current_app
from os import remove as remove_file
from os import path

from ..config import Config
from ..input_validation import get_json_schema
from ..logger import get_logger

from pysis import isis
from pysis.exceptions import ProcessError

CMD_NAME = "isis2std"
logger = get_logger(CMD_NAME)

ALLOWED_STD_TYPES = [
    "png",
    "bmp",
    "tif",
    "jpeg",
    "jp2"
]


@expects_json(get_json_schema(file_type="string"))
def post_isis_2_std():
    """
    Called when a client POSTs to /isis2std
    """

    # Either output_file or err will be set, but not both
    # output_file is set on success
    # err is set on failure
    input_file = None
    temp_file = None
    output_file = None
    error = None
    file_type = request.json["args"]["file_type"].lower()

    try:
        if file_type not in ALLOWED_STD_TYPES:
            raise Exception(
                "Allowed file types are {}".format(", ".join(ALLOWED_STD_TYPES))
            )

        input_file = current_app.s3_client.download(request.json["from"])

        temp_file = Config.get_tmp_file(".{}".format(file_type))

        logger.debug("Running isis2std...")

        isis.isis2std(from_=input_file, format=file_type, to=temp_file)

        output_file = current_app.s3_client.upload(temp_file)

        logger.debug("{} completed".format(CMD_NAME))

    except ProcessError as e:
        error = e.stderr.decode("utf-8")

    except Exception as e:
        error = str(e)

    if error is not None:
        logger.error("{} threw an error: {}".format(CMD_NAME, error))

    # Clean up
    if input_file is not None and path.exists(input_file):
        remove_file(input_file)

    if temp_file is not None and path.exists(temp_file):
        remove_file(temp_file)

    return jsonify({
        "to": output_file,
        "err": error
    })
