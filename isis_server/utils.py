from uuid import uuid4
from os import remove as remove_file
from os.path import exists as path_exists, join as path_join
from tempfile import gettempdir


class Utils:
    @staticmethod
    def remove_file_if_exists(file: str):
        if path_exists(file):
            remove_file(file)

    @staticmethod
    def get_tmp_file(extension: str):
        tmp_file = "{}.{}".format(
            uuid4(),
            extension.lower().strip(".")
        )
        return path_join(gettempdir(), tmp_file)
