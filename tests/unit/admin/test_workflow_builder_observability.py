from __future__ import annotations

from multi_agent_platform.admin.workflow_registry.observability import (
    builder_log_context,
    safe_observability_payload,
)


def test_builder_log_context_keeps_safe_optional_identifiers() -> None:
    context = builder_log_context(
        action="publish_gate",
        scope_type="tenant",
        trace_id="trace-1",
        request_id="request-1",
        workflow_draft_id="draft-1",
        outcome="blocked",
    )

    assert context == {
        "builder_action": "publish_gate",
        "scope_type": "tenant",
        "trace_id": "trace-1",
        "request_id": "request-1",
        "workflow_draft_id": "draft-1",
        "outcome": "blocked",
    }


def test_safe_observability_payload_redacts_secret_material() -> None:
    payload = safe_observability_payload(
        {
            "workflow_draft_id": "draft-1",
            "secret_reference_id": "secret-1",
            "apiToken": "token-1",
            "credential_status": "ready",
            "none_value": None,
            "count": 2,
        }
    )

    assert payload == {
        "workflow_draft_id": "draft-1",
        "count": "2",
    }
