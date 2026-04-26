from __future__ import annotations

from multi_agent_platform.observability.logging import audit_log_context
from multi_agent_platform.observability.tracing import audit_trace_attributes


def test_audit_observability_helpers_include_safe_correlation_fields() -> None:
    context = audit_log_context(
        action="record_event",
        tenant_id="tenant",
        workflow_run_id="run",
        trace_id="trace",
        timeline_event_id="event",
    )
    assert context["extra"]["trace_id"] == "trace"
    attrs = audit_trace_attributes(
        action="lookup",
        workflow_run_id="run",
        tenant_id="tenant",
        trace_id="trace",
        correlation_id="corr",
    )
    assert attrs["correlation_id"] == "corr"
