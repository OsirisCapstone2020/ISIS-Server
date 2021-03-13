from smtplib import SMTP
from email.message import EmailMessage
from mimetypes import guess_type
from os import remove as remove_file

from flask import current_app, request, jsonify

from ..logger import get_logger

CMD_NAME = "email"

EMAIL_SCHEMA = {
    "type": "object",
    "properties": {
        "from": {"type": "string"},
        "args": {
            "type": "object",
            "properties": {
                "recipient": {"type": "string"}
            },
            "required": ["recipient"]
        },
    },
    "required": ["args", "from"],
    "additionalProperties": False
}

logger = get_logger(CMD_NAME)

SUBJECT = "Output from Pipeline"
FROM = "ascbot@usgs.gov"


def post_email():
    input_file = current_app.s3_client.download(request.json["from"])

    # Will return one of these but not both
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

        with SMTP("localhost") as s:
            s.send_message(email_message)

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
