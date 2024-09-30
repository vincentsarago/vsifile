"""test vsifile."""

import logging
import os
import time
from unittest.mock import patch

import pytest

from vsifile import VSIFile
from vsifile.io import FileReader
from vsifile.settings import VSISettings

fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")
cog = os.path.join(fixtures_dir, "cog.tif")


def test_vsifile_file():
    """Test VSIFile Local File reader."""
    with pytest.raises(ValueError):
        with VSIFile(cog, "r") as f:
            pass

    with pytest.raises(ValueError):
        with VSIFile(cog, "w") as f:
            pass

    with VSIFile(cog, "rb") as f:
        assert isinstance(f, FileReader)
        assert hash(f)
        assert "FileReader" in str(f)

        assert not f.closed
        assert f.header_cache
        assert len(f.header) == 32768
        assert f.tell() == 0
        assert f.seekable

        b = f.read(100)
        assert len(b) == 100
        assert f.header[0:100] == b
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

        b = f.get_byte_ranges([100, 200], [10, 20])
        assert len(b) == 2
        assert len(b[0]) == 10
        assert len(b[1]) == 20
        assert f.tell() == 220

    assert f.closed

    with VSIFile(f"file://{cog}", "rb") as f:
        assert isinstance(f, FileReader)


def test_vsifile_header_cache(caplog, tmp_path):
    """Test VSIFile header cache."""
    caplog.set_level(logging.DEBUG, logger="vsifile")
    d = tmp_path / "cache"
    d.mkdir()

    with patch(
        "vsifile.io.base.vsi_settings",
        new=VSISettings(
            cache_headers_ttl=2,
            cache_directory=str(d),
        ),
    ):
        with VSIFile(cog, "rb") as f:
            assert len(f.header) == 32768
        messages = [rec.message for rec in caplog.records]
        assert f"Using {str(d)} Cache directory" in messages
        assert "Adding Header in cache" in messages

        caplog.clear()
        with VSIFile(cog, "rb") as f:
            assert len(f.header) == 32768
        messages = [rec.message for rec in caplog.records]
        assert f"Using {str(d)} Cache directory" in messages
        assert "Found Header in cache" in messages

        caplog.clear()
        # Check that TTL worked (header should not be in cache anymore)
        time.sleep(2)
        with VSIFile(cog, "rb") as f:
            assert len(f.header) == 32768
        messages = [rec.message for rec in caplog.records]
        assert f"Using {str(d)} Cache directory" in messages
        assert "Adding Header in cache" in messages
