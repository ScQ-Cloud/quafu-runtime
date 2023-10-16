import warnings
from .utils.jsonutil import to_base64_string, from_base64_string
from typing import Optional, Union, Dict, Any
from .rtexceptions.rtexceptions import *
from .clients.account import Account
from .program.program import RuntimeProgram
from .clients.runtime_client import RuntimeClient
from .job.job import RuntimeJob
from .utils.check_python import check
from .utils.keywords import MESSAGE


class RuntimeService:
    """Class for interacting with the Quafu Runtime service.

    A sample workflow of using the runtime service::

        from clients import Account
        from job import Job
        from quafu_runtime_service import RuntimeService

        # get RuntimeService
        account = Account(api_token="testapitoken")
        service = RuntimeService(account)

        # Upload program
        metadata = {"name": "long-run-task", "backend": "testbackend"}
        id1 = service.upload_program(data='/program/hello.py',metadata=metadata)
        print(id1)

        # Run a program
        job1 = service.run(name='long-run-task',params={'TestParam':'xxxxxx'})

        # Define callback function
        def callback(job_id, message):
        print(message)
        # Get job interim result
        job1.interim_results(callback=callback)

        # Get job result
        result = job1.result(wait=True)
        print(result)

        # Get job logs
        logs = job1.logs()

    The simple example above use teh :meth`run` method directly to invoke a program.

    If the program has any interim results, you can use the :meth: `Job.interim_results` method to stream
    the results at a later time, but before the interim result expires.

    The :meth:`run` method returns a
    :class:`RuntimeJob` object. You can use its methods to perform tasks like checking job status, getting job result, and
    canceling job.

    See more message about program templates in quafu_runtime.program.template
    """

    def __init__(self, account: Account = None):
        """QiskitRuntimeService constructor

        Args:
            account: Account instance.

        Returns:
            An instance of service.
        """
        if account is None:
            account = Account()
        self._account = account
        self._url = account.get_url()
        self._token = account.get_token()
        self._client = RuntimeClient(self._token, self._url)
        self._programs = {}

    def list_programs(
        self,
        refresh: bool = False,
        detailed: bool = False,
        limit: int = 10,
        skip: int = 0,
    ) -> None:
        """Pretty print information about available runtime programs.

        Args:
            refresh: If `True`, re-query the server for the programs. Otherwise, return the cached value.
            detailed: If ``True`` print all details about available runtime programs.
            limit: The number of programs returned at a time. Default and maximum
                value of 20.
            skip: The number of programs to skip.
        """
        programs = self.programs(refresh=refresh, limit=limit, skip=skip)
        if programs is None:
            print("No programs")
            return
        for prog in programs:
            print("-" * 50)
            if detailed:
                print(str(prog))
            else:
                print(
                    f"program_id:{prog['program_id']}",
                )
                print(f" -Name: {prog['name']}")
                print(f" -Description: {prog['description']}")

    def programs(self, refresh: bool = False, limit: int = 10, skip: int = 0):
        """
        Return available programs on server.

        Just return metadata.

        Args:
            refresh: If ``True``, re-query the server for the programs. Or return the cached value.
            limit: The number of programs returned at a time. ``None`` means no limit.
            skip: The number of programs to skip.

        Returns:
            A list of runtime programs.
        """
        # Need to fetch
        if len(self._programs) == 0 or refresh:
            fetch_page_limit = 10
            offset = 0
            while True:
                status, response = self._client.get_programs(
                    limit=fetch_page_limit, skip=offset
                )
                # TODO(zhaoyilun): the backend code has changed to 400
                # for api token error, unify this and put status codes in another file
                if status == 201 or status == 400:
                    raise CheckApiTokenError(
                        "API_TOKEN ERROR.", response[MESSAGE]
                    ) from None
                elif status == 405:
                    raise ArgsException(
                        "Limit or offset is wrong or not provided."
                    ) from None
                elif status != 200:
                    raise UploadException(
                        f"Failed to fetch programs: Unkown Error."
                    ) from None

                response = response["data"]
                program_page = response.get("programs", [])
                # count is the total number of programs that would be returned if
                # there was no limit or skip
                count = response.get("count", 0)
                for prog_dict in program_page:
                    program_id = prog_dict["program_id"]
                    self._programs[program_id] = prog_dict
                if (
                    len(self._programs) == count
                    or len(self._programs) >= limit + skip
                    or len(program_page) < fetch_page_limit
                ):
                    # Stop if there are no more programs returned by the server or
                    # if the number of cached programs is greater than the sum of limit and skip or
                    # if the server has no more page
                    break
                offset += len(program_page)

        if skip >= len(self._programs):
            print("SKIP IS OUT OF RANGE")
            return None
        if limit + skip > len(self._programs):
            return list(self._programs.values())[skip:]
        return list(self._programs.values())[skip : limit + skip]

    def program(self, refresh: bool = False, name: str = None, program_id: str = None):
        """
        Return a program by id or name.

        Args:
            refresh: if refresh is true or never fetch the program, get it from server.
            name: Program name.
            program_id: Program ID.

        Returns:
            Program Msg.
        """
        # return result from cache
        if refresh is False:
            if program_id in self._programs and "data" in self._programs[program_id]:
                return self._programs[program_id]

        if name is None and program_id is None:
            raise ArgsException(f"name or program_id is a required field.")
        status, response = self._client.program_get(program_id=program_id, name=name)
        if status == 201:
            raise CheckApiTokenError("API_TOKEN ERROR.", response[MESSAGE]) from None
        if status == 403:
            raise NotAuthorizedException(
                "You are not authorized to get program."
            ) from None
        elif status == 404:
            raise ProgramNotFoundException(
                f"Program not found: program_id:{program_id}, Name:{name}"
            ) from None
        elif status == 405:
            raise ArgsException(
                "Your args program_id or name is wrong or not provided."
            ) from None
        elif status != 200:
            raise UploadException(f"Failed to fetch program: Unkown Error.") from None
        program = RuntimeProgram(program_id=program_id)
        response = response["data"]
        if "data" in response:
            response["data"] = from_base64_string(response["data"]).decode("utf-8")
        program.update(response)
        if self._programs is None:
            self._programs = {}
        self._programs[program_id] = response
        return program

    def upload_program(self, data: str, metadata: dict = None):
        """Upload a program to runtime server.

        Args:
            data: program str or the path of a program file(base64 encoded).
            metadata: a dict or a file path.
                 * name: Name of the program.
                 * backend: Backend to run the circuits of the program.
                 * group: Not used. Group the program shared.
                 * description: Program description.
                 * max_execution_time: Maximum execution time.
                 * is_public: Whether the program should be public.

        Return:
            Program_id, if upload succeed.
        """
        program_metadata = self._read_metadata(metadata)
        if "name" not in program_metadata or not program_metadata["name"]:
            raise ArgsException(f"name is a required metadata field.")
        if "backend" not in program_metadata or not program_metadata["backend"]:
            raise ArgsException(f"backend is a required metadata field.")

        filename = None
        if "def run(" not in data:
            # This is the program file
            with open(data, "r", encoding="utf-8") as file:
                data = file.read()
            filename = data
        # Check the program before upload it!
        if filename is None:
            filename = "upload_temp.py"
            file = open(filename, "w")
            file.write(data)
            file.close()
        check(data, filename)

        # Upload it.
        program_data = to_base64_string(data)
        status_code, response = self._client.program_upload(
            program_data=program_data, **program_metadata
        )
        if status_code == 201:
            raise CheckApiTokenError("API_TOKEN ERROR.", response[MESSAGE]) from None
        if status_code == 409:
            raise DuplicateProgramException(
                "Program with the same name already exists."
            ) from None
        elif status_code == 406:
            raise ArgsException("You have not provide enough args.") from None
        elif status_code != 200:
            raise UploadException(f"Failed to upload program: Unkown Error.") from None
        response = response["data"]
        return response["id"]

    def update_program(
        self,
        program_id: str,
        data: str = None,
        description: str = None,
        max_execution_time: int = None,
        is_public: bool = None,
        backend: str = None,
        group: str = None,
        metadata: dict = None,
    ):
        """Update a program.

        Program metadata can be specified using the `metadata` parameter or
        individual parameters, such as `description`. The individual parameter
        takes precedence.

        Args:
            program_id: Program ID.
            data: Program data or path of the file containing program data to upload.
            metadata: Name of the program metadata dictionary.
            description: New program description.
            max_execution_time: New maximum execution time.
            is_public: Program set to public or not.
            backend: Backend to run the circuits of the program.
            group: Not used. Group the program shared.

        Returns:
            Program msg of the updated program.
        """
        if not any(
            [data, metadata, description, max_execution_time, is_public, backend, group]
        ):
            warnings.warn(
                "None of the 'data', 'metadata', 'name', 'description', "
                "'max_execution_time', or 'spec' parameters is specified. "
                "No update is made."
            )
            return
        if data:
            filename = None
            if "def run(" not in data:
                # This is the program file
                with open(data, "r", encoding="utf-8") as file:
                    data = file.read()
                filename = data
            # Check the program before upload it!
            if filename is None:
                filename = "upload_temp.py"
                file = open(filename, "w")
                file.write(data)
                file.close()
            check(data, filename)
            data = to_base64_string(data)

        if metadata:
            metadata = self._read_metadata(metadata=metadata)
        combined_metadata = self._merge_metadata(
            metadata=metadata,
            description=description,
            max_execution_time=max_execution_time,
            backend=backend,
            is_public=is_public,
            group=group,
        )
        if not combined_metadata:
            warnings.warn(
                "None of the 'data', 'metadata', 'name', 'description', "
                "'max_execution_time', or 'spec' parameters is specified. "
                "No update is made."
            )
            return
        # update it
        status_code, response = self._client.program_update(
            program_id=program_id, program_data=data, **combined_metadata
        )
        if status_code == 201:
            raise CheckApiTokenError("API_TOKEN ERROR.", response[MESSAGE]) from None
        elif status_code == 404:
            raise ProgramNotFoundException(f"Program not found: {program_id}") from None
        elif status_code != 200:
            raise UpdateException(f"Failed to update program: Unkown Error.") from None
        response = response["data"]
        program = RuntimeProgram(program_id=program_id)
        if "data" in response:
            response["data"] = from_base64_string(response["data"]).decode("utf-8")
        program.update(response)
        print("After update, the program is:\n", program)
        if self._programs is None:
            self._programs = {}
        self._programs[program_id] = response
        return

    def delete_program(self, program_id: str):
        """Delete a runtime program.

        Args:
            program_id: Program ID.
        """
        status_code, response = self._client.program_delete(program_id=program_id)
        if status_code == 201:
            raise CheckApiTokenError("API_TOKEN ERROR.", response[MESSAGE]) from None
        if status_code == 404:
            raise ProgramNotFoundException(f"Program not found: {program_id}") from None
        elif status_code != 200:
            raise UpdateException(f"Failed to delete program: Unkown Error.") from None
        if program_id in self._programs:
            del self._programs[program_id]
        print(f"Program {program_id} deleted.")
        return

    def run(
        self,
        program_id: str = None,
        name: str = None,
        backend: str = None,
        params: dict = None,
    ) -> RuntimeJob:
        """
        Run a program on the server.

        Args:
            program_id: Program ID.
            name: Optional, use it to find Program ID.
            backend: Optional, it will be used in the program. It's useless up to now.
            params: Program input parameters. These input values are passed
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
            params=params,
        )
        if status_code == 201:
            raise CheckApiTokenError("API_TOKEN ERROR", response[MESSAGE]) from None
        elif status_code == 404:
            raise ProgramNotFoundException(
                f"Program not found: {program_id}; Name:{name}"
            ) from None
        elif status_code == 401:
            raise InputValueException(f"params of run is invalid:{params}") from None
        elif status_code == 405:
            raise ProgramNotValidException(
                f"Program is invalid, please check it and update it"
            ) from None
        elif status_code != 200:
            raise RunFailedException(f"Failed to run program: {program_id}") from None
        response = response["data"]
        if backend is None:
            backend = response["backend"]
        if program_id is None:
            program_id = response["program_id"]
        job = RuntimeJob(
            account=self._account,
            status=response["status"],
            backend=backend,
            api_client=self._client,
            job_id=response["job_id"],
            creation_date=response["creation_time"],
            program_id=program_id,
            params=params,
        )
        print(f"job created, job_id is {job.job_id()}")
        return job

    def _read_metadata(self, metadata: Optional[str] = None) -> dict:
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
                "group" "max_execution_time",
                "description",
                "is_public",
            ]
            return {key: val for key, val in metadata.items() if key in metadata_keys}
        return {}

    def _merge_metadata(self, metadata: Optional[dict] = None, **kwargs: Any) -> dict:
        """Merge multiple copies of metadata.
        Args:
            metadata: Program metadata.
            **kwargs: Additional metadata fields to overwrite.
        Returns:
            Merged metadata.
        """
        merged = {}
        metadata = metadata or {}
        metadata_keys = [
            "name",
            "max_execution_time",
            "description",
            "is_public",
            "backend",
            "group",
        ]
        for key in metadata_keys:
            if kwargs.get(key, None) is not None:
                merged[key] = kwargs[key]
            elif key in metadata.keys():
                merged[key] = metadata[key]

        return merged
