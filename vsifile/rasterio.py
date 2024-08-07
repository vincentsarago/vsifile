"""Rasterio Opener."""

from typing import List

from rasterio._vsiopener import _AbstractOpener

from vsifile import BaseReader, VSIFile


class VSIOpener(_AbstractOpener):
    """VSIOpener compatible with rasterio's vsiopener.

    Example:
        import rasterio
        from vsifile.rasterio import VSIOpener
        with rasterio.open("cog.tif", opener=VSIOpener()) as src:
            ...

    """

    def __init__(self):
        """init."""
        self._obj = VSIFile

    def open(self, path, mode="r", **kwds) -> BaseReader:
        """Return Obj."""
        return self._obj(path, mode=mode, **kwds)

    def isfile(self, path) -> bool:
        """isfile."""
        return True

    def isdir(self, path) -> bool:
        """isdir."""
        return False

    def ls(self, path) -> List:
        """ls."""
        return []

    def mtime(self, path) -> int:
        """mtime."""
        return 0

    def size(self, path) -> int:
        """size."""
        with self._obj(path) as f:
            return f.size()

    def read_multi_range(self) -> bool:
        """read_multi_range."""
        return True


opener = VSIOpener()
