"""Base VSIFile reader"""

from __future__ import annotations

import abc
import datetime
from functools import cached_property
from threading import Lock
from typing import TYPE_CHECKING, List

import obstore as obs
from attrs import define, field
from cachetools import TTLCache, cached
from cachetools.keys import hashkey
from diskcache import Cache

from vsifile.logger import logger
from vsifile.settings import VSISettings

if TYPE_CHECKING:
    from obstore.store import ObjectStore


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

    header: bytes = field(init=False)
    header_cache: Cache = field(init=False, factory=lambda: header_cache)

    _key: str = field(init=False)
    _store: ObjectStore = field(init=False)
    _loc: int = field(init=False, default=0)
    _closed: bool = field(init=False, default=True)
    _size: int = field(init=False)

    @abc.abstractmethod
    def __repr__(self) -> str:
        """Reader repr."""
        ...

    @abc.abstractmethod
    def __hash__(self):
        """Object hash."""
        ...

    def _get_header(self) -> bytes:
        logger.debug("VSIFILE_INFO: HEAD (Open)")
        head = obs.head(self._store, self._key)
        self._size = head["size"]

        header = self.header_cache.get(f"{self.name}-header", read=True)
        if not header:
            end = (
                vsi_settings.ingested_bytes_at_open
                if self._size > vsi_settings.ingested_bytes_at_open
                else self._size
            )
            logger.debug("VSIFILE_INFO: GET")
            logger.debug(f"VSIFILE: Downloading: 0-{end}")
            header = bytes(obs.get_range(self._store, self._key, start=0, end=end))

            logger.debug("VSIFILE: Adding Header in cache")
            self.header_cache.set(
                f"{self.name}-header",
                header,
                expire=vsi_settings.cache_headers_ttl,
                read=True,
                tag="data",
            )
            return header

        else:
            logger.debug("VSIFILE: Found Header in cache")
            return header.read()

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

    @cached_property
    def mtime(self) -> datetime.datetime:
        """return file modified date."""
        logger.debug("VSIFILE_INFO: HEAD (mtime)")
        head = obs.head(self._store, self._key)
        return head["last_modified"]

    @property
    def size(self) -> int:
        """return file size."""
        return self._size

    @cached_property
    def seekable(self) -> bool:
        """file seekable."""
        logger.debug("VSIFILE_INFO: HEAD (seekable)")
        return obs.head(self._store, self._key) is not None

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
        return bytes(
            obs.get_range(
                self._store,
                self._key,
                start=offset,
                end=offset + size,
            )
        )

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
            bytes(buff)
            for buff in obs.get_ranges(self._store, self._key, starts=offsets, ends=ends)
        ]
