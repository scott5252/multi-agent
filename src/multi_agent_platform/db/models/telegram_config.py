from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from multi_agent_platform.db.base import Base, TimestampMixin, utcnow


def _revision_token() -> str:
    return uuid4().hex


class TelegramTenantConfiguration(Base, TimestampMixin):
    __tablename__ = "telegram_tenant_configs"
    __table_args__ = (
        Index("ix_telegram_tenant_configs_tenant", "tenant_id", unique=True),
        Index("ix_telegram_tenant_configs_revision", "tenant_id", "revision_token"),
    )

    telegram_tenant_config_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=False
    )
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    protected_commands: Mapped[list[str]] = mapped_column(JSON, default=list)
    status_note: Mapped[str | None] = mapped_column(String(500))
    revision_token: Mapped[str] = mapped_column(String(64), default=_revision_token)
    updated_by_principal_id: Mapped[str] = mapped_column(String(255))


class TelegramLinkTokenAudit(Base):
    __tablename__ = "telegram_link_token_audits"
    __table_args__ = (
        Index("ix_telegram_link_token_audits_tenant_status", "tenant_id", "status"),
        Index(
            "ix_telegram_link_token_audits_fingerprint",
            "token_fingerprint",
            unique=True,
        ),
    )

    telegram_link_token_audit_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=False
    )
    issued_by_principal_id: Mapped[str] = mapped_column(String(255))
    token_fingerprint: Mapped[str] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(32), default="issued")
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_by_principal_id: Mapped[str | None] = mapped_column(String(255))
    trace_id: Mapped[str] = mapped_column(String(128))


class TelegramLinkedIdentitySummary(Base):
    __tablename__ = "telegram_linked_identity_summaries"
    __table_args__ = (
        Index(
            "ix_telegram_linked_identity_summaries_tenant_status",
            "tenant_id",
            "status",
        ),
        Index(
            "ix_telegram_linked_identity_summaries_fingerprints",
            "tenant_id",
            "telegram_user_fingerprint",
            "telegram_chat_fingerprint",
            unique=True,
        ),
    )

    telegram_linked_identity_summary_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=False
    )
    platform_identity_id: Mapped[str] = mapped_column(String(255))
    telegram_user_fingerprint: Mapped[str] = mapped_column(String(128))
    telegram_chat_fingerprint: Mapped[str] = mapped_column(String(128))
    telegram_user_display: Mapped[str] = mapped_column(String(64))
    telegram_chat_display: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), default="linked")
    linked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_by_principal_id: Mapped[str | None] = mapped_column(String(255))
    command_ready: Mapped[bool] = mapped_column(Boolean, default=True)
    trace_id: Mapped[str] = mapped_column(String(128))


class TelegramDiagnosticEvent(Base):
    __tablename__ = "telegram_diagnostic_events"
    __table_args__ = (
        Index(
            "ix_telegram_diagnostic_events_tenant_created",
            "tenant_id",
            "created_at",
        ),
        Index("ix_telegram_diagnostic_events_category", "category", "status"),
    )

    telegram_diagnostic_event_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID | None] = mapped_column(ForeignKey("tenants.tenant_id"))
    principal_id: Mapped[str | None] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(64))
    summary: Mapped[str] = mapped_column(String(500))
    trace_id: Mapped[str] = mapped_column(String(128))
    redacted_metadata: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
