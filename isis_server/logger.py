from logging import getLogger, DEBUG, StreamHandler
from sys import stdout


def get_logger(label: str):
    isis_logger = getLogger(label)
    isis_logger.setLevel(DEBUG)
    isis_logger.addHandler(StreamHandler(stdout))
