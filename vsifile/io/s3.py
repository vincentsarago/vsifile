"""HTTP VSIFile reader"""

import os
import urllib.error
import urllib.request
from typing import Dict, Optional
from urllib.parse import urlparse

from attrs import define, field
from obstore.store import S3Store

from vsifile.io.base import BaseReader
from vsifile.logger import logger


def _find_bucket_region(bucket: str) -> Optional[str]:
    try:
        logger.debug("VSIFILE_INFO_HEADER_OUT: GET")
        response = urllib.request.urlopen(f"https://{bucket}.s3.amazonaws.com")
        return response.getheader("x-amz-bucket-region")
    except urllib.error.HTTPError:
        pass

    return None


@define
class AWSS3Reader(BaseReader):
    """S3 VSIFILE Reader."""

    requester_pays: bool = field(
        factory=lambda: os.environ.get("AWS_REQUEST_PAYER", "").lower() == "requester"
    )
    config: Dict = field(factory=dict)
    client_options: Dict = field(factory=dict)
    retry_config: Optional[Dict] = field(default=None)
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

        region_name_env = (
            os.environ.get("AWS_REGION", os.environ.get("AWS_DEFAULT_REGION")) or None
        )

        region_keys = [
            "AWS_REGION",
            "aws_region",
            "region",
            "AWS_DEFAULT_REGION",
            "aws_default_region",
            "default_region",
        ]
        region_name_config = next(
            (self.config[k] for k in region_keys if k in self.config), None
        )
        if self.infer_region and not region_name_config:
            config["AWS_REGION"] = _find_bucket_region(bucket) or region_name_env

        self._store = S3Store(
            bucket,
            config={**self.config, **config},
            client_options={**self.client_options, **options},
            retry_config=self.retry_config,
        )

        return self
