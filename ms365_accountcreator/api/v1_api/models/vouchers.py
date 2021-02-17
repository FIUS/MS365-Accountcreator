"""Module containing all API schemas for the account creation API."""

import marshmallow as ma
from marshmallow.validate import Length, Email
from flask_babel import gettext

from ...util import MaBaseSchema, meta
from ....db_models import STD_STRING_SIZE

__all__ = [
    "VoucherVerificationRequest",
    "VoucherVerificationAnswer",
    "Voucher"
]

class VoucherVerificationRequest(MaBaseSchema):
    voucher_token = ma.fields.String(required=True, allow_none=False, metadata=meta("Voucher token to verify"))

class VoucherVerificationAnswer(MaBaseSchema):
    valid = ma.fields.Boolean(required=True, allow_none=False, dump_only=True, metadata=meta('Whether the voucher is valid'))
    reason = ma.fields.String(required=True, allow_none=True, dump_only=True, metadata=meta('If it is invalid, the reason why it is invalid, null if it is valid'))

class VoucherLinks(MaBaseSchema):
    self = ma.fields.Url(required=True, allow_none=False, dump_only=True, metadata=meta("Link to this object"))
class Voucher(MaBaseSchema):
    id = ma.fields.Integer(required=True, allow_none=False, dump_only=True, metadata=meta("The id of the voucher."))
    links = ma.fields.Nested(VoucherLinks, required=True, allow_none=False, dump_only=True, metadata=meta("Relevant links for this object."))
    name = ma.fields.String(required=True, allow_none=False, validate=Length(0,STD_STRING_SIZE,error=gettext("Name to long.")), metadata=meta("The name of the voucher"))
    description = ma.fields.String(required=True, allow_none=False, metadata=meta("The description of the voucher"))
    user_lifetime = ma.fields.Integer(required=False, allow_none=True, metadata=meta("The lifetime in seconds that users created by this voucher should live. Omit or null for infinite."))
    voucher_total_uses = ma.fields.Integer(required=False, allow_none=True, metadata=meta("The number of times this voucher can be used. Omit or null for infinite."))
    token_encoded = ma.fields.String(required=True, allow_none=False, dump_only=True, data_key='token', metadata=meta("The token of the voucher"))
    voucher_current_uses = ma.fields.Integer(required=True, allow_none=False, dump_only=True, metadata=meta("The number of times this voucher has been used."))
