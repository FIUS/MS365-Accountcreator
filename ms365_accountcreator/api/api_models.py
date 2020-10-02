"""
Module containing models for whole API to use.
"""

from flask_restx import fields
from . import API
from ..db_models import STD_STRING_SIZE

ID = API.model('Id', {
    'id': fields.Integer(min=1, example=1, readonly=True, title="Internal identifier"),
})

ROOT_MODEL = API.model('RootModel', {
    'account_creation': fields.Url('api.account_creation_account_creation'),
    'email_verification': fields.Url('api.email_verification_email_verification')
})

ACCOUNT_CREATION_POST = API.model('AccountCreationPOST', {
    'first_name': fields.String(title="First name of the user"),
    'last_name': fields.String(title="Last name of the user"),
    'email': fields.String(max_length=STD_STRING_SIZE, title="E-Mail to send the password to")
})

EMAIL_VERIFICATION_POST = API.model('EmailVerificationPOST', {
    'email': fields.String(max_length=STD_STRING_SIZE, title="E-Mail to verify")
})
