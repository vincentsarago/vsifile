"""Base VSIFile reader"""

import abc
from threading import Lock
from typing import List, Union

from attrs import define, field
from cachetools import TTLCache, cached
from cachetools.keys import hashkey
from diskcache import Cache

from vsifile.logger import logger
from vsifile.settings import VSISettings

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

    header: Union[str, bytes] = field(init=False)
    header_cache: Cache = field(init=False, factory=lambda: header_cache)

    def __repr__(self) -> str:
        """Reader repr."""
        return f"{self.__class__.__name__}({self.name})"

    def __hash__(self):
        """Object hash."""
        return hash((self.name, self.mode))

    def _get_header(self) -> bytes:
        header = self.header_cache.get(f"{self.name}-header", read=True)
        if not header:
            logger.debug("Adding Header in cache")
            header = self._read(vsi_settings.ingested_bytes_at_open)
            self.seek(0)
            self.header_cache.set(
                f"{self.name}-header",
                header,
                expire=vsi_settings.cache_headers_ttl,
                read=True,
                tag="data",
            )
            return header

        else:
            logger.debug("Found Header in cache")
            return header.read()

    @abc.abstractmethod
    def __enter__(self):
        """Open file and fetch header."""
        ...

    def open(self):
        """Open."""
        return self.__enter__()

    @abc.abstractmethod
    def close(self):
        """Close."""
        ...

    def __exit__(self, exc_type, exc_value, traceback):
        """Context Exit."""
        self.close()

    @abc.abstractmethod
    def seekable(self) -> bool:
        """file seekable."""
        ...

    @property
    @abc.abstractmethod
    def closed(self) -> bool:
        """Closed?"""
        ...

    @abc.abstractmethod
    def seek(self, loc: int, whence: int = 0) -> int:
        """Change stream position."""
        ...

    @abc.abstractmethod
    def tell(self) -> int:
        """Return stream position."""
        ...

    @abc.abstractmethod
    def _read(self, length: int = -1) -> Union[str, bytes]:
        """Low level read method."""
        ...

    @property
    @abc.abstractmethod
    def mtime(self) -> int:
        """return file modified date."""
        ...

    @property
    @abc.abstractmethod
    def size(self) -> int:
        """return file size."""
        ...

    def read(self, length: int = -1) -> Union[str, bytes]:
        """Read stream."""
        if self.closed:
            raise ValueError("I/O operation on closed file.")

        if length == 0:
            return b""

        # TODO: maybe check if gdal is trying to make a bigger header request?
        loc = self.tell()
        if loc + length <= len(self.header):
            logger.debug(f"Reading {loc}->{loc+length} from Header cache")
            _ = self.seek(loc + length, 0)
            return self.header[loc : loc + length]

        output_data = self._cached_read(length)

        # If we read from cache, the stream position won't be updated
        # so we need to do it manually
        if self.tell() == loc:
            _ = self.seek(loc + length, 0)

        return output_data

    @cached(
        block_cache,
        key=lambda self, length: hashkey(self.name, self.tell(), length),
        lock=Lock(),
    )
    def _cached_read(self, length: int = -1) -> Union[str, bytes]:
        return self._read(length)

    def _read_range(self, offset, size) -> Union[str, bytes]:
        _ = self.seek(offset)
        return self.read(size)

    def get_byte_ranges(
        self,
        offsets: List[int],
        sizes: List[int],
    ) -> List[Union[str, bytes]]:
        """Read multiple ranges."""
        logger.debug(f"Using MultiRange Reads for {len(offsets)} ranges")
        return [self._read_range(offset, size) for (offset, size) in zip(offsets, sizes)]
