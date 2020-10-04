"""Module containing default config values."""

from typing import Union, Type
from numbers import Number


class Config(object):
    DEBUG = False
    TESTING = False
    RESTPLUS_VALIDATE = True
    JWT_CLAIMS_IN_REFRESH_TOKEN = True
    JWT_SECRET_KEY = ''
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DB_UNIQUE_CONSTRAIN_FAIL = 'UNIQUE constraint failed'

    REVERSE_PROXY_COUNT = 0

    LOGGING_CONFIGS = ['logging_config.json']

    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False
    RESTPLUS_JSON = {'indent': None}

    DEBUG_DONT_CONNECT_TO_API = False

    GENERATED_PASSWORD_BYTES = 8

    # Should be regex compatible with https://docs.python.org/3/library/re.html
    # as well as https://www.w3schools.com/TAGS/att_input_pattern.asp
    EMAIL_ADDRESS_FILTER = ".*"

    GRAPH_API_AUTH_AUTHORITY = "https://login.microsoftonline.com/00000000-0000-0000-0000-000000000000"
    GRAPH_API_AUTH_CLIENT_ID = "00000000-0000-0000-0000-000000000000"
    GRAPH_API_AUTH_PUBKEY_THUMBPRINT = "0000000000000000000000000000000000000000"
    GRAPH_API_AUTH_PRIVKEY_PATH = "/path/to/ms365AccountCreator.key"

    GRAPH_API_USER_MAIL_DOMAIN = "example.onmicrosoft.com"
    GRAPH_API_GROUPS_FOR_NEW_USERS = ["00000000-0000-0000-0000-000000000000"]

    MAIL_SERVER_HOST = ""
    MAIL_SERVER_PORT = 25
    MAIL_SERVER_SSL = False
    MAIL_SERVER_STARTTLS = True
    MAIL_SERVER_LOGIN = True
    MAIL_SERVER_USER = ""
    MAIL_SERVER_PW = ""
    MAIL_SENDING_ADDRESS = ""

    SUPPORT_EMAIL = ""

class ProductionConfig(Config):
    pass


class DebugConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'
    JWT_SECRET_KEY = 'debug'

    DEBUG_DONT_CONNECT_TO_API = True

    LOGGING_CONFIGS = ['logging_config.json', 'logging_config_debug.json']


class TestingConfig(Config):
    TESTING = True


def coerce_value_to(value: Union[str, Number, bool], target_type: Union[Type[str], Type[Number], Type[bool], Type[int], Type[float]]):
    """Coearce a config value to the given target type if possible."""
    if isinstance(value, target_type):
        return value
    if target_type == bool:
        if isinstance(value, Number):
            return bool(value)
        if isinstance(value, str):
            return value.lower() == 'true' # assume anything not 'true' as false
        if value is None:
            return None
    if target_type == Number or target_type == float:
        if isinstance(value, bool):
            return 1 if value else 0
        if isinstance(value, str):
            if value.isdecimal():
                return int(value)
            else:
                try:
                    return float(value)
                except ValueError as exc:
                    raise ValueError(f'Could not coerce {value} to float.') from exc
    if target_type == int:
        if isinstance(value, bool):
            return 1 if value else 0
        if isinstance(value, str):
            if value.isdecimal():
                return int(value)
    raise ValueError(f'Could not coerce {value} to {target_type}.')
