"""vsifile.io"""

from urllib.parse import urlparse

from .file import FileReader
from .http import HttpReader
from .s3 import AWSS3Reader


def VSIFile(uri: str, mode: str):
    """TopLevel file Opener."""
    parsed = urlparse(uri)

    # https://{hostname}/{path}
    if parsed.scheme in ["https", "http"]:
        return HttpReader(uri, mode)

    # TODO:
    # - add s3
    # - add az
    # - add gs

    # s3://{bucket}/{key}
    elif parsed.scheme == "s3":
        return AWSS3Reader(uri, mode)

    # file:///{path}
    elif parsed.scheme == "file":
        return FileReader(uri.replace("file://", ""), mode)

    # Invalid Scheme
    elif parsed.scheme:
        raise ValueError(f"'{parsed.scheme}' is not supported")

    # fallback to FileReader
    else:
        return FileReader(uri, mode)
