"""HTTP VSIFile reader"""

from dataclasses import dataclass

import httpx

from vsifile.io.base import BaseReader
from vsifile.logger import logger


@dataclass
class HttpReader(BaseReader):
    """HTTP VSIFILE Reader."""

    name: str
    mode: str = "rb"

    _header: bytes = None

    _loc: int = 0
    _size: int = 0
    client: httpx.Client = None

    def __repr__(self) -> str:
        """Reader repr."""
        return f"{self.__class__.__name__}({self.name})"

    def __hash__(self):
        """Object hash."""
        return hash((self.name, self.mode))

    def __post_init__(self):
        """Setupg cache."""
        super().__post_init__()
        self.client = self.client or httpx.Client()

    def __enter__(self):
        """Open file and fetch header."""
        logger.debug(f"Opening: {self.name} (mode: {self.mode})")
        head = self.client.head(self.name)
        assert head.status_code == 200
        assert head.headers.get("accept-ranges") == "bytes"

        self._size = head.headers.get("content-length") or 0
        self._header = self._get_header()
        return self

    def close(self):
        """Close."""
        self._cache.close()
        self.client.close()

    @property
    def closed(self) -> bool:
        """Closed?"""
        return self.client.is_closed

    @property
    def seekable(self) -> bool:
        """seekable stream."""
        return True

    def seek(self, loc: int, whence: int = 0) -> int:
        """Change stream position."""
        if whence == 0:
            self._loc = loc

        elif whence == 1:
            self._loc += loc

        elif whence == 2:
            if not self._size:
                raise ValueError(
                    "Cannot use end of stream because we don't know the size of the stream"
                )
            self._loc = self._size + loc

        else:
            raise ValueError(f"Invalid Whence value: {whence}")

        return self._loc

    def tell(self) -> int:
        """Return stream position."""
        return self._loc

    def _read(self, length: int = -1) -> bytes:
        """Low level read method."""
        logger.debug(f"Fetching {self.tell()}->{self.tell() + length}")
        headers = {"Range": f"bytes={self._loc}-{self._loc + length - 1}"}
        response = self.client.get(self.name, headers=headers)
        response.raise_for_status()
        _ = self.seek(self._loc + length, 0)
        return response.content
