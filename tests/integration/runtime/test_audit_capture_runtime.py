from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.audit.capture import AuditCaptureService
from multi_agent_platform.db.repositories.audit_debugging import (
    AuditDebuggingRepository,
)
from multi_agent_platform.runtime.orchestration.service import (
    RuntimeOrchestrationService,
)


async def test_runtime_start_emits_audit_capture_when_service_is_supplied(
    session,
) -> None:
    repository = AuditDebuggingRepository(session)
    runtime = RuntimeOrchestrationService()
    run = await runtime.start_run(
        tenant_id=None,
        scope_type="platform",
        principal_id="system",
        published_workflow_version_id=uuid4(),
        input_payload={"safe": True},
        idempotency_key=None,
        trace_id="trace",
        audit_capture_service=AuditCaptureService(repository),
    )
    events = await repository.list_timeline_events(
        tenant_id=None, workflow_run_id=run.workflow_run_id
    )
    assert events[0].event_category == "accepted"
