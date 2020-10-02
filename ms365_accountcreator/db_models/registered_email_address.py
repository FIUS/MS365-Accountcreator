"""
Module containing database models for everything concerning the registered email adresses.
"""

import time

from .. import DB
from . import STD_STRING_SIZE

__all__ = ['RegisteredEmailAddress']

class RegisteredEmailAddress(DB.Model):
    """
    The representation of a RegisteredEmailAddress
    """

    __tablename__ = 'RegisteredEmailAddress'

    id = DB.Column(DB.Integer, primary_key=True)
    email = DB.Column(DB.String(STD_STRING_SIZE))
    ms365_created = DB.Column(DB.Boolean, default=False, nullable=False)
    timestamp = DB.Column(DB.Integer)

    def __init__(self, email: str, ms365_created: bool):
        self.email = email
        self.timestamp = int(time.time())
        self.ms365_created = ms365_created
