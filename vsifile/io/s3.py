"""HTTP VSIFile reader"""

import os
from typing import Any, Optional, Union
from urllib.parse import urlparse

from attrs import define, field

from vsifile.io.base import BaseReader
from vsifile.logger import logger

try:
    from boto3.session import Session as boto3_session
    from botocore.exceptions import ClientError
except ImportError:  # pragma: nocover
    boto3_session = None  # type: ignore
    ClientError = None  # type: ignore


@define
class AWSS3Reader(BaseReader):
    """S3 VSIFILE Reader."""

    requester_pays: bool = field(
        factory=lambda: os.environ.get("AWS_REQUEST_PAYER", "").lower() == "requester"
    )
    client: Optional[Any] = field(default=None)

    bucket: str = field(init=False, default=None)
    key: str = field(init=False, default=None)

    loc: int = field(default=0, init=False)
    is_closed: bool = field(default=False, init=False)

    _size: int = field(default=0, init=False)
    _mtime: int = field(default=0, init=False)

    def __repr__(self) -> str:
        """Reader repr."""
        return f"{self.__class__.__name__}({self.name})"

    def __hash__(self):
        """Object hash."""
        return hash((self.name, self.mode))

    def __attrs_post_init__(self):
        """Setup Boto3 Client."""
        assert boto3_session is not None, "'boto3' must be installed to use AWSS3Reader"

        if not self.client:
            if profile_name := os.environ.get("AWS_PROFILE", None):
                session = boto3_session(profile_name=profile_name)

            else:
                access_key = os.environ.get("AWS_ACCESS_KEY_ID", None)
                secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY", None)
                access_token = os.environ.get("AWS_SESSION_TOKEN", None)

                # AWS_REGION is GDAL specific. Later overloaded by standard AWS_DEFAULT_REGION
                region_name = os.environ.get(
                    "AWS_DEFAULT_REGION", os.environ.get("AWS_REGION", None)
                )

                session = boto3_session(
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_access_key,
                    aws_session_token=access_token,
                    region_name=region_name or None,
                )

            # AWS_S3_ENDPOINT and AWS_HTTPS are GDAL config options of vsis3 driver
            # https://gdal.org/user/virtual_file_systems.html#vsis3-aws-s3-files
            endpoint_url = os.environ.get("AWS_S3_ENDPOINT", None)
            if endpoint_url:
                use_https = os.environ.get("AWS_HTTPS", "YES")
                if use_https.upper() in ["YES", "TRUE", "ON"]:
                    endpoint_url = "https://" + endpoint_url

                else:
                    endpoint_url = "http://" + endpoint_url

            self.client = session.client("s3", endpoint_url=endpoint_url)

        parsed = urlparse(self.name)
        self.bucket = parsed.netloc
        self.key = parsed.path.strip("/")

    def __enter__(self):
        """Open file and fetch header."""
        logger.debug(f"Opening: {self.name} (mode: {self.mode})")

        head = self.client.head_object(Bucket=self.bucket, Key=self.key)
        assert head["ResponseMetadata"]["HTTPStatusCode"] == 200
        assert head.get("AcceptRanges") == "bytes"

        self._mtime = int(head["LastModified"].timestamp())
        self._size = int(head.get("ContentLength")) or 0
        self.header = self._get_header()

        return self

    def close(self):
        """Close."""
        self.client.close()
        self.is_closed = True

    @property
    def closed(self) -> bool:
        """Closed?"""
        return self.is_closed

    def seekable(self) -> bool:
        """seekable stream."""
        return True

    def seek(self, loc: int, whence: int = 0) -> int:
        """Change stream position."""
        if whence == 0:
            self.loc = loc

        elif whence == 1:
            self.loc += loc

        elif whence == 2:
            if not self.size:
                raise ValueError(
                    "Cannot use end of stream because we don't know the size of the stream"
                )
            self.loc = self.size + loc

        else:
            raise ValueError(f"Invalid Whence value: {whence}")

        return self.loc

    def tell(self) -> int:
        """Return stream position."""
        return self.loc

    @property
    def size(self) -> int:
        """return file size."""
        return self._size

    @property
    def mtime(self) -> int:
        """retunr file modified date."""
        return self._mtime

    def _read(self, length: int = -1) -> Union[str, bytes]:
        """Low level read method."""
        logger.debug(f"Fetching {self.tell()}->{self.tell() + length}")

        params = {
            "Bucket": self.bucket,
            "Key": self.key,
            "Range": f"bytes={self.loc}-{self.loc + length - 1}",
        }
        if self.requester_pays:
            params["RequestPayer"] = "requester"

        response = self.client.get_object(**params)
        _ = self.seek(self.loc + length, 0)
        return response["Body"].read()
