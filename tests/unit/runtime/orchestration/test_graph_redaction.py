from __future__ import annotations

import json

from multi_agent_platform.runtime.orchestration.graph_redaction import (
    contains_sensitive_key,
    redact_graph_value,
    safe_graph_ref,
)


def test_graph_redaction_replaces_sensitive_values() -> None:
    value = {
        "safe": "visible",
        "secret_token": "super-secret-value",
        "nested": {"raw_payload": {"message": "private"}},
    }

    redacted = redact_graph_value(value)
    encoded = json.dumps(redacted)

    assert "visible" in encoded
    assert "super-secret-value" not in encoded
    assert "private" not in encoded
    assert "payload_digest" in encoded
    assert contains_sensitive_key(value)


def test_safe_graph_ref_includes_digest_and_safe_summary() -> None:
    ref = safe_graph_ref(
        source="node-a",
        payload={"result": "ok", "credential": "abc"},
        safe_summary="Node A completed.",
    )

    assert ref["source"] == "node-a"
    assert ref["safe_summary"] == "Node A completed."
    assert "payload_digest" in ref
    assert "abc" not in json.dumps(ref)
