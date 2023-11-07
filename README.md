# vsifile

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


---

**Source Code**: https://github.com/vincentsarago/vsifile

---


## Description

### Usage

```python
import rasterio
from vsifile import VSIFile

with rasterio.open("tests/fixtures/cog.tif",  opener=VSIFile) as src:
    ...
```

### Cache Configuration

*vsifile* uses [DiskCache](https://grantjenks.com/docs/diskcache/) to create a **persistent** File Header cache.
By default the cache will be cleaned up when closing the file handle, you can change this behaviour by setting `VSIFILE_CACHE_DIRECTORY="{your temp directory}"` environment variable.


## Contribution & Development

See [CONTRIBUTING.md](https://github.com/vincentsarago/vsifile/blob/main/CONTRIBUTING.md)

## Authors

See [AUTHORS.txt](https://github.com/vincentsarago/vsifile/blob/main/AUTHORS.txt) for a listing of individual contributors.

## Changes

See [CHANGES.md](https://github.com/vincentsarago/vsifile/blob/main/CHANGES.md).

## License

See [LICENSE](https://github.com/vincentsarago/vsifile/blob/main/LICENSE)
