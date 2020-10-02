"""
The init file of logic module
"""
from typing import Dict

import secrets

from . import graph_api
from .email import Email

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

    def create_account(self, first_name: str, last_name: str, email_to_send_pw_to: str):
        """
        Create a new account for the user with the given name and email
        """
        password: str = "!1Aa" + secrets.token_urlsafe(self.config["GENERATED_PASSWORD_BYTES"])
        username: str = self.graph_api.create_user(first_name, last_name, password)
        self.email.send_registraion_email(email_to_send_pw_to, username, password)
