from __future__ import annotations

import pytest

from multi_agent_platform.prompts.fixture_safety import (
    UnsafeFixtureValueError,
    sanitize_fixture_values,
)


def test_sanitize_fixture_values_preserves_safe_synthetic_values() -> None:
    result = sanitize_fixture_values({"name": "Ada Lovelace"})

    assert result.values_by_variable == {"name": "Ada Lovelace"}
    assert result.redaction_categories == ()


@pytest.mark.parametrize(
    "value",
    [
        "sk-live-123456789012",
        "password=super-secret",
        "Authorization: Bearer token",
    ],
)
def test_sanitize_fixture_values_rejects_secret_like_content(value: str) -> None:
    with pytest.raises(UnsafeFixtureValueError):
        sanitize_fixture_values({"name": value})
