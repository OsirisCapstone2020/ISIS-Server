from typing import List

from flask import Request, current_app
from os.path import splitext, basename, exists as path_exists, join as path_join
from tempfile import gettempdir
from os import remove as remove_file
from uuid import uuid4


class ISISInputFile:
    def __init__(self, downloaded_file: str, output_extension=None):
        self.input_target = downloaded_file

        if output_extension is None:
            input_basename = basename(self.input_target)
            _, ext = splitext(input_basename)
            self.output_target = ISISInputFile.get_tmp_file(ext)
        else:
            self.output_target = ISISInputFile.get_tmp_file(output_extension)

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


class ISISRequest:
    def __init__(self, req: Request, output_extension=None):
        self.input_files: List[ISISInputFile] = list()

        req_input_files = req.json["from"]

        # Make sure we're dealing with an array no matter what
        if isinstance(req_input_files, str):
            req_input_files = [req_input_files]

        temp_files = current_app.s3_client.multi_download(req_input_files)

        for tf in temp_files:
            isis_file = ISISInputFile(tf, output_extension=output_extension)
            self.input_files.append(isis_file)

    def upload_output(self):
        output_files = [isis_file.output_target for isis_file in self.input_files]
        return current_app.s3_client.multi_upload(output_files)

    def cleanup(self):
        for file in self.input_files:
            ISISInputFile.remove_file_if_exists(file.input_target)
            ISISInputFile.remove_file_if_exists(file.output_target)
