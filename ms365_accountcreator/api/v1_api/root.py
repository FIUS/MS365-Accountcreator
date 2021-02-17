"""
This module contains the root namespace
"""
from dataclasses import dataclass
from flask.helpers import url_for
from flask_smorest import Blueprint
from flask.views import MethodView
from .models import RootSchema

API_V1 = Blueprint("api-v1", __name__, url_prefix="/api/v1", description="The root of the api.")

@dataclass()
class RootData:
    account_creation: str
    email_verification: str
    voucher_verification: str
    voucher: str

@API_V1.route('/')
class RootView(MethodView):
    """
    The API root element
    """

    @API_V1.response(200, RootSchema())
    # pylint: disable=R0201
    def get(self):
        """
        Get the urls of the next endpoints
        """
        return RootData(account_creation=url_for("api-v1.AccountCreation", _external=True),
                        email_verification=url_for("api-v1.EmailVerification", _external=True),
                        voucher_verification=url_for("api-v1.VoucherVerification", _external=True),
                        voucher=url_for("api-v1.VoucherList", _external=True))
