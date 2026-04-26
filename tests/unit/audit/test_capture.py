from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

import pytest

from multi_agent_platform.audit.capture import (
    AuditCaptureError,
    AuditCaptureService,
    build_lifecycle_event,
    build_trace_record,
)
from multi_agent_platform.audit.models import (
    CaptureCriticality,
    CaptureOutcome,
    RunStatusAfter,
    TimelineEventCategory,
    TraceType,
)
from multi_agent_platform.db.repositories.audit_debugging import (
    AuditDebuggingRepository,
)


class FailingRepository:
    async def create_timeline_event(self, payload):
        raise RuntimeError("db unavailable")

    async def create_capture_gap(self, payload):
        return SimpleNamespace(capture_gap_id=uuid4())


async def test_diagnostic_capture_failure_records_unavailable_marker() -> None:
    service = AuditCaptureService(FailingRepository())
    result = await service.record_event(
        build_lifecycle_event(
            tenant_id=None,
            workflow_run_id=uuid4(),
            category=TimelineEventCategory.STARTED,
            status_after=RunStatusAfter.RUNNING,
            trace_id="trace",
            source_event_id="source",
            criticality=CaptureCriticality.DIAGNOSTIC,
        )
    )
    assert result.capture_outcome is CaptureOutcome.UNAVAILABLE
    assert result.unavailable_marker_id is not None


async def test_security_governance_capture_fails_closed() -> None:
    service = AuditCaptureService(FailingRepository())
    with pytest.raises(AuditCaptureError):
        await service.record_event(
            build_lifecycle_event(
                tenant_id=None,
                workflow_run_id=uuid4(),
                category=TimelineEventCategory.SECRET_ACCESS,
                status_after=RunStatusAfter.RUNNING,
                trace_id="trace",
                source_event_id="source",
                criticality=CaptureCriticality.SECURITY_GOVERNANCE,
            )
        )


async def test_capture_records_trace_with_redaction(session) -> None:
    repository = AuditDebuggingRepository(session)
    service = AuditCaptureService(repository)
    run_id = uuid4()
    event = await repository.create_timeline_event(
        build_lifecycle_event(
            tenant_id=None,
            workflow_run_id=run_id,
            category=TimelineEventCategory.STARTED,
            status_after=RunStatusAfter.RUNNING,
            trace_id="trace",
            source_event_id="source",
        )
    )
    result = await service.record_trace(
        build_trace_record(
            tenant_id=None,
            workflow_run_id=run_id,
            timeline_event_id=event.timeline_event_id,
            trace_type=TraceType.SECRET_ACCESS,
            trace_id="trace",
            safe_input_summary={"api_token": "secret"},
        )
    )
    assert result.trace_record_id is not None
