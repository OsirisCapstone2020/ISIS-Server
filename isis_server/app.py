from tempfile import tempdir

from flask import Flask, jsonify, request, make_response
from .s3 import s3_download, s3_upload
from .isis import lowpass, CMD_LOWPASS
from .validator import REQUEST_SCHEMA
from werkzeug.exceptions import BadRequest
from os import path, listdir, remove as file_remove
from flask_expects_json import expects_json

from .xml_reader import XMLReader

STATUS_SERVER_ERROR = 500
STATUS_BAD_REQUEST = 400

TEST_BUCKET = "test"
XML_LOCATION = path.relpath(path.join(path.dirname(__file__), "..", "xml"))


def get_command_xml():
    """
    :return: A list of all the XML file in the data directory
    """
    all_files = [path.join(XML_LOCATION, f) for f in listdir(XML_LOCATION)]
    return [XMLReader.get_isis_command(f) for f in all_files]


# Create the APP
app = Flask(__name__)
app.isis_commands = get_command_xml()


# ===========
# App routes
# ===========

@app.route("/", methods=["POST"])
@expects_json(REQUEST_SCHEMA)
def post_index():
    """
    Called when a user POSTs to /
    """
    input_data = request.json

    # Download input
    temp_in_file = s3_download(TEST_BUCKET, input_data["input_file"])

    in_file_name, in_file_ext = path.splitext(input_data["input_file"])
    out_obj_name = "{}.lowpass{}".format(in_file_name, in_file_ext)
    out_obj_full_path = path.join(
        tempdir,
        out_obj_name
    )

    # Run ISIS
    # TODO: Better design than if statements
    if input_data["cmd"] == CMD_LOWPASS:
        lowpass(temp_in_file, out_obj_full_path)
    else:
        raise BadRequest("Command not found")

    # Upload output
    upload_res = s3_upload(TEST_BUCKET, out_obj_full_path)

    if path.exists(temp_in_file):
        file_remove(temp_in_file)

    if path.exists(out_obj_full_path):
        file_remove(out_obj_full_path)

    return jsonify({"output": out_obj_name})


@app.route("/commands", methods=["GET"])
def get_all_commands():
    return jsonify(app.isis_commands)


@app.route("/commands/<command_name>", methods=["GET"])
def get_command(command_name):
    for command in app.isis_commands:
        if command["name"] == command_name:
            return jsonify(command)

    return make_response(jsonify(), 404)
