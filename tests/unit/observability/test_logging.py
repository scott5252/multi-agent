from __future__ import annotations

from multi_agent_platform.observability.logging import (
    REDACTED,
    redact_mapping,
    workflow_log_context,
)


def test_redact_mapping_hides_secret_values() -> None:
    payload = redact_mapping(
        {"api_key": "123", "nested": {"token": "abc"}, "plain": "ok"}
    )
    assert payload["api_key"] == REDACTED
    assert payload["nested"]["token"] == REDACTED
    assert payload["plain"] == "ok"


def test_workflow_log_context_includes_trace_and_ids() -> None:
    payload = workflow_log_context(
        action="workflow_registry.create_draft",
        scope_type="platform",
        trace_id="trace-1",
        workflow_lineage_id="lineage-1",
        workflow_draft_id="draft-1",
        principal_id="platform-admin",
    )
    assert payload["extra"]["trace_id"] == "trace-1"
    assert payload["extra"]["workflow_draft_id"] == "draft-1"
