"""HTTP VSIFile reader"""

from datetime import datetime

import httpx
from attrs import define, field

from vsifile.io.base import BaseReader
from vsifile.logger import logger


@define
class HttpReader(BaseReader):
    """HTTP VSIFILE Reader."""

    client: httpx.Client = field(factory=httpx.Client)

    loc: int = field(default=0, init=False)

    _size: int = field(default=0, init=False)
    _mtime: int = field(default=0, init=False)

    def __repr__(self) -> str:
        """Reader repr."""
        return f"{self.__class__.__name__}({self.name})"

    def __hash__(self):
        """Object hash."""
        return hash((self.name, self.mode))

    def __enter__(self):
        """Open file and fetch header."""
        logger.debug(f"Opening: {self.name} (mode: {self.mode})")
        head = self.client.head(self.name)
        assert head.status_code == 200
        assert head.headers.get("accept-ranges") == "bytes"

        if d := head.headers.get("last-modified"):
            self._mtime = int(
                datetime.strptime(d, "%a, %d %b %Y %H:%M:%S %Z").timestamp()
            )
        else:
            self._mtime = int(datetime.today().timestamp())

        self._size = int(head.headers.get("content-length")) or 0
        self.header = self._get_header()

        return self

    def close(self):
        """Close."""
        self.client.close()

    @property
    def closed(self) -> bool:
        """Closed?"""
        return self.client.is_closed

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

    def _read(self, length: int = -1) -> bytes:
        """Low level read method."""
        logger.debug(f"Fetching {self.tell()}->{self.tell() + length}")
        headers = {"Range": f"bytes={self.loc}-{self.loc + length - 1}"}
        response = self.client.get(self.name, headers=headers)
        response.raise_for_status()
        _ = self.seek(self.loc + length, 0)
        return response.content
