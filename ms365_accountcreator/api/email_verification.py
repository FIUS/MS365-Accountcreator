"""
This module contains all API endpoints for the namespace 'email_verification'
"""
from flask import request
from flask_restx import Resource, abort

from . import API
from .api_models import EMAIL_VERIFICATION_POST

from .. import LOGIC

EMAIL_VERIFICATION_NS = API.namespace('email_verification', description='Verify email addresses', path='/email-verification')

@EMAIL_VERIFICATION_NS.route('/')
class EmailVerification(Resource):
    """
    The api class for verifying emails adresses
    """

    @EMAIL_VERIFICATION_NS.doc(body=EMAIL_VERIFICATION_POST)
    @EMAIL_VERIFICATION_NS.response(204, 'Valid.')
    @EMAIL_VERIFICATION_NS.response(400, "Email illegal")
    @EMAIL_VERIFICATION_NS.response(400, "Email already used")
    # pylint: disable=R0201
    def post(self):
        """
        Verify the email address
        """
        email: str = request.get_json()['email']
        if not LOGIC.verify_mail_is_legal(email):
            abort(400, "Email illegal")
        if not LOGIC.verify_mail_has_not_been_used(email):
            abort(400, "Email already used")
        return "", 204
