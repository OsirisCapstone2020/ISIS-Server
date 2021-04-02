from flask import request, jsonify
from flask_expects_json import expects_json
from pysis import IsisPool
from pysis.exceptions import ProcessError

from ..ISISRequest import ISISRequest
from ..input_validation import get_json_schema
from ..logger import get_logger

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
    MAP_FILE = "/data/disk/isisdata/npolar90.map"

    isis_request = ISISRequest(request)

    output_files = list()
    error = None

    try:
        logger.debug("Running {}...".format(CMD_NAME))
        with IsisPool() as isis:
            for file in isis_request.input_files:
                isis.cam2map(
                    from_=file.input_target,
                    to=file.output_target,
                    map=MAP_FILE
                )

        logger.debug("{} complete".format(CMD_NAME))
        output_files = isis_request.upload_output()

    except ProcessError as e:
        error = e.stderr.decode("utf-8")
        logger.error("{} threw an error: {}".format(CMD_NAME, error))

    isis_request.cleanup()

    return jsonify({
        "to": output_files,
        "err": error
    })
