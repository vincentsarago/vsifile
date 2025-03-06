"""vsifile."""

from __future__ import annotations

from typing import TYPE_CHECKING, Type
from urllib.parse import urlparse

if TYPE_CHECKING:
    from obstore.store import ObjectStore

from .io import AWSS3Reader, BaseReader, FileReader, HttpReader

__version__ = "0.3.0"


def _get_filesystem_class(protocol) -> Type[BaseReader]:
    # https://{hostname}/{path}
    if protocol in ["https", "http"]:
        return HttpReader

    # TODO:
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
    return FileReader


def filesystem(protocol) -> Type[BaseReader]:
    """get filesystems for given protocol"""
    return _get_filesystem_class(protocol)


def from_uri(uri) -> Type[BaseReader]:
    """get filesystems for given uri"""
    parsed = urlparse(uri)
    return _get_filesystem_class(parsed.scheme)


def VSIFile(
    uri: str, mode: str = "rb", store: ObjectStore | None = None, **kwargs
) -> BaseReader:
    """TopLevel file Opener."""
    if store:
        return BaseReader(name=uri, mode=mode, store=store, **kwargs)  # type: ignore

    fs = from_uri(uri)
    return fs(name=uri, mode=mode, **kwargs)  # type: ignore
