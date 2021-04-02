from flask_expects_json import expects_json
from flask import request, jsonify, current_app
from os import remove as remove_file
from os import path
from subprocess import check_output, CalledProcessError

from ..config import Config
from ..input_validation import get_json_schema
from ..logger import get_logger

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

    # Either output_file or err will be set, but not both
    # output_file is set on success
    # err is set on failure
    input_files = request.json["from"]
    cleanup_files = list()
    output_file = None
    error = None

    try:
        input_file = current_app.s3_client.download()

        temp_file = Config.get_tmp_file(".tif")

        logger.debug("Running {}...".format(CMD_NAME))

        cog_covert(input_file, temp_file)

        output_file = current_app.s3_client.upload(temp_file)

        logger.debug("{} completed".format(CMD_NAME))

    except CalledProcessError as e:
        error = e.stderr.decode("utf-8")

    except Exception as e:
        error = str(e)

    if error is not None:
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
