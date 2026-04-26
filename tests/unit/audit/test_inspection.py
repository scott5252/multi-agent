from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.audit.capture import build_lifecycle_event
from multi_agent_platform.audit.inspection import (
    assemble_replay_events,
    assemble_timeline,
)
from multi_agent_platform.audit.models import RunStatusAfter, TimelineEventCategory
from multi_agent_platform.db.repositories.audit_debugging import (
    AuditDebuggingRepository,
)


async def test_timeline_assembly_orders_events_and_replay_checkpoints(session) -> None:
    tenant_id = uuid4()
    run_id = uuid4()
    repository = AuditDebuggingRepository(session)
    completed = await repository.create_timeline_event(
        build_lifecycle_event(
            tenant_id=tenant_id,
            workflow_run_id=run_id,
            category=TimelineEventCategory.COMPLETED,
            status_after=RunStatusAfter.COMPLETED,
            trace_id="trace",
            source_event_id="completed",
        )
    )
    started = await repository.create_timeline_event(
        build_lifecycle_event(
            tenant_id=tenant_id,
            workflow_run_id=run_id,
            category=TimelineEventCategory.STARTED,
            status_after=RunStatusAfter.RUNNING,
            trace_id="trace",
            source_event_id="started",
        )
    )
    view = assemble_timeline(
        workflow_run_id=run_id,
        tenant_id=tenant_id,
        events=[completed, started],
        traces_by_event={},
    )
    assert [event["sequence"] for event in view.events] == [1, 2]
    replay = assemble_replay_events(view.events)
    assert replay[0]["checkpoint"] is True
