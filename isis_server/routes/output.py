from flask import send_file, current_app, jsonify
from os.path import exists as path_exists
from os import remove as remove_file


def get_output_file(file_name):
    # Download the file from s3
    out_file = None

    try:
        out_file = current_app.s3_client.download(file_name)
        return send_file(out_file)

    except Exception as e:
        return jsonify({"err": str(e)}), 404

    finally:
        if out_file is not None and path_exists(out_file):
            remove_file(out_file)
