"""Module containing default config values."""

class Config(object):
    DEBUG = False
    TESTING = False
    RESTPLUS_VALIDATE = True
    JWT_CLAIMS_IN_REFRESH_TOKEN = True
    JWT_SECRET_KEY = ''
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DB_UNIQUE_CONSTRAIN_FAIL = 'UNIQUE constraint failed'
    URI_BASE_PATH = '/'

    LOGGING_CONFIGS = ['logging_config.json']

    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False
    RESTPLUS_JSON = {'indent': None}

    DEBUG_DONT_CONNECT_TO_API=False

    GENERATED_PASSWORD_BYTES = 8

    # Regex as defined by https://docs.python.org/3/library/re.html
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

    DEBUG_DONT_CONNECT_TO_API=True

    LOGGING_CONFIGS = ['logging_config.json', 'logging_config_debug.json']


class TestingConfig(Config):
    TESTING = True
