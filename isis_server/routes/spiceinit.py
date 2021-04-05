from flask import request, jsonify
from flask_expects_json import expects_json
from pysis import IsisPool
from pysis.exceptions import ProcessError

from ..ISISRequest import ISISRequest
from ..input_validation import get_json_schema
from ..logger import get_logger

CMD_NAME = "spiceinit"
logger = get_logger(CMD_NAME)


@expects_json(get_json_schema())
def post_spiceinit():
    """
    Called when a client POSTs to /spiceinit
    """
    error = None
    output_files = list()

    isis_request = ISISRequest(request)

    # For spiceinit, output files are the same as input files
    for isis_file in isis_request.input_files:
        isis_file.output_target = isis_file.input_target

    try:
        with IsisPool() as isis:
            for file in isis_request.input_files:
                logger.debug("Running {}...".format(CMD_NAME))
                isis.spiceinit(
                    from_=file.input_target,
                    web=True
                )
                logger.debug(
                    "{} complete: {}".format(CMD_NAME, file.output_target)
                )

        output_files = isis_request.upload_output()

    except ProcessError as e:
        error = e.stderr.decode("utf-8")
        logger.error("{} threw an error: {}".format(CMD_NAME, error))

    isis_request.cleanup()

    return jsonify({
        "to": output_files,
        "err": error
    })
