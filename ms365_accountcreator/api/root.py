"""
This module contains the root namespace
"""
from flask_restplus import Resource
from .api_models import ROOT_MODEL
from . import API

ROOT_NS = API.namespace('default', path='/')

@ROOT_NS.route('/')
class RootResource(Resource):
    """
    The API root element
    """

    @API.doc(security=None)
    @API.marshal_with(ROOT_MODEL)
    # pylint: disable=R0201
    def get(self):
        """
        Get the root element
        """
        return {}
