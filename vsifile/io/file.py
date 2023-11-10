"""File VSIFile reader"""

from dataclasses import dataclass

from vsifile.io.base import BaseReader
from vsifile.logger import logger


@dataclass
class FileReader(BaseReader):
    """Local File VSIFILE Reader."""

    def __repr__(self) -> str:
        """Reader repr."""
        return f"{self.__class__.__name__}({self.name})"

    def __hash__(self):
        """Object hash."""
        return hash((self.name, self.mode))

    def __enter__(self):
        """Open file and fetch header."""
        logger.debug(f"Opening: {self.name} (mode: {self.mode})")
        self.file = open(self.name, self.mode)
        self._header = self._get_header()
        return self

    def close(self):
        """Close."""
        self._cache.close()
        self.file.close()

    @property
    def seekable(self) -> bool:
        """file seekable."""
        return self.file.seekable

    @property
    def closed(self) -> bool:
        """Closed?"""
        return self.file.closed

    def seek(self, loc: int, whence: int = 0) -> int:
        """Change stream position."""
        return self.file.seek(loc, whence)

    def tell(self) -> int:
        """Return stream position."""
        return self.file.tell()

    def _read(self, length: int = -1) -> bytes:
        """Low level read method."""
        logger.debug(f"Fetching {self.tell()}->{self.tell() + length}")
        return self.file.read(length)
