# Load the environment other code is called
from dotenv import load_dotenv
load_dotenv()

from flask import Flask

from .routes import post_start, post_spiceinit, get_all_commands, get_command, \
    post_mro_ctx_2_isis, post_cam_2_map, get_output_file
from .routes.email import post_email
from .s3 import S3Client
from os import path, listdir

from .xml_reader import XMLReader

STATUS_SERVER_ERROR = 500
STATUS_BAD_REQUEST = 400
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
app.add_url_rule('/commands/<command_name>', view_func=get_command, methods=["GET"])
app.add_url_rule('/commands', view_func=get_all_commands, methods=["GET"])

# Add n8n node routes
app.add_url_rule('/start', view_func=post_start, methods=["POST"])
app.add_url_rule('/email', view_func=post_email, methods=["POST"])
app.add_url_rule('/spiceinit', view_func=post_spiceinit, methods=["POST"])
app.add_url_rule('/mroctx2isis', view_func=post_mro_ctx_2_isis, methods=["POST"])
app.add_url_rule('/cam2map', view_func=post_cam_2_map, methods=["POST"])

# Add the output route, which will serve output files
app.add_url_rule('/output/<file_name>', view_func=get_output_file, methods=["GET"])
