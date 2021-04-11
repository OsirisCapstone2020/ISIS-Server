from flask import request, jsonify
from flask_expects_json import expects_json
from pysis import IsisPool
from pysis.exceptions import ProcessError

from isis_server.ISISCommand import ISISCommand
from isis_server.ISISRequest import ISISRequest
from isis_server.input_validation import get_json_schema
from isis_server.logger import get_logger

CMD_NAME = "ctxevenodd"
logger = get_logger(CMD_NAME)


@expects_json(get_json_schema())
def post_ctx_even_odd():
    """
    Called when a client POSTs to /ctxevenodd
    """
    isis_request = ISISRequest(request)

    output_files = list()
    error = None

    ctxevenodd = ISISCommand(CMD_NAME)
    errors = ctxevenodd.run(*isis_request.input_files)

    if len(errors) > 0:
        error = "\n".join(errors)
    else:
        output_files = isis_request.upload_output()

    isis_request.cleanup()

    return jsonify({
        "to": output_files,
        "err": error
    })
