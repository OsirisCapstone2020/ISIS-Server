from smtplib import SMTP
from email.message import EmailMessage
from mimetypes import guess_type
from os import remove as remove_file
from zlib import compress as compress_bytes

from flask import current_app, request, jsonify
from flask_expects_json import expects_json

from ..input_validation import get_json_schema
from ..logger import get_logger
from ..config import Config

CMD_NAME = "email"
logger = get_logger(CMD_NAME)

SUBJECT = "Output from Pipeline"
FROM = "ascbot@usgs.gov"

CHUNK_SZ = 1024


@expects_json(get_json_schema(recipient="string"))
def post_email():
    s3_file = current_app.s3_client.download(request.json["from"])
    input_file = "{}.gz".format(s3_file)

    with open(s3_file, 'rb') as input_f, open(input_file, 'wb') as output_f:
        chunk = input_f.read(CHUNK_SZ)
        while chunk:
            compressed = compress_bytes(chunk)
            output_f.write(compressed)
            chunk = input_f.read(CHUNK_SZ)

    # One of these will be set but not both
    error = None
    to = None

    try:
        email_message = EmailMessage()

        email_message['Subject'] = SUBJECT
        email_message['To'] = request.json["args"]["recipient"]
        email_message['From'] = FROM

        filetype, _ = guess_type(input_file)
        if filetype is None:
            filetype = "application/octet-stream"

        main_type, sub_type = filetype.split("/")

        with open(input_file, 'rb') as f:
            img_data = f.read()
            email_message.add_attachment(
                img_data,
                maintype=main_type,
                subtype=sub_type
            )

        logger.info("Sending email...")

        with SMTP(Config.app.smtp_server, Config.app.smtp_port) as s:
            s.ehlo()
            s.starttls()
            s.login(Config.app.smtp_username, Config.app.smtp_password)
            s.send_message(email_message)

        logger.info("Email sent successfully")

        # File is unchanged, we just emailed it. So pass it through to the
        # next node
        to = input_file

    except Exception as e:
        error = str(e)

    finally:
        remove_file(input_file)

    return jsonify({
        "err": error,
        "to": to,
    })
