from __future__ import annotations

import pytest

from multi_agent_platform.channels.callbacks import (
    sign_callback_payload,
    validate_callback_url,
)
from multi_agent_platform.channels.errors import ChannelError


def test_callback_url_validation_allows_https_and_local_dev_http() -> None:
    validate_callback_url("https://example.test/callback", allow_local_http=False)
    validate_callback_url("http://127.0.0.1:9000/callback", allow_local_http=True)

    with pytest.raises(ChannelError):
        validate_callback_url("http://example.test/callback", allow_local_http=False)


def test_callback_signatures_are_stable_for_sorted_payloads() -> None:
    first = sign_callback_payload({"b": 2, "a": 1}, "secret")
    second = sign_callback_payload({"a": 1, "b": 2}, "secret")

    assert first == second
    assert len(first) == 64
