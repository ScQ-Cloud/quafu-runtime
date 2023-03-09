class Job:
    """
    Class for a job instance running on runtime server.

    Attributes:
        token (str): Apitoken that associate to your Quafu account.
        job_id (str): ID of the job running on server.
        program_id (str): ID of the program which excuted by job.
        creation_date.
        status.

    """

    def __init__(self,
                 status: int,
                 job_id: str=None ,
                 program_id: str=None,
                 creation_date: str=None,
                 error_msg: str=None):
        status_map = {0: "In Queue", 1: "Running", 2: "Completed", "Canceled": 3, 4: "Failed"}
        self._url = ""
        self._job_id = job_id
        self._program_id = program_id
        self._creation_date = creation_date
        self._status=status_map[status]
        self._error_msg = error_msg


    def result(self):
        """
        Get the result from server.
        """
        pass

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
        pass
    def job_id(self):
        """
        Return job id.
        """
        pass
