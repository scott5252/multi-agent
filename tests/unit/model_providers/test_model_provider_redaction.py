from __future__ import annotations

from multi_agent_platform.model_providers.redaction import (
    redact_text,
    safe_mapping_summary,
    safe_url,
)


def test_safe_url_removes_userinfo_and_redacts_secret_query() -> None:
    assert (
        safe_url("http://user:pass@localhost:11434/v1?token=abc&mode=test")
        == "http://localhost:11434/v1?token=%5Bredacted%5D&mode=test"
    )


def test_safe_mapping_summary_redacts_sensitive_keys() -> None:
    summary = safe_mapping_summary({"Authorization": "Bearer abc", "status": "ok"})

    assert summary["Authorization"] == "[redacted]"
    assert summary["status"] == "ok"


def test_redaction_helpers_fallback_for_empty_and_sensitive_text() -> None:
    assert safe_url(None) is None
    assert redact_text("", fallback="empty") == "empty"
    assert redact_text("Bearer abc.def") == "Protected detail"
    assert redact_text("sk-abcdefghijklmnopqrstuvwxyz") == "[redacted]"


def test_safe_mapping_summary_handles_scalar_and_complex_values() -> None:
    summary = safe_mapping_summary(
        {
            "count": 3,
            "enabled": True,
            "metadata": {"request_id": "req-safe"},
            "nullable": None,
        }
    )

    assert summary["count"] == 3
    assert summary["enabled"] is True
    assert summary["metadata"] == "{'request_id': 'req-safe'}"
    assert summary["nullable"] is None
