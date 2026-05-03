"""user tenant membership administration

Revision ID: 0018_membership_admin
Revises: 0017_telegram_config_console
Create Date: 2026-05-03 00:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0018_membership_admin"
down_revision = "0017_telegram_config_console"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_invitations",
        sa.Column("user_invitation_id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column("invited_email", sa.String(320), nullable=False),
        sa.Column("invited_email_hash", sa.String(128), nullable=False),
        sa.Column("masked_email", sa.String(320), nullable=False),
        sa.Column("requested_roles", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("idempotency_key", sa.String(128)),
        sa.Column("invited_by_principal_id", sa.String(255), nullable=False),
        sa.Column(
            "principal_identity_id",
            sa.Uuid(),
            sa.ForeignKey("principal_identities.principal_identity_id"),
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("accepted_at", sa.DateTime(timezone=True)),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("trace_id", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_user_invitations_tenant_status",
        "user_invitations",
        ["tenant_id", "status"],
    )
    op.create_index(
        "ix_user_invitations_email_hash",
        "user_invitations",
        ["tenant_id", "invited_email_hash"],
    )
    op.create_index(
        "ix_user_invitations_idempotency",
        "user_invitations",
        ["idempotency_key"],
    )

    op.create_table(
        "tenant_memberships",
        sa.Column("tenant_membership_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), nullable=False
        ),
        sa.Column(
            "principal_identity_id",
            sa.Uuid(),
            sa.ForeignKey(
                "principal_identities.principal_identity_id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column(
            "invitation_id",
            sa.Uuid(),
            sa.ForeignKey("user_invitations.user_invitation_id"),
        ),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("revision_token", sa.String(64), nullable=False),
        sa.Column("membership_source", sa.String(64), nullable=False),
        sa.Column("created_by_principal_id", sa.String(255), nullable=False),
        sa.Column("updated_by_principal_id", sa.String(255), nullable=False),
        sa.Column("suspended_at", sa.DateTime(timezone=True)),
        sa.Column("removed_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("tenant_id", "principal_identity_id"),
    )
    op.create_index(
        "ix_tenant_memberships_tenant_status",
        "tenant_memberships",
        ["tenant_id", "status"],
    )
    op.create_index(
        "ix_tenant_memberships_principal",
        "tenant_memberships",
        ["principal_identity_id", "tenant_id"],
    )
    op.create_index(
        "ix_tenant_memberships_revision",
        "tenant_memberships",
        ["tenant_id", "revision_token"],
    )

    op.create_table(
        "membership_audit_records",
        sa.Column("membership_audit_record_id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column("actor_principal_id", sa.String(255), nullable=False),
        sa.Column(
            "target_principal_identity_id",
            sa.Uuid(),
            sa.ForeignKey("principal_identities.principal_identity_id"),
        ),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("decision", sa.String(32), nullable=False),
        sa.Column("summary", sa.String(500), nullable=False),
        sa.Column("trace_id", sa.String(128), nullable=False),
        sa.Column("redacted_metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_membership_audit_tenant_created",
        "membership_audit_records",
        ["tenant_id", "created_at"],
    )
    op.create_index(
        "ix_membership_audit_actor",
        "membership_audit_records",
        ["actor_principal_id", "created_at"],
    )
    op.create_index(
        "ix_membership_audit_target",
        "membership_audit_records",
        ["target_principal_identity_id"],
    )
    op.create_index(
        "ix_membership_audit_action",
        "membership_audit_records",
        ["action", "decision"],
    )


def downgrade() -> None:
    op.drop_index("ix_membership_audit_action", table_name="membership_audit_records")
    op.drop_index("ix_membership_audit_target", table_name="membership_audit_records")
    op.drop_index("ix_membership_audit_actor", table_name="membership_audit_records")
    op.drop_index(
        "ix_membership_audit_tenant_created",
        table_name="membership_audit_records",
    )
    op.drop_table("membership_audit_records")
    op.drop_index("ix_tenant_memberships_revision", table_name="tenant_memberships")
    op.drop_index("ix_tenant_memberships_principal", table_name="tenant_memberships")
    op.drop_index(
        "ix_tenant_memberships_tenant_status",
        table_name="tenant_memberships",
    )
    op.drop_table("tenant_memberships")
    op.drop_index("ix_user_invitations_idempotency", table_name="user_invitations")
    op.drop_index("ix_user_invitations_email_hash", table_name="user_invitations")
    op.drop_index("ix_user_invitations_tenant_status", table_name="user_invitations")
    op.drop_table("user_invitations")
