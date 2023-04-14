from clients.runtime_client import RuntimeClient
from rtexceptions.rtexceptions import ArgsException, JobNotFoundException, NotAuthorizedException, RunFailedException


class Job:
    """
    Class for a job instance running on runtime server.
    Use Job instance to get result of an execution.
    """

    def __init__(self,
                 status: int,
                 api_client: RuntimeClient,
                 backend: str,
                 creation_date: str,
                 job_id: str = None,
                 program_id: str = None,
                 params: str = None,
                 ):
        self.params = params
        self._client = api_client
        self.backend = backend
        self._status_map = {0: "In Queue", 1: "Running", 2: "Completed", 3: "Canceled", 4: "Failed"}
        self._job_id = job_id
        self._program_id = program_id
        self._creation_date = creation_date
        self._status = self._status_map[status]
        self._error_msg = None
        self._result = None
        self._finish_time = None
        self._logs = None

    #def result(self,
    #           wait: bool):
    #    """
    #    Get the result from server. It will wait until job stop.
    #    """
    #    if self._job_id is None:
    #        raise ArgsException("job_id is needed.")
    #    job_id = self.job_id()
    #    if self._result is not None:
    #        return{
    #            'result': self._result,
    #            'finished_time': self._finish_time,
    #            'status': self._status
    #        }
    #    if wait:
    #        status, finish_time, result = self._client.job_result_wait(job_id)
    #        if status != -1:
    #            self._status = self._status_map[status]
    #            self._finish_time = finish_time
    #            self._result = result
    #    else:
    #        status_code, response = self._client.job_result_nowait(
    #            job_id=job_id
    #        )
    #        if status_code == 404:
    #            raise JobNotFoundException(
    #                f"Job not found: {job_id}"
    #            ) from None
    #        elif status_code == 405:
    #            raise NotAuthorizedException(
    #                f"You are not the owner of Job:{job_id}"
    #            )from None
    #        elif status_code != 200:
    #            raise RunFailedException(f"Failed to get result: {job_id}") from None
    #        # self._result = response[]
    #        self._result = response['result']
    #        self._status = self._status_map[response['status']]
    #        self._finish_time = response['finish_time']
    #        return response

    def result(self,
               wait: bool):
        """
        Get the result from server. It will wait until job stop.
        """
        if self._job_id is None:
            raise ArgsException("job_id is needed.")
        job_id = self.job_id()
        if self._result is not None:
            return{
                'result': self._result,
                'finished_time': self._finish_time,
                'status': self._status
            }
        status_code, response = self._client.job_result(
            job_id=job_id,
            wait=wait
        )
        if status_code == 404:
            raise JobNotFoundException(
                f"Job not found: {job_id}"
            ) from None
        elif status_code == 405:
            raise NotAuthorizedException(
                f"You are not the owner of Job:{job_id}"
            )from None
        elif status_code != 200:
            raise RunFailedException(f"Failed to get result: {job_id}") from None
        # self._result = response[]
        self._result = response['result']
        self._status = self._status_map[response['status']]
        self._finish_time = response['finish_time']
        return response

    def interim_results(self):
        """
        Return the interim results of the job.
        """
        pass

    def cancel(self):
        """
        Cancel the job.
        """
        if self._job_id is None:
            raise ArgsException("job_id is needed.")
        job_id = self.job_id()
        status_code, response = self._client.job_cancel(job_id=job_id)
        if status_code == 404:
            raise JobNotFoundException(
                f"Job not found: {job_id}"
            ) from None
        elif status_code == 405:
            raise NotAuthorizedException(
                f"You are not the owner of Job:{job_id}"
            )from None
        elif status_code != 200:
            raise RunFailedException(f"Failed to cancel job: {job_id}") from None
        return response

    def status(self):
        """
        Return the status of the job.
        """
        if self._job_id is None:
            raise ArgsException("job_id is needed.")
        if self._status in ['Canceled', 'Completed', 'Failed']:
            print(f"Job {self._job_id} status: {self._status}")
            return self._status
        job_id = self._job_id
        status_code, response = self._client.job_status(job_id=job_id)
        if status_code == 404:
            raise JobNotFoundException(
                f"Job not found: {job_id}"
            ) from None
        elif status_code == 403:
            raise NotAuthorizedException(
                f"You are not the owner of Job:{job_id}"
            )from None
        elif status_code != 200:
            raise RunFailedException(f"Failed to get job: {job_id} status") from None
        self._status = self._status_map[response['status']]
        self._result = response['result']
        if self._status == 'Failed':
            self._error_msg = self._result
        self._finish_time = response['finished_time']
        print(f"Job status: {self._status}")
        return self._status

    def logs(self):
        """
        Return job logs.
        """
        # Already Have Logs
        if self._logs != None:
            print(f"Job status: {self._status},logs:{self._logs}")
            return self._logs
        if self._job_id is None:
            raise ArgsException("job_id is needed.")
        job_id = self.job_id()
        status_code, response = self._client.job_logs(job_id=job_id)
        if status_code == 404:
            raise JobNotFoundException(
                f"Job not found: {job_id}"
            ) from None
        elif status_code == 403:
            raise NotAuthorizedException(
                f"You are not the owner of Job:{job_id}"
            )from None
        elif status_code != 200:
            raise RunFailedException(f"Failed to get job: {job_id} logs") from None
        self._status = self._status_map[response['status']]
        if self._status in ['Canceled', 'Failed', 'Completed']:
            self._logs = response['logs']
            if self._logs is None:
                self._logs = 'None'
        print(f"Job status: {self._status},logs:{self._logs}")
        return response['logs']

    def delete(self) -> bool:
        """
        Delete the job only if the status of job is in 'Canceled', 'Failed' and 'Completed'
        """
        if self._job_id is None:
            raise ArgsException("job_id is needed.")
        if self._status not in ['Canceled', 'Completed', 'Failed']:
            print(f"Job {self._job_id} status: {self._status}, can't be delete")
            return False
        job_id = self._job_id
        status_code, response = self._client.job_delete(job_id=job_id)
        if status_code == 404:
            raise JobNotFoundException(
                f"Job not found: {job_id}"
            ) from None
        elif status_code == 403:
            raise NotAuthorizedException(
                f"You are not the owner of Job:{job_id}"
            )from None
        elif status_code != 200:
            raise RunFailedException(f"Failed to get job: {job_id} logs") from None
        self._status = self._status_map[response['status']]
        deled = response['deled']
        err = response['err']
        if response['status'] < 2:
            err = "job is running"
        print(f"Job deleted: {deled}, error msg: {err}")
        return deled

    def program_id(self):
        """
        Return program id.
        """
        return self._program_id

    def job_id(self):
        """
        Return job id.
        """
        return self._job_id

    def err_msg(self):
        """
        Return job error message.
        """
        if self.status == "Failed":
            if self._error_msg is None:
                self._error_msg = self._result
            return self._error_msg
        else:
            return f"The job's status is:{self._status}"
