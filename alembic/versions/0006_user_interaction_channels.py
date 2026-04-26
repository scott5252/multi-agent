"""user interaction channels schema

Revision ID: 0006_user_interaction_channels
Revises: 0005_immutable_memory
Create Date: 2026-04-24 00:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0006_user_interaction_channels"
down_revision = "0005_immutable_memory"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "channel_sessions",
        sa.Column("channel_session_id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column("platform_identity_id", sa.String(128), nullable=False),
        sa.Column("channel_type", sa.String(32), nullable=False),
        sa.Column("channel_subject", sa.String(255), nullable=False),
        sa.Column("auth_state", sa.String(32), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "tenant_id",
            "channel_type",
            "channel_subject",
            name="uq_channel_sessions_subject",
        ),
    )
    op.create_table(
        "telegram_identity_links",
        sa.Column("telegram_identity_link_id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column("platform_identity_id", sa.String(128), nullable=False),
        sa.Column("telegram_user_id", sa.String(64), nullable=False),
        sa.Column("telegram_chat_id", sa.String(64), nullable=False),
        sa.Column("link_token_hash", sa.String(128), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("linked_at", sa.DateTime(timezone=True)),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint(
            "tenant_id",
            "telegram_user_id",
            "telegram_chat_id",
            name="uq_telegram_links_user_chat",
        ),
    )
    op.create_table(
        "normalized_channel_requests",
        sa.Column("normalized_request_id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column("platform_identity_id", sa.String(128), nullable=False),
        sa.Column(
            "channel_session_id",
            sa.Uuid(),
            sa.ForeignKey("channel_sessions.channel_session_id"),
        ),
        sa.Column("channel_type", sa.String(32), nullable=False),
        sa.Column("action_type", sa.String(64), nullable=False),
        sa.Column("run_id", sa.Uuid()),
        sa.Column("prompt_id", sa.Uuid()),
        sa.Column("idempotency_key", sa.String(128)),
        sa.Column("trace_id", sa.String(64), nullable=False),
        sa.Column("source_request_id", sa.String(128)),
        sa.Column("input_payload", sa.JSON(), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("authorization_outcome", sa.String(64)),
        sa.Column("user_visible_outcome", sa.String(64)),
        sa.Column("source_metadata", sa.JSON(), nullable=False),
    )
    op.create_table(
        "channel_idempotency_records",
        sa.Column("idempotency_record_id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column("platform_identity_id", sa.String(128), nullable=False),
        sa.Column("channel_type", sa.String(32), nullable=False),
        sa.Column("action_type", sa.String(64), nullable=False),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.Column("request_fingerprint", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("stored_response", sa.JSON(), nullable=False),
        sa.Column("run_id", sa.Uuid()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "tenant_id",
            "platform_identity_id",
            "channel_type",
            "action_type",
            "idempotency_key",
            name="uq_channel_idempotency_scope",
        ),
    )
    op.create_table(
        "channel_timeline_events",
        sa.Column("timeline_event_id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column("run_id", sa.Uuid(), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("visible_state", sa.String(32), nullable=False),
        sa.Column("summary", sa.String(1000), nullable=False),
        sa.Column("severity", sa.String(16), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("trace_id", sa.String(64), nullable=False),
        sa.Column("source_channel", sa.String(32)),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.UniqueConstraint("tenant_id", "run_id", "sequence"),
    )
    op.create_table(
        "run_notification_subscriptions",
        sa.Column("notification_subscription_id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column("run_id", sa.Uuid(), nullable=False),
        sa.Column("platform_identity_id", sa.String(128), nullable=False),
        sa.Column("channel_session_id", sa.Uuid()),
        sa.Column("channel_type", sa.String(32), nullable=False),
        sa.Column("event_types", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("created_by", sa.String(128), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "notification_delivery_attempts",
        sa.Column("notification_delivery_attempt_id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column("notification_subscription_id", sa.Uuid(), nullable=False),
        sa.Column("run_id", sa.Uuid(), nullable=False),
        sa.Column("channel_type", sa.String(32), nullable=False),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("payload_fingerprint", sa.String(64), nullable=False),
        sa.Column("delivery_status", sa.String(32), nullable=False),
        sa.Column("provider_message_id", sa.String(128)),
        sa.Column("failure_category", sa.String(64)),
        sa.Column("attempt_number", sa.Integer(), nullable=False),
        sa.Column("next_retry_at", sa.DateTime(timezone=True)),
        sa.Column("trace_id", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("delivered_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "api_callback_registrations",
        sa.Column("api_callback_registration_id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column("run_id", sa.Uuid(), nullable=False),
        sa.Column("platform_identity_id", sa.String(128), nullable=False),
        sa.Column("callback_url", sa.String(1000), nullable=False),
        sa.Column("event_types", sa.JSON(), nullable=False),
        sa.Column("signing_secret_ref", sa.String(255)),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "api_callback_delivery_attempts",
        sa.Column("api_callback_delivery_attempt_id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column("api_callback_registration_id", sa.Uuid(), nullable=False),
        sa.Column("run_id", sa.Uuid(), nullable=False),
        sa.Column("event_id", sa.Uuid(), nullable=False),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("payload_fingerprint", sa.String(64), nullable=False),
        sa.Column("signature", sa.String(128), nullable=False),
        sa.Column("delivery_status", sa.String(32), nullable=False),
        sa.Column("http_status", sa.Integer()),
        sa.Column("failure_category", sa.String(64)),
        sa.Column("attempt_number", sa.Integer(), nullable=False),
        sa.Column("next_retry_at", sa.DateTime(timezone=True)),
        sa.Column("trace_id", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("delivered_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "artifact_access_grants",
        sa.Column("artifact_access_grant_id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column("run_id", sa.Uuid(), nullable=False),
        sa.Column("artifact_id", sa.Uuid(), nullable=False),
        sa.Column("platform_identity_id", sa.String(128), nullable=False),
        sa.Column("channel_type", sa.String(32), nullable=False),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.Column("download_url", sa.String(1000), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("trace_id", sa.String(64), nullable=False),
    )
    op.create_table(
        "interaction_audit_records",
        sa.Column("interaction_audit_record_id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column("platform_identity_id", sa.String(128)),
        sa.Column("channel_type", sa.String(32), nullable=False),
        sa.Column("channel_session_id", sa.Uuid()),
        sa.Column("action_type", sa.String(64), nullable=False),
        sa.Column("run_id", sa.Uuid()),
        sa.Column("prompt_id", sa.Uuid()),
        sa.Column("artifact_id", sa.Uuid()),
        sa.Column("authorization_outcome", sa.String(64), nullable=False),
        sa.Column("error_category", sa.String(64)),
        sa.Column("user_visible_outcome", sa.String(64), nullable=False),
        sa.Column("trace_id", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("redacted_metadata", sa.JSON(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("interaction_audit_records")
    op.drop_table("artifact_access_grants")
    op.drop_table("api_callback_delivery_attempts")
    op.drop_table("api_callback_registrations")
    op.drop_table("notification_delivery_attempts")
    op.drop_table("run_notification_subscriptions")
    op.drop_table("channel_timeline_events")
    op.drop_table("channel_idempotency_records")
    op.drop_table("normalized_channel_requests")
    op.drop_table("telegram_identity_links")
    op.drop_table("channel_sessions")
