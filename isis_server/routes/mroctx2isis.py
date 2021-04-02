from flask import request, jsonify
from flask_expects_json import expects_json
from pysis import IsisPool
from pysis.exceptions import ProcessError

from ..ISISRequest import ISISRequest
from ..input_validation import get_json_schema
from ..logger import get_logger

CMD_NAME = "mroctx2isis"
logger = get_logger(CMD_NAME)


@expects_json(get_json_schema())
def post_mro_ctx_2_isis():
    """
    Called when a client POSTs to /cam2map
    """

    # TODO: change hardcoded map file dynamically
    isis_request = ISISRequest(request)

    output_files = list()
    error = None

    try:
        with IsisPool() as isis:
            for file in isis_request.input_files:
                logger.debug("Running {}...".format(CMD_NAME))
                isis.mroctx2isis(
                    from_=file.input_target,
                    to=file.output_target
                )
                logger.debug("{} complete: {}".format(CMD_NAME, file.output_target))

        output_files = isis_request.upload_output()

    except ProcessError as e:
        error = e.stderr.decode("utf-8")
        logger.error("{} threw an error: {}".format(CMD_NAME, error))

    isis_request.cleanup()

    return jsonify({
        "to": output_files,
        "err": error
    })
