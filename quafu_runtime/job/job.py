import logging
import queue
import traceback
from concurrent import futures
from typing import Optional, Callable, Type
from ..clients.runtime_client import RuntimeClient
from ..clients.runtime_client_ws import WebsocketClientCloseCode, RuntimeWebsocketClient
from ..job.decoder import ResultDecoder
from ..job.jobstatus import JOB_FINAL_STATES, JobStatus
from ..rtexceptions.rtexceptions import ArgsException, JobNotFoundException, NotAuthorizedException, RunFailedException, \
    RuntimeInvalidStateError, CheckApiTokenError
from ..clients.account import Account

logger = logging.getLogger(__name__)


class RuntimeJob:
    """Class represent a job instance running on runtime server.

    A new `Job` instance is returned when you call
    :meth:`Service.run` to execute a program, or retrieve a previously executed job by
    :meth:`Job` .
    If you want directly use `Job` to construct/retrieve an instance,

    The job's status is Queued, Running, Done, Canceled, Failed. You can get your job's status by call
    :meth:`status()`. When your program raised some exceptions,
    the job is Failed. So, review your code before run it.

    Some methods in the class are blocking, if you call
    :meth:`result(wait=True)` with argument `wait` set to True,
    it would block until job's over and return result.

    If the program has any interim result, you can use the ``callback``
    parameter of the
    :meth:`~Job.interim_result` method to stream the interim results after creating job, but before the job finishes.
    """

    _POISON_PILL = "_poison_pill"

    _executor = futures.ThreadPoolExecutor(thread_name_prefix="runtime_job")

    def __init__(self,
                 job_id: str,
                 account: Account = None,
                 status: int = 0,
                 api_client: RuntimeClient = None,
                 backend: str = None,
                 creation_date: str = None,
                 program_id: str = None,
                 params: str = None,
                 ):
        """Job constructor.
        If you want to retrieve a job instance in this way,
        you should provide `job_id` and your `account` instance of Account.

        Args:
            account: Account
            job_id: job's id generated by server
            status: job's status
            backend: The backend instance.
            creation_date: The time create job.
            api_client: Instance for connecting to the server.
            program_id: Program ID this job is for.
            params: The params used by run method of program.

        Returns:
            An instance of job.
        """
        if account is None:
            account = Account()
        self._job_id = job_id
        self._client = api_client
        if self._client is None:
            self._client = RuntimeClient(token=account.get_token(), url=account.get_url())
        self.params = params
        self.backend = backend
        self._status_map = {0: JobStatus.QUEUED, 1: JobStatus.RUNNING, 2: JobStatus.DONE, 3: JobStatus.CANCELLED,
                            4: JobStatus.ERROR}
        self._program_id = program_id
        self._creation_date = creation_date
        self._status = self._status_map[status]
        self._error_msg = None
        self._result = None
        self._finish_time = None
        self._logs = None
        self._final_interim_results = False
        self._interim_result_decoder = ResultDecoder

        # used for streaming result
        self._ws_client_future = None  # type: Optional[futures.Future]
        self._result_queue = queue.Queue()  # type: queue.Queue
        self._ws_client = RuntimeWebsocketClient(
            account=account,
            job_id=job_id,
            message_queue=self._result_queue,
        )

    def result(self,
               wait: bool):
        """Get the result from server.

        Args:
            wait: Weather wait if job is not done. Wait if set to True, otherwise return immediately.

        Returns:
            Result of the job.
        """
        if self._job_id is None:
            raise ArgsException("job_id is needed.")
        job_id = self.job_id()
        if self._result is not None:
            return {
                'result': self._result,
                'finished_time': self._finish_time,
                'status': self._status
            }
        status_code, response = self._client.job_result(
            job_id=job_id,
            wait=wait
        )
        if status_code == 201:
            raise CheckApiTokenError("API_TOKEN ERROR.") from None
        if status_code == 404:
            raise JobNotFoundException(
                f"Job not found: {job_id}"
            ) from None
        elif status_code != 200:
            raise RunFailedException(f"Failed to get result: {job_id}") from None
        response = response['data']
        # self._result = response[]
        self._result = response['result']
        self._status = self._status_map[response['status']]
        self._finish_time = response['finish_time']
        if response['status'] != 2:
            del response['finish_time']
            self._finish_time = None
        if response['status'] == 4:
            self._error_msg = response['result']
            response['error_msg'] = self._error_msg
            del response['result']
        response['status'] = self._status
        return response

    def interim_results(
            self, callback: Callable, decoder: Optional[Type[ResultDecoder]] = None
    ) -> None:
        """Start streaming interim job results.

        Args:
            callback: Callback function to be invoked for any interim results and final result.
                The callback function will receive 2 positional parameters:
                    1. Job ID
                    2. Job result data.
            decoder: A :class:`decoder.ResultDecoder` subclass used to decode job results and interim result.
                The result will be jsonfy before send to client,
                so you should encode your data, and decode it with `decoder` when you get it.

        Raises:
            RuntimeInvalidStateError: If a callback function is already streaming results or
                if the job already finished.
        """
        if self._status in JOB_FINAL_STATES:
            raise RuntimeInvalidStateError("Job already finished.")
        if self._is_streaming():
            raise RuntimeInvalidStateError(
                "A callback function is already streaming results."
            )
        self._executor.submit(self._start_websocket_client)
        self._stream_results(
            result_queue=self._result_queue,
            user_callback=callback,
            decoder=decoder,)

    def _is_streaming(self) -> bool:
        """Return whether job results are being streamed.

        Returns:
            Whether job results are being streamed.
        """
        if self._ws_client_future is None:
            return False

        if self._ws_client_future.done():
            return False

        return True

    def _start_websocket_client(self) -> None:
        """Start websocket client to stream results."""
        try:
            print("Start websocket client for job ", self.job_id())
            self._ws_client.job_results()
        except Exception:  # pylint: disable=broad-except
            print(
                f"An error occurred while streaming results"
                f" from the server for job {self.job_id()}:\n {traceback.format_exc()}"
            )
        finally:
            self._result_queue.put_nowait(self._POISON_PILL)

    def interim_result_cancel(self) -> None:
        """Cancel result streaming."""
        if not self._is_streaming():
            return
        self._ws_client.disconnect(WebsocketClientCloseCode.CANCEL)

    def _stream_results(
            self,
            result_queue: queue.Queue,
            user_callback: Callable,
            decoder: Optional[Type[ResultDecoder]] = None,
    ) -> None:
        """Stream results.

        Args:
            result_queue: Queue used to pass websocket messages.
            user_callback: User callback function.
            decoder: A :class:`ResultDecoder` (sub)class used to decode job results.
        """
        print("Start interim result streaming for job", self.job_id())
        _decoder = decoder or self._interim_result_decoder
        while True:
            try:
                response = result_queue.get(timeout=1)
                if response == self._POISON_PILL:
                    self._empty_result_queue(result_queue)
                    print("Interim result streaming finished")
                    return
                user_callback(self.job_id(), _decoder.decode(response))
            except queue.Empty:
                pass
            except Exception:  # pylint: disable=broad-except
                logger.warning(
                    "An error occurred while streaming results " "for job %s:\n%s",
                    self.job_id(),
                    traceback.format_exc(),
                )

    def _empty_result_queue(self, result_queue: queue.Queue) -> None:
        """Empty the result queue.

        Args:
            result_queue: Result queue to empty.
        """
        try:
            while True:
                result_queue.get_nowait()
        except queue.Empty:
            pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}('{self._job_id}', '{self._program_id}')>"

    def cancel(self):
        """Cancel the job.

        Returns:
            job's status.
        """
        if self._job_id is None:
            raise ArgsException("job_id is needed.")
        job_id = self.job_id()
        status_code, response = self._client.job_cancel(job_id=job_id)
        # check api_token error
        if status_code == 201:
            raise CheckApiTokenError("API_TOKEN ERROR.") from None
        if status_code == 404:
            raise JobNotFoundException(
                f"Job not found: {job_id}"
            ) from None
        elif status_code == 403:
            raise NotAuthorizedException(
                f"You are not the owner of Job:{job_id}"
            )from None
        elif status_code != 200:
            raise RunFailedException(f"Failed to cancel job: {job_id}") from None
        response = response['data']
        if response['status'] != -1:
            self._status = self._status_map[response['status']]
            response['status'] = self._status
        else:
            print("Job cancel failed")
        self.interim_result_cancel()
        return response

    def status(self):
        """Return the status of the job."""
        if self._job_id is None:
            raise ArgsException("job_id is needed.")
        if self._status in JOB_FINAL_STATES:
            print(f"Job {self._job_id} status: {self._status}")
            return self._status
        job_id = self._job_id
        status_code, response = self._client.job_status(job_id=job_id)
        if status_code == 201:
            raise CheckApiTokenError("API_TOKEN ERROR.") from None
        if status_code == 404:
            raise JobNotFoundException(
                f"Job not found: {job_id}"
            ) from None
        elif status_code != 200:
            raise RunFailedException(f"Failed to get job: {job_id} status") from None
        response = response['data']
        self._status = self._status_map[response['status']]
        self._result = response['result']
        self._finish_time = response['finished_time']
        if self._status == JobStatus.ERROR:
            self._error_msg = self._result
            self._result = None
        if response['status'] < 2:
            self._finish_time = None
        print(f"Job status: {self._status}")
        return self._status

    def logs(self):
        """Return job logs."""
        # Already Have Logs
        if self._status in JOB_FINAL_STATES and self._logs is not None:
            print(f"Job status: {str(self._status)},logs:{self._logs}")
            return self._logs
        if self._job_id is None:
            raise ArgsException("job_id is needed.")
        job_id = self.job_id()
        status_code, response = self._client.job_logs(job_id=job_id)
        if status_code == 201:
            raise CheckApiTokenError("API_TOKEN ERROR.") from None
        if status_code == 404:
            raise JobNotFoundException(
                f"Job not found: {job_id}"
            ) from None
        elif status_code != 200:
            raise RunFailedException(f"Failed to get job: {job_id} logs") from None
        response = response['data']
        self._status = self._status_map[response['status']]
        self._logs = response['logs']
        print(f"Job status: {self._status}")
        return response['logs']

    def delete(self) -> bool:
        """Delete the job.
        Only if the status of job is in 'Canceled', 'Failed' and 'Completed', delete successfully.
        """
        if self._job_id is None:
            raise ArgsException("job_id is needed.")
        if self._status not in JOB_FINAL_STATES:
            print(f"Job {self._job_id} status: {self._status}, can't be delete")
            return False
        job_id = self._job_id
        status_code, response = self._client.job_delete(job_id=job_id)
        if status_code == 201:
            raise CheckApiTokenError("API_TOKEN ERROR.") from None
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
        response = response['data']
        self._status = self._status_map[response['status']]
        deleted = response['deleted']
        err = None
        if response['status'] < 2:
            err = "job is running"
        print(f"Job deleted: {deleted}, Error: {err}")
        return deleted

    def program_id(self):
        """Return program id."""
        return self._program_id

    def job_id(self):
        """Return job id."""
        return self._job_id

    def err_msg(self):
        """Return job error message."""
        if self._status == JobStatus.ERROR:
            if self._error_msg is None:
                self._error_msg = self._result
            return self._error_msg
        else:
            return f"The job's status is: {self._status}"
