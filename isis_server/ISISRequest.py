from typing import List

from flask import Request, current_app
from os.path import splitext, basename, exists as path_exists

from .S3Client import S3File
from .Utils import Utils


class ISISInputFile:
    def __init__(self, downloaded_file: S3File, output_extension=None):
        self.input_target = downloaded_file.path
        self.tags = downloaded_file.tags

        if output_extension is None:
            input_basename = basename(self.input_target)
            _, ext = splitext(input_basename)
            self.output_target = Utils.get_tmp_file(ext)
        else:
            self.output_target = Utils.get_tmp_file(output_extension)


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
        output_files = list()
        for isis_file in self.input_files:
            if path_exists(isis_file.output_target):
                output_file = S3File(isis_file.output_target, isis_file.tags)
                output_files.append(output_file)
        return current_app.s3_client.multi_upload(output_files)

    def cleanup(self):
        for file in self.input_files:
            Utils.remove_file_if_exists(file.input_target)
            Utils.remove_file_if_exists(file.output_target)
