from email.message import EmailMessage
from email.mime.text import MIMEText
from os.path import splitext
from smtplib import SMTP

from concurrent.futures import ThreadPoolExecutor
from flask import request, jsonify, current_app
from flask_expects_json import expects_json

from ..Config import Config
from ..input_validation import get_json_schema
from ..logger import get_logger

CMD_NAME = "email"
logger = get_logger(CMD_NAME)

SUBJECT = "Your ISIS Pipeline Output is Ready"
FROM = "ascbot@usgs.gov"


@expects_json(get_json_schema(recipient="string"))
def post_email():
    # One of these will be set but not both
    copy_threads = list()
    error = None
    to = None

    try:
        input_files = request.json["from"]
        recipient = request.json["args"]["recipient"]

        with ThreadPoolExecutor() as thread_pool:
            for s3_obj in input_files:
                tags = current_app.s3_client.get_tags(s3_obj)
                original_file = tags["original_file"]
                _, new_ext = splitext(s3_obj)
                original_file += new_ext

                copy_thread = thread_pool.submit(
                    current_app.s3_client.copy,
                    s3_obj,
                    original_file,
                    True
                )
                copy_threads.append(copy_thread)

        urls = [t.result() for t in copy_threads]

        email_message = EmailMessage()
        email_message['subject'] = SUBJECT
        email_message['to'] = recipient
        email_message['from'] = FROM

        email_body = "Hi there, your pipeline output is ready. "
        email_body += "Links will expire in 30 days.\n\n"
        email_body += "\n".join(urls)

        email_message.set_content(MIMEText(email_body, "plain"))

        with SMTP(Config.app.smtp_server, Config.app.smtp_port) as s:
            should_login = (
                Config.app.smtp_username is not None and
                Config.app.smtp_password is not None
            )
            if should_login:
                s.ehlo()
                s.starttls()
                s.login(Config.app.smtp_username, Config.app.smtp_password)

            s.send_message(email_message)

        logger.info("Email sent successfully")

    except Exception as e:
        error = str(e)

    return jsonify({
        "err": error,
        "to": to,
    })
