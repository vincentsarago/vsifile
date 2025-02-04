"""File VSIFile reader"""

from pathlib import Path

from attrs import define
from obstore.store import LocalStore

from vsifile.io.base import BaseReader


@define
class FileReader(BaseReader):
    """Local File VSIFILE Reader."""

    def __attrs_post_init__(self):
        """Create Store and parse name."""
        self._store = LocalStore()
        self._key = str(Path(self.name.replace("file://", "")).resolve())

    def __repr__(self) -> str:
        """Reader repr."""
        return f"{self.__class__.__name__}({self.name})"

    def __hash__(self):
        """Object hash."""
        return hash((self.name, self.mode))
