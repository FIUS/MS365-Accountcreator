"""
This module contains all API endpoints for the namespace 'voucher_verification'
"""
from typing import Dict
from flask.views import MethodView
from flask_babel import gettext


from .root import API_V1
from .models import VoucherVerificationRequest, VoucherVerificationAnswer, LangSchema

from ...logic import InvalidVoucherException, VoucherUsedUpException

from ... import LOGIC


@API_V1.route('/voucher-verification')
class VoucherVerification(MethodView):
    """
    The api class for verifying vouchers
    """

    @API_V1.arguments(VoucherVerificationRequest)
    @API_V1.arguments(LangSchema, location="headers")
    @API_V1.response(200, VoucherVerificationAnswer, description="Ok.")
    # pylint: disable=R0201
    def post(self, new_data, _lang_data):
        """
        Verify the voucher
        """
        token: str = new_data['voucher_token']
        try:
            voucher = LOGIC.load_voucher(token)
        except InvalidVoucherException:
            return {'valid': False, 'reason': gettext("Voucher invalid")}
        try:
            LOGIC.check_voucher(voucher)
        except VoucherUsedUpException:
            return {'valid': False, 'reason': gettext("Voucher used up")}
        return {'valid': True}
