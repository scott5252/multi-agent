from __future__ import annotations

from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from multi_agent_platform.db.base import Base, TimestampMixin


class ChannelSessionAuthState(StrEnum):
    AUTHENTICATED = "authenticated"
    LINK_PENDING = "link_pending"
    LINKED = "linked"
    REVOKED = "revoked"


class TelegramIdentityLinkStatus(StrEnum):
    PENDING = "pending"
    LINKED = "linked"
    EXPIRED = "expired"
    REVOKED = "revoked"


class ChannelIdempotencyStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    ACCEPTED = "accepted"
    FAILED = "failed"


class ChannelDeliveryStatus(StrEnum):
    SCHEDULED = "scheduled"
    DELIVERED = "delivered"
    RETRYING = "retrying"
    FAILED = "failed"
    SUPPRESSED = "suppressed"


class ChannelSessionRecord(Base, TimestampMixin):
    __tablename__ = "channel_sessions"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "channel_type",
            "channel_subject",
            name="uq_channel_sessions_subject",
        ),
    )

    channel_session_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID | None] = mapped_column(ForeignKey("tenants.tenant_id"))
    platform_identity_id: Mapped[str] = mapped_column(String(128))
    channel_type: Mapped[str] = mapped_column(String(32))
    channel_subject: Mapped[str] = mapped_column(String(255))
    auth_state: Mapped[str] = mapped_column(String(32), default="authenticated")
    expires_at: Mapped[object | None] = mapped_column(DateTime(timezone=True))
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)


class TelegramIdentityLinkRecord(Base):
    __tablename__ = "telegram_identity_links"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "telegram_user_id",
            "telegram_chat_id",
            name="uq_telegram_links_user_chat",
        ),
    )

    telegram_identity_link_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID | None] = mapped_column(ForeignKey("tenants.tenant_id"))
    platform_identity_id: Mapped[str] = mapped_column(String(128))
    telegram_user_id: Mapped[str] = mapped_column(String(64))
    telegram_chat_id: Mapped[str] = mapped_column(String(64))
    link_token_hash: Mapped[str] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(32), default="pending")
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[object] = mapped_column(DateTime(timezone=True))
    linked_at: Mapped[object | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[object | None] = mapped_column(DateTime(timezone=True))


class NormalizedChannelRequestRecord(Base):
    __tablename__ = "normalized_channel_requests"

    normalized_request_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID | None] = mapped_column(ForeignKey("tenants.tenant_id"))
    platform_identity_id: Mapped[str] = mapped_column(String(128))
    channel_session_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("channel_sessions.channel_session_id")
    )
    channel_type: Mapped[str] = mapped_column(String(32))
    action_type: Mapped[str] = mapped_column(String(64))
    run_id: Mapped[UUID | None] = mapped_column()
    prompt_id: Mapped[UUID | None] = mapped_column()
    idempotency_key: Mapped[str | None] = mapped_column(String(128))
    trace_id: Mapped[str] = mapped_column(String(64))
    source_request_id: Mapped[str | None] = mapped_column(String(128))
    input_payload: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    received_at: Mapped[object] = mapped_column(DateTime(timezone=True))
    authorization_outcome: Mapped[str | None] = mapped_column(String(64))
    user_visible_outcome: Mapped[str | None] = mapped_column(String(64))
    source_metadata: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)


class ChannelIdempotencyRecord(Base):
    __tablename__ = "channel_idempotency_records"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "platform_identity_id",
            "channel_type",
            "action_type",
            "idempotency_key",
            name="uq_channel_idempotency_scope",
        ),
    )

    idempotency_record_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID | None] = mapped_column(ForeignKey("tenants.tenant_id"))
    platform_identity_id: Mapped[str] = mapped_column(String(128))
    channel_type: Mapped[str] = mapped_column(String(32))
    action_type: Mapped[str] = mapped_column(String(64))
    idempotency_key: Mapped[str] = mapped_column(String(128))
    request_fingerprint: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32))
    stored_response: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    run_id: Mapped[UUID | None] = mapped_column()
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[object] = mapped_column(DateTime(timezone=True))


class ChannelTimelineEventRecord(Base):
    __tablename__ = "channel_timeline_events"
    __table_args__ = (UniqueConstraint("tenant_id", "run_id", "sequence"),)

    timeline_event_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID | None] = mapped_column(ForeignKey("tenants.tenant_id"))
    run_id: Mapped[UUID] = mapped_column()
    sequence: Mapped[int] = mapped_column(Integer)
    event_type: Mapped[str] = mapped_column(String(64))
    visible_state: Mapped[str] = mapped_column(String(32))
    summary: Mapped[str] = mapped_column(String(1000))
    severity: Mapped[str] = mapped_column(String(16), default="info")
    occurred_at: Mapped[object] = mapped_column(DateTime(timezone=True))
    trace_id: Mapped[str] = mapped_column(String(64))
    source_channel: Mapped[str | None] = mapped_column(String(32))
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)


