# vsifile

---

**Documentation**: <a href="https://vincentsarago.github.io/vsifile/" target="_blank">https://vincentsarago.github.io/vsifile/</a>

**Source Code**: <a href="https://github.com/vincentsarago/vsifile" target="_blank">https://github.com/vincentsarago/vsifile</a>

---

## Description

Experiment using Rasterio/GDAL **Python file opener VSI plugin** https://github.com/rasterio/rasterio/pull/2898/files

Future version of rasterio will accept an custom dataset `opener`:

```
opener : callable, optional
        A custom dataset opener which can serve GDAL's virtual
        filesystem machinery via Python file-like objects. The
        underlying file-like object is obtained by calling *opener* with
        (*fp*, *mode*) or (*fp*, *mode* + "b") depending on the format
        driver's native mode. *opener* must return a Python file-like
        object that provides read, seek, tell, and close methods.
```
ref: https://github.com/rasterio/rasterio/blob/d966440c06f3324aca1fa761d490cc780a9f619c/rasterio/__init__.py#L185-L191


## Install

You can install `vsifile` using pip

```bash
python -m pip install -U pip
python -m pip install -U vsifile
```

or install from source:

```bash
git clone https://github.com/vincentsarago/vsifile.git
cd vsifile
python -m pip install -U pip
python -m pip install -e .
```

## Usage

```python
from vsifile import VSIFile, FileReader

src_path = "tests/fixture.cog.tif"

with VSIFile(src_path, "rb") as f:
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

    b = f.get_byte_ranges([100, 200], [10, 20])
    assert len(b) == 2
    assert len(b[0]) == 10
    assert len(b[1]) == 20
    assert f.tell() == 220
```

#### With Rasterio

```python
import rasterio
from vsifile.rasterio import opener

with rasterio.open("tests/fixtures/cog.tif",  opener=opener) as src:
    ...
```

### Cache Configuration

*vsifile* uses [DiskCache](https://grantjenks.com/docs/diskcache/) to create a **persistent** File Header cache.
By default the cache will be cleaned up when closing the file handle, you can change this behaviour by setting `VSIFILE_CACHE_DIRECTORY="{your temp directory}"` environment variable.


## Contribution & Development

See [CONTRIBUTING.md](https://github.com/vincentsarago/vsifile/blob/main/CONTRIBUTING.md)

## Changes

See [CHANGES.md](https://github.com/vincentsarago/vsifile/blob/main/CHANGES.md).

## License

See [LICENSE](https://github.com/vincentsarago/vsifile/blob/main/LICENSE)
