"""telegram configuration console

Revision ID: 0017_telegram_config_console
Revises: 0016_token_usage_cost_analytics
Create Date: 2026-05-03 00:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0017_telegram_config_console"
down_revision = "0016_token_usage_cost_analytics"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "telegram_tenant_configs",
        sa.Column("telegram_tenant_config_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), nullable=False
        ),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("protected_commands", sa.JSON(), nullable=False),
        sa.Column("status_note", sa.String(500)),
        sa.Column("revision_token", sa.String(64), nullable=False),
        sa.Column("updated_by_principal_id", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_telegram_tenant_configs_tenant",
        "telegram_tenant_configs",
        ["tenant_id"],
        unique=True,
    )
    op.create_index(
        "ix_telegram_tenant_configs_revision",
        "telegram_tenant_configs",
        ["tenant_id", "revision_token"],
    )

    op.create_table(
        "telegram_link_token_audits",
        sa.Column("telegram_link_token_audit_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), nullable=False
        ),
        sa.Column("issued_by_principal_id", sa.String(255), nullable=False),
        sa.Column("token_fingerprint", sa.String(128), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True)),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("revoked_by_principal_id", sa.String(255)),
        sa.Column("trace_id", sa.String(128), nullable=False),
    )
    op.create_index(
        "ix_telegram_link_token_audits_tenant_status",
        "telegram_link_token_audits",
        ["tenant_id", "status"],
    )
    op.create_index(
        "ix_telegram_link_token_audits_fingerprint",
        "telegram_link_token_audits",
        ["token_fingerprint"],
        unique=True,
    )

    op.create_table(
        "telegram_linked_identity_summaries",
        sa.Column("telegram_linked_identity_summary_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), nullable=False
        ),
        sa.Column("platform_identity_id", sa.String(255), nullable=False),
        sa.Column("telegram_user_fingerprint", sa.String(128), nullable=False),
        sa.Column("telegram_chat_fingerprint", sa.String(128), nullable=False),
        sa.Column("telegram_user_display", sa.String(64), nullable=False),
        sa.Column("telegram_chat_display", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("linked_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("revoked_by_principal_id", sa.String(255)),
        sa.Column("command_ready", sa.Boolean(), nullable=False),
        sa.Column("trace_id", sa.String(128), nullable=False),
    )
    op.create_index(
        "ix_telegram_linked_identity_summaries_tenant_status",
        "telegram_linked_identity_summaries",
        ["tenant_id", "status"],
    )
    op.create_index(
        "ix_telegram_linked_identity_summaries_fingerprints",
        "telegram_linked_identity_summaries",
        ["tenant_id", "telegram_user_fingerprint", "telegram_chat_fingerprint"],
        unique=True,
    )

    op.create_table(
        "telegram_diagnostic_events",
        sa.Column("telegram_diagnostic_event_id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column("principal_id", sa.String(255)),
        sa.Column("category", sa.String(64), nullable=False),
        sa.Column("status", sa.String(64), nullable=False),
        sa.Column("summary", sa.String(500), nullable=False),
        sa.Column("trace_id", sa.String(128), nullable=False),
        sa.Column("redacted_metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_telegram_diagnostic_events_tenant_created",
        "telegram_diagnostic_events",
        ["tenant_id", "created_at"],
    )
    op.create_index(
        "ix_telegram_diagnostic_events_category",
        "telegram_diagnostic_events",
        ["category", "status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_telegram_diagnostic_events_category",
        table_name="telegram_diagnostic_events",
    )
    op.drop_index(
        "ix_telegram_diagnostic_events_tenant_created",
        table_name="telegram_diagnostic_events",
    )
    op.drop_table("telegram_diagnostic_events")
    op.drop_index(
        "ix_telegram_linked_identity_summaries_fingerprints",
        table_name="telegram_linked_identity_summaries",
    )
    op.drop_index(
        "ix_telegram_linked_identity_summaries_tenant_status",
        table_name="telegram_linked_identity_summaries",
    )
    op.drop_table("telegram_linked_identity_summaries")
    op.drop_index(
        "ix_telegram_link_token_audits_fingerprint",
        table_name="telegram_link_token_audits",
    )
    op.drop_index(
        "ix_telegram_link_token_audits_tenant_status",
        table_name="telegram_link_token_audits",
    )
    op.drop_table("telegram_link_token_audits")
    op.drop_index(
        "ix_telegram_tenant_configs_revision",
        table_name="telegram_tenant_configs",
    )
    op.drop_index(
        "ix_telegram_tenant_configs_tenant",
        table_name="telegram_tenant_configs",
    )
    op.drop_table("telegram_tenant_configs")
