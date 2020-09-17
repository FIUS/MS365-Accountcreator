"""
Module containing database models for everything concerning the registered email adresses.
"""
from typing import Dict

from json import loads, dumps

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
    timestamp = DB.Column(DB.Integer)

    def __init__(self, email: str):
        self.email = email
        self.timestamp = int(time.time())

    def get_data_json(self) -> Dict:
        """
        Get the json with the data about this object
        """
        print(str(self.data_json_string))
        data = loads(self.data_json_string)
        print(str(data))
        return data
