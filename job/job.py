from clients.runtime_client import RuntimeClient
from exceptions.exceptions import ArgsException, JobNotFoundException, NotAuthorizedException, RunFailedException


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
        status_map = {0: "In Queue", 1: "Running", 2: "Completed", 3: "Canceled", 4: "Failed"}
        self._job_id = job_id
        self._program_id = program_id
        self._creation_date = creation_date
        self._status = status_map[status]
        self._error_msg = None

    def result(self):
        """
        Get the result from server. It will wait until job stop.
        """
        if self._job_id is None:
            raise ArgsException("one of program_id and name is needed.")
        job_id = self.job_id()
        status_code, response = self._client.job_result(
            job_id=job_id
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
        pass

    def status(self):
        """
        Return the status of the job.
        """
        pass

    def logs(self):
        """
        Return job logs.
        """
        pass

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
            return self._error_msg
        else:
            return f"The job's status is:{self._status}"

    def get_url(self, identifier: str) -> str:
        """Return the resolved URL for the specified identifier.

        Args:
            identifier: Internal identifier of the endpoint.

        Returns:
            The resolved URL of the endpoint (relative to the session base URL).
        """
        return "{}{}{}".format(self._url, "/", identifier)
