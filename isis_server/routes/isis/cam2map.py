from flask import request, jsonify
from flask_expects_json import expects_json
from pysis import isis as Isis
from pysis.exceptions import ProcessError

from isis_server.ISISCommand import ISISCommand
from isis_server.ISISRequest import ISISRequest
from isis_server.input_validation import get_json_schema
from isis_server.logger import get_logger
from isis_server.Utils import Utils

CMD_NAME = "cam2map"
logger = get_logger(CMD_NAME)

json_schema = {
    "projection": "string",
    "extra_args": {
        "type": "object",
        "properties": {
            "args": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "arg_key": {"type": "string"},
                        "arg_val": {"type": ["string", "number", "boolean"]}
                    },
                    "additionalArguments": "false",
                    "required": ["arg_key", "arg_val"]
                }
            }
        },
        "additionalArguments": "false",
        "required": ["args"]
    }
}


@expects_json(get_json_schema(**json_schema))
def post_cam_2_map():
    """
    Called when a client POSTs to /cam2map
    """

    isis_request = ISISRequest(request)
    map_file = Utils.get_tmp_file("map")

    map_projection = request.json["args"]["projection"]
    proj_extras = dict()

    for kv_pair in request.json["args"]["extra_args"]["args"]:
        proj_extras[kv_pair["arg_key"]] = kv_pair["arg_val"]

    output_files = list()
    error = None

    try:
        Isis.maptemplate(
            map=map_file,
            projection=map_projection,
            **proj_extras
        )
    except ProcessError as e:
        error = e.stderr.decode("utf-8")
        logger.error("maptemplate threw an error: {}".format(error))

    if error is None:
        cam2map = ISISCommand(CMD_NAME, {"map": map_file})
        errors = cam2map.run(*isis_request.input_files)

        if len(errors) > 0:
            error = "\n".join(errors)
        else:
            output_files = isis_request.upload_output()

    isis_request.cleanup()
    Utils.remove_file_if_exists(map_file)

    return jsonify({
        "to": output_files,
        "err": error
    })
