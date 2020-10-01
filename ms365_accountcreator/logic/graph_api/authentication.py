"""
The file for authentication for the graph api
"""
from typing import Dict
from msal import ConfidentialClientApplication

AUTHENTICATION_SCOPE = [ "https://graph.microsoft.com/.default" ]


class Authenticator:
    app: ConfidentialClientApplication

    def __init__(self, config: Dict):
        client_id: str = config['GRAPH_API_AUTH_CLIENT_ID']
        authority: str = config['GRAPH_API_AUTH_AUTHORITY']
        thumprint: str = config['GRAPH_API_AUTH_PUBKEY_THUMBPRINT']
        privKeyPath: str = config['GRAPH_API_AUTH_PRIVKEY_PATH']

        client_credential: dict = {
            "thumbprint": thumprint, "private_key": open(privKeyPath).read()}

        self.app = ConfidentialClientApplication(
            client_id=client_id, authority=authority, client_credential=client_credential)

    def get_auth_token(self) -> str:
        """
        Returns a valid auth_token or throws a value exception
        """
        result = None
        # Check in cache
        result = self.app.acquire_token_silent(
            AUTHENTICATION_SCOPE, account=None)

        if not result:
            print("Getting new token")
            result = self.app.acquire_token_for_client(
                scopes=AUTHENTICATION_SCOPE)
        if "access_token" in result:
            return result["access_token"]
        else:
            print(result.get("error"))
            print(result.get("error_description"))
            # You may need this when reporting a bug
            print(result.get("correlation_id"))
            raise ValueError(result)
