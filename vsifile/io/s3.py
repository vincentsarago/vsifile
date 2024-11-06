"""HTTP VSIFile reader"""

import os
from typing import Dict, Optional
from urllib.parse import urlparse

from attrs import define, field
from obstore.store import S3Store

from vsifile.io.base import BaseReader

try:
    from boto3.session import Session as boto3_session
except ImportError:  # pragma: nocover
    boto3_session = None  # type: ignore


@define
class AWSS3Reader(BaseReader):
    """S3 VSIFILE Reader."""

    requester_pays: bool = field(
        factory=lambda: os.environ.get("AWS_REQUEST_PAYER", "").lower() == "requester"
    )
    config: Dict = field(factory=dict)
    client_options: Dict = field(factory=dict)
    retry_config: Optional[Dict] = field(default=None)

    def __repr__(self) -> str:
        """Reader repr."""
        return f"{self.__class__.__name__}({self.name})"

    def __hash__(self):
        """Object hash."""
        return hash((self.name, self.mode))

    def __attrs_post_init__(self):
        """Setup Boto3 Client."""
        parsed = urlparse(self.name)
        bucket = parsed.netloc
        self._key = parsed.path.strip("/")

        config = {}
        keys = {k.upper() for k in list(self.config)}
        endpoint_url = os.environ.get("AWS_S3_ENDPOINT", None)
        use_https = os.environ.get("AWS_HTTPS", "YES")
        if not {"AWS_ENDPOINT_URL", "AWS_ENDPOINT"}.intersection(keys) and endpoint_url:
            # AWS_S3_ENDPOINT and AWS_HTTPS are GDAL config options of vsis3 driver
            # https://gdal.org/user/virtual_file_systems.html#vsis3-aws-s3-files
            if use_https.upper() in ["YES", "TRUE", "ON"]:
                config["AWS_ENDPOINT_URL"] = "https://" + endpoint_url
            else:
                config["AWS_ENDPOINT_URL"] = "http://" + endpoint_url

        options = {}
        keys = [k.upper() for k in list(self.client_options)]
        if "ALLOW_HTTP" not in keys and use_https in ["NO", "FALSE", "OFF"]:
            options["ALLOW_HTTP"] = "TRUE"

        # 1. Create Store from session
        if boto3_session:
            if aws_profile := os.environ.get("AWS_PROFILE"):
                session = boto3_session(profile_name=aws_profile)

            else:
                access_key = os.environ.get("AWS_ACCESS_KEY_ID")
                secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
                access_token = os.environ.get("AWS_SESSION_TOKEN")

                # AWS_REGION is GDAL specific. Later overloaded by standard AWS_DEFAULT_REGION
                region_name = (
                    os.environ.get("AWS_DEFAULT_REGION", os.environ.get("AWS_REGION"))
                    or None
                )

                session = boto3_session(
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_access_key,
                    aws_session_token=access_token,
                    region_name=region_name,
                )

            self._store = S3Store.from_session(
                session,
                bucket,
                config={**self.config, **config},
                client_options={**self.client_options, **options},
                retry_config=self.retry_config,
            )

        else:
            self._store = S3Store.from_env(
                bucket,
                config={**self.config, **config},
                client_options={**self.client_options, **options},
                retry_config=self.retry_config,
            )

        return self
