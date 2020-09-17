"""Module containing default config values."""

class Config(object):
    DEBUG = False
    TESTING = False
    RESTPLUS_VALIDATE = True
    JWT_CLAIMS_IN_REFRESH_TOKEN = True
    JWT_SECRET_KEY = ''
    SQLALCHEMY_DATABASE_URI = 'sqlite://:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DB_UNIQUE_CONSTRAIN_FAIL = 'UNIQUE constraint failed'
    URI_BASE_PATH = '/'

    LOGGING_CONFIGS = ['logging_config.json']

    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False
    RESTPLUS_JSON = {'indent': None}

    GRAPH_API_AUTH_AUTHORITY = "https://login.microsoftonline.com/00000000-0000-0000-0000-000000000000"
    GRAPH_API_AUTH_CLIENT_ID = "00000000-0000-0000-0000-000000000000"
    GRAPH_API_AUTH_PUBKEY_THUMBPRINT = "0000000000000000000000000000000000000000"
    GRAPH_API_AUTH_PRIVKEY_PATH = "/path/to/ms365AccountCreator.key"

class ProductionConfig(Config):
    pass


class DebugConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'
    JWT_SECRET_KEY = 'debug'

    LOGGING_CONFIGS = ['logging_config.json', 'logging_config_debug.json']


class TestingConfig(Config):
    TESTING = True
