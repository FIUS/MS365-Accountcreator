from flask import render_template, request, url_for
from werkzeug.datastructures import LanguageAccept
from . import APP

from . import api

if APP.config.get('DEBUG', False):
    from . import debug_routes


@APP.route('/', defaults={'lang': ''})
@APP.route('/<string:lang>')
def default_route(lang):
    if lang:
        # inject language from url as first choice into request
        values = (lang, 1), *request.accept_languages
        request.accept_languages = LanguageAccept(values)
    email_regex = APP.config.get('EMAIL_ADDRESS_FILTER', '.*')
    url_email_verification = url_for("api.email_verification_email_verification")
    url_account_creation = url_for("api.account_creation_account_creation")
    return render_template('index.html', email_regex=email_regex,
        url_api_endpoint_email_verification=url_email_verification, url_api_endpoint_account_creation=url_account_creation)
