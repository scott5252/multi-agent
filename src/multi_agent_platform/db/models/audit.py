from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from multi_agent_platform.db.base import Base


class AuditActorType(StrEnum):
    SYSTEM = "system"
    SERVICE = "service"
    USER = "user"


class AuditEvent(Base):
    __tablename__ = "audit_events"

    audit_event_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    scope_type: Mapped[str] = mapped_column(String(32))
    actor_type: Mapped[AuditActorType] = mapped_column(
        Enum(AuditActorType, native_enum=False),
        default=AuditActorType.SYSTEM,
    )
    actor_id: Mapped[str] = mapped_column(String(128))
    action: Mapped[str] = mapped_column(String(128))
    entity_type: Mapped[str] = mapped_column(String(128))
    entity_id: Mapped[str] = mapped_column(String(128))
    trace_id: Mapped[str] = mapped_column(String(64))
    request_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    payload_redacted: Mapped[dict[str, str]] = mapped_column(JSON, default=dict)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
