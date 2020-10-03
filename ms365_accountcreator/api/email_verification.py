"""
This module contains all API endpoints for the namespace 'email_verification'
"""
from typing import Dict
from flask import request
from flask_restx import Resource, abort

from . import API
from .api_models import EMAIL_VERIFICATION_POST, EMAIL_VERIFICATION_ANSWER

from .. import LOGIC

EMAIL_VERIFICATION_NS = API.namespace('email_verification', description='Verify email addresses', path='/email-verification')

@EMAIL_VERIFICATION_NS.route('/')
class EmailVerification(Resource):
    """
    The api class for verifying emails adresses
    """

    @EMAIL_VERIFICATION_NS.doc(body=EMAIL_VERIFICATION_POST, model=EMAIL_VERIFICATION_ANSWER)
    @EMAIL_VERIFICATION_NS.marshal_with(EMAIL_VERIFICATION_ANSWER)
    @EMAIL_VERIFICATION_NS.response(200, 'Ok.')
    # pylint: disable=R0201
    def post(self):
        """
        Verify the email address
        """
        email: str = request.get_json()['email']
        result: Dict = {'valid': True}
        if not LOGIC.verify_mail_is_legal(email):
            result = { 'valid': False, 'reason': "Email illegal"}
        elif not LOGIC.verify_mail_has_not_been_used(email):
            result = { 'valid': False, 'reason': "Email already used"}
        return result
