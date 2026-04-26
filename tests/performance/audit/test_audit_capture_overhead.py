from __future__ import annotations

from time import perf_counter
from uuid import uuid4

from multi_agent_platform.audit.capture import build_lifecycle_event
from multi_agent_platform.audit.models import RunStatusAfter, TimelineEventCategory


def test_audit_capture_builder_overhead_under_10ms_p95() -> None:
    durations = []
    for index in range(50):
        started = perf_counter()
        build_lifecycle_event(
            tenant_id=None,
            workflow_run_id=uuid4(),
            category=TimelineEventCategory.STARTED,
            status_after=RunStatusAfter.RUNNING,
            trace_id="trace",
            source_event_id=f"event-{index}",
            details={"safe_reason": "started"},
        )
        durations.append((perf_counter() - started) * 1000)
    p95 = sorted(durations)[int(len(durations) * 0.95) - 1]
    assert p95 <= 10
