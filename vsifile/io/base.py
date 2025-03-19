"""Base VSIFile reader"""

from __future__ import annotations

import abc
import datetime
from threading import Lock
from typing import TYPE_CHECKING, List

from attrs import define, field
from cachetools import TTLCache, cached
from cachetools.keys import hashkey
from diskcache import Cache

from vsifile.logger import logger
from vsifile.settings import VSISettings

if TYPE_CHECKING:
    from obstore.store import (
        AzureConfigInput,
        ClientConfig,
        GCSConfigInput,
        ObjectStore,
        RetryConfig,
        S3ConfigInput,
    )

vsi_settings = VSISettings()

# TTL Block Cache (in-memory)
block_cache: TTLCache = TTLCache(
    maxsize=vsi_settings.cache_blocks_maxsize,
    ttl=vsi_settings.cache_blocks_ttl,
)

# TTL Header Cache (in-disk)
header_cache: Cache = Cache(
    directory=vsi_settings.cache_directory,
    size_limit=vsi_settings.cache_headers_maxsize,
)


def _check_mode(instance, attribute, value):
    if value != "rb":
        raise ValueError(
            f"Unsupported mode '{instance.__class__.__name__}'. VSIFILE offers only `read-only (rb)` mode"
        )


@define
class BaseReader(metaclass=abc.ABCMeta):
    """Abstract Base class for VSIFILE Reader."""

    name: str = field()
    mode: str = field(default="rb", validator=_check_mode)

    config: S3ConfigInput | GCSConfigInput | AzureConfigInput | None = field(default=None)
    client_options: ClientConfig | None = field(default=None)
    retry_config: RetryConfig | None = field(default=None)

    header: bytes = field(init=False)
    header_cache: Cache = field(init=False, factory=lambda: header_cache)

    _key: str = field(init=False)
    _store: ObjectStore = field(init=False)
    _loc: int = field(init=False, default=0)
    _closed: bool = field(init=False, default=True)
    _size: int = field(init=False)
    _mtime: datetime.datetime = field(init=False)
    _seekable: bool = field(init=False, default=False)

    @abc.abstractmethod
    def __repr__(self) -> str:
        """Reader repr."""
        ...

    @abc.abstractmethod
    def __hash__(self):
        """Object hash."""
        ...

    def _get_header(self) -> bytes:
        cache = self.header_cache.get(f"{self.name}-header", read=True)
        if not cache:
            logger.debug("VSIFILE_INFO: GET")
            logger.debug(f"VSIFILE: Downloading: 0-{vsi_settings.ingested_bytes_at_open}")
            response = self._store.get(
                self._key,
                options={"range": (0, vsi_settings.ingested_bytes_at_open)},
            )

            meta = response.meta
            header = response.bytes().to_bytes()

            logger.debug("VSIFILE: Adding Header in cache")
            self.header_cache.set(
                f"{self.name}-header",
                (header, meta),
                expire=vsi_settings.cache_headers_ttl,
                tag="data",
            )

        else:
            logger.debug("VSIFILE: Found Header in cache")
            header, meta = cache

        self._size = meta["size"]
        self._mtime = meta["last_modified"]
        self._seekable = True

        return header

    def __enter__(self):
        """Open file and fetch header."""
        logger.debug(f"VSIFILE: Opening {self.name} (mode: {self.mode})")
        self._closed = False
        self.header = self._get_header()
        return self

    def open(self):
        """Open."""
        return self.__enter__()

    def close(self):
        """Close."""
        self._closed = True

    def __exit__(self, exc_type, exc_value, traceback):
        """Context Exit."""
        self.close()

    @property
    def closed(self) -> bool:
        """Closed?"""
        return self._closed

    @property
    def mtime(self) -> datetime.datetime:
        """return file modified date."""
        return self._mtime

    @property
    def size(self) -> int:
        """return file size."""
        return self._size

    @property
    def seekable(self) -> bool:
        """file seekable."""
        return self._seekable

    def seek(self, loc: int, whence: int = 0) -> int:
        """Change stream position."""
        if whence == 0:
            self._loc = loc

        elif whence == 1:
            self._loc += loc

        else:
            raise ValueError(f"do not support whence={whence}")

        return self._loc

    def tell(self) -> int:
        """Return stream position."""
        return self._loc

    def read(self, length: int = -1) -> bytes:
        """Read stream."""
        if self.closed:
            raise ValueError("I/O operation on closed file.")

        if length == 0:
            return b""

        # TODO: maybe check if gdal is trying to make a bigger header request?
        loc = self.tell()
        if loc + length <= len(self.header):
            logger.debug(f"VSIFILE: Reading {loc}->{loc+length} from Header cache")
            _ = self.seek(loc + length, 0)
            return self.header[loc : loc + length]

        output_data = self.get_byte_range(loc, length)

        # If we read from cache, the stream position won't be updated
        # so we need to do it manually
        if self.tell() == loc:
            _ = self.seek(loc + length, 0)

        return output_data

    @cached(
        block_cache,
        key=lambda self, offset, size: hashkey(self.name, offset, size),
        lock=Lock(),
    )
    def get_byte_range(self, offset, size) -> bytes:
        """Read range."""
        logger.debug("VSIFILE_INFO: GET")
        logger.debug(f"VSIFILE: Downloading: {offset}-{offset + size}")
        self._loc += size
        return self._store.get_range(
            self._key,
            start=offset,
            end=offset + size,
        ).to_bytes()

    def get_byte_ranges(
        self,
        offsets: List[int],
        sizes: List[int],
    ) -> List[bytes]:
        """Read multiple ranges."""
        logger.debug("VSIFILE_INFO: GET")
        logger.debug("VSIFILE: Using MultiRange Reads")

        ends = [offset + size for offset, size in zip(offsets, sizes)]
        ranges = [f"{s}-{e}" for s, e in zip(offsets, ends)]
        logger.debug(f"VSIFILE: Downloading: {', '.join(ranges)}")

        self._loc = offsets[-1] + sizes[-1]

        # TODO add blocks in cache
        return [
            buff.to_bytes()
            for buff in self._store.get_ranges(self._key, starts=offsets, ends=ends)
        ]
