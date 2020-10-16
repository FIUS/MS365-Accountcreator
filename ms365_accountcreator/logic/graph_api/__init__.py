"""
The init file of the graph_api module
"""
from typing import Dict, Union, Tuple

import json
import logging
import requests
import unicodedata

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
    """
    The api adapter for the MS graph api
    """
    config: Dict
    auth: Authenticator = None
    user_mail_domain: str = ""

    def __init__(self, config: Dict):
        """
        Create a new api adpater.
        Arguments:
         * config: A dict with configuration variables
        """
        self.config = config
        self.user_mail_domain = config['GRAPH_API_USER_MAIL_DOMAIN']

    def internal_get_auth(self) -> Authenticator:
        if self.auth is None:
            self.auth = Authenticator(self.config)
        return self.auth

    def create_user(self, first_name: str, last_name: str, password: str):
        """
        Create a user on the MS365 Tenant using the api.
        Also adds the student license to the user and the user to the configured groups
        The parameters are:
         * first_name: The users first name
         * last_name: The users last name
         * password: The passord for the new user
        The attributes displayName and mailNickname are constrcuted from the first and last name
        The attributes userPrincipalName and mail are constructed from the mailNickname and the domain from the config
        For more info about the parameters see:
        https://docs.microsoft.com/en-us/graph/api/user-post-users?view=graph-rest-1.0&tabs=http#request-body
        If the config var DEBUG_DONT_CONNECT_TO_API is set to true, this method just logs that it was called and returns
        Returns the userPrincipalName on success
        Raises a NameFormatError if the name is illegal
        Raises a GraphApiError if the api returns a bad status code
        """
        if self.config['DEBUG_DONT_CONNECT_TO_API']:
            logging.getLogger(__name__).info(
                "Would create user now but api connection is disabled. FirstName: %s, LastName: %s, Password: %s", 
                first_name, last_name, password)
            return "username"

        found_free_user: bool = False
        user_deduplicate_number: int = 1
        user_attrs: Tuple = ()
        while not found_free_user:
            user_attrs = self.internal_get_user_attrs(first_name, last_name, user_deduplicate_number, password)
            response = self.internal_get_user(user_attrs[4])
            if response.status_code == 404:
                found_free_user = True
            elif response.status_code > 299:
                raise GraphApiError("Failed to check if user name is free.", response.status_code, response.text)
            else:
                # User exists
                user_deduplicate_number += 1

        response: requests.Response = self.internal_create_user(user_attrs)

        response_object = json.loads(response.text)
        response = self.internal_assign_user_license(response_object['id'], GRAPH_API_UID_STUDENT_LICENSE)
        if response.status_code > 299:
            raise GraphApiError("Failed to assign license to user.", response.status_code, response.text)
        for group_id in self.config['GRAPH_API_GROUPS_FOR_NEW_USERS']:
            response = self.internal_add_user_to_group(response_object['id'], group_id)
            if response.status_code > 299:
                raise GraphApiError("Failed to add user to group.", response.status_code, response.text)
        return user_attrs[4]

    def internal_normalize(self, token: str):
        '''Normalize the given Token.'''
        # strip all ' characters that don't occur inside the word
        # leaves I'M intact but not house'
        token = token.strip("'''")
        # lowercase everything
        token = token.lower()
        # replace umlauts
        token = token.replace('ä', 'ae').replace('ü', 'ue').replace('ö', 'oe').replace('ß', 'ss')
        # split diacritics like axons from letters (one char with axon becomes
        # two chars: axon+basechar)
        token = unicodedata.normalize('NFKD', token)
        # remove all diacritics
        token = ''.join(c for c in token if unicodedata.combining(c) == 0)
        # remove any remaining non ascii characters
        token = token.encode('ascii', 'ignore').decode('ascii')
        token = token.replace(' ', '.')
        return token

    def internal_get_user_attrs(self, first_name: str, last_name: str, user_deduplicate_number: int, password: str) -> Tuple[str]:
        """
        Get a tuple of the relevant attributes for a user
        The parameters are:
         * first_name: The users first name
         * last_name: The users last name
         * user_deduplicate_number: A number, which, if it is greater than one, will be appendend to the unique names
         * password: The passord for the new user
        The attributes displayName and mailNickname are constrcuted from the first and last name
        The attributes userPrincipalName and mail are constructed from the mailNickname and the domain from the config
        For more info about the parameters see:
        https://docs.microsoft.com/en-us/graph/api/user-post-users?view=graph-rest-1.0&tabs=http#request-body
        Returns a tuple of firstName, lastName, mailNickname, displayName, userPrincipalName and password
        Raises NameFormatError when the name is not legal
        """
        first_name = first_name.strip()
        last_name = last_name.strip()
        mail_nickname = self.internal_normalize(first_name) + "." + self.internal_normalize(last_name)
        if len(mail_nickname) < 3:
            raise NameFormatError("Name invalid")
        if user_deduplicate_number > 1:
            mail_nickname = mail_nickname + "." + str(user_deduplicate_number)
        display_name = first_name + " " + last_name
        user_principal_name = mail_nickname + "@" + self.user_mail_domain
        return first_name, last_name, mail_nickname, display_name, user_principal_name, password

    def internal_create_user(self, user_attrs: Tuple) -> requests.Response:
        """
        Create a user on the MS365 Tenant using the api.
        Also adds the student license to the user and the user to the configured groups
        The parameters are:
         * user_attrs: A dict with the attributes for the new user as returned by internal_get_user_attrs
        Returns the response from the api as a requests.Response
        Raises a GraphApiError if the api returns a bad status code
        """
        first_name, last_name, mail_nickname, display_name, user_principal_name, password = user_attrs
        payload = {
            'accountEnabled': True,
            'userPrincipalName': user_principal_name,
            'displayName': display_name,
            'mailNickname': mail_nickname,
            'passwordPolicies': "DisablePasswordExpiration",
            'passwordProfile': {
                'password': password,
                'forceChangePasswordNextSignIn': True
            },
            # Above are required, below optional
            'givenName': first_name,
            'surname': last_name,
            'usageLocation': "DE",
            'mail': user_principal_name
        }
        response = self.internal_create_user_with_payload(payload)
        if response.status_code > 299:
            raise GraphApiError("Failed to create user.", response.status_code, response.text)
        return response

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
    response_text: str
    response_data: Dict = None
    message: str
    def __init__(self, message: str, status: int, response: str):
        self.status = status
        self.message = message
        self.response_text = response
        error_message: str = None
        try:
            self.response_data = json.loads(response)
            error_message = self.response_data.get("error", {}).get("message", None)
        except json.decoder.JSONDecodeError:
            pass
        cause: str = ""
        if error_message is not None:
            cause = "{} StatusCode: {}, ServerErrorMessage: {}".format(message, status, error_message)
        else:
            cause = "{} StatusCode: {}, ServerRespone: {}".format(message, status, response)

        super().__init__(cause)

class NameFormatError(Exception):
    """
    Error raised when invlaid name is given
    """
    message: str
    def __init__(self, message: str,):
        self.message = message
        super().__init__(message)