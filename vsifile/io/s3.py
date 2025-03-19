"""HTTP VSIFile reader"""

import os
from typing import Optional
from urllib.parse import urlparse

import httpx
from attrs import define, field
from obstore.store import S3Store

from vsifile.io.base import BaseReader
from vsifile.logger import logger


def _find_bucket_region(bucket: str, use_https: bool = True) -> Optional[str]:
    logger.debug("VSIFILE_INFO_HEADER_OUT: GET")
    prefix = "https" if use_https else "http"
    response = httpx.get(f"{prefix}://{bucket}.s3.amazonaws.com")
    return response.headers.get("x-amz-bucket-region")


@define
class AWSS3Reader(BaseReader):
    """S3 VSIFILE Reader."""

    requester_pays: bool = field(
        factory=lambda: os.environ.get("AWS_REQUEST_PAYER", "").lower() == "requester"
    )
    infer_region: bool = field(default=True)

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

        # AWS_S3_ENDPOINT and AWS_HTTPS are GDAL config options of vsis3 driver
        # https://gdal.org/user/virtual_file_systems.html#vsis3-aws-s3-files
        endpoint_url = os.environ.get("AWS_S3_ENDPOINT", None)
        use_https = os.environ.get("AWS_HTTPS", "YES") in ["YES", "TRUE", "ON"]
        region_name_env = (
            os.environ.get("AWS_REGION", os.environ.get("AWS_DEFAULT_REGION")) or None
        )

        # client_options: obstore.store.ClientConfig
        options = {}
        client_options = self.client_options or {}
        keys = [k.upper() for k in list(client_options)]
        if "ALLOW_HTTP" not in keys and not use_https:
            options["ALLOW_HTTP"] = "TRUE"

        # config: obstore.store.S3Config | obstore.store.S3ConfigInput
        config = {}
        s3_config = self.config or {}

        if "endpoint" not in s3_config and endpoint_url:
            config["endpoint"] = (
                "https://" + endpoint_url if use_https else "http://" + endpoint_url
            )

        if "request_payer" not in s3_config and self.requester_pays:
            config["request_payer"] = True

        if "region" not in s3_config and self.infer_region:
            # infer region or fallback to env variables
            config["region"] = _find_bucket_region(bucket, use_https) or region_name_env

        self._store = S3Store(
            bucket,
            config={**s3_config, **config},
            client_options={**client_options, **options},
            retry_config=self.retry_config,
        )

        return self
