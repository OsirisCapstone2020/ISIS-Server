from flask_expects_json import expects_json
from flask import request, jsonify, current_app
from uuid import uuid4

from ..logger import get_logger

from pysis import isis
from pysis.exceptions import ProcessError

CMD_NAME = "mroctx2isis"

MRO_CTX_SCHEMA = {
    "type": "object",
    "properties": {
        "from": {"type": "string"},
        "args": {
            "type": "object",
            "properties": {},
        },
    },
    "required": ["args", "from"],
    "additionalProperties": False
}

logger = get_logger(CMD_NAME)


@expects_json(MRO_CTX_SCHEMA)
def post_mro_ctx_2_isis():
    """
    Called when a client POSTs to /mroctx2isis
    """
    logger.debug("Running {}...".format(CMD_NAME))

    # Either output_file or err will be set, but not both
    # output_file is set on success
    # err is set on failure
    output_file = None
    error = None

    try:
        input_file = current_app.s3_client.download(request.json["from"])

        temp_file_name = "/tmp/{}.cub".format(str(uuid4()))
        isis.mroctx2isis(from_=input_file, to=temp_file_name)

        output_file = current_app.s3_client.upload(temp_file_name)

        logger.debug("{} completed".format(CMD_NAME))

    except ProcessError as e:
        error = e.stderr.decode("utf-8")
        logger.error("{} threw an error: {}".format(CMD_NAME, error))

    return jsonify({
        "to": output_file,
        "err": error
    })
