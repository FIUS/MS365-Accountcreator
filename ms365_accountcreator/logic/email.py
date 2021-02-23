"""
The logic for sending emails
"""
from typing import Dict

import smtplib
from logging import Logger, getLogger
from email.message import EmailMessage

from flask_babel import gettext

class Email:
    """
    Class for sending emails
    """
    config: Dict = {}
    logger: Logger = None
    def __init__(self, config: Dict):
        """
        Create a new email class.
        Arguments:
         * config: A dict with configuration variables
        """
        self.config = config
        self.logger = getLogger(__name__)

    def send_email(self, recipient_address: str, subject: str, body: str):
        """
        Sends a email with the given body and subject the the given address.
        """
        log_msg = "mail to " + recipient_address + " with subject " + subject + " and body " + body
        if self.config['DEBUG_DONT_SEND_MAIL']:
            self.logger.info("Not sending mail, becaue we are debugging. Would send " + log_msg)
            return
        else:
            self.logger.debug("Sending " + log_msg)


        host = self.config["MAIL_SERVER_HOST"]
        port = self.config["MAIL_SERVER_PORT"]

        smtp: smtplib.SMTP

        if self.config["MAIL_SERVER_SSL"]:
            smtp = smtplib.SMTP_SSL(host, port)
        else:
            smtp = smtplib.SMTP(host, port)

        smtp.ehlo_or_helo_if_needed()

        if self.config["MAIL_SERVER_STARTTLS"]:
            smtp.starttls()

        if self.config["MAIL_SERVER_LOGIN"]:
            smtp.login(self.config["MAIL_SERVER_USER"], self.config["MAIL_SERVER_PW"])

        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = self.config["MAIL_SENDING_ADDRESS"]
        msg['To'] = recipient_address
        smtp.send_message(msg)


    def send_registraion_email(self, recipient_address: str, username: str, password: str):
        """
        Sends the registration email to the given recipient,
        containing the given token_url for mail verification
        """
        self.send_email(recipient_address,
                        gettext("registration mail subject"),
                        gettext("registration mail body with %(username)s and %(password)s",
                                username=username, password=password))
