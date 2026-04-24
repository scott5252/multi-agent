from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.audit.service import AuditService
from multi_agent_platform.db.models.audit import AuditActorType, AuditEvent
from multi_agent_platform.runtime.orchestration.events import (
    RuntimeEventType,
    runtime_audit_action,
)


class FakeAuditRepository:
    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    async def create(self, audit_event: AuditEvent) -> AuditEvent:
        self.events.append(audit_event)
        return audit_event


async def test_record_runtime_event_redacts_payload_and_uses_runtime_actor() -> None:
    repository = FakeAuditRepository()
    service = AuditService(repository)  # type: ignore[arg-type]
    workflow_run_id = uuid4()

    event = await service.record_runtime_event(
        tenant_id=None,
        scope_type="platform",
        action=runtime_audit_action(RuntimeEventType.SIDE_EFFECT),
        workflow_run_id=workflow_run_id,
        trace_id="trace-runtime",
        payload_redacted={"secret_token": "should-not-survive", "status": "applied"},
    )

    assert event in repository.events
    assert event.actor_type is AuditActorType.SYSTEM
    assert event.actor_id == "runtime"
    assert event.entity_type == "workflow_run"
    assert event.entity_id == str(workflow_run_id)
    assert event.payload_redacted["secret_token"] == "***REDACTED***"
    assert event.payload_redacted["status"] == "applied"
