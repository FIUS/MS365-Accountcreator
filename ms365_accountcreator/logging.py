"""
Module for logging
"""
from sys import modules

from logging import Logger, getLogger
from logging.config import dictConfig

from json import load
from flask import Flask
from flask.logging import create_logger

APP_LOGGER: Logger = None
AUTH_LOGGER: Logger = None

THIS = modules[__name__]

def dict_merge(a, b):
    """
    Merge to dicts
    """
    if not isinstance(b, dict):
        return b
    result = a
    for key in b.keys():
        value = b[key]
        if key in result and isinstance(result[key], dict):
            result[key] = dict_merge(result[key], value)
        else:
            result[key] = value
    return result

def init_logging(app: Flask):
    """
    Init the logging
    """
    result_dict = {}

    for config_file in app.config['LOGGING_CONFIGS']:
        file_handle = open(config_file, 'r')
        new_dict = load(file_handle)
        result_dict = dict_merge(result_dict, new_dict)

    dictConfig(result_dict)

    THIS.APP_LOGGER = create_logger(app)
    THIS.AUTH_LOGGER = getLogger('flask.app.auth')

    APP_LOGGER.debug('Debug logging enabled')

def get_logging():
    """
    Get the logging module
    """
    return THIS
    