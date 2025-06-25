"""vsifile."""

from typing import Type
from urllib.parse import urlparse

from .io import AWSS3Reader, BaseReader, FileReader, HttpReader

__version__ = "0.4.1"


def _get_filesystem_class(protocol) -> Type[BaseReader]:
    # https://{hostname}/{path}
    if protocol in ["https", "http"]:
        return HttpReader

    # TODO:
    # - add s3
    # - add az
    # - add gs

    # s3://{bucket}/{key}
    elif protocol == "s3":
        return AWSS3Reader

    # file:///{path}
    elif protocol == "file":
        return FileReader

    # Invalid Scheme
    elif protocol:
        raise ValueError("'protocol' is not supported")

    # fallback to FileReader
    else:
        return FileReader


def filesystem(protocol) -> Type[BaseReader]:
    """get filesystems for given protocol"""
    return _get_filesystem_class(protocol)


def from_uri(uri) -> Type[BaseReader]:
    """get filesystems for given uri"""
    parsed = urlparse(uri)
    return _get_filesystem_class(parsed.scheme)


def VSIFile(uri: str, mode: str = "rb", **kwargs) -> BaseReader:
    """TopLevel file Opener."""
    fs = from_uri(uri)
    return fs(name=uri, mode=mode, **kwargs)  # type: ignore
