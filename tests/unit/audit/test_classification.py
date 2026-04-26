from __future__ import annotations

import pytest

from multi_agent_platform.audit.classification import (
    assert_no_raw_sensitive_values,
    build_safe_summary,
    classify_field,
    decision_for_field,
    redact_payload,
    summarize_value,
)
from multi_agent_platform.audit.models import SensitivityLabel
from multi_agent_platform.observability.logging import REDACTED


def test_redacts_raw_secrets_prompts_memory_and_unknown_dynamic_fields() -> None:
    payload = {
        "trace_id": "trace",
        "api_token": "secret",
        "prompt_body": "do private work",
        "memory_content": "private memory",
        "unexpected_payload": {"raw": "value"},
    }
    redacted = redact_payload(payload)
    assert redacted["trace_id"] == "trace"
    assert redacted["api_token"] == REDACTED
    assert redacted["prompt_body"] == REDACTED
    assert redacted["memory_content"] == REDACTED
    assert redacted["unexpected_payload"] == REDACTED
    assert classify_field("secret_reference") is SensitivityLabel.SECRET


def test_safe_summary_bounds_large_payloads() -> None:
    summary = build_safe_summary({f"field_{i}": i for i in range(20)}, max_items=3)
    assert summary["truncated_field_count"] == 17


def test_classification_rejects_nested_raw_sensitive_values() -> None:
    with pytest.raises(ValueError):
        assert_no_raw_sensitive_values({"safe": {"password": "secret"}})
    assert summarize_value(["a", "b"]) == {"redacted": True, "item_count": 2}
    assert decision_for_field("safe_reason").redaction_action.value == "allow"
