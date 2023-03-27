import asyncio
import json
from typing import Optional

import requests
import websockets


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
        self._socket_url = 'ws://192.168.220.55:8765'
        self._session = requests.session()
        self.headers = {'Content-Type': 'application/json;charset=UTF-8', 'api_token': self._token}

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
        res = self._session.post(url, headers=self.headers, data=data)
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
        url = self.get_url("programs_run_deploy")
        payload = {
            "program_id": program_id,
            "program_name": name,
            "backend": backend,
            "params": params
        }
        data = json.dumps(payload)
        res = self._session.post(url, headers=self.headers, data=data)
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

    def job_result_nowait(self,
                          job_id: str):
        """
        Try to get result.

        TODO:
            USE WEBSOCKET.
        """
        url = self.get_url("get_result_nowait")
        payload = {
            "job_id": job_id,
        }
        data = json.dumps(payload)
        res = self._session.post(url, headers=self.headers, data=data)
        if res.status_code == 200:
            return res.status_code, res.json()
        else:
            return res.status_code, None

    async def get_result(self,
                         url: str,
                         job_id: str):
        count_retry = 0
        retries = 5
        flag = True
        while flag:
            try:
                # Connect to the WebSocket server
                print('Connecting to ', url)
                async with websockets.connect('ws://192.168.220.55:8765') as websocket:
                    print("try to get result...")
                    message = {'type': 'result', 'job_id': job_id, 'api_token': self._token}
                    await websocket.send(json.dumps(message))
                    # Process incoming messages
                    async for message in websocket:
                        mess = json.loads(message)
                        type_ = mess['type']
                        if type == 'failed':
                            print('Something wrong: ', mess['error'])
                            flag = False
                            break
                        elif type_ == 'done':
                            finish_time = mess['finish_time']
                            result = mess['result']
                            status = mess['status']
                            code = 'done' if status == 2 else 'error'
                            if code != 'done':
                                code = 'canceled' if status == 3 else 'failed'
                            print(f'Job done, status: {code} , finish_time: {finish_time} ,result: {result}')
                            flag = False
                            break
                        elif type_ == 'wait':
                            status = mess['status']
                            code = 'in queue' if status == 0 else 'running'
                            print(f'Job has not finished, status: {code}, waiting...')

            except websockets.WebSocketException as e:
                # An error has occurred; schedule a restart
                print("Connect to server Error: ", e)
                print("Trying reconnect...")
                await asyncio.sleep(1)
                count_retry += 1
                if retries <= count_retry:
                    print("Can't connect to server.")
                    break

    def job_result_wait(self,
                        job_id: str):
        """
        Wait until job done. Implemented by websockets.
        """
        url = self.get_url("get_result_wait")
        asyncio.get_event_loop().run_until_complete(self.get_result(url, job_id))

    def job_interim_results(self):
        pass

    def job_cancel(self, job_id):
        url = self.get_url("job_cancel")
        payload = {
            "job_id": job_id,
        }
        data = json.dumps(payload)
        res = self._session.post(url, headers=self.headers, data=data)
        if res.status_code == 200:
            return res.status_code, res.json()
        else:
            return res.status_code, None

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
        if '_wait' in identifier:
            return self._socket_url
        return "{}{}{}".format(self._url, "/", identifier)
