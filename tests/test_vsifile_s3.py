"""test vsifile.AWSS3Reader."""

import datetime
from unittest.mock import patch

import pytest
import rasterio
from diskcache import Cache

from vsifile import VSIFile
from vsifile.io import AWSS3Reader
from vsifile.rasterio import VSIOpener

s3_url = "s3://sentinel-cogs/sentinel-s2-l2a-cogs/15/T/VK/2023/10/S2B_15TVK_20231008_0_L2A/TCI.tif"


def test_vsifile_s3():
    """Test VSIFile S3 store."""
    config = {"skip_signature": True, "aws_region": "us-west-2"}
    with pytest.raises(ValueError):
        with VSIFile(s3_url, "r", config=config) as f:
            pass

    with pytest.raises(ValueError):
        with VSIFile(s3_url, "w", config=config) as f:
            pass

    with VSIFile(s3_url, "rb", config=config) as f:
        assert isinstance(f, AWSS3Reader)
        assert hash(f)
        assert "AWSS3Reader" in str(f)

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

        assert f.size
        assert isinstance(f.mtime, datetime.datetime)

    assert f.closed


def test_vsifile_s3_rasterio():
    """Test Rasterio with VSIOpener options."""
    cache = Cache(directory=None, size_limit=0)
    with patch("vsifile.io.base.header_cache", new=cache):
        with pytest.raises((rasterio.errors.RasterioIOError, Exception)):
            with rasterio.open(s3_url, opener=VSIOpener()) as src:
                assert src.meta

        with rasterio.open(
            s3_url,
            opener=VSIOpener(config={"skip_signature": True, "aws_region": "us-west-2"}),
        ) as src:
            assert src.meta
