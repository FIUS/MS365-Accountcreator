"""
The init file of logic module
"""
from typing import Dict

import secrets
import re

from . import graph_api
from .email import Email

from .. import DB
from ..db_models.registered_email_address import RegisteredEmailAddress


class Logic:
    """
    The main logic class
    """
    config: Dict
    graph_api: graph_api.ApiAdapter
    email: Email

    def __init__(self, config: Dict):
        """
        Create a new logic class.
        Arguments:
         * config: A dict with configuration variables
        """
        self.config = config
        self.graph_api = graph_api.ApiAdapter(config)
        self.email = Email(config)

    def create_account(self, first_name: str, last_name: str, email: str):
        """
        Create a new account for the user with the given name and use the given email to send the password to
        Raises EmailIllegalError if the email is not legal
        Raises EmailAlreadyUsedError if the email has been used to create an account before
        Raises GraphApiError if the api returns an unexpected error
        Raises NameFormatError when the name is not legal
        """
        if not self.verify_mail_is_legal(email):
            raise EmailIllegalError("Email is not valid")
        if not self.verify_mail_has_not_been_used(email):
            raise EmailAlreadyUsedError("Email is already in use")
        password: str = "!1Aa" + secrets.token_urlsafe(self.config["GENERATED_PASSWORD_BYTES"])
        username: str = self.graph_api.create_user(first_name, last_name, password)
        self.email.send_registraion_email(email, username, password)
        DB.session.add(RegisteredEmailAddress(email, True))
        DB.session.commit()

    def verify_mail_is_legal(self, email: str) -> bool:
        """
        Verify that the given email fullfills the required format
        Returns the result as bool
        """
        return re.fullmatch(self.config['EMAIL_ADDRESS_FILTER'], email) is not None

    def verify_mail_has_not_been_used(self, email: str) -> bool:
        """
        Verify that the given email has not been used to create an account before
        Returns the result as bool
        """
        return RegisteredEmailAddress.query.filter(RegisteredEmailAddress.email == email).filter(RegisteredEmailAddress.ms365_created == True).first() is None

class EmailIllegalError(Exception):
    """
    Error raised when a given email is not legal
    """
    message: str
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

class EmailAlreadyUsedError(Exception):
    """
    Error raised when a given email was already used to create an account
    """
    message: str
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
