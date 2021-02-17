"""Module containing all schemas of the API."""

import marshmallow as ma
from marshmallow import validate
from flask_babel import gettext

from ...util import MaBaseSchema, meta
from ....babel import SUPPORTED_LOCALES

from .account_creation import *
from .email_verification import *
from .vouchers import *


class RootSchema(MaBaseSchema):
    account_creation = ma.fields.Url(required=True, allow_none=False, dump_only=True)
    email_verification = ma.fields.Url(required=True, allow_none=False, dump_only=True)
    voucher_verification = ma.fields.Url(required=True, allow_none=False, dump_only=True)
    voucher = ma.fields.Url(required=True, allow_none=False, dump_only=True)

class LangSchema(MaBaseSchema):
    lang = ma.fields.String(required=False, allow_none=False, load_only=True, metadata=meta('Language for the response'),
                            validate=validate.OneOf(SUPPORTED_LOCALES, error=gettext("Unsupported language.")))
