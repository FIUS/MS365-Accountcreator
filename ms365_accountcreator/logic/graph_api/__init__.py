"""
The init file of the graph_api module
"""
from typing import Dict, Union, Tuple

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
#See https://docs.microsoft.com/en-us/graph/api/user-get?view=graph-rest-1.0&tabs=http
GRAPH_API_URL_GET_USER = "https://graph.microsoft.com/v1.0/users/{}"
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
        Also adds the student license to the user and the user to the configured groups
        The parameters are:
         * firstName: The users first name
         * lastName: The users last name
         * password: The passord for the new user
        The displayName and mailNickname are constrcuted from the first and last name
        The userPrincipalName and mail attributes are constrcuted from the mailNickname and the mail domain configured in the config
        For more info about the parameters see: https://docs.microsoft.com/en-us/graph/api/user-post-users?view=graph-rest-1.0&tabs=http#request-body
        If the config var DEBUG_DONT_CONNECT_TO_API is set to true, this method just logs that it was called and returns
        Raises a GraphApiError if the api returns a bad status code
        """
        if self.config['DEBUG_DONT_CONNECT_TO_API']:
            logging.getLogger(__name__).info("Would create user now but api connection is disabled. FirstName: %s, LastName: %s, Password: %s", firstName, lastName, password)
            return

        found_free_user: bool = False
        user_deduplicate_number: int = 1
        while not found_free_user:
            _, _, userPrincipalName = self.internal_get_user_attrs(firstName, lastName, user_deduplicate_number)
            r = self.internal_get_user(userPrincipalName)
            if r.status_code == 404:
                found_free_user = True
            elif r.status_code > 299:
                raise GraphApiError("Failed to check if user name is free.", r.status_code, r.text)
            else:
                # User exists
                user_deduplicate_number += 1

        r: requests.Response = self.internal_create_user(firstName, lastName, password, user_deduplicate_number)

        responseObject = json.loads(r.text)
        r = self.internal_assign_user_license(responseObject['id'], GRAPH_API_UID_STUDENT_LICENSE)
        if r.status_code > 299:
            raise GraphApiError("Failed to assign license to user.", r.status_code, r.text)
        for group_id in self.config['GRAPH_API_GROUPS_FOR_NEW_USERS']:
            r = self.internal_add_user_to_group(responseObject['id'], group_id)
            if r.status_code > 299:
                raise GraphApiError("Failed to add user to group.", r.status_code, r.text)

    def internal_get_user_attrs(self, firstName:str, lastName: str, user_deduplicate_number: int) -> Tuple[str]:
        """
        Returns a tuple of mailNickname, displayName and userPrincipalName
        """
        mailNickname = firstName.lower() + "." + lastName.lower()
        if user_deduplicate_number > 1:
            mailNickname = mailNickname + "." + str(user_deduplicate_number)
        displayName = firstName + " " + lastName
        userPrincipalName = mailNickname + "@" + self.user_mail_domain
        return mailNickname, displayName, userPrincipalName

    def internal_create_user(self, firstName:str, lastName: str, password: str, user_deduplicate_number: int) -> requests.Response:
        """
        Create a user on the MS365 Tenant using the api.
        The parameters are:
         * firstName: The users first name
         * lastName: The users last name
         * password: The passord for the new user
        The displayName and mailNickname are constrcuted from the first and last name
        The userPrincipalName and mail attributes are constrcuted from the mailNickname and the mail domain configured in the config
        For more info about the parameters see: https://docs.microsoft.com/en-us/graph/api/user-post-users?view=graph-rest-1.0&tabs=http#request-body
        Returns the response from the api as a requests.Response
        Raises a GraphApiError if the api returns a bad status code
        """
        mailNickname, displayName, userPrincipalName = self.internal_get_user_attrs(firstName, lastName, user_deduplicate_number)
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
        r = self.internal_create_user_with_payload(payload)
        if r.status_code > 299:
            raise GraphApiError("Failed to create user.", r.status_code, r.text)
        return r

    def internal_create_user_with_payload(self, payload: Dict[str, Union[str, int, float, bool]]) -> requests.Response:
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

    def internal_get_user(self, user_id):
        """
        Get the given user
        The user_id may be it's id or it's userPrincipalName
        """
        url = GRAPH_API_URL_GET_USER.format(user_id)
        return requests.get(url, headers=self.internal_get_headers())

    def internal_get_headers(self):
        token = self.internal_get_auth().get_auth_token()
        headers = {
            'Authorization': 'Bearer ' + token
        }
        return headers

class GraphApiError(Exception):
    """
    Error representing an api error
    """
    status: int
    responseText: str
    responseData: Dict = None
    message: str
    def __init__(self, message: str, status: int, response: str):
        self.status = status
        self.message = message
        self.responseText = response
        errorMessage: str = None
        try:
            self.responseData = json.loads(response)
            errorMessage = self.responseData.get("error", {}).get("message", None)
        except:
            pass
        cause: str = ""
        if errorMessage is not None:
            cause = "{} StatusCode: {}, ServerErrorMessage: {}".format(message, status, errorMessage)
        else:
            cause = "{} StatusCode: {}, ServerRespone: {}".format(message, status, response)

        super().__init__(cause)
