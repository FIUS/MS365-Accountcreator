"""
This module contains all API endpoints for the namespace 'email_verification'
"""
from typing import Dict
from flask.views import MethodView
from flask_babel import gettext

from .root import API_V1
from .models import EmailVerificationRequest, EmailVerificationAnswer, LangSchema

from ... import LOGIC


@API_V1.route('/email-verification')
class EmailVerification(MethodView):
    """
    The api class for verifying emails adresses
    """

    @API_V1.arguments(EmailVerificationRequest)
    @API_V1.arguments(LangSchema, location="headers")
    @API_V1.response(200, EmailVerificationAnswer, description="Ok.")
    # pylint: disable=R0201
    def post(self, new_data, _lang_data):
        """
        Verify the email address
        """
        email: str = new_data['email']
        result: Dict = {'valid': True}
        if not LOGIC.verify_mail_is_legal(email):
            result = {'valid': False, 'reason': gettext("Email illegal")}
        elif not LOGIC.verify_mail_has_not_been_used(email):
            result = {'valid': False, 'reason': gettext("Email already used")}
        return result
