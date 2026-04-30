"""skill registry lifecycle

Revision ID: 0014_skill_registry_lifecycle
Revises: 0013_prp_v2_gateway_ops
Create Date: 2026-04-29 00:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0014_skill_registry_lifecycle"
down_revision = "0013_prp_v2_gateway_ops"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "skill_packages",
        sa.Column("skill_package_id", sa.Uuid(), primary_key=True),
        sa.Column("slug", sa.String(128), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("owner_principal_id", sa.String(255), nullable=False),
        sa.Column("approval_status", sa.String(64), nullable=False),
        sa.Column("lifecycle_state", sa.String(64), nullable=False),
        sa.Column("safe_documentation_summary", sa.JSON(), nullable=False),
        sa.Column("latest_published_version", sa.String(64)),
        sa.Column("created_by_principal_id", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("retired_at", sa.DateTime(timezone=True)),
        sa.Column("quarantined_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_skill_packages_slug", "skill_packages", ["slug"], unique=True)

    op.create_table(
        "skill_package_versions",
        sa.Column("skill_package_version_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "skill_package_id",
            sa.Uuid(),
            sa.ForeignKey("skill_packages.skill_package_id"),
            nullable=False,
        ),
        sa.Column("slug", sa.String(128), nullable=False),
        sa.Column("semantic_version", sa.String(64), nullable=False),
        sa.Column("manifest_digest", sa.String(128), nullable=False),
        sa.Column("manifest_snapshot", sa.JSON(), nullable=False),
        sa.Column("safe_manifest_summary", sa.JSON(), nullable=False),
        sa.Column("artifact_id", sa.Uuid(), sa.ForeignKey("artifacts.artifact_id")),
        sa.Column("artifact_digest", sa.String(128), nullable=False),
        sa.Column(
            "documentation_artifact_id",
            sa.Uuid(),
            sa.ForeignKey("artifacts.artifact_id"),
        ),
        sa.Column("documentation_digest", sa.String(128)),
        sa.Column(
            "fixture_artifact_id", sa.Uuid(), sa.ForeignKey("artifacts.artifact_id")
        ),
        sa.Column("fixture_digest", sa.String(128)),
        sa.Column("compatibility_metadata", sa.JSON(), nullable=False),
        sa.Column("validation_status", sa.String(64), nullable=False),
        sa.Column("validation_summary", sa.JSON(), nullable=False),
        sa.Column("lifecycle_state", sa.String(64), nullable=False),
        sa.Column("availability_mode", sa.String(64), nullable=False),
        sa.Column("published_by_principal_id", sa.String(255)),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.Column("withdrawn_at", sa.DateTime(timezone=True)),
        sa.Column("quarantined_at", sa.DateTime(timezone=True)),
        sa.Column("runtime_blocked_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_skill_package_versions_package_semver",
        "skill_package_versions",
        ["skill_package_id", "semantic_version"],
        unique=True,
    )
    op.create_index(
        "ix_skill_package_versions_slug_semver",
        "skill_package_versions",
        ["slug", "semantic_version"],
    )

    op.create_table(
        "skill_package_tenant_grants",
        sa.Column("tenant_grant_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "skill_package_version_id",
            sa.Uuid(),
            sa.ForeignKey("skill_package_versions.skill_package_version_id"),
            nullable=False,
        ),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column("grant_mode", sa.String(64), nullable=False),
        sa.Column("status", sa.String(64), nullable=False),
        sa.Column("granted_by_principal_id", sa.String(255), nullable=False),
        sa.Column("granted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("reason", sa.Text()),
        sa.Column("audit_record_id", sa.Uuid()),
    )
    op.create_index(
        "ix_skill_package_tenant_grants_version_tenant",
        "skill_package_tenant_grants",
        ["skill_package_version_id", "tenant_id"],
        unique=True,
    )

    op.create_table(
        "skill_installations",
        sa.Column("skill_installation_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), nullable=False
        ),
        sa.Column(
            "skill_package_version_id",
            sa.Uuid(),
            sa.ForeignKey("skill_package_versions.skill_package_version_id"),
            nullable=False,
        ),
        sa.Column("slug", sa.String(128), nullable=False),
        sa.Column("semantic_version", sa.String(64), nullable=False),
        sa.Column("installation_version", sa.Integer(), nullable=False),
        sa.Column("previous_installation_id", sa.Uuid()),
        sa.Column("manifest_digest", sa.String(128), nullable=False),
        sa.Column("manifest_summary", sa.JSON(), nullable=False),
        sa.Column("artifact_digest", sa.String(128), nullable=False),
        sa.Column("readiness_state", sa.String(64), nullable=False),
        sa.Column("credential_status", sa.String(64), nullable=False),
        sa.Column("compatibility_status", sa.String(64), nullable=False),
        sa.Column("permission_status", sa.String(64), nullable=False),
        sa.Column("smoke_test_status", sa.String(64), nullable=False),
        sa.Column("binding_eligibility_status", sa.String(64), nullable=False),
        sa.Column("policy_summary", sa.JSON(), nullable=False),
        sa.Column("findings", sa.JSON(), nullable=False),
        sa.Column("quarantine_state", sa.String(64), nullable=False),
        sa.Column("runtime_blocked", sa.Boolean(), nullable=False),
        sa.Column("installed_by_principal_id", sa.String(255), nullable=False),
        sa.Column("installed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ready_at", sa.DateTime(timezone=True)),
        sa.Column("retired_at", sa.DateTime(timezone=True)),
        sa.Column("revision_token", sa.String(128), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_skill_installations_tenant_slug_version",
        "skill_installations",
        ["tenant_id", "slug", "installation_version"],
        unique=True,
    )
    op.create_index(
        "ix_skill_installations_tenant_state",
        "skill_installations",
        ["tenant_id", "readiness_state"],
    )

    op.create_table(
        "skill_installation_credentials",
        sa.Column("credential_readiness_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "skill_installation_id",
            sa.Uuid(),
            sa.ForeignKey("skill_installations.skill_installation_id"),
            nullable=False,
        ),
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), nullable=False
        ),
        sa.Column("requirement_key", sa.String(128), nullable=False),
        sa.Column("credential_kind", sa.String(64), nullable=False),
        sa.Column("secret_reference_id", sa.Uuid()),
        sa.Column("secret_reference_version_id", sa.Uuid()),
        sa.Column("delegated_credential_link_id", sa.Uuid()),
        sa.Column("status", sa.String(64), nullable=False),
        sa.Column("failure_reason", sa.Text()),
        sa.Column("safe_summary", sa.JSON(), nullable=False),
        sa.Column("configured_by_principal_id", sa.String(255)),
        sa.Column("configured_at", sa.DateTime(timezone=True)),
        sa.Column("last_checked_at", sa.DateTime(timezone=True)),
        sa.Column("audit_record_id", sa.Uuid()),
    )
    op.create_index(
        "ix_skill_installation_credentials_installation_requirement",
        "skill_installation_credentials",
        ["skill_installation_id", "requirement_key"],
        unique=True,
    )

    op.create_table(
        "skill_installation_tests",
        sa.Column("skill_installation_test_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "skill_installation_id",
            sa.Uuid(),
            sa.ForeignKey("skill_installations.skill_installation_id"),
            nullable=False,
        ),
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), nullable=False
        ),
        sa.Column(
            "skill_package_version_id",
            sa.Uuid(),
            sa.ForeignKey("skill_package_versions.skill_package_version_id"),
            nullable=False,
        ),
        sa.Column("installation_version", sa.Integer(), nullable=False),
        sa.Column("fixture_key", sa.String(128), nullable=False),
        sa.Column("test_run_id", sa.String(128), nullable=False),
        sa.Column("idempotency_key", sa.String(255), nullable=False),
        sa.Column("runner_status", sa.String(64), nullable=False),
        sa.Column("outcome", sa.String(64), nullable=False),
        sa.Column("credential_readiness_summary", sa.JSON(), nullable=False),
        sa.Column("policy_decision_summary", sa.JSON(), nullable=False),
        sa.Column("failure_reasons", sa.JSON(), nullable=False),
        sa.Column("safe_output_summary", sa.JSON(), nullable=False),
        sa.Column(
            "evidence_artifact_id", sa.Uuid(), sa.ForeignKey("artifacts.artifact_id")
        ),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("duration_ms", sa.Integer()),
        sa.Column("trace_id", sa.String(128)),
        sa.Column("audit_record_id", sa.Uuid()),
    )
    op.create_index(
        "ix_skill_installation_tests_installation_idempotency",
        "skill_installation_tests",
        ["skill_installation_id", "idempotency_key"],
        unique=True,
    )
    op.create_index(
        "ix_skill_installation_tests_tenant_run",
        "skill_installation_tests",
        ["tenant_id", "test_run_id"],
    )

    op.create_table(
        "skill_quarantine_decisions",
        sa.Column("quarantine_decision_id", sa.Uuid(), primary_key=True),
        sa.Column("target_type", sa.String(64), nullable=False),
        sa.Column("target_id", sa.String(128), nullable=False),
        sa.Column("state", sa.String(64), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("actor_principal_id", sa.String(255), nullable=False),
        sa.Column("blocks_new_installs", sa.Boolean(), nullable=False),
        sa.Column("blocks_readiness", sa.Boolean(), nullable=False),
        sa.Column("blocks_bindings", sa.Boolean(), nullable=False),
        sa.Column("blocks_runtime", sa.Boolean(), nullable=False),
        sa.Column("safe_summary", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True)),
    )
    op.create_index(
        "ix_skill_quarantine_decisions_target",
        "skill_quarantine_decisions",
        ["target_type", "target_id"],
    )

    op.create_table(
        "skill_audit_records",
        sa.Column("skill_audit_record_id", sa.Uuid(), primary_key=True),
        sa.Column("event_type", sa.String(128), nullable=False),
        sa.Column("actor_principal_id", sa.String(255), nullable=False),
        sa.Column("outcome", sa.String(64), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column("skill_package_id", sa.Uuid()),
        sa.Column("skill_package_version_id", sa.Uuid()),
        sa.Column("skill_installation_id", sa.Uuid()),
        sa.Column("package_slug", sa.String(128)),
        sa.Column("package_version", sa.String(64)),
        sa.Column("safe_summary", sa.JSON(), nullable=False),
        sa.Column("redaction_metadata", sa.JSON(), nullable=False),
        sa.Column("trace_id", sa.String(128)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_skill_audit_records_package",
        "skill_audit_records",
        ["package_slug", "package_version"],
    )
    op.create_index(
        "ix_skill_audit_records_tenant_created",
        "skill_audit_records",
        ["tenant_id", "created_at"],
    )
    op.create_index(
        "ix_skill_audit_records_installation",
        "skill_audit_records",
        ["skill_installation_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_skill_audit_records_installation", table_name="skill_audit_records"
    )
    op.drop_index(
        "ix_skill_audit_records_tenant_created", table_name="skill_audit_records"
    )
    op.drop_index("ix_skill_audit_records_package", table_name="skill_audit_records")
    op.drop_table("skill_audit_records")
    op.drop_index(
        "ix_skill_quarantine_decisions_target",
        table_name="skill_quarantine_decisions",
    )
    op.drop_table("skill_quarantine_decisions")
    op.drop_index(
        "ix_skill_installation_tests_tenant_run",
        table_name="skill_installation_tests",
    )
    op.drop_index(
        "ix_skill_installation_tests_installation_idempotency",
        table_name="skill_installation_tests",
    )
    op.drop_table("skill_installation_tests")
    op.drop_index(
        "ix_skill_installation_credentials_installation_requirement",
        table_name="skill_installation_credentials",
    )
    op.drop_table("skill_installation_credentials")
    op.drop_index(
        "ix_skill_installations_tenant_state",
        table_name="skill_installations",
    )
    op.drop_index(
        "ix_skill_installations_tenant_slug_version",
        table_name="skill_installations",
    )
    op.drop_table("skill_installations")
    op.drop_index(
        "ix_skill_package_tenant_grants_version_tenant",
        table_name="skill_package_tenant_grants",
    )
    op.drop_table("skill_package_tenant_grants")
    op.drop_index(
        "ix_skill_package_versions_slug_semver",
        table_name="skill_package_versions",
    )
    op.drop_index(
        "ix_skill_package_versions_package_semver",
        table_name="skill_package_versions",
    )
    op.drop_table("skill_package_versions")
    op.drop_index("ix_skill_packages_slug", table_name="skill_packages")
    op.drop_table("skill_packages")
