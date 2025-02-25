"""test rasterio vsiopener."""

import logging
import os

import rasterio

import vsifile
from vsifile.rasterio import opener

fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")
cog = os.path.join(fixtures_dir, "cog.tif")


def test_rasterio_opener(caplog):
    """Test Rasterio Opener with Local File reader."""
    caplog.set_level(logging.DEBUG, logger="vsifile")

    with rasterio.open(cog, opener=opener) as src:
        profile = src.profile
        assert profile["driver"] == "GTiff"
        assert profile["count"] == 1
        arr = src.read()
        assert arr.shape == (1, 2667, 2658)
    assert [
        rec.message
        for rec in caplog.records
        if "VSIFILE: Using MultiRange Reads" in rec.message
    ]


def test_rasterio_without_multi_range(caplog):
    """Test VSIFile Local File reader."""
    caplog.set_level(logging.DEBUG, logger="vsifile")

    # This won't use the read-multi-range optimization
    # because `vsi` is not a `MultiByteRangeResourceContainer`
    vsi = vsifile.filesystem("file")
    with rasterio.open(cog, opener=vsi) as src:
        profile = src.profile
        assert profile["driver"] == "GTiff"
        assert profile["count"] == 1
        arr = src.read()
        assert arr.shape == (1, 2667, 2658)
    assert not [
        rec.message
        for rec in caplog.records
        if "VSIFILE: Using MultiRange Reads" in rec.message
    ]
