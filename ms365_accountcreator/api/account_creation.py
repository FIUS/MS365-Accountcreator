"""
This module contains all API endpoints for the namespace 'account_creation'
"""
from flask import request
from flask_restx import Resource, abort
from flask_babel import gettext
from werkzeug.datastructures import LanguageAccept
from flask_babel import refresh as flask_babel_refresh


from . import API
from .api_models import ACCOUNT_CREATION_POST

from .. import APP_LOGGER, LOGIC

from ..logic import EmailAlreadyUsedError, EmailIllegalError
from ..logic.graph_api import GraphApiError

ACCOUNT_CREATION_NS = API.namespace('account_creation', description='Create accounts', path='/account_creation')

@ACCOUNT_CREATION_NS.route('/')
class AccountCreation(Resource):
    """
    The api class for actually creating accounts
    """

    @ACCOUNT_CREATION_NS.doc(body=ACCOUNT_CREATION_POST)
    @ACCOUNT_CREATION_NS.response(204, 'Created.')
    @ACCOUNT_CREATION_NS.response(400, "Email illegal")
    @ACCOUNT_CREATION_NS.response(400, "Email already used")
    @ACCOUNT_CREATION_NS.response(500, "Upstream API error")
    # pylint: disable=R0201
    def post(self):
        """
        Create a new account
        """
        if 'lang' in request.headers:
            # inject language from custom header as first choice into request
            lang: str = request.headers.get('lang')
            values = (lang, 10), *request.accept_languages
            request.accept_languages = LanguageAccept(values)
            flask_babel_refresh()

        try:
            LOGIC.create_account(** request.get_json())
            return "", 204
        except EmailIllegalError:
            abort(400, gettext("Email illegal"))
        except EmailAlreadyUsedError:
            abort(400, gettext("Email already used"))
        except GraphApiError as err:
            abort(500, gettext("Upstream API error"))
            APP_LOGGER.error(err)
