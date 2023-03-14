from utils.jsonutil import to_base64_string
from typing import Union, Dict
from exceptions.exceptions import *
from clients.account import Account
from clients.runtime_client import RuntimeClient
from job.job import Job
class RuntimeService:
    """
    Class for interacting with the Quafu Runtime service.
    """
    def __init__(self,
                 account: Account):
        self._url = account.get_url()
        self._token = account.get_token()
        self._client = RuntimeClient(self._token, self._url)
    def programs(self):
        """
        Return available programs on server. Just return metadata.
        """
        pass

    def program(self):
        """
        Return a program.
        """
        pass

    def backends(self):
        """
        Get backends provided by server.
        """
        pass

    def upload_program(self,
                       data: str,
                       metadata: dict=None):
        """
        Upload a program to runtime server.
        Args :
            data: program str or the path of a program file(base64 encoded).
            metadata: a dict or a file path.
                - name: Name of the program.
                - backend: Backend to run the circuits of the program.
                - group: Not used. Group the program shared.
                - description: Program description.
                - max_execution_time: Maximum execution time.
                - is_public: Whether the program should be public.
        """
        program_metadata = self._read_metadata(metadata)
        if "name" not in program_metadata or not program_metadata["name"]:
            raise ArgsException(f"name is a required metadata field.")
        if "backend" not in program_metadata or not program_metadata["name"]:
            raise ArgsException(f"backend is a required metadata field.")

        if "def main(" not in data:
            # This is the program file
            with open(data, "r", encoding="utf-8") as file:
                data = file.read()

        program_data = to_base64_string(data)
        status_code, response = self._client.program_upload(
            program_data=program_data, **program_metadata
        )
        # status_code = response["status"]
        if status_code == 409:
            raise DuplicateProgramException(
                "Program with the same name already exists."
            ) from None
        elif status_code == 403:
            raise NotAuthorizedException(
                "You are not authorized to upload programs."
            ) from None
        elif status_code == 406:
            raise ArgsException(
                "You have not provide enough args."
            ) from None
        elif status_code != 200:
            raise UploadException(f"Failed to create program: Unkown Error.") from None
        return response["id"]

    def update_program(self):
        pass

    def delete_program(self):
        pass

    def run(self,
            program_id: str = None,
            name: str = None,
            backend: str = None,
            inputs: dict = None) -> Job:
        """
        Run a program on the server.

        Args:
            program_id: Program ID.
            name: Optional, use it to find Program ID.
            backend: Optional, it will be used in the program.
            inputs: Program input parameters. These input values are passed
                to the runtime program.

        Returns:
            A ``Job`` instance representing the execution.

        """
        if program_id is None and name is None:
            raise ArgsException("one of program_id and name is needed.")

        status_code, response = self._client.program_run(
            program_id=program_id,
            name=name,
            backend=backend,
            params=inputs,
        )
        if status_code == 404:
            raise ProgramNotFoundException(
                f"Program not found: {program_id}"
            ) from None
        elif status_code == 401:
            raise InputValuexception(
                f"Input is invalid:{inputs}"
            )from None
        elif status_code == 405:
            raise ProgramNotValidException(
                f"Program is invalid:{inputs}"
            )from None
        elif status_code != 200:
            raise RunFailedException(f"Failed to run program: {program_id}") from None
        if backend is None:
            backend = response["backend"]
        job = Job(
            status=response["status"],
            backend=backend,
            api_client=self._client,
            job_id=response["id"],
            creation_date=response["creation_date"],
            program_id=program_id,
            params=inputs,
        )
        return job

    def _read_metadata(self, metadata:  str = None) -> Dict:
        """Read metadata.

        Args:
            metadata: Name of the program metadata file or metadata dictionary.

        Returns:
            Return metadata.
        """
        if metadata is not None:
            metadata_keys = [
                "name",
                "backend",
                "group"
                "max_execution_time",
                "description",
                "is_public",
            ]
            return {key: val for key, val in metadata.items() if key in metadata_keys}