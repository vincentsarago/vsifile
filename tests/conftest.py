"""``pytest`` configuration."""

import pytest


@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    """Set Env variables."""
    monkeypatch.delenv("VSIFILE_CACHE_DIRECTORY", raising=False)
    monkeypatch.setenv("VSIFILE_CACHE_HEADERS_TTL", "0")
    monkeypatch.setenv("VSIFILE_CACHE_HEADERS_MAXSIZE", "0")
