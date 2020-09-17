"""
The init file of the graph_api module
"""
from typing import Dict
from .authentication import Authenticator

class ApiAdapter:
    config: Dict
    auth: Authenticator = None
    
    def __init__(self, config: Dict): 
        self.config = config

    def getAuth(self) -> Authenticator:
        if self.auth is None:
            self.auth = Authenticator(self.config)
        return self.auth

    def testAuth(self):
        print(self.getAuth().get_auth_token())
