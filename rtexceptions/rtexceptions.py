class ClientExceptions(Exception):
    def __init__(self, *message):
        """Set the error message."""
        super().__init__(" ".join(message))
        self.message = " ".join(message)

    def __str__(self):
        """Return the message."""
        return repr(self.message)


class UserException(ClientExceptions):
    """
    Exception raised when can't load token.
    """
    pass


class ArgsException(ClientExceptions):
    """
    Exception raised when input wrong args.
    """


class RequestException(ClientExceptions):
    """
    Exception rasied when request failed.
    """

    def __init__(self, message: str, status_code: int = -1):
        super().__init__(message)
        self.status_code = status_code


class DuplicateProgramException(ClientExceptions):
    """
    Exception raised after upload a program with duplicated name.
    """
    pass


class NotAuthorizedException(ClientExceptions):
    """
    Exception raised when a service is invoked from an unauthorized account.
    """
    pass


class UploadException(ClientExceptions):
    """Exception raised when Upload a program failed."""
    pass


class UpdateException(ClientExceptions):
    """Exception raised when Update a program failed."""
    pass


class ProgramNotFoundException(ClientExceptions):
    """Exception raised when program id not found."""
    pass


class RunFailedException(ClientExceptions):
    """Exception raised when program run failed."""


class InputValueException(ClientExceptions):
    """Exception raised when program input is invalid."""
    pass


class ProgramNotValidException(ClientExceptions):
    """Exception raised when program data is invalid."""
    pass


class JobNotFoundException(ClientExceptions):
    """Exception raised when job is not found."""
    pass


class WebsocketError(ClientExceptions):
    """Exceptions related to websockets."""
    pass


class WebsocketTimeoutError(ClientExceptions):
    """Exceptions related to websockets."""
    pass


class RuntimeJobTimeoutError(ClientExceptions):
    """Exception raised when waiting for jobs time out."""


class RuntimeInvalidStateError(ClientExceptions):
    """Error raised when job state is not expected."""


class AsyncioWebsocketError(ClientExceptions):
    """Error raised when Async websocket client failed."""
