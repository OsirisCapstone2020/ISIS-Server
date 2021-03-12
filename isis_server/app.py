from flask import Flask

from .routes import post_start, post_spiceinit, get_all_commands, get_command
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


# Create the app
app = Flask(__name__)
app.s3_client = S3Client()
app.isis_commands = get_command_xml()

# ===========
# App routes
# ===========

# Add xml routes
app.add_url_rule('/commands/<command_name>', 'single_command', get_command, methods=["GET"])
app.add_url_rule('/commands', 'commands', get_all_commands, methods=["GET"])

# Add n8n node routes
app.add_url_rule('/start', 'start', post_start, methods=["POST"])
app.add_url_rule('/spiceinit', 'spiceinit', post_spiceinit, methods=["POST"])
