import base64
import importlib
import inspect
import io
import zlib

from typing import Any, Callable, Dict


def to_base64_string(data: str) -> str:
    """Convert string to base64 string.

    Args:
        data: string to convert

    Returns:
        data as base64 string
    """
    return base64.b64encode(data.encode("utf-8")).decode("utf-8")


def from_base64_string(data: str) -> str:
    """Convert base64 string to string.

    Args:
        data: base64 string to convert

    Returns:
        data as string
    """
    return base64.b64decode(data)


def _serialize_and_encode(
    data: Any, serializer: Callable, compress: bool = True, **kwargs: Any
) -> str:
    """Serialize the input data and return the encoded string.

    Args:
        data: Data to be serialized.
        serializer: Function used to serialize data.
        compress: Whether to compress the serialized data.
        kwargs: Keyword arguments to pass to the serializer.

    Returns:
        String representation.
    """
    with io.BytesIO() as buff:
        serializer(buff, data, **kwargs)
        buff.seek(0)
        serialized_data = buff.read()

    if compress:
        serialized_data = zlib.compress(serialized_data)
    return base64.standard_b64encode(serialized_data).decode("utf-8")


def _decode_and_deserialize(
    data: str, deserializer: Callable, decompress: bool = True
) -> Any:
    """Decode and deserialize input data.

    Args:
        data: Data to be deserialized.
        deserializer: Function used to deserialize data.
        decompress: Whether to decompress.

    Returns:
        Deserialized data.
    """
    buff = io.BytesIO()
    decoded = base64.standard_b64decode(data)
    if decompress:
        decoded = zlib.decompress(decoded)

    with io.BytesIO() as buff:
        buff.write(decoded)
        buff.seek(0)
        return deserializer(buff)


def _deserialize_from_settings(mod_name: str, class_name: str, settings: Dict) -> Any:
    """Deserialize an object from its settings.

    Args:
        mod_name: Name of the module.
        class_name: Name of the class.
        settings: Object settings.

    Returns:
        Deserialized object.

    Raises:
        ValueError: If unable to find the class.
    """
    mod = importlib.import_module(mod_name)
    for name, clz in inspect.getmembers(mod, inspect.isclass):
        if name == class_name:
            return clz(**settings)
    raise ValueError(f"Unable to find class {class_name} in module {mod_name}")
