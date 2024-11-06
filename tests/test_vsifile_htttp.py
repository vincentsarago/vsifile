"""test vsifile.HttpReader."""

import datetime
import functools
import os
import threading
from http.server import HTTPServer

import pytest
from RangeHTTPServer import RangeRequestHandler

from vsifile import VSIFile
from vsifile.io import HttpReader

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


def test_vsifile_http(http_server):
    """Test VSIFile Local File reader."""

    url = f"{http_server}/cog.tif"
    with pytest.raises(ValueError):
        with VSIFile(url, "r") as f:
            pass

    with pytest.raises(ValueError):
        with VSIFile(url, "w") as f:
            pass

    with VSIFile(url, "rb") as f:
        assert isinstance(f, HttpReader)
        assert hash(f)
        assert "HttpReader" in str(f)

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
