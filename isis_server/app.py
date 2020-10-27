from tempfile import tempdir

from flask import Flask, jsonify, request
from .s3 import s3_download, s3_upload
from .isis import lowpass, CMD_LOWPASS
from .validator import REQUEST_SCHEMA
from werkzeug.exceptions import BadRequest
from os import path, remove as file_remove
from flask_expects_json import expects_json

STATUS_SERVER_ERROR = 500
STATUS_BAD_REQUEST = 400

TEST_BUCKET = "test"

# Create the APP
app = Flask(__name__)

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
