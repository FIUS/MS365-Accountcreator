"""
This module contains all API endpoints for the namespace 'account_creation'
"""
from flask_smorest import abort
from flask.views import MethodView
from flask_babel import gettext
from smtplib import SMTPException

from .root import API_V1
from .models import AccountCreation, LangSchema

from ... import APP_LOGGER, LOGIC

from ...logic import EmailAlreadyUsedError, EmailIllegalError
from ...logic.graph_api import GraphApiError, NameFormatError

@API_V1.route('/account_creation')
class AccountCreation(MethodView):
    """
    The api class for actually creating accounts
    """

    @API_V1.arguments(AccountCreation, description="The account to create")
    @API_V1.arguments(LangSchema, location="headers")
    @API_V1.response(204, description='Created.')
    @API_V1.alt_response(400, None, description="Some of the given data is not usable.")
    @API_V1.alt_response(500, None, description="Upstream API error")
    # pylint: disable=R0201
    def post(self, new_data, _lang_data):
        """
        Create a new account
        """
        try:
            LOGIC.create_account(** new_data)
            return "", 204
        except EmailIllegalError:
            abort(400, message=gettext("Email illegal"))
        except EmailAlreadyUsedError:
            abort(400, message=gettext("Email already used"))
        except NameFormatError:
            abort(400, message=gettext("Name format not supported"))
        except GraphApiError as err:
            APP_LOGGER.error("GraphAPI error", err, new_data)
            abort(500, message=gettext("Upstream API error"))
        except SMTPException as err:
            APP_LOGGER.error("SMTP error", err, new_data)
            abort(500, message=gettext("Error with SMTP Server"))
