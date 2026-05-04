"""briefing preferences

Revision ID: 0020_briefing_preferences
Revises: 0019_telegram_alias_delivery
Create Date: 2026-05-04 00:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0020_briefing_preferences"
down_revision = "0019_telegram_alias_delivery"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "briefing_preference_profiles",
        sa.Column("briefing_preference_profile_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), nullable=False
        ),
        sa.Column("principal_id", sa.String(255), nullable=False),
        sa.Column("location_label", sa.String(120), nullable=False),
        sa.Column("timezone", sa.String(120), nullable=False),
        sa.Column("news_topics", sa.JSON(), nullable=False),
        sa.Column("vip_senders", sa.JSON(), nullable=False),
        sa.Column("workday_start", sa.String(5), nullable=False),
        sa.Column("workday_end", sa.String(5), nullable=False),
        sa.Column("commute_mode", sa.String(32), nullable=False),
        sa.Column("calendar_account_ref", sa.String(255), nullable=False),
        sa.Column("email_account_ref", sa.String(255), nullable=False),
        sa.Column("output_style", sa.String(32), nullable=False),
        sa.Column("scheduled_enabled", sa.Boolean(), nullable=False),
        sa.Column("scheduled_time", sa.String(5)),
        sa.Column("current_revision_id", sa.Uuid(), nullable=False),
        sa.Column("revision_number", sa.Integer(), nullable=False),
        sa.Column("content_digest", sa.String(128), nullable=False),
        sa.Column("safe_summary", sa.JSON(), nullable=False),
        sa.Column("revision_token", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "tenant_id",
            "principal_id",
            name="uq_briefing_preference_profiles_tenant_principal",
        ),
    )
    op.create_index(
        "ix_briefing_preference_profiles_tenant_updated",
        "briefing_preference_profiles",
        ["tenant_id", "updated_at"],
    )
    op.create_index(
        "ix_briefing_preference_profiles_revision",
        "briefing_preference_profiles",
        ["tenant_id", "revision_token"],
    )

    op.create_table(
        "briefing_preference_revisions",
        sa.Column("briefing_preference_revision_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "briefing_preference_profile_id",
            sa.Uuid(),
            sa.ForeignKey(
                "briefing_preference_profiles.briefing_preference_profile_id"
            ),
            nullable=False,
        ),
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), nullable=False
        ),
        sa.Column("principal_id", sa.String(255), nullable=False),
        sa.Column("revision_number", sa.Integer(), nullable=False),
        sa.Column("preference_payload", sa.JSON(), nullable=False),
        sa.Column("safe_summary", sa.JSON(), nullable=False),
        sa.Column("content_digest", sa.String(128), nullable=False),
        sa.Column("created_by_principal_id", sa.String(255), nullable=False),
        sa.Column("trace_id", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "briefing_preference_profile_id",
            "revision_number",
            name="uq_briefing_preference_revisions_profile_number",
        ),
    )
    op.create_index(
        "ix_briefing_preference_revisions_tenant_principal_created",
        "briefing_preference_revisions",
        ["tenant_id", "principal_id", "created_at"],
    )

    op.create_table(
        "briefing_preference_audit_events",
        sa.Column("briefing_preference_audit_event_id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column("principal_id", sa.String(255)),
        sa.Column("actor_principal_id", sa.String(255)),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("decision", sa.String(32), nullable=False),
        sa.Column("summary", sa.String(500), nullable=False),
        sa.Column("profile_id", sa.Uuid()),
        sa.Column("revision_id", sa.Uuid()),
        sa.Column("content_digest", sa.String(128)),
        sa.Column("trace_id", sa.String(128), nullable=False),
        sa.Column("redacted_metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_briefing_preference_audit_events_tenant_created",
        "briefing_preference_audit_events",
        ["tenant_id", "created_at"],
    )
    op.create_index(
        "ix_briefing_preference_audit_events_action",
        "briefing_preference_audit_events",
        ["action", "decision"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_briefing_preference_audit_events_action",
        table_name="briefing_preference_audit_events",
    )
    op.drop_index(
        "ix_briefing_preference_audit_events_tenant_created",
        table_name="briefing_preference_audit_events",
    )
    op.drop_table("briefing_preference_audit_events")
    op.drop_index(
        "ix_briefing_preference_revisions_tenant_principal_created",
        table_name="briefing_preference_revisions",
    )
    op.drop_table("briefing_preference_revisions")
    op.drop_index(
        "ix_briefing_preference_profiles_revision",
        table_name="briefing_preference_profiles",
    )
    op.drop_index(
        "ix_briefing_preference_profiles_tenant_updated",
        table_name="briefing_preference_profiles",
    )
    op.drop_table("briefing_preference_profiles")
