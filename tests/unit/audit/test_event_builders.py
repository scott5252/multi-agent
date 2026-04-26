from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.audit.capture import (
    build_failed_stage_event,
    build_tool_usage_trace,
)
from multi_agent_platform.audit.models import TraceType


def test_failed_stage_event_and_tool_trace_build_safe_metadata() -> None:
    event = build_failed_stage_event(
        tenant_id=None,
        workflow_run_id=uuid4(),
        trace_id="trace",
        source_event_id="failed",
        failed_stage="tool",
        safe_failure_reason="policy denied",
        investigation_category="tool_policy",
    )
    assert event.safe_details["failed_stage"] == "tool"
    trace = build_tool_usage_trace(
        tenant_id=None,
        workflow_run_id=event.workflow_run_id,
        timeline_event_id=uuid4(),
        trace_id="trace",
        safe_input_summary={"api_token": "secret"},
    )
    assert trace.trace_type is TraceType.TOOL_USAGE
    assert trace.safe_input_summary["api_token"]["redacted"] is True
