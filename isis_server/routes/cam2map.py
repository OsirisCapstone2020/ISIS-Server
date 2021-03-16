from flask_expects_json import expects_json
from flask import request, jsonify, current_app
from uuid import uuid4
from os import remove as remove_file
from os import path
from tempfile import gettempdir

from ..input_validation import get_json_schema
from ..logger import get_logger

from pysis import isis
from pysis.exceptions import ProcessError

CMD_NAME = "cam2map"
logger = get_logger(CMD_NAME)


@expects_json(get_json_schema())
def post_cam_2_map():
    """
    Called when a client POSTs to /cam2map
    """

    # Either output_file or err will be set, but not both
    # output_file is set on success
    # err is set on failure
    # TODO: change hardcoded map file dynamically
    input_file = None
    output_file = None
    error = None

    try:
        input_file = current_app.s3_client.download(request.json["from"])

        temp_file_name = path.join(gettempdir(), "{}.cub".format(str(uuid4())))

        logger.debug("Running cam2map...")

        isis.cam2map(from_=input_file, map="/isisdata/npolar90.map", to=temp_file_name)

        output_file = current_app.s3_client.upload(temp_file_name)

        logger.debug("{} completed".format(CMD_NAME))

    except ProcessError as e:
        error = e.stderr.decode("utf-8")
        logger.error("{} threw an error: {}".format(CMD_NAME, error))

    # Clean up
    if input_file is not None and path.exists(input_file):
        remove_file(input_file)

    if output_file is not None and path.exists(output_file):
        remove_file(output_file)

    return jsonify({
        "to": output_file,
        "err": error
    })