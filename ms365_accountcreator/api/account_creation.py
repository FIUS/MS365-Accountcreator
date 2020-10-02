"""
This module contains all API endpoints for the namespace 'account_creation'
"""
from flask import request
from flask_restx import Resource, abort

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
        try:
            LOGIC.create_account(** request.get_json())
            return "", 204
        except EmailIllegalError:
            abort(400, "Email illegal")
        except EmailAlreadyUsedError:
            abort(400, "Email already used")
        except GraphApiError as err:
            abort(500, "Upstream API error")
            APP_LOGGER.error(err)
