from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.audit.capture import build_lifecycle_event
from multi_agent_platform.audit.models import RunStatusAfter, TimelineEventCategory
from multi_agent_platform.db.repositories.audit_debugging import (
    AuditDebuggingRepository,
)


async def test_timeline_completeness_for_core_lifecycle_states(session) -> None:
    repository = AuditDebuggingRepository(session)
    run_id = uuid4()
    for category, status in (
        (TimelineEventCategory.STARTED, RunStatusAfter.RUNNING),
        (TimelineEventCategory.WAITING, RunStatusAfter.WAITING),
        (TimelineEventCategory.RETRIED, RunStatusAfter.RETRYING),
        (TimelineEventCategory.CANCELLED, RunStatusAfter.CANCELLED),
    ):
        await repository.create_timeline_event(
            build_lifecycle_event(
                tenant_id=None,
                workflow_run_id=run_id,
                category=category,
                status_after=status,
                trace_id="trace",
                source_event_id=category.value,
            )
        )
    events = await repository.list_timeline_events(
        tenant_id=None, workflow_run_id=run_id
    )
    assert [event.event_category for event in events] == [
        "started",
        "waiting",
        "retried",
        "cancelled",
    ]
