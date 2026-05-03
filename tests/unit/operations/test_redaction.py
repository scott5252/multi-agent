from __future__ import annotations

from multi_agent_platform.operations.redaction import (
    redaction_notice,
    sanitize_operations_metadata,
    sanitize_operations_text,
)


def test_operations_redaction_masks_sensitive_keys_and_values() -> None:
    metadata = sanitize_operations_metadata(
        {
            "trace_id": "trace-1",
            "prompt": "write the secret",
            "safe": "dependency ready",
            "authorization": "Bearer abc",
        }
    )

    assert metadata["trace_id"] == "trace-1"
    assert metadata["prompt"] == "[redacted]"
    assert metadata["authorization"] == "[redacted]"
    assert "secret" not in metadata["safe"].lower()
    assert sanitize_operations_text("raw payload traceback") == "Protected detail"
    assert "Raw prompts" in redaction_notice()


def test_operations_redaction_handles_nested_lists_empty_keys_and_limits() -> None:
    metadata = sanitize_operations_metadata(
        {
            "": "empty-key",
            "tags": ["alpha", "beta", "gamma", "delta", "epsilon", "zeta"],
            "nested": {"safe": "ok", "token": "hidden"},
            "very_long_key_" + ("x" * 120): "safe",
        },
        max_items=10,
    )

    assert metadata["field"] == "empty-key"
    assert metadata["tags"] == "alpha, beta, gamma, delta, epsilon"
    assert "hidden" not in metadata["nested"]
    assert any(key.endswith("...") for key in metadata)
    assert sanitize_operations_metadata(None) == {}
    assert sanitize_operations_text("", fallback="empty") == "empty"
    assert sanitize_operations_text("x" * 300).endswith("...")
    assert sanitize_operations_metadata({"one": 1, "two": 2}, max_items=1) == {
        "one": "1"
    }
