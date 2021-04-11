# Load the environment other code is called
from dotenv import load_dotenv
load_dotenv()

from .app import app
from .Config import Config
