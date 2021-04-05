from concurrent.futures import ThreadPoolExecutor
from os.path import splitext, basename, join as path_join
from tempfile import gettempdir
from typing import List
from urllib.parse import urlparse

from flask import request, jsonify, current_app
from flask_expects_json import expects_json
from requests import get as req_get

from ..ISISRequest import ISISInputFile
from ..S3Client import S3File
from ..input_validation import get_json_schema
from ..logger import get_logger
from ..utils import Utils

READ_CHUNK_SZ = 8192

logger = get_logger("start")


def download(url) -> S3File:
    """
    Downloads the file at url to a temporary file & returns the temporary file
    """
    input_path = urlparse(url).path
    orig_file = basename(input_path)
    _, orig_ext = splitext(orig_file)
    output_file = Utils.get_tmp_file(orig_ext)

    logger.debug("Downloading {}...".format(url))

    with req_get(url, stream=True) as req, open(output_file, mode='wb') as temp_file:
        req.raise_for_status()
        for req_chunk in req.iter_content(READ_CHUNK_SZ):
            temp_file.write(req_chunk)

    logger.debug("{} downloaded to {}".format(url, output_file))
    return S3File(output_file, tags={"original_file": orig_file})


@expects_json(get_json_schema())
def post_start():
    input_files = request.json["from"]

    # Either err or output_file will be set, but not both
    err = None
    dl_threads = list()
    ul_threads = list()
    s3_objects: List[str] = list()
    downloaded_files: List[S3File] = list()

    try:
        with ThreadPoolExecutor() as download_thread_pool:
            for file in input_files:
                dl_thread = download_thread_pool.submit(download, file)
                dl_threads.append(dl_thread)

        downloaded_files = [t.result() for t in dl_threads]

        with ThreadPoolExecutor() as upload_thread_pool:
            for s3_file in downloaded_files:
                ul_thread = upload_thread_pool.submit(
                    current_app.s3_client.upload,
                    s3_file
                )
                ul_threads.append(ul_thread)

        s3_objects = [t.result() for t in ul_threads]

    except Exception as e:
        err = str(e)

    for temp_file in downloaded_files:
        Utils.remove_file_if_exists(temp_file.path)

    return jsonify({
        "to": s3_objects,
        "err": err
    })
