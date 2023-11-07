"""HTTP VSIFile reader"""

from dataclasses import dataclass, field

import httpx
from diskcache import Cache

from vsifile.logger import logger
from vsifile.settings import cache_settings


@dataclass
class HttpReader:
    """HTTP VSIFILE Reader."""

    name: str
    mode: str = "rb"

    _loc: int = 0
    _size: int = 0
    _header: bytes = None

    _client: httpx.Client = field(default_factory=httpx.Client)

    def __post_init__(self):
        """Setupg cache."""
        logger.info(f"Using {cache_settings.directory} Cache directory")
        self._cache = Cache(
            directory=cache_settings.directory,
            size_limit=cache_settings.headers_maxsize,
        )

    def __hash__(self):
        """Object hash."""
        return hash((self.name, self.mode))

    def __enter__(self):
        """Open file and fetch header."""
        logger.info(f"Opening: {self.name} (mode: {self.mode})")
        head = self._client.head(self.name)
        assert head.status_code == 200
        assert head.headers.get("accept-ranges") == "bytes"

        self._size = head.headers.get("content-length") or 0
        self._header = self._get_header()
        return self

    def _get_header(self):
        header = self._cache.get(f"{self.name}-header", read=True)
        if not header:
            logger.info("Adding Header in cache")
            header = self._read(cache_settings.header_size)
            self.seek(0)
            self._cache.set(
                f"{self.name}-header",
                header,
                expire=cache_settings.headers_ttl,
                read=True,
                tag="data",
            )
            return header

        return header.read()

    def open(self):
        """Open."""
        return self.__enter__()

    def close(self):
        """Close."""
        self._cache.close()
        self._client.close()

    def __exit__(self, exc_type, exc_value, traceback):
        """Context Exit."""
        self.close()

    def tell(self):
        """Return stream position."""
        return self._loc

    @property
    def seekable(self):
        """seekable stream."""
        return True

    def seek(self, loc: int, whence: int = 0):
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

    @property
    def closed(self) -> bool:
        """Closed?"""
        return self._client.is_closed

    # TODO
    # # add LRU cache for blocks here
    # # based on lengh and _loc
    # @cached(  # type: ignore
    #     TTLCache(maxsize=cache_settings.blocks_maxsize, ttl=cache_settings.blocks_ttl),
    #     key=lambda self, length: hashkey(self.name, self._loc, length),
    # )
    def read(self, length: int = -1) -> bytes:
        """Read stream"""
        if self.closed:
            raise ValueError("I/O operation on closed file.")

        if length == 0:
            return b""

        # TODO: maybe check if gdal is trying to make a bigger header request?
        loc = self.tell()
        if loc + length <= len(self._header):
            self.seek(loc + length, 0)
            logger.info(f"Reading {loc}->{loc+length} from Header cache")
            return self._header[loc : loc + length]

        return self._read(length)

    def _read(self, length: int):
        logger.info(f"Fetching {self.tell()}->{self.tell() + length}")
        headers = {"Range": f"bytes={self._loc}-{self._loc + length - 1}"}
        response = self._client.get(self.name, headers=headers)
        response.raise_for_status()
        self.seek(self._loc + length, 0)
        return response.content
