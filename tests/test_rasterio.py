"""test rasterio vsiopener."""

import os

import rasterio

import vsifile
from vsifile.rasterio import VSIOpener, opener

fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")
cog = os.path.join(fixtures_dir, "cog.tif")


def test_rasterio_opener():
    """Test VSIFile Local File reader."""
    with rasterio.open(cog, opener=VSIOpener) as src:
        profile = src.profile
        assert profile["driver"] == "GTiff"
        assert profile["count"] == 1
        arr = src.read()
        assert arr.shape == (1, 2667, 2658)

    with rasterio.open(cog, opener=opener) as src:
        profile = src.profile
        assert profile["driver"] == "GTiff"
        assert profile["count"] == 1
        arr = src.read()
        assert arr.shape == (1, 2667, 2658)

    vsi = vsifile.filesystem("file")
    with rasterio.open(cog, opener=vsi) as src:
        profile = src.profile
        assert profile["driver"] == "GTiff"
        assert profile["count"] == 1
        arr = src.read()
        assert arr.shape == (1, 2667, 2658)
