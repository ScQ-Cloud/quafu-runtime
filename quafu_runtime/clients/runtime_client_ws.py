import enum
import logging
import time
import traceback
from abc import ABC
from typing import Optional, Any
from queue import Queue
from websocket import WebSocketApp, STATUS_ABNORMAL_CLOSED, STATUS_NORMAL
from ..rtexceptions.rtexceptions import WebsocketError, WebsocketTimeoutError

from ..clients.account import Account

logger = logging.getLogger(__name__)


class WebsocketClientCloseCode(enum.IntEnum):
    """Possible values used for closing websocket connection."""

    NORMAL = 1
    TIMEOUT = 2
    PROTOCOL_ERROR = 3
    CANCEL = 4


def format_exception(error: Exception) -> str:
    """Format the exception.

    Args:
        error: Exception to be formatted.

    Returns:
        Formatted exception.
    """
    return "".join(
        traceback.format_exception(
            type(error), error, getattr(error, "__traceback__", "")
        )
    )


class RuntimeWebsocketClient(ABC):
    """Client for websocket communication with the IBM Quantum runtime service."""

    BACKOFF_MAX = 8

    def __init__(
        self,
        job_id: str,
        account: Account,
        message_queue: Optional[Queue] = None,
    ) -> None:
        """WebsocketClient constructor.

        Args:
            account: Account used to get token.
            job_id: Job ID.
            message_queue: Queue used to hold received messages.
        """
        self._websocket_url = account.get_url_ws()
        self._access_token = account.get_token()
        self._job_id = job_id
        self._message_queue = message_queue
        self._header = {"api_token": self._access_token, "job_id": self._job_id}
        self._ws: Optional[WebSocketApp] = None
        self._authenticated = False
        self._cancelled = False
        self.connected = False
        self._last_message: Any = None
        self._current_retry = 0
        self._server_close_code = STATUS_ABNORMAL_CLOSED
        self._client_close_code = None
        self._error: Optional[str] = None

    def _handle_message(self, message: str) -> None:
        """Handle received message.

        Args:
            message: Message received.
        """
        if not self._authenticated:
            self._authenticated = True  # First message is an ACK
        else:
            self._message_queue.put_nowait(message)
            self._current_retry = 0

    def job_results(self, max_retries: int = 8, backoff_factor: float = 0.5) -> None:
        """Return the interim result of a runtime job.

        Args:
            max_retries: Max number of retries.
            backoff_factor: Backoff factor used to calculate the
                time to wait between retries.

        Raises:
            WebsocketError: If a websocket error occurred.
        """
        url = self._websocket_url
        self.stream(url=url, retries=max_retries, backoff_factor=backoff_factor)

    def _handle_stream_iteration(self) -> None:
        """Handle a streaming iteration."""
        pass

    def on_open(self, wsa: WebSocketApp) -> None:
        """Called when websocket connection established.

        Args:
            wsa: WebSocketApp object.
        """
        logger.debug("Websocket connection established for job %s", self._job_id)
        self.connected = True
        if self._cancelled:
            # Immediately disconnect if pre-cancelled.
            self.disconnect(WebsocketClientCloseCode.CANCEL)

    def on_message(self, wsa: WebSocketApp, message: str) -> None:
        """Called when websocket message received.

        Args:
            wsa: WebSocketApp object.
            message: Message received.
        """
        try:
            self._handle_message(message)
        except Exception as err:  # pylint: disable=broad-except
            self._error = format_exception(err)
            self.disconnect(WebsocketClientCloseCode.PROTOCOL_ERROR)

    def on_close(self, wsa: WebSocketApp, status_code: int, msg: str) -> None:
        """Called when websocket connection closed.

        Args:
            wsa: WebSocketApp object.
            status_code: Status code.
            msg: Close message.
        """
        # Assume abnormal close if no code is given.
        self._server_close_code = status_code or STATUS_ABNORMAL_CLOSED
        self.connected = False
        logger.debug(
            "Websocket connection for job %s closed. status code=%s, message=%s",
            self._job_id,
            status_code,
            msg,
        )

    def on_error(self, wsa: WebSocketApp, error: Exception) -> None:
        """Called when a websocket error occurred.

        Args:
            wsa: WebSocketApp object.
            error: Encountered error.
        """
        self._error = format_exception(error)

    def stream(
        self,
        url: str,
        retries: int = 8,
        backoff_factor: float = 0.5,
    ) -> Any:
        """Stream from the websocket.

        Args:
            url: Websocket url to use.
            retries: Max number of retries.
            backoff_factor: Backoff factor used to calculate the
                time to wait between retries.

        Returns:
            The final message received.

        Raises:
            WebsocketError: If the websocket connection ended unexpectedly.
            WebsocketTimeoutError: If the operation timed out.
        """
        self._reset_state()
        self._cancelled = False

        while self._current_retry <= retries:
            self._ws = WebSocketApp(
                url,
                header=self._header,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
            )
            try:
                self._reset_state()
                self._ws.run_forever(ping_interval=60, ping_timeout=10)
                self.connected = False

                # Handle path-specific errors
                self._handle_stream_iteration()

                if self._client_close_code in (
                    WebsocketClientCloseCode.NORMAL,
                    WebsocketClientCloseCode.CANCEL,
                ):
                    # If we closed the connection with a normal code.
                    return self._last_message

                if self._client_close_code == WebsocketClientCloseCode.TIMEOUT:
                    raise WebsocketTimeoutError(
                        "Timeout reached while getting job interim_result."
                    ) from None

                if self._server_close_code == STATUS_NORMAL and self._error is None:
                    return self._last_message

                msg_to_log = (
                    f"A websocket error occurred while streaming for job "
                    f"{self._job_id}. Connection closed with {self._server_close_code}."
                )
                if self._error is not None:
                    msg_to_log += f"\n{self._error}"
                logger.info(msg_to_log)

                self._current_retry += 1
                if self._current_retry > retries:
                    error_message = "Max retries exceeded: Failed to establish a websocket connection."
                    if self._error:
                        error_message += f" Error: {self._error}"

                    raise WebsocketError(error_message)
            finally:
                self.disconnect(None)

            # Sleep then retry.
            backoff_time = self._backoff_time(backoff_factor, self._current_retry)
            logger.info(
                "Retrying get_job_status via websocket after %s seconds: "
                "Attempt #%s",
                backoff_time,
                self._current_retry,
            )
            time.sleep(backoff_time)

        # Execution should not reach here, sanity check.
        exception_message = (
            "Max retries exceeded: Failed to establish a websocket "
            "connection due to a network error."
        )

        logger.info(exception_message)
        raise WebsocketError(exception_message)

    def _backoff_time(self, backoff_factor: float, current_retry_attempt: int) -> float:
        """Calculate the backoff time to wait for.

        Exponential backoff time formula::
            {backoff_factor} * (2 ** (current_retry_attempt - 1))

        Args:
            backoff_factor: Backoff factor, in seconds.
            current_retry_attempt: Current number of retry attempts.

        Returns:
            The number of seconds to wait for, before making the next retry attempt.
        """
        backoff_time = backoff_factor * (2 ** (current_retry_attempt - 1))
        return min(self.BACKOFF_MAX, backoff_time)

    def disconnect(
        self,
        close_code: Optional[
            WebsocketClientCloseCode
        ] = WebsocketClientCloseCode.NORMAL,
    ) -> None:
        """Close the websocket connection.

        Args:
            close_code: Disconnect status code.
        """
        if self._ws is not None:
            logger.debug(
                "Client closing websocket connection with code %s.", close_code
            )
            self._client_close_code = close_code
            self._ws.close()
        if close_code == WebsocketClientCloseCode.CANCEL:
            self._cancelled = True

    def _reset_state(self) -> None:
        """Reset state for a new connection."""
        self._authenticated = False
        self.connected = False
        self._error = None
        self._server_close_code = None
        self._client_close_code = None
