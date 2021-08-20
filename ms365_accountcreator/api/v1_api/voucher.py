"""
This module contains all API endpoints for the namespace 'voucher'
"""
from flask import url_for
from flask_smorest import abort
from flask.views import MethodView
from flask_babel import gettext


from .root import API_V1
from .models import Voucher, LangSchema

from ...db_models.vouchers import Voucher as VoucherDB
from ... import DB

class VoucherLinks():
    def __init__(self, voucher_id) -> None:
        self.self = url_for("api-v1.VoucherDetail", voucher_id=voucher_id,  _external=True)
class VoucherData():
    def __init__(self, voucher_db_obj: VoucherDB) -> None:
        self.id = voucher_db_obj.id
        self.links = VoucherLinks(self.id)
        self.name = voucher_db_obj.name
        self.description = voucher_db_obj.description
        self.user_lifetime = voucher_db_obj.user_lifetime
        self.user_deletion_date = voucher_db_obj.user_deletion_date
        self.voucher_total_uses = voucher_db_obj.voucher_total_uses
        self.token_encoded = voucher_db_obj.token_encoded
        self.voucher_current_uses = voucher_db_obj.voucher_current_uses

@API_V1.route('/voucher')
class VoucherList(MethodView):
    """
    The api class for the list of all vouchers
    """

    @API_V1.arguments(LangSchema, location="headers")
    @API_V1.response(200, Voucher(many=True), description='Ok.')
    def get(self, _lang_data):
        """
        Get all vouchers
        """
        return [VoucherData(voucher_db_obj) for voucher_db_obj in VoucherDB.query.all()]


    @API_V1.arguments(Voucher, description="The voucher to create")
    @API_V1.arguments(LangSchema, location="headers")
    @API_V1.response(200, Voucher, description='Created.')
    # pylint: disable=R0201
    def post(self, new_data, _lang_data):
        """
        Create a new voucher
        """
        new = VoucherDB(** new_data)
        DB.session.add(new)
        DB.session.commit()
        return VoucherData(new)

@API_V1.route('/voucher/<int:voucher_id>/')
class VoucherDetail(MethodView):
    """
    The api class for a single voucher
    """

    @API_V1.arguments(LangSchema, location="headers")
    @API_V1.response(200, Voucher, description='Ok.')
    @API_V1.alt_response(404, None, description="Voucher not found.")
    def get(self, _lang_data, voucher_id):
        """
        Get the voucher with the given voucher_id
        """
        voucher = VoucherDB.query.filter(VoucherDB.id == voucher_id).first()
        if voucher is None:
            abort(404, gettext('Voucher not found.'))
        return VoucherData(voucher)

    @API_V1.arguments(Voucher, description="The new")
    @API_V1.arguments(LangSchema, location="headers")
    @API_V1.response(200, Voucher, description='Updated.')
    @API_V1.alt_response(404, None, description="Voucher not found.")
    def put(self, new_data, _lang_data, voucher_id):
        """
        Update the voucher with the given voucher_id
        If one of the optional values is omitted, null is asumed.
        """
        voucher: VoucherDB = VoucherDB.query.filter(VoucherDB.id == voucher_id).first()
        if voucher is None:
            abort(404, gettext('Voucher not found.'))
        voucher.update(** new_data)
        DB.session.commit()
        return VoucherData(voucher)

    @API_V1.arguments(LangSchema, location="headers")
    @API_V1.response(204, description='Deleted.')
    @API_V1.alt_response(404, None, description="Voucher not found.")
    def delete(self, _lang_data, voucher_id):
        """
        Delete the voucher with the given voucher_id
        """
        voucher: VoucherDB = VoucherDB.query.filter(VoucherDB.id == voucher_id).first()
        if voucher is None:
            abort(404, gettext('Voucher not found.'))
        DB.session.delete(voucher)
        DB.session.commit()
        return "", 204
