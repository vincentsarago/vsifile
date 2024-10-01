"""test vsifile."""

import concurrent.futures
import os
import random
from unittest.mock import patch

from diskcache import Cache

from vsifile import VSIFile

fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")
cog = os.path.join(fixtures_dir, "cog.tif")


def test_vsifile_multithread(tmp_path):
    """Test VSIFile with MultiThreads."""
    d = tmp_path / "cache"
    d.mkdir()

    cache = Cache(directory=str(d), size_limit=5120000000)
    with patch("vsifile.io.base.header_cache", new=cache):

        def _read_range(start, stop):
            with VSIFile(cog, "rb") as f:
                _ = f.get_byte_ranges([start], [stop])
                return f.get_byte_ranges([start], [stop])

        offsets = [random.randint(50000, 50100) for ii in range(200)]
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(_read_range, offset, 100) for offset in offsets}
            for future in concurrent.futures.as_completed(futures):
                try:
                    _ = future.result()
                except Exception as exc:
                    print("%r generated an exception: %s" % exc)
