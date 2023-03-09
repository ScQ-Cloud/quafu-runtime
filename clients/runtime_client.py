import json
from typing import Optional, Dict

import requests


class RuntimeClient:
    """
    Class for accessing Quafu runtime server.

    One RuntimeClient represent one session.
    So we can check cookie instead token.
    """
    def __init__(self,
                 token: str,
                 url: str
                 ):
        self._token = token
        self._url = url + "/runtime"
        self._session = requests.session()

    def program_upload(self,
                       program_data: str,
                       name: str,
                       backend: str,
                       group: str = None,
                       max_execution_time: Optional[int] = None,
                       description: Optional[str] = None,
                       is_public: bool = False,
                       ):
        """
        Upload a new program.

        Returns:
            JSON response.
        """
        url = self.get_url("programs_upload")
        headers = {'Content-Type': 'application/json;charset=UTF-8', 'api_token': self._token}
        payload = {
            "name": name,
            "data": program_data,
            "backend": backend,
            "group": group,
            "cost": max_execution_time,
            "description": description,
            "is_public": 1 if is_public is True else 2,
        }
        data = json.dumps(payload)
        return self._session.post(url, headers=headers, data=data).json()

    def program_update(self):
        """
        Update an existed program.
        """
        pass

    def program_delete(self):
        """
        Delete an existed program.
        """
        pass

    def program_run(self):
        """
        Run a program on the runtime server.
        """
        pass

    def program_get(self):
        """
        Get an existed program.
        """
        pass

    def program_validate(self):
        """
        Before upload to server, check the program.
        """
        pass

    def get_url(self, identifier: str) -> str:
        """Return the resolved URL for the specified identifier.

        Args:
            identifier: Internal identifier of the endpoint.

        Returns:
            The resolved URL of the endpoint (relative to the session base URL).
        """
        return "{}{}{}".format(self._url, "/", identifier)
