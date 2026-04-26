from __future__ import annotations

from time import perf_counter
from uuid import uuid4

from multi_agent_platform.audit.capture import build_lifecycle_event
from multi_agent_platform.audit.models import RunStatusAfter, TimelineEventCategory
from multi_agent_platform.db.repositories.audit_debugging import (
    AuditDebuggingRepository,
)


async def test_run_lookup_and_search_latency_under_local_budget(session) -> None:
    repository = AuditDebuggingRepository(session)
    tenant_id = uuid4()
    run_id = uuid4()
    await repository.create_timeline_event(
        build_lifecycle_event(
            tenant_id=tenant_id,
            workflow_run_id=run_id,
            category=TimelineEventCategory.FAILED,
            status_after=RunStatusAfter.FAILED,
            trace_id="trace",
            source_event_id="failed",
            details={"category": "tool_policy"},
        )
    )
    started = perf_counter()
    await repository.list_timeline_events(tenant_id=tenant_id, workflow_run_id=run_id)
    direct_lookup_seconds = perf_counter() - started
    started = perf_counter()
    await repository.search_runs(
        tenant_id=tenant_id, status="failed", failure_category="tool_policy"
    )
    search_seconds = perf_counter() - started
    assert direct_lookup_seconds < 2
    assert search_seconds < 5
