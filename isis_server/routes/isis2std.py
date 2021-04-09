from flask import request, jsonify
from flask_expects_json import expects_json
from pysis.exceptions import ProcessError

from ..ISISCommand import ISISCommand
from ..ISISRequest import ISISRequest
from ..input_validation import get_json_schema
from ..logger import get_logger

CMD_NAME = "isis2std"
logger = get_logger(CMD_NAME)

ALLOWED_STD_TYPES = [
    "png",
    "bmp",
    "tif",
    "jpeg",
    "jp2"
]


@expects_json(get_json_schema(file_type="string"))
def post_isis_2_std():
    """
    Called when a client POSTs to /isis2std
    """

    # Either output_file or err will be set, but not both
    # output_file is set on success
    # err is set on failure
    output_files = list()
    error = None
    file_type = request.json["args"]["file_type"].lower()
    isis_request = ISISRequest(request, output_extension=file_type)

    try:
        if file_type not in ALLOWED_STD_TYPES:
            raise Exception(
                "Allowed file types are {}".format(", ".join(ALLOWED_STD_TYPES))
            )

        isis2std = ISISCommand(CMD_NAME, format=file_type)
        isis2std.run(*isis_request.input_files)

        output_files = isis_request.upload_output()

    except ProcessError as e:
        error = e.stderr.decode("utf-8")
        logger.error("{} threw an error: {}".format(CMD_NAME, error))

    isis_request.cleanup()

    return jsonify({
        "to": output_files,
        "err": error
    })
