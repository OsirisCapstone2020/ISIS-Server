from flask_expects_json import expects_json
from flask import request, jsonify

from ..logger import getLogger
from ..app import app
from pysis import isis
from pysis.exceptions import ProcessError

CMD_NAME = "spiceinit"

SPICE_INIT_SCHEMA = {
    "type": "object",
    "properties": {
        "from": {"type": "string"},
        "args": {
            "type": "object",
            "properties": {
                "web": {"type": "boolean"}
            }
        },
    },
    "required": ["args", "from"],
    "additionalProperties": False
}

logger = getLogger(CMD_NAME)


@app.route("/{}".format(CMD_NAME), methods=["POST"])
@expects_json(SPICE_INIT_SCHEMA)
def post_spiceinit():
    """
    Called when a client POSTs to /spiceinit
    """
    logger.debug("Running {}...".format(CMD_NAME))

    # Either output_file or err will be set, but not both
    # output_file is set on success
    # err is set on failure
    output_file = None
    error = None

    try:
        input_file = app.s3.download(request.json["from"])
        web = request.json["args"]["web"]

        isis.spiceinit(from_=input_file, web=web)

        # For spiceinit, input file is unchanged, so just pass it through
        output_file = input_file

        logger.debug("{} completed".format(CMD_NAME))

    except ProcessError as e:
        error = e.stderr
        logger.error("{} threw an error: {}".format(CMD_NAME, error))

    return jsonify({
        "to": output_file,
        "err": error
    })
