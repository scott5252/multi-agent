from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from multi_agent_platform.audit.models import AuditEventCreate
from multi_agent_platform.db.models.audit import AuditActorType, AuditEvent
from multi_agent_platform.db.repositories.audit import AuditRepository
from multi_agent_platform.observability.logging import redact_mapping

if TYPE_CHECKING:
    from multi_agent_platform.auth.principal import PrincipalContext


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

    async def record_workflow_event(
        self,
        *,
        principal: PrincipalContext,
        scope_type: str,
        tenant_id: UUID | None,
        action: str,
        entity_type: str,
        entity_id: str,
        trace_id: str,
        request_id: str | None,
        payload_redacted: dict[str, str],
    ) -> AuditEvent:
        return await self.record(
            AuditEventCreate(
                tenant_id=tenant_id,
                scope_type=scope_type,
                actor_type=AuditActorType.USER,
                actor_id=principal.principal_id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                trace_id=trace_id,
                request_id=request_id,
                payload_redacted=payload_redacted,
            )
        )
