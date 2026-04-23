"""workflow registry schema

Revision ID: 0003_workflow_registry
Revises: 0002_auth_access_control
Create Date: 2026-04-23 00:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0003_workflow_registry"
down_revision = "0002_auth_access_control"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "workflow_lineages",
        sa.Column(
            "workflow_lineage_id",
            sa.Uuid(),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("scope_type", sa.String(length=32), nullable=False),
        sa.Column(
            "tenant_id",
            sa.Uuid(),
            sa.ForeignKey("tenants.tenant_id"),
            nullable=True,
        ),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "workflow_kind",
            sa.Enum(
                "main_workflow",
                "subworkflow",
                name="workflowkind",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "drafting",
                "published",
                "archived",
                name="workflowlineagestatus",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("latest_published_version_id", sa.Uuid(), nullable=True),
        sa.Column(
            "created_by_principal_id",
            sa.Uuid(),
            sa.ForeignKey("principal_identities.principal_identity_id"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("scope_type", "tenant_id", "slug"),
    )
    op.create_table(
        "workflow_draft_revisions",
        sa.Column(
            "workflow_draft_revision_id",
            sa.Uuid(),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("workflow_draft_id", sa.Uuid(), nullable=False),
        sa.Column("revision_number", sa.Integer(), nullable=False),
        sa.Column("authoring_document_json", sa.JSON(), nullable=False),
        sa.Column("document_sha256", sa.String(length=64), nullable=False),
        sa.Column("change_summary", sa.Text(), nullable=True),
        sa.Column(
            "created_by_principal_id",
            sa.Uuid(),
            sa.ForeignKey("principal_identities.principal_identity_id"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("workflow_draft_id", "revision_number"),
    )
    op.create_table(
        "workflow_drafts",
        sa.Column("workflow_draft_id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column(
            "workflow_lineage_id",
            sa.Uuid(),
            sa.ForeignKey("workflow_lineages.workflow_lineage_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("scope_type", sa.String(length=32), nullable=False),
        sa.Column(
            "tenant_id",
            sa.Uuid(),
            sa.ForeignKey("tenants.tenant_id"),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "active",
                "published_source",
                "archived",
                "replaced",
                name="workflowdraftstatus",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("current_revision_number", sa.Integer(), nullable=False),
        sa.Column("latest_revision_id", sa.Uuid(), nullable=True),
        sa.Column("created_from_version_id", sa.Uuid(), nullable=True),
        sa.Column(
            "created_by_principal_id",
            sa.Uuid(),
            sa.ForeignKey("principal_identities.principal_identity_id"),
            nullable=False,
        ),
        sa.Column(
            "last_edited_by_principal_id",
            sa.Uuid(),
            sa.ForeignKey("principal_identities.principal_identity_id"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["latest_revision_id"],
            ["workflow_draft_revisions.workflow_draft_revision_id"],
        ),
    )
    op.create_table(
        "validation_results",
        sa.Column("validation_result_id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column(
            "workflow_draft_revision_id",
            sa.Uuid(),
            sa.ForeignKey(
                "workflow_draft_revisions.workflow_draft_revision_id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column("rule_set_version", sa.String(length=64), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "passed",
                "failed",
                "superseded",
                name="validationresultstatus",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("blocking_issue_count", sa.Integer(), nullable=False),
        sa.Column("advisory_issue_count", sa.Integer(), nullable=False),
        sa.Column("findings_json", sa.JSON(), nullable=False),
        sa.Column(
            "report_artifact_id",
            sa.Uuid(),
            sa.ForeignKey("artifacts.artifact_id"),
            nullable=True,
        ),
        sa.Column(
            "executed_by_principal_id",
            sa.Uuid(),
            sa.ForeignKey("principal_identities.principal_identity_id"),
            nullable=False,
        ),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "workflow_version_bundles",
        sa.Column(
            "workflow_version_bundle_id",
            sa.Uuid(),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "workflow_lineage_id",
            sa.Uuid(),
            sa.ForeignKey("workflow_lineages.workflow_lineage_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("scope_type", sa.String(length=32), nullable=False),
        sa.Column(
            "tenant_id",
            sa.Uuid(),
            sa.ForeignKey("tenants.tenant_id"),
            nullable=True,
        ),
        sa.Column("version_sequence", sa.Integer(), nullable=False),
        sa.Column("display_version", sa.String(length=32), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "published",
                "hidden",
                "retired",
                name="workflowversionstatus",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "published_from_draft_id",
            sa.Uuid(),
            sa.ForeignKey("workflow_drafts.workflow_draft_id"),
            nullable=False,
        ),
        sa.Column(
            "published_from_revision_id",
            sa.Uuid(),
            sa.ForeignKey("workflow_draft_revisions.workflow_draft_revision_id"),
            nullable=False,
        ),
        sa.Column(
            "validation_result_id",
            sa.Uuid(),
            sa.ForeignKey("validation_results.validation_result_id"),
            nullable=True,
        ),
        sa.Column("previous_version_bundle_id", sa.Uuid(), nullable=True),
        sa.Column(
            "compiled_bundle_artifact_id",
            sa.Uuid(),
            sa.ForeignKey("artifacts.artifact_id"),
            nullable=True,
        ),
        sa.Column("compiled_bundle_digest", sa.String(length=64), nullable=True),
        sa.Column("compiler_version", sa.String(length=32), nullable=True),
        sa.Column("summary_json", sa.JSON(), nullable=False),
        sa.Column(
            "published_by_principal_id",
            sa.Uuid(),
            sa.ForeignKey("principal_identities.principal_identity_id"),
            nullable=False,
        ),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("workflow_lineage_id", "version_sequence"),
    )
    op.create_table(
        "registry_sharing_grants",
        sa.Column(
            "registry_sharing_grant_id",
            sa.Uuid(),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "workflow_version_bundle_id",
            sa.Uuid(),
            sa.ForeignKey(
                "workflow_version_bundles.workflow_version_bundle_id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column(
            "grantee_tenant_id",
            sa.Uuid(),
            sa.ForeignKey("tenants.tenant_id"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "active",
                "revoked",
                name="registrysharinggrantstatus",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "granted_by_principal_id",
            sa.Uuid(),
            sa.ForeignKey("principal_identities.principal_identity_id"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("workflow_version_bundle_id", "grantee_tenant_id"),
    )


def downgrade() -> None:
    op.drop_table("registry_sharing_grants")
    op.drop_table("workflow_version_bundles")
    op.drop_table("validation_results")
    op.drop_table("workflow_drafts")
    op.drop_table("workflow_draft_revisions")
    op.drop_table("workflow_lineages")
