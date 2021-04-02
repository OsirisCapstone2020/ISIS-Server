from concurrent.futures import ThreadPoolExecutor
from os.path import splitext, basename
from urllib.parse import urlparse

from flask import request, jsonify, current_app
from flask_expects_json import expects_json
from requests import get as req_get

from ..ISISRequest import ISISInputFile
from ..input_validation import get_json_schema
from ..logger import get_logger

READ_CHUNK_SZ = 8192

logger = get_logger("start")


def download(url):
    """
    Downloads the file at url to a temporary file & returns the temporary file
    """
    input_path = urlparse(url).path
    orig_file = basename(input_path)
    _, ext = splitext(orig_file)
    output_file = ISISInputFile.get_tmp_file(ext)

    logger.debug("Downloading {}...".format(url))

    with req_get(url, stream=True) as req, open(output_file, mode='wb') as temp_file:
        req.raise_for_status()
        for req_chunk in req.iter_content(READ_CHUNK_SZ):
            temp_file.write(req_chunk)

    logger.debug("{} downloaded to {}".format(url, output_file))

    return output_file


@expects_json(get_json_schema())
def post_start():
    input_files = request.json["from"]

    # Either err or output_file will be set, but not both
    err = None
    dl_threads = list()
    s3_objects = list()
    downloaded_files = list()

    try:
        with ThreadPoolExecutor() as download_thread_pool:
            for file in input_files:
                dl_thread = download_thread_pool.submit(download, file)
                dl_threads.append(dl_thread)

        downloaded_files = [t.result() for t in dl_threads]
        s3_objects = current_app.s3_client.multi_upload(downloaded_files)

    except Exception as e:
        err = str(e)

    for temp_file in downloaded_files:
        ISISInputFile.remove_file_if_exists(temp_file)

    return jsonify({
        "to": s3_objects,
        "err": err
    })
