from __future__ import annotations

from multi_agent_platform.observability.logging import REDACTED, redact_mapping


def test_redact_mapping_hides_secret_values() -> None:
    payload = redact_mapping(
        {"api_key": "123", "nested": {"token": "abc"}, "plain": "ok"}
    )
    assert payload["api_key"] == REDACTED
    assert payload["nested"]["token"] == REDACTED
    assert payload["plain"] == "ok"
