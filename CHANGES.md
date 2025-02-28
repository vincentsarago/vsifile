
# 0.3.0 (2025-02-28)

* replace `HEAD` with `GET` request on file opening

* cache `header` and file `metadata` to the *Header Cache*

* add `kwargs` to `vsifile.rasterio.VSIOpener` class to forward configurations (config, client_config, retry_config) to the `obstore.Store`

    ```python
    import rasterio
    from vsifile.rasterio import VSIOpener

    # This would fail if no AWS credentials are found
    with rasterio.open(
        "s3://sentinel-cogs/sentinel-s2-l2a-cogs/15/T/VK/2023/10/S2B_15TVK_20231008_0_L2A/TCI.tif",
        opener=VSIOpener()
    ):
        pass

    # We forward `skip_signature` to Obstore.store.S3Store creation
    with rasterio.open(
        "s3://sentinel-cogs/sentinel-s2-l2a-cogs/15/T/VK/2023/10/S2B_15TVK_20231008_0_L2A/TCI.tif",
        opener=VSIOpener(
            config={"skip_signature": True, "aws_region": "us-west-2"}
        ),
    ):
        ...
    ```

# 0.2.0 (2025-02-26)

* switch to `Obstore` for I/O (https://github.com/vincentsarago/vsifile/pull/15)
* refactor logging messages
* `rasterio.VSIOpener.mtime` and `rasterio.VSIOpener.size` now return fake values (`0` and `1`) (https://github.com/vincentsarago/vsifile/pull/16)

# 0.1.0 (2024-10-11)

* first initial release
