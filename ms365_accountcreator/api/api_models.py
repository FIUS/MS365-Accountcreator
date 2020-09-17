"""
Module containing models for whole API to use.
"""

from flask_restplus import fields
from . import API
from ..db_models import STD_STRING_SIZE
from .. import PROFILE_ADAPTER


ID = API.model('Id', {
    'id': fields.Integer(min=1, example=1, readonly=True, title="Internal identifier"),
})

ROOT_MODEL = API.model('RootModel', {
    
})