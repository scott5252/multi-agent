from __future__ import annotations

from multi_agent_platform.audit.models import AuditEventCreate
from multi_agent_platform.db.models.audit import AuditEvent
from multi_agent_platform.db.repositories.audit import AuditRepository
from multi_agent_platform.observability.logging import redact_mapping


class AuditService:
    def __init__(self, repository: AuditRepository) -> None:
        self.repository = repository

    async def record(self, event: AuditEventCreate) -> AuditEvent:
        audit_event = AuditEvent(
            tenant_id=event.tenant_id,
            scope_type=event.scope_type,
            actor_type=event.actor_type,
            actor_id=event.actor_id,
            action=event.action,
            entity_type=event.entity_type,
            entity_id=event.entity_id,
            trace_id=event.trace_id,
            request_id=event.request_id,
            payload_redacted=redact_mapping(event.payload_redacted),
            occurred_at=event.occurred_at,
        )
        return await self.repository.create(audit_event)
