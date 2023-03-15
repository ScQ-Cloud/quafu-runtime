import json
from typing import Optional

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
        res = self._session.post(url, headers=headers, data=data)
        if res.status_code == 200:
            return res.status_code, res.json()
        else:
            return res.status_code, None

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

    def program_run(self,
                    program_id: str = None,
                    name: str = None,
                    backend: str = None,
                    params: dict = None):
        """
        Run a program on the runtime server.
        """
        url = self.get_url("programs_run")
        headers = {'Content-Type': 'application/json;charset=UTF-8', 'api_token': self._token}
        payload = {
            "program_id": program_id,
            "program_name": name,
            "backend": backend,
            "params": params
        }
        data = json.dumps(payload)
        res = self._session.post(url, headers=headers, data=data)
        if res.status_code == 200:
            return res.status_code, res.json()
        else:
            return res.status_code, None

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

    def job_result(self,
                   job_id: str):
        """
        Try to get result.

        TODO:
            USE WEBSOCKET.
        """
        url = self.get_url("get_result")
        headers = {'Content-Type': 'application/json;charset=UTF-8', 'api_token': self._token}
        payload = {
            "job_id": job_id,
        }
        data = json.dumps(payload)
        res = self._session.post(url, headers=headers, data=data)
        if res.status_code == 200:
            return res.status_code, res.json()
        else:
            return res.status_code, None

    def job_interim_results(self):
        pass

    def job_cancel(self):
        pass

    def job_status(self):
        pass

    def job_logs(self):
        pass

    def get_url(self, identifier: str) -> str:
        """Return the resolved URL for the specified identifier.

        Args:
            identifier: Internal identifier of the endpoint.

        Returns:
            The resolved URL of the endpoint (relative to the session base URL).
        """
        return "{}{}{}".format(self._url, "/", identifier)