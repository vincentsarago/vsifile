"""File VSIFile reader"""

import abc
from dataclasses import dataclass
from typing import List

from cachetools import TTLCache, cached
from cachetools.keys import hashkey
from diskcache import Cache

from vsifile.logger import logger
from vsifile.settings import vsi_settings


@dataclass
class BaseReader(metaclass=abc.ABCMeta):
    """Abstract Base class for VSIFILE Reader."""

    name: str
    mode: str = "rb"

    _header: bytes = None

    def __post_init__(self):
        """Setupg cache."""
        logger.debug(f"Using {vsi_settings.cache_directory} Cache directory")
        self._cache = Cache(
            directory=vsi_settings.cache_directory,
            size_limit=vsi_settings.cache_headers_maxsize,
        )

    def __repr__(self) -> str:
        """Reader repr."""
        return f"{self.__class__.__name__}({self.name})"

    def __hash__(self):
        """Object hash."""
        return hash((self.name, self.mode))

    def _get_header(self):
        header = self._cache.get(f"{self.name}-header", read=True)
        if not header:
            logger.debug("Adding Header in cache")
            header = self._read(vsi_settings.ingested_bytes_at_open)
            self.seek(0)
            self._cache.set(
                f"{self.name}-header",
                header,
                expire=vsi_settings.cache_headers_ttl,
                read=True,
                tag="data",
            )
            return header

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

    @property
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
    def _read(self, length: int = -1) -> bytes:
        """Low level read method."""
        ...

    def read(self, length: int = -1) -> bytes:
        """Read stream."""
        if self.closed:
            raise ValueError("I/O operation on closed file.")

        if length == 0:
            return b""

        # TODO: maybe check if gdal is trying to make a bigger header request?
        loc = self.tell()
        if loc + length <= len(self._header):
            logger.debug(f"Reading {loc}->{loc+length} from Header cache")
            _ = self.seek(loc + length, 0)
            return self._header[loc : loc + length]

        output_data = self._cached_read(length)

        # If we read from cache, the stream position won't be updated
        # so we need to do it manually
        if self.tell() == loc:
            _ = self.seek(loc + length, 0)

        return output_data

    @cached(  # type: ignore
        TTLCache(
            maxsize=vsi_settings.cache_blocks_maxsize, ttl=vsi_settings.cache_blocks_ttl
        ),
        key=lambda self, length: hashkey(self.name, self.tell(), length),
    )
    def _cached_read(self, length: int = -1) -> bytes:
        return self._read(length)

    # Not Yet in Rasterio
    # see: https://github.com/rasterio/rasterio/pull/2898#issuecomment-1803743898
    def read_multi_range(
        self,
        nranges: int,
        offsets: List[int],
        sizes: List[int],
    ) -> List[bytes]:
        """Read multiple ranges."""
        return [
            self._read_range(offset, size) for (offset, size) in zip(offsets, sizes)
        ]

    def _read_range(self, offset, size) -> bytes:
        _ = self.seek(offset)
        return self.read(size)
