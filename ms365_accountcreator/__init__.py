"""
ms365_accountcreator init file.
"""
from os import environ
from os.path import abspath

from flask import Flask, request
from flask_babel import Babel
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.schema import MetaData
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

from .logging import init_logging, get_logging

APP = Flask(__name__, instance_relative_config=True)  # type: Flask
APP.config['MODE'] = environ.get('MODE', 'PRODUCTION').upper()
if APP.config['MODE'] == 'PRODUCTION':
    APP.config.from_object('ms365_accountcreator.config.ProductionConfig')
elif APP.config['MODE'] == 'DEBUG':
    APP.config.from_object('ms365_accountcreator.config.DebugConfig')
elif APP.config['MODE'] == 'TEST':
    APP.config.from_object('ms365_accountcreator.config.TestingConfig')

APP.config.from_pyfile('/etc/ms365_accountcreator.conf', silent=True)
APP.config.from_pyfile('ms365_accountcreator.conf', silent=True)
if 'CONFIG_FILE' in environ:
    APP.config.from_pyfile(environ.get('CONFIG_FILE', 'ms365_accountcreator.conf'), silent=True)

ENV_VARS = ['SQLALCHEMY_DATABASE_URI', 'JWT_SECRET_KEY', 'REVERSE_PROXY_COUNT']
for env_var in ENV_VARS:
    value = environ.get(env_var, APP.config.get(env_var))
    if value is None:
        pass
    elif value.lower() == "true":
        value = True
    elif value.lower() == "false":
        value = False
    elif value.isnumeric():
        value = int(value)
    APP.config[env_var] = value


SECRETS = ['JWT_SECRET_KEY']
for var in SECRETS:
    if var not in APP.config or len(APP.config[var]) == 0:
        raise ValueError("The secret " + var + " is not set!")

init_logging(APP)

r_p_count = APP.config['REVERSE_PROXY_COUNT']
if r_p_count > 0:
    APP.wsgi_app = ProxyFix(APP.wsgi_app, x_for=r_p_count, x_host=r_p_count, x_port=r_p_count, x_prefix=r_p_count, x_proto=r_p_count)

APP_LOGGER = get_logging().APP_LOGGER

# Setup DB with Migrations and bcrypt
APP_LOGGER.info('Connecting to database %s.', APP.config['SQLALCHEMY_DATABASE_URI'])
DB: SQLAlchemy
DB = SQLAlchemy(APP, metadata=MetaData(naming_convention={
    'pk': 'pk_%(table_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s',
    'ix': 'ix_%(table_name)s_%(column_0_name)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(column_0_name)s',
}))

MIGRATE: Migrate = Migrate(APP, DB)

# Setup JWT
JWT: JWTManager = JWTManager(APP)

# Setup Headers
CORS(APP)

# Setup Babel translations
BABEL = Babel(APP)


@BABEL.localeselector
def get_locale():
    # try to guess the language from the user accept
    # header the browser transmits. We support de/en. The best match wins.
    return request.accept_languages.best_match(['de', 'en'])


# pylint: disable=C0413
from . import db_models
# pylint: disable=C0413
from .logic import Logic
LOGIC: Logic = Logic(APP.config)
# pylint: disable=C0413
from . import routes
