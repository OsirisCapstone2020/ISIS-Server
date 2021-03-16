from smtplib import SMTP
from email.message import EmailMessage
from email.mime.text import MIMEText

from flask import request, jsonify
from flask_expects_json import expects_json

from ..input_validation import get_json_schema
from ..logger import get_logger
from ..config import Config

CMD_NAME = "email"
logger = get_logger(CMD_NAME)

SUBJECT = "Your ISIS Pipeline Output is Ready"
FROM = "ascbot@usgs.gov"


@expects_json(get_json_schema(recipient="string"))
def post_email():
    # One of these will be set but not both
    error = None
    to = None

    try:
        input_file = request.json["from"]
        email_message = EmailMessage()

        email_message['subject'] = SUBJECT
        email_message['to'] = request.json["args"]["recipient"]
        email_message['from'] = FROM
        email_body = "Hi there, your pipeline output is ready at http://{}:{}/output/{}".format(
            # TODO: Make this address configurable
            "127.0.0.1",
            Config.app.port,
            input_file
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
        # next node
        to = input_file

    except Exception as e:
        error = str(e)

    return jsonify({
        "err": error,
        "to": to,
    })
