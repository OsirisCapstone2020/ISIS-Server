from flask import request, jsonify
from flask_expects_json import expects_json

from isis_server.ISISCommand import ISISCommand
from isis_server.ISISRequest import ISISRequest
from isis_server.input_validation import get_json_schema
from isis_server.logger import get_logger

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

    output_files = list()
    error = None

    file_type = request.json["args"]["file_type"].lower()
    if file_type not in ALLOWED_STD_TYPES:
        return jsonify({
            "to": output_files,
            "err": "Allowed file types are {}".format(
                ", ".join(ALLOWED_STD_TYPES)
            )
        })

    isis_request = ISISRequest(request, output_extension=file_type)

    isis2std = ISISCommand(CMD_NAME, {"format": file_type})
    errors = isis2std.run(*isis_request.input_files)

    if len(errors) > 0:
        error = "\n".join(errors)
    else:
        output_files = isis_request.upload_output()

    isis_request.cleanup()

    return jsonify({
        "to": output_files,
        "err": error
    })
