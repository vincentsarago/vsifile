"""test vsifile."""

import os

from vsifile import VSIFile
from vsifile.io import FileReader

fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")
cog = os.path.join(fixtures_dir, "cog.tif")


def test_vsifile_file():
    """Test VSIFile Local File reader."""
    with VSIFile(cog, "rb") as f:
        assert isinstance(f, FileReader)
        assert hash(f)
        assert "FileReader" in str(f)

        assert not f.closed
        assert f._cache
        assert len(f._header) == 32768
        assert f.tell() == 0
        assert f.seekable

        b = f.read(100)
        assert len(b) == 100
        assert f._header[0:100] == b
        assert f.tell() == 100

        _ = f.seek(0)
        assert f.tell() == 0

        _ = f.seek(40000)
        assert f.tell() == 40000

        b = f.read(100)
        assert f.tell() == 40100

        # fetch the same block (should be from LRU cache)
        _ = f.seek(40000)
        b_cache = f.read(100)
        assert f.tell() == 40100
        assert b_cache == b

        b = f.read_multi_range(2, [100, 200], [10, 20])
        assert len(b) == 2
        assert len(b[0]) == 10
        assert len(b[1]) == 20
        assert f.tell() == 220

    assert f.closed

    with VSIFile(f"file://{cog}", "rb") as f:
        assert isinstance(f, FileReader)
