from __future__ import annotations

from typing import Type, Optional

from requests import HTTPError

from slurmpy.v0041 import ClientV0041
from slurmpy.v0042 import ClientV0042
from slurmpy.base_api import BaseClient
from slurmpy.logger import slurmpy_logger

SLURM_IMPLEMENTATIONS: list[Type[BaseClient]] = list(sorted([ClientV0042, ClientV0041], key=lambda x: x.version_str, reverse=True))

def _get_implementations_before(version):
    return [implementation for implementation in SLURM_IMPLEMENTATIONS if implementation.version_str <= version]


class SlurmClient(BaseClient):
    client: BaseClient
    def __init__(self, url: str, user: str, token: str, version: Optional[str] = None):
        if version is None:
            for implementation in SLURM_IMPLEMENTATIONS:
                try:
                    client = implementation(url, user, token)
                    client.diag()
                    self.max_version = client.version_str
                    self.client = client
                    self.client_impl = implementation
                    break
                except HTTPError as e:
                    slurmpy_logger.info(f'Attempted version {implementation.version_str}, but diag returned {e}')
        else:
            implementation = next(filter(lambda x: x.version_str == version, SLURM_IMPLEMENTATIONS))
            self.client = implementation(url, user, token)

        if self.client is None:
            raise HTTPError('None of the supported Slurm versions could connect to the server.')

    def __getattribute__(self, name):
        # Always allow access to core/internal attributes first
        if name in {
            "client",
            "client_impl",
            "max_version",
            "__class__",
            "__dict__",
            "__getattribute__",
            "__getattr__",
        }:
            return object.__getattribute__(self, name)

        # Delegate to selected client BEFORE falling back to SlurmClient's own attrs.
        # This ensures version_str resolve from the active client.
        client = object.__getattribute__(self, "client")
        client_impl = object.__getattribute__(self, "client_impl")
        if client is not None and name in client_impl.__dict__:
            slurmpy_logger.debug(f"Dispatching request to preset client: {name}")
            return getattr(client, name)

        # Last resort: try older implementations by version
        max_version = object.__getattribute__(self, "max_version")
        implementations = _get_implementations_before(max_version)

        for implementation in implementations:
            if name in implementation.__dict__:
                fallback_client = implementation(client.url, client.user, client.token)
                slurmpy_logger.debug(f"Dispatching request via fallback for: {name}")
                return getattr(fallback_client, name)

        raise AttributeError(f"`{name}` is not implemented for slurm versions <= {max_version}")