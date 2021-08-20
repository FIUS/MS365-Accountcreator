"""
Module containing database models for everything concerning the vouchers.
"""
from secrets import randbits

from sqlalchemy_utils import UUIDType
from uuid import UUID
from base64 import b32decode, b32encode

from .. import DB, APP
from . import STD_STRING_SIZE

__all__ = ['Voucher', 'VoucherLicense', 'VoucherGroup']

token_bits = APP.config["VOUCHER_TOKEN_BITS"]
token_bytes = int((((8 - (token_bits % 8))%8) + token_bits) / 8)

class Voucher(DB.Model):
    """
    The representation of a Voucher

    It has:
     id: internal id
     token: token which is given to users
     name: name only seen by admin
     description: description only seen by admin
     user_lifetime: Time in seconds users live after creation by this token. None for forever
     user_deletion_date: Unix-Timestamp for when the user should be deleted. None for never
     voucher_total_uses: The number of uses this voucher has. None for infinte
     voucher_current_uses: the number of uses this voucher currently has.

    If both user_lifetime and user_deletion_date are set, user_lifetime takes precendence
    """

    __tablename__ = 'Voucher'

    id: int = DB.Column(DB.Integer, primary_key=True)
    token: bytes = DB.Column('token', DB.LargeBinary)
    name: str = DB.Column(DB.String(STD_STRING_SIZE), nullable=False)
    description: str = DB.Column(DB.Text(), nullable=False, default="")
    user_lifetime: int = DB.Column(DB.Integer, nullable=True)
    user_deletion_date: int = DB.Column(DB.Integer, nullable=True)
    voucher_total_uses: int = DB.Column(DB.Integer, nullable=True)
    voucher_current_uses: int = DB.Column(DB.Integer, nullable=False, default=0)

    def __init__(self, name: str, description: str, user_lifetime: int = None, user_deletion_date: int = None, voucher_total_uses: int = None):
        self.token = randbits(token_bits).to_bytes(token_bytes, 'little')
        self.update(name, description, user_lifetime, user_deletion_date, voucher_total_uses)

    def update(self, name: str, description: str, user_lifetime: int = None, user_deletion_date: int = None, voucher_total_uses: int = None):
        self.name = name
        self.description = description
        self.user_lifetime = user_lifetime
        self.user_deletion_date = user_deletion_date
        self.voucher_total_uses = voucher_total_uses

    @staticmethod
    def encode_token(token_raw: bytes) -> str:
        b: bytes = b32encode(token_raw)
        b = b.replace(b'I', b'8')
        b = b.replace(b'O', b'9')
        b = b.replace(b'=', b'')
        return b.decode("utf-8")

    @staticmethod
    def decode_token(token_urlsafe: str) -> bytes:
        b: bytes = token_urlsafe.encode("utf-8")
        b = b.replace(b'8', b'I')
        b = b.replace(b'9', b'O')
        l = len(b)
        to_pad = 8 - (l % 8)
        for i in range(to_pad):
            b += b'='
        return b32decode(b, casefold=True)

    @property
    def token_encoded(self) -> str:
        return self.encode_token(self.token)

class VoucherLicense(DB.Model):
    """
    Represents a MS365 license associated with a voucher.
    """

    __tablename__ = 'VoucherLicense'

    id = DB.Column(DB.Integer, primary_key=True)
    voucher_id = DB.Column(DB.Integer, DB.ForeignKey('Voucher.id'), nullable=False)
    license_uuid = DB.Column(UUIDType(binary=True), nullable=False)

    def __init__(self, voucher_id: int, license_uuid: UUID):
        self.voucher_id = voucher_id
        self.license_uuid = license_uuid

class VoucherGroup(DB.Model):
    """
    Represents a MS365 group associated with a voucher.
    """

    __tablename__ = 'VoucherGroup'

    id = DB.Column(DB.Integer, primary_key=True)
    voucher_id = DB.Column(DB.Integer, DB.ForeignKey('Voucher.id'), nullable=False)
    group_uuid = DB.Column(UUIDType(binary=True), nullable=False)

    def __init__(self, voucher_id: int, group_uuid: UUID):
        self.voucher_id = voucher_id
        self.group_uuid = group_uuid
