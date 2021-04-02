from subprocess import check_output, CalledProcessError

from flask import request, jsonify
from flask_expects_json import expects_json

from ..ISISRequest import ISISRequest
from ..input_validation import get_json_schema
from ..logger import get_logger
from concurrent.futures import ProcessPoolExecutor

CMD_NAME = "cog"
logger = get_logger(CMD_NAME)


def cog_covert(input_file: str, output_file: str, compression="LZW"):
    """
    https://www.cogeo.org/developers-guide.html
    """

    if not input_file.lower().endswith("tif"):
        raise Exception("This command takes a .tif file as input")

    # TODO: Make PROJ_LIB more configurable
    check_output([
        "gdal_translate",
        input_file,
        output_file,
        "-of",
        "COG",
        "-co",
        "COMPRESS={}".format(compression)
    ], env={"PROJ_LIB": "/usr/share/proj"})


@expects_json(get_json_schema())
def post_cog():
    """
    Called when a client POSTs to /cog
    """

    isis_request = ISISRequest(request)
    output_files = list()
    error = None

    try:
        logger.debug("Running {}...".format(CMD_NAME))
        with ProcessPoolExecutor() as process_pool:
            for isis_file in isis_request.input_files:
                process_pool.submit(
                    cog_covert,
                    isis_file.input_target,
                    isis_file.output_target
                )

        logger.debug("{} complete".format(CMD_NAME))
        output_files = isis_request.upload_output()

    except CalledProcessError as e:
        error = e.stderr.decode("utf-8")
        logger.error("{} threw an error: {}".format(CMD_NAME, error))

    isis_request.cleanup()

    return jsonify({
        "to": output_files,
        "err": error
    })
