"""Quafu runtime job result decoder."""

import json
from typing import Any


class ResultDecoder:
    """Runtime job result decoder.

    You can subclass this class and overwrite the :meth:`decode` method
    to create a custom result decoder for the
    interim results and final result of your runtime program. For example::

        class MyResultDecoder(ResultDecoder):

            @classmethod
            def decode(cls, data):
                decoded = super().decode(data)
                custom_processing(decoded)  # perform custom processing

    Note that you have to decode your result because we can just send you bytes.
    You have to decode and encode your interim result and final result yourself.
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
