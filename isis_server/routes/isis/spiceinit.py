from flask import request, jsonify
from flask_expects_json import expects_json
from pysis import IsisPool
from pysis.exceptions import ProcessError

from isis_server.ISISCommand import ISISCommand
from isis_server.ISISRequest import ISISRequest
from isis_server.input_validation import get_json_schema
from isis_server.logger import get_logger

CMD_NAME = "spiceinit"
logger = get_logger(CMD_NAME)


@expects_json(get_json_schema())
def post_spiceinit():
    """
    Called when a client POSTs to /spiceinit
    """

    isis_request = ISISRequest(request)

    output_files = list()
    error = None

    # Spiceinit only: Output files are the same as input files
    for target in isis_request.input_files:
        target.output_target = target.input_target

    logger.debug("Running {}...".format(CMD_NAME))
    spiceinit = ISISCommand(CMD_NAME, disable_to_arg=True)
    errors = spiceinit.run(*isis_request.input_files)

    if len(errors) > 0:
        error = "\n".join(errors)
    else:
        output_files = isis_request.upload_output()

    logger.debug("{} complete".format(CMD_NAME))

    isis_request.cleanup()

    return jsonify({
        "to": output_files,
        "err": error
    })
