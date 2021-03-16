from flask_expects_json import expects_json
from flask import request, jsonify, current_app
from os.path import exists as path_exists
from os import remove as remove_file

from ..input_validation import get_json_schema
from ..logger import get_logger

from pysis import isis
from pysis.exceptions import ProcessError

CMD_NAME = "spiceinit"
logger = get_logger(CMD_NAME)


@expects_json(get_json_schema(web="boolean"))
def post_spiceinit():
    """
    Called when a client POSTs to /spiceinit
    """
    logger.debug("Running {}...".format(CMD_NAME))

    # Either output_file or err will be set, but not both
    # output_file is set on success
    # err is set on failure
    temp_file = None
    output_file = None
    error = None

    try:
        req_file = request.json["from"]
        temp_file = current_app.s3_client.download(req_file)
        web = request.json["args"]["web"]

        isis.spiceinit(from_=temp_file, web=web)

        # For spiceinit, input file is unchanged, so just pass it through
        output_file = req_file

        logger.debug("{} completed".format(CMD_NAME))

    except ProcessError as e:
        error = e.stderr.decode("utf-8")
        logger.error("{} threw an error: {}".format(CMD_NAME, error))

    if temp_file is not None and path_exists(temp_file):
        remove_file(temp_file)

    return jsonify({
        "to": output_file,
        "err": error
    })
