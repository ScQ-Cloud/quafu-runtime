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


class NotAuthorizedException(ClientExceptions):
    """
    Exception raised when a service is invoked from an unauthorized account.
    """


class UploadException(ClientExceptions):
    """Base class for errors raised by the runtime service modules."""


class ProgramNotFoundException(ClientExceptions):
    """Exception raised when program id not found."""


class RunFailedException(ClientExceptions):
    """Exception raised when program run failed."""


class InputValuexception(ClientExceptions):
    """Exception raised when program input is invalid."""


class ProgramNotValidException(ClientExceptions):
    """Exception raised when program data is invalid."""


class JobNotFoundException(ClientExceptions):
    """Exception raised when job is not found."""


