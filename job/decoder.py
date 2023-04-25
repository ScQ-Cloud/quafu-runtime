"""Qiskit runtime job result decoder."""

import json
from typing import Any, Dict, Tuple

class ResultDecoder:
    """Runtime job result decoder.

    You can subclass this class and overwrite the :meth:`decode` method
    to create a custom result decoder for the
    results of your runtime program. For example::

        class MyResultDecoder(ResultDecoder):

            @classmethod
            def decode(cls, data):
                decoded = super().decode(data)
                custom_processing(decoded)  # perform custom processing

    Users of your program will need to pass in the subclass when invoking
    """

    @classmethod
    def decode(cls, data: str) -> Any:
        """Decode the result data.

        Args:
            data: Result data to be decoded.

        Returns:
            Decoded result data.
        """
        try:
            return json.loads(data, cls=json.JSONDecoder)
        except json.JSONDecodeError:
            return data

