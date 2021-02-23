"""Module containing all API schemas for the account creation API."""

import marshmallow as ma
from marshmallow.validate import Length, Email
from flask_babel import gettext

from ...util import MaBaseSchema, meta
from ....db_models import STD_STRING_SIZE

__all__ = [
    "AccountCreation"
]

class AccountCreation(MaBaseSchema):
    first_name = ma.fields.String(required=True, allow_none=False, metadata=meta('First name of the user'))
    last_name = ma.fields.String(required=True, allow_none=False, metadata=meta('Last name of the user'))
    email = ma.fields.Email(required=True, allow_none=False, metadata=meta('E-Mail to send the password to'), error_messages= {"invalid": gettext("Not a valid email.")},
                            validate=Length(0,STD_STRING_SIZE,error=gettext("Email to long.")))
