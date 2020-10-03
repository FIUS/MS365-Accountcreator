"""
Main API Module
"""
from flask import Blueprint, request
from flask_restx import Api
from flask_babel import refresh as flask_babel_refresh
from werkzeug.datastructures import LanguageAccept

from .. import APP

AUTHORIZATIONS = {
    'jwt': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'Standard JWT access token.'
    },
    'jwt-refresh': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'JWT refresh token.'
    }
}

API_BLUEPRINT = Blueprint('api', __name__)


def inject_lang_from_header():
    """Inject the language defined in the 'lang' into the accepted languages of the request if present."""
    if 'lang' in request.headers:
        # inject language from custom header as first choice into request
        lang: str = request.headers.get('lang')
        values = (lang, 10), *request.accept_languages
        request.accept_languages = LanguageAccept(values)
        # Force refresh to make sure that the change is applied
        flask_babel_refresh()


API_BLUEPRINT.before_request(inject_lang_from_header)


API = Api(API_BLUEPRINT, version='0.1', title='ms365_accountcreator API', doc='/doc/',
          description='The FIUS ms365_accountcreator api.', authorizations=AUTHORIZATIONS, security='jwt')

# pylint: disable=C0413
from . import auth_helper, root, account_creation, email_verification

APP.register_blueprint(API_BLUEPRINT, url_prefix='/api')
