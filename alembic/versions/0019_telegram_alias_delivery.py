"""telegram alias delivery persistence

Revision ID: 0019_telegram_alias_delivery
Revises: 0018_membership_admin
Create Date: 2026-05-04 00:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0019_telegram_alias_delivery"
down_revision = "0018_membership_admin"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "telegram_command_aliases",
        sa.Column("telegram_command_alias_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), nullable=False
        ),
        sa.Column("alias_text", sa.String(120), nullable=False),
        sa.Column("alias_normalized", sa.String(120), nullable=False),
        sa.Column("published_workflow_version_id", sa.Uuid(), nullable=False),
        sa.Column("description", sa.String(500)),
        sa.Column("protected", sa.Boolean(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("revision_token", sa.String(64), nullable=False),
        sa.Column("created_by_principal_id", sa.String(255), nullable=False),
        sa.Column("updated_by_principal_id", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "tenant_id",
            "alias_normalized",
            name="uq_telegram_command_aliases_tenant_alias",
        ),
    )
    op.create_index(
        "ix_telegram_command_aliases_tenant_enabled",
        "telegram_command_aliases",
        ["tenant_id", "enabled"],
    )
    op.create_index(
        "ix_telegram_command_aliases_revision",
        "telegram_command_aliases",
        ["tenant_id", "revision_token"],
    )

    op.create_table(
        "telegram_update_receipts",
        sa.Column("telegram_update_receipt_id", sa.Uuid(), primary_key=True),
        sa.Column("telegram_update_id", sa.BigInteger(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column("platform_identity_id", sa.String(255)),
        sa.Column("telegram_chat_fingerprint", sa.String(128)),
        sa.Column("action_type", sa.String(64), nullable=False),
        sa.Column("response_payload", sa.JSON(), nullable=False),
        sa.Column("run_id", sa.Uuid()),
        sa.Column("delivery_attempt_id", sa.Uuid()),
        sa.Column("trace_id", sa.String(128), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "telegram_update_id",
            name="uq_telegram_update_receipts_update_id",
        ),
    )
    op.create_index(
        "ix_telegram_update_receipts_tenant_received",
        "telegram_update_receipts",
        ["tenant_id", "received_at"],
    )
    op.create_index(
        "ix_telegram_update_receipts_action",
        "telegram_update_receipts",
        ["action_type"],
    )

    op.add_column(
        "notification_delivery_attempts",
        sa.Column("destination_fingerprint", sa.String(128)),
    )


def downgrade() -> None:
    op.drop_column("notification_delivery_attempts", "destination_fingerprint")
    op.drop_index(
        "ix_telegram_update_receipts_action",
        table_name="telegram_update_receipts",
    )
    op.drop_index(
        "ix_telegram_update_receipts_tenant_received",
        table_name="telegram_update_receipts",
    )
    op.drop_table("telegram_update_receipts")
    op.drop_index(
        "ix_telegram_command_aliases_revision",
        table_name="telegram_command_aliases",
    )
    op.drop_index(
        "ix_telegram_command_aliases_tenant_enabled",
        table_name="telegram_command_aliases",
    )
    op.drop_table("telegram_command_aliases")
