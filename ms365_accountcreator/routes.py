from flask import render_template, request, url_for
from werkzeug.datastructures import LanguageAccept
from flask_babel import refresh as flask_babel_refresh
from flask_babel import get_locale
from . import APP

from . import api

if APP.config.get('DEBUG', False):
    from . import debug_routes

api.register_root_api(APP)

@APP.route('/', defaults={'lang': ''})
@APP.route('/<string:lang>')
def default_route(lang):
    if lang:
        # inject language from url as first choice into request
        values = (lang, 10), *request.accept_languages
        request.accept_languages = LanguageAccept(values)
        flask_babel_refresh()
    email_regex = APP.config.get('EMAIL_ADDRESS_FILTER', '.*')
    support_email = APP.config.get('SUPPORT_EMAIL', "")
    url_email_verification = url_for("api-v1.EmailVerification")
    url_account_creation = url_for("api-v1.AccountCreation")
    lang_used = "en"
    locale = get_locale()
    if locale is not None:
        lang_used = locale.language
    return render_template('index.html', email_regex=email_regex, lang = lang_used, support_email=support_email,
        url_api_endpoint_email_verification=url_email_verification, url_api_endpoint_account_creation=url_account_creation)
