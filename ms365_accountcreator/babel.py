"""Module for setting up Babel support for flask app."""

from typing import Optional
from flask import Flask, request
from flask_babel import Babel, refresh as flask_babel_refresh
from werkzeug.datastructures import LanguageAccept

"""The list of locales to support."""
SUPPORTED_LOCALES = ["de", "en"]

BABEL = Babel()


@BABEL.localeselector
def get_locale():
    # try to guess the language from the user accept
    # header the browser transmits. We support SUPPORTED_LOCALES The best match wins.
    return request.accept_languages.best_match(SUPPORTED_LOCALES)


def inject_lang_from_header():
    """Inject the language defined in the 'lang' into the accepted languages of the request if present."""
    if 'lang' in request.headers:
        # inject language from custom header as first choice into request
        lang: str = request.headers.get('lang')
        values = (lang, 10), *request.accept_languages
        request.accept_languages = LanguageAccept(values)
        # Force refresh to make sure that the change is applied
        flask_babel_refresh()

def register_babel(app: Flask):
    """Register babel to enable translations for this app."""
    BABEL.init_app(app)
    app.before_request(inject_lang_from_header)
