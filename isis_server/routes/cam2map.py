from flask import request, jsonify
from flask_expects_json import expects_json
from pysis import isis as Isis
from pysis.exceptions import ProcessError

from ..ISISRequest import ISISRequest
from ..input_validation import get_json_schema
from ..logger import get_logger
from ..utils import Utils
from ..ISISCommand import ISISCommand

CMD_NAME = "cam2map"
logger = get_logger(CMD_NAME)


@expects_json(
    get_json_schema(projection="string", extra_args="object")
)
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

        cam2map = ISISCommand(CMD_NAME, map=map_file)
        cam2map.run(*isis_request.input_files)

        output_files = isis_request.upload_output()

    except ProcessError as e:
        error = e.stderr.decode("utf-8")
        logger.error("{} threw an error: {}".format(CMD_NAME, error))

    isis_request.cleanup()
    Utils.remove_file_if_exists(map_file)

    return jsonify({
        "to": output_files,
        "err": error
    })
