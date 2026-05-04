from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from multi_agent_platform.db.base import Base, TimestampMixin, utcnow


def _revision_token() -> str:
    return uuid4().hex


class BriefingPreferenceProfile(Base, TimestampMixin):
    __tablename__ = "briefing_preference_profiles"
    __table_args__ = (
        Index(
            "uq_briefing_preference_profiles_tenant_principal",
            "tenant_id",
            "principal_id",
            unique=True,
        ),
        Index(
            "ix_briefing_preference_profiles_tenant_updated",
            "tenant_id",
            "updated_at",
        ),
        Index(
            "ix_briefing_preference_profiles_revision",
            "tenant_id",
            "revision_token",
        ),
    )

    briefing_preference_profile_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=False
    )
    principal_id: Mapped[str] = mapped_column(String(255), nullable=False)
    location_label: Mapped[str] = mapped_column(String(120), nullable=False)
    timezone: Mapped[str] = mapped_column(String(120), nullable=False)
    news_topics: Mapped[list[str]] = mapped_column(JSON, default=list)
    vip_senders: Mapped[list[str]] = mapped_column(JSON, default=list)
    workday_start: Mapped[str] = mapped_column(String(5), nullable=False)
    workday_end: Mapped[str] = mapped_column(String(5), nullable=False)
    commute_mode: Mapped[str] = mapped_column(String(32), nullable=False)
    calendar_account_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    email_account_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    output_style: Mapped[str] = mapped_column(String(32), nullable=False)
    scheduled_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    scheduled_time: Mapped[str | None] = mapped_column(String(5))
    current_revision_id: Mapped[UUID] = mapped_column(nullable=False)
    revision_number: Mapped[int] = mapped_column(Integer, default=1)
    content_digest: Mapped[str] = mapped_column(String(128), nullable=False)
    safe_summary: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    revision_token: Mapped[str] = mapped_column(String(64), default=_revision_token)


class BriefingPreferenceRevision(Base):
    __tablename__ = "briefing_preference_revisions"
    __table_args__ = (
        Index(
            "uq_briefing_preference_revisions_profile_number",
            "briefing_preference_profile_id",
            "revision_number",
            unique=True,
        ),
        Index(
            "ix_briefing_preference_revisions_tenant_principal_created",
            "tenant_id",
            "principal_id",
            "created_at",
        ),
    )

    briefing_preference_revision_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    briefing_preference_profile_id: Mapped[UUID] = mapped_column(
        ForeignKey("briefing_preference_profiles.briefing_preference_profile_id"),
        nullable=False,
    )
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=False
    )
    principal_id: Mapped[str] = mapped_column(String(255), nullable=False)
    revision_number: Mapped[int] = mapped_column(Integer, nullable=False)
    preference_payload: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    safe_summary: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    content_digest: Mapped[str] = mapped_column(String(128), nullable=False)
    created_by_principal_id: Mapped[str] = mapped_column(String(255), nullable=False)
    trace_id: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class BriefingPreferenceAuditEvent(Base):
    __tablename__ = "briefing_preference_audit_events"
    __table_args__ = (
        Index(
            "ix_briefing_preference_audit_events_tenant_created",
            "tenant_id",
            "created_at",
        ),
        Index("ix_briefing_preference_audit_events_action", "action", "decision"),
    )

    briefing_preference_audit_event_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID | None] = mapped_column(ForeignKey("tenants.tenant_id"))
    principal_id: Mapped[str | None] = mapped_column(String(255))
    actor_principal_id: Mapped[str | None] = mapped_column(String(255))
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    decision: Mapped[str] = mapped_column(String(32), nullable=False)
    summary: Mapped[str] = mapped_column(String(500), nullable=False)
    profile_id: Mapped[UUID | None] = mapped_column()
    revision_id: Mapped[UUID | None] = mapped_column()
    content_digest: Mapped[str | None] = mapped_column(String(128))
    trace_id: Mapped[str] = mapped_column(String(128), nullable=False)
    redacted_metadata: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
