"""
Main API Module
"""
from flask import Blueprint
from flask_restx import Api
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

API = Api(API_BLUEPRINT, version='0.1', title='ms365_accountcreator API', doc='/doc/',
          description='The FIUS ms365_accountcreator api.', authorizations=AUTHORIZATIONS, security='jwt')

# pylint: disable=C0413
from . import auth_helper, root

APP.register_blueprint(API_BLUEPRINT, url_prefix='/api')
