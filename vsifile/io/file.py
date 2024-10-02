"""File VSIFile reader"""

import io
import os
from typing import Union

from attrs import define, field

from vsifile.io.base import BaseReader
from vsifile.logger import logger


@define
class FileReader(BaseReader):
    """Local File VSIFILE Reader."""

    file: Union[io.TextIOBase, io.RawIOBase, io.BufferedIOBase] = field(init=False)

    def __repr__(self) -> str:
        """Reader repr."""
        return f"{self.__class__.__name__}({self.name})"

    def __hash__(self):
        """Object hash."""
        return hash((self.name, self.mode))

    def __enter__(self):
        """Open file and fetch header."""
        logger.debug(f"Opening: {self.name} (mode: {self.mode})")
        name = self.name.replace("file://", "")
        self.file = io.open(name, self.mode)
        self.header = self._get_header()
        return self

    def close(self):
        """Close."""
        self.file.close()

    def seekable(self) -> bool:
        """file seekable."""
        return self.file.seekable()

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

    def _read(self, length: int = -1) -> Union[str, bytes]:
        """Low level read method."""
        logger.debug(f"Fetching {self.tell()}->{self.tell() + length}")
        return self.file.read(length)

    @property
    def mtime(self) -> int:
        """retunr file modified date."""
        return int(os.stat(self.name).st_mtime)

    @property
    def size(self) -> int:
        """return file size."""
        self.seek(0, os.SEEK_END)
        size = self.tell()
        self.seek(0)
        return size
