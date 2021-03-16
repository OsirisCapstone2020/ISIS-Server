from smtplib import SMTP
from email.message import EmailMessage
from email.mime.text import MIMEText

from flask import request, jsonify, current_app
from flask_expects_json import expects_json

from ..input_validation import get_json_schema
from ..logger import get_logger
from ..config import Config

CMD_NAME = "email"
logger = get_logger(CMD_NAME)

SUBJECT = "Your ISIS Pipeline Output is Ready"
FROM = "ascbot@usgs.gov"


@expects_json(get_json_schema(file_name="string", recipient="string"))
def post_email():
    # One of these will be set but not both
    error = None
    to = None

    try:
        input_file = request.json["from"]
        recipient = request.json["args"]["recipient"]

        # Returns s3 URL to the copied object, which has the user's file_name
        output_file = current_app.s3_client.copy(
            input_file,
            request.json["args"]["file_name"],
            public=True
        )

        logger.debug("Emailing {} to {}...".format(output_file, recipient))
        email_message = EmailMessage()

        email_message['subject'] = SUBJECT
        email_message['to'] = recipient
        email_message['from'] = FROM
        email_body = "Hi there, your pipeline output is ready at {}. This link will expire in 30 days.".format(
            output_file
        )
        email_message.set_content(MIMEText(email_body, "plain"))

        with SMTP(Config.app.smtp_server, Config.app.smtp_port) as s:
            if Config.app.smtp_username is not None and Config.app.smtp_password is not None:
                s.ehlo()
                s.starttls()
                s.login(Config.app.smtp_username, Config.app.smtp_password)

            s.send_message(email_message)

        logger.info("Email sent successfully")

        # File is unchanged, we just emailed it. So pass it through to the
        # next node (if any)
        to = input_file

    except Exception as e:
        error = str(e)

    return jsonify({
        "err": error,
        "to": to,
    })
