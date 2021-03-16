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

CMD_NAME = "mroctx2isis"
logger = get_logger(CMD_NAME)


@expects_json(get_json_schema())
def post_mro_ctx_2_isis():
    """
    Called when a client POSTs to /mroctx2isis
    """

    # Either output_file or err will be set, but not both
    # output_file is set on success
    # err is set on failure
    input_file = None
    temp_file = None
    output_file = None
    error = None

    try:
        input_file = current_app.s3_client.download(request.json["from"])

        temp_file = path.join(gettempdir(), "{}.cub".format(str(uuid4())))

        logger.debug("Running mroctx2isis...")

        isis.mroctx2isis(from_=input_file, to=temp_file)

        output_file = current_app.s3_client.upload(temp_file)

        logger.debug("{} completed".format(CMD_NAME))

    except ProcessError as e:
        error = e.stderr.decode("utf-8")
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
