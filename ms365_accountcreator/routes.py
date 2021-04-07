from os import path
from flask import render_template, request, url_for
from werkzeug.datastructures import LanguageAccept
from flask_babel import refresh as flask_babel_refresh
from flask_babel import get_locale
from . import APP

from . import api
from .db_models.vouchers import Voucher

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
    voucher = request.args.get("voucher", None)
    email_regex = APP.config.get('EMAIL_ADDRESS_FILTER', '.*')
    support_email = APP.config.get('SUPPORT_EMAIL', "")
    voucher_enabled = APP.config.get('USE_VOUCHERS', False)
    voucher_required = APP.config.get('REQUIRE_VOUCHERS', False)
    url_voucher_verification = url_for("api-v1.VoucherVerification")
    url_email_verification = url_for("api-v1.EmailVerification")
    url_account_creation = url_for("api-v1.AccountCreation")
    lang_used = "en"
    locale = get_locale()
    if locale is not None:
        lang_used = locale.language
    return render_template('index.html', email_regex=email_regex, lang = lang_used, support_email=support_email,
        url_api_endpoint_email_verification=url_email_verification, url_api_endpoint_account_creation=url_account_creation,
        voucher_enabled=voucher_enabled, voucher_required=voucher_required, url_api_endpoint_voucher_verification=url_voucher_verification,
        voucher_token=voucher)

@APP.route('/voucher/', defaults={'lang': ''})
@APP.route('/voucher/<string:lang>')
def voucher_route(lang):
    if lang:
        # inject language from url as first choice into request
        values = (lang, 10), *request.accept_languages
        request.accept_languages = LanguageAccept(values)
        flask_babel_refresh()
    lang_used = "en"
    locale = get_locale()
    if locale is not None:
        lang_used = locale.language

    with open(path.join(APP.root_path, "templates", "voucher_list_entry_template.html")) as f:
        voucher_list_entry_template = f.read()

    vouchers = Voucher.query.all()
    return render_template('voucher.html', lang = lang_used, vouchers=vouchers, voucher_list_entry_template=voucher_list_entry_template)
