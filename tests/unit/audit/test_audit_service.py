from __future__ import annotations

from multi_agent_platform.audit.models import AuditEventCreate
from multi_agent_platform.audit.service import AuditService
from multi_agent_platform.db.models.audit import AuditActorType
from multi_agent_platform.db.repositories.audit import AuditRepository


async def test_audit_service_records_redacted_event(session) -> None:
    repository = AuditRepository(session)
    service = AuditService(repository)
    event = AuditEventCreate(
        scope_type="platform",
        actor_type=AuditActorType.SERVICE,
        actor_id="api",
        action="created",
        entity_type="job",
        entity_id="job-1",
        trace_id="trace-1",
        payload_redacted={"api_key": "secret", "plain": "ok"},
    )
    recorded = await service.record(event)
    events = await repository.list_by_trace("trace-1")
    assert recorded.payload_redacted["api_key"] == "***REDACTED***"
    assert events[0].actor_type == AuditActorType.SERVICE
