"""VSIFILE settings."""

from typing import Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings


class VSISettings(BaseSettings):
    """Cache settings"""

    # Diskcache Headers settings
    cache_headers_ttl: int = 300  # in seconds
    cache_headers_maxsize: int = 5120000000  # in bytes
    cache_directory: Optional[str] = None

    # LRU Blocks cache
    cache_blocks_ttl: int = 300  # in seconds
    cache_blocks_maxsize: int = 512  # in number of entries

    # Whether or not caching is enabled
    cache_disable: bool = False

    # equivalent of GDAL_INGESTED_BYTES_AT_OPEN
    ingested_bytes_at_open: int = 32768

    model_config = {
        "env_prefix": "VSIFILE_",
        "env_file": ".env",
        "extra": "ignore",
    }

    @model_validator(mode="after")
    def check_enable(self):
        """Check if cache is disabled."""
        if self.cache_disable:
            self.cache_headers_ttl = 0
            self.cache_headers_maxsize = 0
            self.cache_blocks_ttl = 0
            self.cache_blocks_maxsize = 0

        return self
