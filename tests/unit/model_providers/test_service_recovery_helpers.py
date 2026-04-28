from __future__ import annotations

from multi_agent_platform.model_providers.service import _safe_int


def test_safe_int_normalizes_catalog_recovery_counts() -> None:
    assert _safe_int(3) == 3
    assert _safe_int("4") == 4
    assert _safe_int("not-a-count") == 0
    assert _safe_int(None) == 0
