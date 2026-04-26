from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.audit.capture import build_lifecycle_event
from multi_agent_platform.audit.models import (
    RunStatusAfter,
    TimelineEventCategory,
    TraceType,
)
from multi_agent_platform.db.repositories.audit_debugging import (
    AuditDebuggingRepository,
)


async def test_repository_idempotent_timeline_and_same_tenant_trace(session) -> None:
    tenant_id = uuid4()
    run_id = uuid4()
    repository = AuditDebuggingRepository(session)
    event = build_lifecycle_event(
        tenant_id=tenant_id,
        workflow_run_id=run_id,
        category=TimelineEventCategory.STARTED,
        status_after=RunStatusAfter.RUNNING,
        trace_id="trace",
        source_event_id="source",
    )
    first = await repository.create_timeline_event(event)
    second = await repository.create_timeline_event(event)
    assert first.timeline_event_id == second.timeline_event_id
    assert first.sequence == 1

    from multi_agent_platform.audit.capture import build_trace_record

    trace = await repository.create_trace_record(
        build_trace_record(
            tenant_id=tenant_id,
            workflow_run_id=run_id,
            timeline_event_id=first.timeline_event_id,
            trace_type=TraceType.TOOL_USAGE,
            trace_id="trace",
        )
    )
    assert trace.timeline_event_id == first.timeline_event_id

    with pytest.raises(ValueError):
        await repository.create_trace_record(
            build_trace_record(
                tenant_id=uuid4(),
                workflow_run_id=run_id,
                timeline_event_id=first.timeline_event_id,
                trace_type=TraceType.TOOL_USAGE,
                trace_id="trace",
            )
        )
