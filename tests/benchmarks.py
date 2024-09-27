"""Benchmark."""

import functools
import os
import threading
from http.server import HTTPServer

import pytest
import rasterio
from RangeHTTPServer import RangeRequestHandler

from vsifile.rasterio import opener

fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")


@pytest.fixture(scope="session")
def http_server():
    """Serves files from the test data directory."""

    Handler = functools.partial(RangeRequestHandler, directory=fixtures_dir)
    httpd = HTTPServer(("", 8081), Handler)
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.start()
    print("Server started at http://localhost:8081")
    yield "http://localhost:8081"
    httpd.shutdown()
    server_thread.join()


@pytest.mark.parametrize("op", [None, opener])
def test_preview(op, http_server, benchmark):
    """Test file read"""

    # benchmark.name = f"With VSIFILE Opener: {op is not None}"
    benchmark.group = f"With VSIFILE Opener: {op is not None}"

    def read():
        with rasterio.Env(
            GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
            GDAL_INGESTED_BYTES_AT_OPEN="32768",
            GDAL_HTTP_MERGE_CONSECUTIVE_RANGES="TRUE",
        ):
            with rasterio.open(
                f"{http_server}/cog.tif",
                opener=op,
            ) as src:
                return src.read(indexes=1, out_shape=(1, src.height // 2, src.width // 2))

    _ = benchmark.pedantic(read, iterations=1, rounds=50)
