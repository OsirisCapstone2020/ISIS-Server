from flask import Flask, jsonify, request, make_response
from .s3 import S3Client
from os import path, listdir

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
app.s3_client = S3Client()
app.isis_commands = get_command_xml()


# ===========
# App routes
# Other commands can be found in ./routes
# ===========

@app.route("/commands", methods=["GET"])
def get_all_commands():
    return jsonify(app.isis_commands)


@app.route("/commands/<command_name>", methods=["GET"])
def get_command(command_name):
    for command in app.isis_commands:
        if command["name"] == command_name:
            return jsonify(command)

    return make_response(jsonify(), 404)
