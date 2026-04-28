"""admin console shell schema

Revision ID: 0010_admin_console_shell
Revises: 0009_reliability_scale_hardening
Create Date: 2026-04-27 00:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0010_admin_console_shell"
down_revision = "0009_reliability_scale_hardening"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "admin_saved_filters",
        sa.Column("admin_saved_filter_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "principal_identity_id",
            sa.Uuid(),
            sa.ForeignKey(
                "principal_identities.principal_identity_id", ondelete="CASCADE"
            ),
            nullable=True,
        ),
        sa.Column("principal_id", sa.String(128), nullable=False),
        sa.Column("admin_area", sa.String(64), nullable=False),
        sa.Column("filter_key", sa.String(128), nullable=False),
        sa.Column("scope_type", sa.String(32), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column("display_name", sa.String(120), nullable=False),
        sa.Column("criteria", sa.JSON(), nullable=False),
        sa.Column("safe_summary", sa.JSON(), nullable=False),
        sa.Column(
            "criteria_schema_version",
            sa.String(32),
            nullable=False,
            server_default="2026-04-27",
        ),
        sa.Column("last_restored_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "(scope_type = 'platform' AND tenant_id IS NULL) OR "
            "(scope_type = 'tenant' AND tenant_id IS NOT NULL)",
            name="ck_admin_saved_filters_scope_tenant",
        ),
        sa.UniqueConstraint(
            "principal_identity_id",
            "principal_id",
            "admin_area",
            "filter_key",
            "scope_type",
            "tenant_id",
            "display_name",
            name="uq_admin_saved_filters_scope_name",
        ),
    )
    op.create_index(
        "ix_admin_saved_filters_list_scope",
        "admin_saved_filters",
        [
            "principal_identity_id",
            "admin_area",
            "scope_type",
            "tenant_id",
            "updated_at",
        ],
    )
    op.create_index(
        "ix_admin_saved_filters_restore_scope",
        "admin_saved_filters",
        [
            "principal_identity_id",
            "admin_area",
            "filter_key",
            "scope_type",
            "tenant_id",
        ],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_admin_saved_filters_restore_scope", table_name="admin_saved_filters"
    )
    op.drop_index("ix_admin_saved_filters_list_scope", table_name="admin_saved_filters")
    op.drop_table("admin_saved_filters")
