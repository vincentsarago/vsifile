"""Rasterio Opener."""

from typing import List

from rasterio.abc import MultiByteRangeResourceContainer

from vsifile import BaseReader, VSIFile


class VSIOpener:
    """VSIOpener compatible with rasterio's vsiopener.

    Example:
        import rasterio
        from vsifile.rasterio import VSIOpener
        with rasterio.open("cog.tif", opener=VSIOpener()) as src:
            ...

    """

    def __init__(self, **kwargs):
        """init."""
        self._obj = VSIFile
        self._kwargs = kwargs

    def open(self, path, mode="rb", **kwds) -> BaseReader:
        """Return Obj."""
        return self._obj(path, mode=mode, **kwds, **self._kwargs)

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
        return 1


MultiByteRangeResourceContainer.register(VSIOpener)

opener = VSIOpener()
