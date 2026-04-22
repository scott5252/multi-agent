from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from multi_agent_platform.db.models.audit import AuditActorType


class AuditEventCreate(BaseModel):
    tenant_id: UUID | None = None
    scope_type: str
    actor_type: AuditActorType = AuditActorType.SYSTEM
    actor_id: str = "system"
    action: str
    entity_type: str
    entity_id: str
    trace_id: str
    request_id: str | None = None
    payload_redacted: dict[str, str] = Field(default_factory=dict)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
