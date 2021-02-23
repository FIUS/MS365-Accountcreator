"""Module containing all API schemas for the email verification API."""

import marshmallow as ma
from marshmallow.validate import Length, Email
from flask_babel import gettext

from ...util import MaBaseSchema, meta
from ....db_models import STD_STRING_SIZE

__all__ = [
    "EmailVerificationRequest",
    "EmailVerificationAnswer"
]

class EmailVerificationRequest(MaBaseSchema):
    email = ma.fields.Email(required=True, allow_none=False, metadata=meta('E-Mail to verify'), error_messages= {"invalid": gettext("Not a valid email.")},
                            validate=Length(0,STD_STRING_SIZE,error=gettext("Email to long.")))

class EmailVerificationAnswer(MaBaseSchema):
    valid = ma.fields.Boolean(required=True, allow_none=False, dump_only=True, metadata=meta('Whether the email is valid'))
    reason = ma.fields.String(required=True, allow_none=True, dump_only=True, metadata=meta('If it is invalid, the reason why it is invalid, null if it is valid'))
