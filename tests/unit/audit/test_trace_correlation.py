from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.audit.capture import build_lifecycle_event, build_trace_record
from multi_agent_platform.audit.models import (
    RunStatusAfter,
    TimelineEventCategory,
    TraceType,
)
from multi_agent_platform.db.repositories.audit_debugging import (
    AuditDebuggingRepository,
)


async def test_trace_correlation_requires_same_tenant_event_and_trace_ids(
    session,
) -> None:
    tenant_id = uuid4()
    run_step_id = uuid4()
    run_id = uuid4()
    repository = AuditDebuggingRepository(session)
    event = await repository.create_timeline_event(
        build_lifecycle_event(
            tenant_id=tenant_id,
            workflow_run_id=run_id,
            category=TimelineEventCategory.TOOL_USAGE,
            status_after=RunStatusAfter.RUNNING,
            trace_id="trace",
            source_event_id="tool",
        )
    )
    trace = await repository.create_trace_record(
        build_trace_record(
            tenant_id=tenant_id,
            workflow_run_id=run_id,
            timeline_event_id=event.timeline_event_id,
            trace_type=TraceType.TOOL_USAGE,
            trace_id="trace",
        ).model_copy(update={"run_step_id": run_step_id, "correlation_id": "corr"})
    )
    assert trace.timeline_event_id == event.timeline_event_id
    assert trace.run_step_id == run_step_id
    assert trace.trace_id == "trace"
    assert trace.correlation_id == "corr"
    with pytest.raises(ValueError):
        await repository.create_trace_record(
            build_trace_record(
                tenant_id=uuid4(),
                workflow_run_id=run_id,
                timeline_event_id=event.timeline_event_id,
                trace_type=TraceType.TOOL_USAGE,
                trace_id="trace",
            )
        )
