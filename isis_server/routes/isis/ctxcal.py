from flask import request, jsonify
from flask_expects_json import expects_json

from isis_server.ISISCommand import ISISCommand
from isis_server.ISISRequest import ISISRequest
from isis_server.input_validation import get_json_schema

CMD_NAME = "ctxcal"


@expects_json(get_json_schema())
def post_ctx_cal():
    """
    Called when a client POSTs to /ctxcal
    """

    isis_request = ISISRequest(request)

    output_files = list()
    error = None

    ctxcal = ISISCommand(CMD_NAME)
    errors = ctxcal.run(*isis_request.input_files)

    if len(errors) > 0:
        error = "\n".join(errors)
    else:
        output_files = isis_request.upload_output()

    isis_request.cleanup()

    return jsonify({
        "to": output_files,
        "err": error
    })
