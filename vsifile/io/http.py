"""HTTP VSIFile reader"""

from attrs import define
from obstore.store import HTTPStore

from vsifile.io.base import BaseReader


@define
class HttpReader(BaseReader):
    """HTTP VSIFILE Reader."""

    def __repr__(self) -> str:
        """Reader repr."""
        return f"{self.__class__.__name__}({self.name})"

    def __hash__(self):
        """Object hash."""
        return hash((self.name, self.mode))

    def __attrs_post_init__(self):
        """Create Store and parse name."""
        options = {}
        client_options = self.client_options or {}
        keys = [k.upper() for k in list(client_options)]
        if "ALLOW_HTTP" not in keys and self.name.startswith("http://"):
            options["ALLOW_HTTP"] = "TRUE"

        self._store = HTTPStore.from_url(
            self.name,
            client_options={**client_options, **options},
            retry_config=self.retry_config,
        )
        self._key = ""
