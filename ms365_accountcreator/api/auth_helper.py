"""
Helper class for authentication in the api
"""
from functools import wraps

from flask_restplus import abort
from flask_jwt_extended import get_jwt_claims, get_jwt_identity
from flask_jwt_extended.exceptions import NoAuthorizationError
from jwt import ExpiredSignatureError, InvalidTokenError

from .. import JWT
from ..logging import AUTH_LOGGER, APP_LOGGER
from ..logic.auth import is_user_allowed_to_create_users

from . import API

class User:
    """
    The representation of a user
    """
    username: str
    uid_token: str

    def __init__(self, username: str, uid_token: str):
        self.username = username
        self.uid_token = uid_token

    def get_username(self) -> str:
        """
        Get the username
        """
        return self.username

    def get_uid_token(self) -> str:
        """
        Get the uid token
        """
        return self.uid_token

@JWT.user_claims_loader
def add_claims_to_access_token(identity: User):
    """
    Automatically get claims for access tokens
    """
    return {
        'uid_token': identity.get_uid_token(),
    }

@JWT.user_identity_loader
def user_identity_lookup(user: User):
    """
    Automatically get the username from the user
    """
    return user.get_username()

@JWT.expired_token_loader
@API.errorhandler(ExpiredSignatureError)
def expired_token():
    """
    Handler function for a expired token
    """
    message = 'Token is expired.'
    log_unauthorized(message)
    abort(401, message)


@JWT.invalid_token_loader
@API.errorhandler(InvalidTokenError)
def invalid_token(message: str):
    """
    Handler function for a invalid token
    """
    log_unauthorized(message)
    abort(401, message)


@JWT.unauthorized_loader
def unauthorized(message: str):
    """
    Handler function for a unauthorized api access
    """
    log_unauthorized(message)
    abort(401, message)


@JWT.needs_fresh_token_loader
def stale_token():
    """
    Handler function for a no more fresh token
    """
    message = 'The JWT Token is not fresh. Please request a new Token directly with the /auth resource.'
    log_unauthorized(message)
    abort(403, message)


@JWT.revoked_token_loader
def revoked_token():
    """
    Handler function for a revoked or invalid token
    """
    message = 'The Token has been revoked.'
    log_unauthorized(message)
    abort(401, message)


@API.errorhandler(NoAuthorizationError)
def missing_header(error):
    """
    Handler function for a NoAuthorizationError
    """
    log_unauthorized(error.message)
    return {'message': error.message}, 401


@API.errorhandler
def default_errorhandler(error):
    """
    Handler function for a logging all errors
    """
    APP_LOGGER.exception(error.message)
    return {'message': error.message}, 500


def log_unauthorized(message):
    """
    Logs unauthorized access
    """
    AUTH_LOGGER.debug('Unauthorized access: %s', message)


def requires_user_creator():
    """
    Check if the requesting user is a user creator.

    Must be applied after jwt_required decorator!
    """
    def reqires_user_creator_decorator(func):
        """
        Decorator function
        """
        @wraps(func)
        # pylint: disable=R1710
        def wrapper(*args, **kwargs):
            """
            Wrapper function
            """
            username = get_jwt_identity()
            uid_token = get_jwt_claims()["uid_token"]

            if not is_user_allowed_to_create_users(uid_token):
                AUTH_LOGGER.debug('Access to ressource with isufficient rights. Requires user creator. User: %s', username)
                abort(403, 'Only users with user creation privileges have access to this resource.')
            else:
                return func(*args, **kwargs)
        return wrapper
    return reqires_user_creator_decorator