class RunNotificationSubscriptionRecord(Base, TimestampMixin):
    __tablename__ = "run_notification_subscriptions"

    notification_subscription_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID | None] = mapped_column(ForeignKey("tenants.tenant_id"))
    run_id: Mapped[UUID] = mapped_column()
    platform_identity_id: Mapped[str] = mapped_column(String(128))
    channel_session_id: Mapped[UUID | None] = mapped_column()
    channel_type: Mapped[str] = mapped_column(String(32))
    event_types: Mapped[list[str]] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(32), default="active")
    created_by: Mapped[str] = mapped_column(String(128))
    revoked_at: Mapped[object | None] = mapped_column(DateTime(timezone=True))


class NotificationDeliveryAttemptRecord(Base):
    __tablename__ = "notification_delivery_attempts"

    notification_delivery_attempt_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID | None] = mapped_column(ForeignKey("tenants.tenant_id"))
    notification_subscription_id: Mapped[UUID] = mapped_column()
    run_id: Mapped[UUID] = mapped_column()
    channel_type: Mapped[str] = mapped_column(String(32))
    event_type: Mapped[str] = mapped_column(String(64))
    payload_fingerprint: Mapped[str] = mapped_column(String(64))
    delivery_status: Mapped[str] = mapped_column(String(32))
    provider_message_id: Mapped[str | None] = mapped_column(String(128))
    failure_category: Mapped[str | None] = mapped_column(String(64))
    attempt_number: Mapped[int] = mapped_column(Integer, default=1)
    next_retry_at: Mapped[object | None] = mapped_column(DateTime(timezone=True))
    trace_id: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True))
    delivered_at: Mapped[object | None] = mapped_column(DateTime(timezone=True))


class ApiCallbackRegistrationRecord(Base, TimestampMixin):
    __tablename__ = "api_callback_registrations"

    api_callback_registration_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID | None] = mapped_column(ForeignKey("tenants.tenant_id"))
    run_id: Mapped[UUID] = mapped_column()
    platform_identity_id: Mapped[str] = mapped_column(String(128))
    callback_url: Mapped[str] = mapped_column(String(1000))
    event_types: Mapped[list[str]] = mapped_column(JSON, default=list)
    signing_secret_ref: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(32), default="active")
    revoked_at: Mapped[object | None] = mapped_column(DateTime(timezone=True))


class ApiCallbackDeliveryAttemptRecord(Base):
    __tablename__ = "api_callback_delivery_attempts"

    api_callback_delivery_attempt_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID | None] = mapped_column(ForeignKey("tenants.tenant_id"))
    api_callback_registration_id: Mapped[UUID] = mapped_column()
    run_id: Mapped[UUID] = mapped_column()
    event_id: Mapped[UUID] = mapped_column()
    event_type: Mapped[str] = mapped_column(String(64))
    payload_fingerprint: Mapped[str] = mapped_column(String(64))
    signature: Mapped[str] = mapped_column(String(128))
    delivery_status: Mapped[str] = mapped_column(String(32))
    http_status: Mapped[int | None] = mapped_column(Integer)
    failure_category: Mapped[str | None] = mapped_column(String(64))
    attempt_number: Mapped[int] = mapped_column(Integer, default=1)
    next_retry_at: Mapped[object | None] = mapped_column(DateTime(timezone=True))
    trace_id: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True))
    delivered_at: Mapped[object | None] = mapped_column(DateTime(timezone=True))


class ArtifactAccessGrantRecord(Base):
    __tablename__ = "artifact_access_grants"

    artifact_access_grant_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID | None] = mapped_column(ForeignKey("tenants.tenant_id"))
    run_id: Mapped[UUID] = mapped_column()
    artifact_id: Mapped[UUID] = mapped_column()
    platform_identity_id: Mapped[str] = mapped_column(String(128))
    channel_type: Mapped[str] = mapped_column(String(32))
    idempotency_key: Mapped[str] = mapped_column(String(128))
    download_url: Mapped[str] = mapped_column(String(1000))
    expires_at: Mapped[object] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(32), default="active")
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True))
    trace_id: Mapped[str] = mapped_column(String(64))


class InteractionAuditRecord(Base):
    __tablename__ = "interaction_audit_records"

    interaction_audit_record_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID | None] = mapped_column(ForeignKey("tenants.tenant_id"))
    platform_identity_id: Mapped[str | None] = mapped_column(String(128))
    channel_type: Mapped[str] = mapped_column(String(32))
    channel_session_id: Mapped[UUID | None] = mapped_column()
    action_type: Mapped[str] = mapped_column(String(64))
    run_id: Mapped[UUID | None] = mapped_column()
    prompt_id: Mapped[UUID | None] = mapped_column()
    artifact_id: Mapped[UUID | None] = mapped_column()
    authorization_outcome: Mapped[str] = mapped_column(String(64))
    error_category: Mapped[str | None] = mapped_column(String(64))
    user_visible_outcome: Mapped[str] = mapped_column(String(64))
    trace_id: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True))
    redacted_metadata: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
