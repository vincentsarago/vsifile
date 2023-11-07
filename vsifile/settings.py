"""VSIFILE settings."""

from typing import Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings


class CacheSettings(BaseSettings):
    """Cache settings"""

    # Diskcache Headers settings
    headers_ttl: int = 300  # in seconds
    headers_maxsize: int = 5120000000  # in bytes
    directory: Optional[str] = None

    # LRU Blocks cache
    blocks_ttl: int = 300  # in seconds
    blocks_maxsize: int = 512  # in Mbytes ?

    # Whether or not caching is enabled
    disable: bool = False

    header_size: int = 32768

    model_config = {"env_prefix": "VSIFILE_CACHE_", "env_file": ".env"}

    @model_validator(mode="after")
    def check_enable(self):
        """Check if cache is disabled."""
        if self.disable:
            self.headers_ttl = 0
            self.headers_maxsize = 0
            self.blocks_ttl = 0
            self.blocks_maxsize = 0

        return self


cache_settings = CacheSettings()
