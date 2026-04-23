"""auth and access control schema

Revision ID: 0002_auth_access_control
Revises: 0001_platform_foundation
Create Date: 2026-04-22 00:30:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0002_auth_access_control"
down_revision = "0001_platform_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "principal_identities",
        sa.Column("principal_identity_id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column(
            "auth_provider",
            sa.Enum(
                "auth0",
                "local_principal",
                "system",
                name="authprovidertype",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("external_subject", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "active",
                "suspended",
                name="principalidentitystatus",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("external_subject"),
    )
    op.create_table(
        "delegated_credential_links",
        sa.Column(
            "delegated_credential_link_id",
            sa.Uuid(),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "secret_reference_id",
            sa.Uuid(),
            sa.ForeignKey("secret_references.secret_reference_id"),
            nullable=False,
        ),
        sa.Column(
            "owner_principal_id",
            sa.Uuid(),
            sa.ForeignKey("principal_identities.principal_identity_id"),
            nullable=False,
        ),
        sa.Column(
            "tenant_id",
            sa.Uuid(),
            sa.ForeignKey("tenants.tenant_id"),
            nullable=False,
        ),
        sa.Column("approved_tool_ids", sa.JSON(), nullable=False),
        sa.Column("granted_scopes", sa.JSON(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "active",
                "revoked",
                "expired",
                name="delegatedcredentialstatus",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("provider_subject", sa.String(length=255), nullable=True),
        sa.Column("granted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "role_grants",
        sa.Column("role_grant_id", sa.Uuid(), primary_key=True, nullable=False),
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
            "scope_type",
            sa.Enum("platform", "tenant", name="rolescopetype", native_enum=False),
            nullable=False,
        ),
        sa.Column(
            "tenant_id",
            sa.Uuid(),
            sa.ForeignKey("tenants.tenant_id"),
            nullable=True,
        ),
        sa.Column(
            "role_code",
            sa.Enum(
                "tenant_user",
                "tenant_admin",
                "platform_admin",
                name="rolecode",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "grant_source",
            sa.Enum(
                "bootstrap",
                "admin_assignment",
                "local_catalog",
                "sync",
                name="grantsource",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "active",
                "revoked",
                "expired",
                name="rolegrantstatus",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("effective_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "granted_by_principal_id",
            sa.Uuid(),
            sa.ForeignKey("principal_identities.principal_identity_id"),
            nullable=True,
        ),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "support_override_requests",
        sa.Column(
            "support_override_request_id",
            sa.Uuid(),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "requester_principal_id",
            sa.Uuid(),
            sa.ForeignKey("principal_identities.principal_identity_id"),
            nullable=False,
        ),
        sa.Column(
            "target_tenant_id",
            sa.Uuid(),
            sa.ForeignKey("tenants.tenant_id"),
            nullable=False,
        ),
        sa.Column("justification", sa.String(length=500), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "approved",
                "rejected",
                "expired",
                "revoked",
                name="supportoverridestatus",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "approver_principal_id",
            sa.Uuid(),
            sa.ForeignKey("principal_identities.principal_identity_id"),
            nullable=True,
        ),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("request_trace_id", sa.String(length=64), nullable=False),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.UniqueConstraint("idempotency_key"),
    )
    op.create_table(
        "access_decision_records",
        sa.Column(
            "access_decision_record_id",
            sa.Uuid(),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "principal_identity_id",
            sa.Uuid(),
            sa.ForeignKey("principal_identities.principal_identity_id"),
            nullable=True,
        ),
        sa.Column(
            "scope_type",
            sa.Enum("platform", "tenant", name="rolescopetype", native_enum=False),
            nullable=False,
        ),
        sa.Column(
            "tenant_id",
            sa.Uuid(),
            sa.ForeignKey("tenants.tenant_id"),
            nullable=True,
        ),
        sa.Column("surface_key", sa.String(length=255), nullable=False),
        sa.Column("requested_action", sa.String(length=128), nullable=False),
        sa.Column(
            "decision",
            sa.Enum("allow", "deny", "error", name="accessdecision", native_enum=False),
            nullable=False,
        ),
        sa.Column(
            "reason_code",
            sa.Enum(
                "unauthenticated",
                "invalid_token",
                "insufficient_permission",
                "insufficient_role",
                "cross_tenant",
                "support_override_required",
                "support_override_unapproved",
                "config_error",
                "delegated_credential_denied",
                "internal_error",
                name="accessreasoncode",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("auth_mode", sa.String(length=32), nullable=False),
        sa.Column("token_subject", sa.String(length=255), nullable=True),
        sa.Column("token_jti", sa.String(length=255), nullable=True),
        sa.Column(
            "support_override_request_id",
            sa.Uuid(),
            sa.ForeignKey("support_override_requests.support_override_request_id"),
            nullable=True,
        ),
        sa.Column(
            "delegated_credential_link_id",
            sa.Uuid(),
            sa.ForeignKey("delegated_credential_links.delegated_credential_link_id"),
            nullable=True,
        ),
        sa.Column("trace_id", sa.String(length=64), nullable=False),
        sa.Column("request_id", sa.String(length=64), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("classification", sa.String(length=64), nullable=False),
        sa.Column("required_roles", sa.JSON(), nullable=False),
        sa.Column("required_permissions", sa.JSON(), nullable=False),
        sa.Column("policy_version", sa.String(length=32), nullable=False),
        sa.Column("secret_free", sa.Boolean(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("access_decision_records")
    op.drop_table("support_override_requests")
    op.drop_table("role_grants")
    op.drop_table("delegated_credential_links")
    op.drop_table("principal_identities")
