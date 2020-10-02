"""
The init file of the graph_api module
"""
from typing import Dict, Union

import requests
import json
import logging

from .authentication import Authenticator

#See https://docs.microsoft.com/en-us/graph/api/user-post-users?view=graph-rest-1.0&tabs=http
GRAPH_API_URL_CREATE_USER = "https://graph.microsoft.com/v1.0/users"
#See https://docs.microsoft.com/en-us/graph/api/user-assignlicense?view=graph-rest-1.0&tabs=http
GRAPH_API_URL_ASSIGN_LICENSE = "https://graph.microsoft.com/v1.0/users/{}/assignLicense"
#See https://docs.microsoft.com/en-us/graph/api/group-post-members?view=graph-rest-1.0&tabs=http
GRAPH_API_URL_GROUP_ADD_MEMBER = "https://graph.microsoft.com/v1.0/groups/{}/members/$ref"
#Found by getting the license on a manually created user
#See https://docs.microsoft.com/en-us/graph/api/user-list-licensedetails?view=graph-rest-1.0&tabs=http
GRAPH_API_UID_STUDENT_LICENSE = "314c4481-f395-4525-be8b-2ec4bb1e9d91"


class ApiAdapter:
    config: Dict
    auth: Authenticator = None
    user_mail_domain: str = ""
    
    def __init__(self, config: Dict): 
        self.config = config
        self.user_mail_domain = config['GRAPH_API_USER_MAIL_DOMAIN']

    def internal_get_auth(self) -> Authenticator:
        if self.auth is None:
            self.auth = Authenticator(self.config)
        return self.auth

    def create_user(self, firstName:str, lastName: str, password: str):
        """
        Create a user on the MS365 Tenant using the api.
        The parameters are:
         * firstName: The users first name
         * lastName: The users last name
         * password: The passord for the new user
        The displayName and mailNickname are constrcuted from the first and last name
        The userPrincipalName and mail attributes are constrcuted from the mailNickname and the mail domain configured in the config
        For more info about the parameters see: https://docs.microsoft.com/en-us/graph/api/user-post-users?view=graph-rest-1.0&tabs=http#request-body
        Raises a ValueError if the api returns a bad status code
        """
        if self.config['DEBUG_DONT_CONNECT_TO_API']:
            logging.getLogger(__name__).info("Would create user now but api connection is disabled. FirstName: %s, LastName: %s, Password: %s", firstName, lastName, password)
            return
        mailNickname = firstName.lower() + "." + lastName.lower()
        displayName = firstName + " " + lastName
        userPrincipalName = mailNickname + "@" + self.user_mail_domain
        payload = {
            'accountEnabled': True,
            'userPrincipalName': userPrincipalName,
            'displayName': displayName,
            'mailNickname': mailNickname,
            'passwordPolicies': "DisablePasswordExpiration",
            'passwordProfile': {
                'password': password,
                'forceChangePasswordNextSignIn': True
            },
            # Above are required, below optional
            'givenName': firstName,
            'surname': lastName,
            'usageLocation': "DE",
            'mail': userPrincipalName
        }
        r = self.internal_create_user(payload)
        if r.status_code != 201:
            raise ValueError("Failed to create user. Status code: {}, Server response: {}".format(r.status_code, r.text), json.loads(r.text))
        responseObject = json.loads(r.text)
        r = self.internal_assign_user_license(responseObject['id'], GRAPH_API_UID_STUDENT_LICENSE)
        if r.status_code != 200:
            raise ValueError("Failed to assign license to user. Status code: {}, Server response: {}".format(r.status_code, r.text), json.loads(r.text))
        for group_id in self.config['GRAPH_API_GROUPS_FOR_NEW_USERS']:
            r = self.internal_add_user_to_group(responseObject['id'], group_id)
            if r.status_code != 204:
                raise ValueError("Failed to add user to group. Status code: {}, Server response: {}".format(r.status_code, r.text), json.loads(r.text))
    
    def internal_create_user(self, payload: Dict[str, Union[str, int, float, bool]]) -> requests.Response:
        """
        Create a user on the MS365 Tenant using the api wih the given payload.
        Returns the response from the api as a requests.Response
        """
        return requests.post(GRAPH_API_URL_CREATE_USER, headers=self.internal_get_headers(), json=payload)

    def internal_assign_user_license(self, user_id, license_uid):
        """
        Assign the given license to the given user with all plans of the license enabled
        """
        payload = {
            'addLicenses': [{
                'disabledPlans': [],
                'skuId': license_uid
            }],
            'removeLicenses': []
        }
        url = GRAPH_API_URL_ASSIGN_LICENSE.format(user_id)
        return requests.post(url, headers=self.internal_get_headers(), json=payload)
    
    def internal_add_user_to_group(self, user_id, group_id):
        """
        Add the given user to the given group.
        """
        payload = {
            "@odata.id": "https://graph.microsoft.com/v1.0/directoryObjects/" + user_id
        }
        url = GRAPH_API_URL_GROUP_ADD_MEMBER.format(group_id)
        return requests.post(url, headers=self.internal_get_headers(), json=payload)

    def internal_get_headers(self):
        token = self.internal_get_auth().get_auth_token()
        headers = {
            'Authorization': 'Bearer ' + token
        }
        return headers
