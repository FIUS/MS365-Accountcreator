"""
The init file of logic module
"""
import base64
import binascii
import time
from typing import Dict

import logging
import secrets
import re
from sqlalchemy import select

from . import graph_api
from .email import Email

from .. import DB
from ..db_models.registered_email_address import RegisteredEmailAddress
from ..db_models.vouchers import Voucher, VoucherGroup, VoucherLicense


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

    def is_email_only_allowed_once(self) -> bool:
        """Returns True if it is configurerd, that an email can only be used once."""
        return self.config["ALLOW_EMAIL_ONLY_ONCE"]

    def load_voucher(self, voucher_token: str) -> Voucher:
        """
        Load the voucher with the given token.

        Raises InvalidVoucherException if the toke does not exist.
        """
        try:
            token_raw = Voucher.decode_token(voucher_token)
            voucher = Voucher.query.filter(Voucher.token == token_raw).first()
        except binascii.Error:
            voucher = None

        if voucher is None:
            time.sleep(1) # ratelimit
            raise InvalidVoucherException("This is an invalid voucher")
        return voucher

    def check_voucher(self, voucher: Voucher):
        """
        Checks the given voucher.

        Raises VoucherUsedUpException if the voucher is used up.
        """
        if voucher.voucher_total_uses is not None and voucher.voucher_current_uses >= voucher.voucher_total_uses:
            raise VoucherUsedUpException("This voucher has no uses left")


    def create_account(self, first_name: str, last_name: str, email: str, voucher_token: str = None):
        """
        Create a new account for the user with the given name and use the given email to send the password to
        If a voucher is given use the data contained in it.
        Raises EmailIllegalError if the email is not legal
        Raises EmailAlreadyUsedError if the email has been used to create an account before
        Raises GraphApiError if the api returns an unexpected error
        Raises NameFormatError when the name is not legal
        Raises VouchersNotEnabledException when a voucher is given but the vouchers are not enabled
        Raises NoVoucherGivenException when no voucher is given but vouchers are required
        Raises VoucherUsedUpException when the given voucher has no more uses left
        Raises InvalidVoucherException when the given voucher is invalid
        """
        if not self.verify_mail_is_legal(email):
            raise EmailIllegalError("Email is not valid")
        if self.is_email_only_allowed_once() and not self.verify_mail_has_not_been_used(email):
            raise EmailAlreadyUsedError("Email is already in use")

        if voucher_token is not None and not self.config["USE_VOUCHERS"]:
            raise VouchersNotEnabledException("Voucher was given even though vouchers are disabled")

        if voucher_token is None and self.config["REQUIRE_VOUCHERS"]:
            raise NoVoucherGivenException("No voucher was given even though vouchers are required")

        groups = self.config['GRAPH_API_GROUPS_FOR_NEW_USERS']
        licenses = self.config['GRAPH_API_LICENSES_FOR_NEW_USERS']

        if voucher_token is not None:
            voucher = self.load_voucher(voucher_token)
            licenses = VoucherLicense.query.filter(VoucherLicense.voucher_id == voucher.id).all()
            groups = VoucherGroup.query.filter(VoucherGroup.voucher_id == voucher.id).all()
            if voucher.voucher_total_uses is not None:
                self.check_voucher(voucher) # Raises exception if over limit
            voucher.voucher_current_uses += 1
            DB.session.commit()

        sucess = False
        password: str = "!1Aa" + secrets.token_urlsafe(self.config["GENERATED_PASSWORD_BYTES"])
        try:
            username: str = self.graph_api.create_user(first_name, last_name, password, licenses, groups)
            sucess = True
        finally: #Don't use except as to not catch the exception
            if not sucess:
                logging.getLogger(__name__).warn("Account creation failed for %s %s (%s)", first_name, last_name, email)
                if voucher_token is not None and voucher.voucher_total_uses is not None:
                    voucher.voucher_current_uses -= 1 # Don't count failed account creation
                    DB.session.commit()

        self.email.send_registraion_email(email, username, password)

        if self.is_email_only_allowed_once():
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

class VouchersNotEnabledException(Exception):
    """
    Error raised when a voucher is given but the vouchers are not enabled
    """
    message: str
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

class NoVoucherGivenException(Exception):
    """
    Error raised when no voucher is given but vouchers are required
    """
    message: str
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

class VoucherUsedUpException(Exception):
    """
    Error raised when voucher has no more uses left
    """
    message: str
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

class InvalidVoucherException(Exception):
    """
    Error raised when no voucher with that token exists
    """
    message: str
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
