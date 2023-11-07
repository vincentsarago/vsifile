"""File VSIFile reader"""

from dataclasses import dataclass

from diskcache import Cache

from vsifile.logger import logger
from vsifile.settings import cache_settings


@dataclass
class FileReader:
    """Local File VSIFILE Reader."""

    name: str
    mode: str = "rb"

    _header: bytes = None

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
        self.file = open(self.name, self.mode)
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
        self.file.close()

    def __exit__(self, exc_type, exc_value, traceback):
        """Context Exit."""
        self.close()

    def tell(self):
        """Return stream position."""
        return self.file.tell()

    @property
    def seekable(self):
        """file seekable."""
        return self.file.seekable

    def seek(self, loc: int, whence: int = 0):
        """Change stream position."""
        return self.file.seek(loc, whence)

    @property
    def closed(self) -> bool:
        """Closed?"""
        return self.file.closed

    # TODO
    # # add LRU cache for blocks here
    # # based on lengh and _loc
    # @cached(  # type: ignore
    #     TTLCache(maxsize=cache_settings.blocks_maxsize, ttl=cache_settings.blocks_ttl),
    #     key=lambda self, length: hashkey(self.name, self._loc, length),
    # )
    def read(self, length: int = -1) -> bytes:
        """Read stream."""
        if self.closed:
            raise ValueError("I/O operation on closed file.")

        if length == 0:
            return b""

        # TODO: maybe check if gdal is trying to make a bigger header request?
        loc = self.tell()
        if loc + length <= len(self._header):
            logger.info(f"Reading {loc}->{loc+length} from Header cache")
            self.seek(loc + length, 0)
            return self._header[loc : loc + length]

        return self._read(length)

    def _read(self, length: int = -1):
        logger.info(f"Fetching {self.tell()}->{self.tell() + length}")
        return self.file.read(length)
