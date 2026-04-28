from __future__ import annotations

import pytest

from multi_agent_platform.model_providers.allowlist import (
    AllowlistError,
    LocalEndpointAllowlist,
    validate_local_endpoint,
)


def test_validate_local_endpoint_accepts_allowlisted_loopback() -> None:
    allowlist = LocalEndpointAllowlist(
        schemes=("http",),
        hosts=("localhost",),
        ports=(11434,),
        cidrs=("127.0.0.0/8",),
    )

    assert (
        validate_local_endpoint("http://127.0.0.1:11434", allowlist)
        == "http://127.0.0.1:11434"
    )


def test_validate_local_endpoint_rejects_secret_query_params() -> None:
    allowlist = LocalEndpointAllowlist(
        schemes=("http",),
        hosts=("localhost",),
        ports=(11434,),
    )

    with pytest.raises(AllowlistError):
        validate_local_endpoint("http://localhost:11434?api_key=value", allowlist)


@pytest.mark.parametrize(
    "url",
    [
        "https://localhost:11434",
        "http://user:pass@localhost:11434",
        "http:///v1",
        "http://localhost:9999",
        "http://modelbox:11434",
    ],
)
def test_validate_local_endpoint_rejects_non_allowlisted_urls(url: str) -> None:
    allowlist = LocalEndpointAllowlist(
        schemes=("http",),
        hosts=("localhost",),
        ports=(11434,),
    )

    with pytest.raises(AllowlistError):
        validate_local_endpoint(url, allowlist)
