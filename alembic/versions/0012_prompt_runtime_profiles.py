"""prompt runtime profiles schema

Revision ID: 0012_prompt_runtime_profiles
Revises: 0011_model_provider_gateway
Create Date: 2026-04-28 00:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0012_prompt_runtime_profiles"
down_revision = "0011_model_provider_gateway"
branch_labels = None
depends_on = None


def _timestamps() -> tuple[sa.Column[sa.DateTime], sa.Column[sa.DateTime]]:
    return (
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )


def upgrade() -> None:
    op.create_table(
        "prompt_lineages",
        sa.Column("prompt_lineage_id", sa.Uuid(), primary_key=True),
        sa.Column("scope_type", sa.String(32), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column("slug", sa.String(128), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("purpose", sa.String(500), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("latest_draft_id", sa.Uuid()),
        sa.Column("latest_published_prompt_version_id", sa.Uuid()),
        sa.Column("created_by_principal_id", sa.String(128), nullable=False),
        *_timestamps(),
        sa.CheckConstraint(
            "(scope_type = 'platform' AND tenant_id IS NULL) OR "
            "(scope_type = 'tenant' AND tenant_id IS NOT NULL)",
            name="ck_prompt_lineages_scope_tenant",
        ),
    )
    op.create_index(
        "ix_prompt_lineages_scope_slug",
        "prompt_lineages",
        ["scope_type", "tenant_id", "slug"],
        unique=True,
    )
    op.create_index("ix_prompt_lineages_status", "prompt_lineages", ["status"])
    op.create_table(
        "prompt_drafts",
        sa.Column("prompt_draft_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "prompt_lineage_id",
            sa.Uuid(),
            sa.ForeignKey("prompt_lineages.prompt_lineage_id"),
            nullable=False,
        ),
        sa.Column("scope_type", sa.String(32), nullable=False),
        sa.Column("tenant_id", sa.Uuid()),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("current_revision_number", sa.Integer(), nullable=False),
        sa.Column("latest_revision_id", sa.Uuid()),
        sa.Column("created_from_prompt_version_id", sa.Uuid()),
        sa.Column("last_validation_result_id", sa.Uuid()),
        sa.Column("created_by_principal_id", sa.String(128), nullable=False),
        sa.Column("last_edited_by_principal_id", sa.String(128), nullable=False),
        *_timestamps(),
    )
    op.create_index(
        "ix_prompt_drafts_lineage_status",
        "prompt_drafts",
        ["prompt_lineage_id", "status"],
    )
    op.create_table(
        "prompt_draft_revisions",
        sa.Column("prompt_draft_revision_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "prompt_draft_id",
            sa.Uuid(),
            sa.ForeignKey("prompt_drafts.prompt_draft_id"),
            nullable=False,
        ),
        sa.Column("revision_number", sa.Integer(), nullable=False),
        sa.Column("prompt_title", sa.String(255), nullable=False),
        sa.Column("purpose", sa.String(500), nullable=False),
        sa.Column("usage_notes", sa.Text(), nullable=False),
        sa.Column("template_content", sa.Text(), nullable=False),
        sa.Column("template_content_sha256", sa.String(64), nullable=False),
        sa.Column("variable_declarations_json", sa.JSON(), nullable=False),
        sa.Column("fixture_value_sets_json", sa.JSON(), nullable=False),
        sa.Column("safe_summary_json", sa.JSON(), nullable=False),
        sa.Column("created_by_principal_id", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "prompt_draft_id",
            "revision_number",
            name="uq_prompt_draft_revisions_draft_number",
        ),
    )
    op.create_index(
        "ix_prompt_draft_revisions_draft",
        "prompt_draft_revisions",
        ["prompt_draft_id", "revision_number"],
    )
    op.create_table(
        "prompt_validation_results",
        sa.Column("prompt_validation_result_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "prompt_draft_revision_id",
            sa.Uuid(),
            sa.ForeignKey("prompt_draft_revisions.prompt_draft_revision_id"),
            nullable=False,
        ),
        sa.Column("rule_set_version", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("blocking_issue_count", sa.Integer(), nullable=False),
        sa.Column("advisory_issue_count", sa.Integer(), nullable=False),
        sa.Column("findings_json", sa.JSON(), nullable=False),
        sa.Column("template_content_sha256", sa.String(64), nullable=False),
        sa.Column("validated_fixture_set_ids", sa.JSON(), nullable=False),
        sa.Column("executed_by_principal_id", sa.String(128), nullable=False),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_prompt_validation_results_revision",
        "prompt_validation_results",
        ["prompt_draft_revision_id", "executed_at"],
    )
    op.create_table(
        "prompt_render_tests",
        sa.Column("prompt_render_test_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "prompt_draft_revision_id",
            sa.Uuid(),
            sa.ForeignKey("prompt_draft_revisions.prompt_draft_revision_id"),
            nullable=False,
        ),
        sa.Column("fixture_set_id", sa.String(128), nullable=False),
        sa.Column("viewer_principal_id", sa.String(128), nullable=False),
        sa.Column("outcome", sa.String(32), nullable=False),
        sa.Column("missing_variables", sa.JSON(), nullable=False),
        sa.Column("redaction_categories", sa.JSON(), nullable=False),
        sa.Column("rendered_preview_sha256", sa.String(64)),
        sa.Column("safe_preview_summary", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "prompt_versions",
        sa.Column("prompt_version_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "prompt_lineage_id",
            sa.Uuid(),
            sa.ForeignKey("prompt_lineages.prompt_lineage_id"),
            nullable=False,
        ),
        sa.Column("scope_type", sa.String(32), nullable=False),
        sa.Column("tenant_id", sa.Uuid()),
        sa.Column("version_sequence", sa.Integer(), nullable=False),
        sa.Column("display_version", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("published_from_draft_id", sa.Uuid(), nullable=False),
        sa.Column("published_from_revision_id", sa.Uuid(), nullable=False),
        sa.Column("validation_result_id", sa.Uuid(), nullable=False),
        sa.Column("template_content", sa.Text(), nullable=False),
        sa.Column("template_content_sha256", sa.String(64), nullable=False),
        sa.Column("variable_declarations_json", sa.JSON(), nullable=False),
        sa.Column("purpose", sa.String(500), nullable=False),
        sa.Column("usage_notes", sa.Text(), nullable=False),
        sa.Column("safe_summary_json", sa.JSON(), nullable=False),
        sa.Column("published_by_principal_id", sa.String(128), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("publication_reason", sa.String(500), nullable=False),
        sa.Column("retired_by_principal_id", sa.String(128)),
        sa.Column("retired_at", sa.DateTime(timezone=True)),
        sa.Column("retirement_reason", sa.String(500)),
        sa.UniqueConstraint(
            "prompt_lineage_id",
            "version_sequence",
            name="uq_prompt_versions_lineage_sequence",
        ),
    )
    op.create_index(
        "ix_prompt_versions_lineage_sequence",
        "prompt_versions",
        ["prompt_lineage_id", "version_sequence"],
    )
    op.create_index(
        "ix_prompt_versions_scope_status",
        "prompt_versions",
        ["scope_type", "tenant_id", "status"],
    )
    op.create_table(
        "tenant_prompt_version_grants",
        sa.Column("tenant_prompt_version_grant_id", sa.Uuid(), primary_key=True),
        sa.Column("prompt_version_id", sa.Uuid(), nullable=False),
        sa.Column("grantee_tenant_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("granted_by_principal_id", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_by_principal_id", sa.String(128)),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("reason", sa.String(500), nullable=False),
    )
    op.create_index(
        "ix_tenant_prompt_version_grants_active",
        "tenant_prompt_version_grants",
        ["prompt_version_id", "grantee_tenant_id", "status"],
    )
    op.create_table(
        "prompt_audit_records",
        sa.Column("prompt_audit_record_id", sa.Uuid(), primary_key=True),
        sa.Column("prompt_lineage_id", sa.Uuid()),
        sa.Column("prompt_version_id", sa.Uuid()),
        sa.Column("agent_runtime_profile_id", sa.Uuid()),
        sa.Column("agent_profile_version_id", sa.Uuid()),
        sa.Column("tenant_id", sa.Uuid()),
        sa.Column("actor_principal_id", sa.String(128), nullable=False),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("outcome", sa.String(32), nullable=False),
        sa.Column("safe_summary_json", sa.JSON(), nullable=False),
        sa.Column("trace_id", sa.String(128)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_prompt_audit_records_scope_time",
        "prompt_audit_records",
        ["tenant_id", "created_at"],
    )
    op.create_index(
        "ix_prompt_audit_records_lineage",
        "prompt_audit_records",
        ["prompt_lineage_id"],
    )
    op.create_table(
        "agent_runtime_profiles",
        sa.Column("agent_runtime_profile_id", sa.Uuid(), primary_key=True),
        sa.Column("scope_type", sa.String(32), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column("agent_key", sa.String(128), nullable=False),
        sa.Column("agent_kind", sa.String(32), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("purpose", sa.String(500), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("latest_draft_id", sa.Uuid()),
        sa.Column("active_profile_version_id", sa.Uuid()),
        sa.Column("created_by_principal_id", sa.String(128), nullable=False),
        *_timestamps(),
        sa.CheckConstraint(
            "(scope_type = 'platform' AND tenant_id IS NULL) OR "
            "(scope_type = 'tenant' AND tenant_id IS NOT NULL)",
            name="ck_agent_runtime_profiles_scope_tenant",
        ),
    )
    op.create_index(
        "ix_agent_runtime_profiles_scope_key",
        "agent_runtime_profiles",
        ["scope_type", "tenant_id", "agent_kind", "agent_key"],
        unique=True,
    )
    op.create_table(
        "agent_profile_drafts",
        sa.Column("agent_profile_draft_id", sa.Uuid(), primary_key=True),
        sa.Column("agent_runtime_profile_id", sa.Uuid(), nullable=False),
        sa.Column("scope_type", sa.String(32), nullable=False),
        sa.Column("tenant_id", sa.Uuid()),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("current_revision_number", sa.Integer(), nullable=False),
        sa.Column("latest_revision_id", sa.Uuid()),
        sa.Column("created_from_profile_version_id", sa.Uuid()),
        sa.Column("last_validation_result_id", sa.Uuid()),
        sa.Column("created_by_principal_id", sa.String(128), nullable=False),
        sa.Column("last_edited_by_principal_id", sa.String(128), nullable=False),
        *_timestamps(),
    )
    op.create_index(
        "ix_agent_profile_drafts_profile_status",
        "agent_profile_drafts",
        ["agent_runtime_profile_id", "status"],
    )
    op.create_table(
        "agent_profile_draft_revisions",
        sa.Column("agent_profile_draft_revision_id", sa.Uuid(), primary_key=True),
        sa.Column("agent_profile_draft_id", sa.Uuid(), nullable=False),
        sa.Column("revision_number", sa.Integer(), nullable=False),
        sa.Column("agent_key", sa.String(128), nullable=False),
        sa.Column("agent_kind", sa.String(32), nullable=False),
        sa.Column("purpose", sa.String(500), nullable=False),
        sa.Column("prompt_references_json", sa.JSON(), nullable=False),
        sa.Column("model_routing_hints_json", sa.JSON(), nullable=False),
        sa.Column("memory_scope_policy_json", sa.JSON(), nullable=False),
        sa.Column("skill_requirements_json", sa.JSON(), nullable=False),
        sa.Column("tool_policy_expectations_json", sa.JSON(), nullable=False),
        sa.Column("output_contract_expectations_json", sa.JSON(), nullable=False),
        sa.Column("test_suite_requirements_json", sa.JSON(), nullable=False),
        sa.Column("safe_summary_json", sa.JSON(), nullable=False),
        sa.Column("created_by_principal_id", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "agent_profile_draft_id",
            "revision_number",
            name="uq_agent_profile_draft_revisions_draft_number",
        ),
    )
    op.create_index(
        "ix_agent_profile_draft_revisions_draft",
        "agent_profile_draft_revisions",
        ["agent_profile_draft_id", "revision_number"],
    )
    op.create_table(
        "agent_profile_validation_results",
        sa.Column("agent_profile_validation_result_id", sa.Uuid(), primary_key=True),
        sa.Column("agent_profile_draft_revision_id", sa.Uuid(), nullable=False),
        sa.Column("rule_set_version", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("blocking_issue_count", sa.Integer(), nullable=False),
        sa.Column("advisory_issue_count", sa.Integer(), nullable=False),
        sa.Column("findings_json", sa.JSON(), nullable=False),
        sa.Column("referenced_prompt_version_ids", sa.JSON(), nullable=False),
        sa.Column("referenced_model_routing_scope_ids", sa.JSON(), nullable=False),
        sa.Column("referenced_memory_policy_hash", sa.String(128)),
        sa.Column("referenced_skill_requirement_hash", sa.String(128)),
        sa.Column("executed_by_principal_id", sa.String(128), nullable=False),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_agent_profile_validation_results_revision",
        "agent_profile_validation_results",
        ["agent_profile_draft_revision_id", "executed_at"],
    )
    op.create_table(
        "agent_profile_versions",
        sa.Column("agent_profile_version_id", sa.Uuid(), primary_key=True),
        sa.Column("agent_runtime_profile_id", sa.Uuid(), nullable=False),
        sa.Column("scope_type", sa.String(32), nullable=False),
        sa.Column("tenant_id", sa.Uuid()),
        sa.Column("agent_key", sa.String(128), nullable=False),
        sa.Column("agent_kind", sa.String(32), nullable=False),
        sa.Column("version_sequence", sa.Integer(), nullable=False),
        sa.Column("display_version", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("activated_from_draft_id", sa.Uuid(), nullable=False),
        sa.Column("activated_from_revision_id", sa.Uuid(), nullable=False),
        sa.Column("validation_result_id", sa.Uuid(), nullable=False),
        sa.Column("purpose", sa.String(500), nullable=False),
        sa.Column("prompt_references_json", sa.JSON(), nullable=False),
        sa.Column("model_routing_hints_json", sa.JSON(), nullable=False),
        sa.Column("memory_scope_policy_json", sa.JSON(), nullable=False),
        sa.Column("skill_requirements_json", sa.JSON(), nullable=False),
        sa.Column("tool_policy_expectations_json", sa.JSON(), nullable=False),
        sa.Column("output_contract_expectations_json", sa.JSON(), nullable=False),
        sa.Column("test_suite_requirements_json", sa.JSON(), nullable=False),
        sa.Column("safe_summary_json", sa.JSON(), nullable=False),
        sa.Column("activated_by_principal_id", sa.String(128), nullable=False),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("activation_reason", sa.String(500), nullable=False),
        sa.Column("retired_by_principal_id", sa.String(128)),
        sa.Column("retired_at", sa.DateTime(timezone=True)),
        sa.Column("retirement_reason", sa.String(500)),
        sa.UniqueConstraint(
            "agent_runtime_profile_id",
            "version_sequence",
            name="uq_agent_profile_versions_profile_sequence",
        ),
    )
    op.create_index(
        "ix_agent_profile_versions_scope_key",
        "agent_profile_versions",
        ["scope_type", "tenant_id", "agent_kind", "agent_key", "status"],
    )
    op.create_table(
        "tenant_profile_version_grants",
        sa.Column("tenant_profile_version_grant_id", sa.Uuid(), primary_key=True),
        sa.Column("agent_profile_version_id", sa.Uuid(), nullable=False),
        sa.Column("grantee_tenant_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("granted_by_principal_id", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_by_principal_id", sa.String(128)),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("reason", sa.String(500), nullable=False),
    )
    op.create_index(
        "ix_tenant_profile_version_grants_active",
        "tenant_profile_version_grants",
        ["agent_profile_version_id", "grantee_tenant_id", "status"],
    )
    op.create_table(
        "active_agent_profile_pointers",
        sa.Column("active_agent_profile_pointer_id", sa.Uuid(), primary_key=True),
        sa.Column("scope_type", sa.String(32), nullable=False),
        sa.Column("tenant_id", sa.Uuid()),
        sa.Column("agent_kind", sa.String(32), nullable=False),
        sa.Column("agent_key", sa.String(128), nullable=False),
        sa.Column("active_profile_version_id", sa.Uuid(), nullable=False),
        sa.Column("activated_by_principal_id", sa.String(128), nullable=False),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("activation_reason", sa.Text(), nullable=False),
        sa.Column("expected_previous_version_id", sa.Uuid()),
    )
    op.create_index(
        "ix_active_agent_profile_pointer_lookup",
        "active_agent_profile_pointers",
        ["scope_type", "tenant_id", "agent_kind", "agent_key"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_active_agent_profile_pointer_lookup",
        table_name="active_agent_profile_pointers",
    )
    op.drop_table("active_agent_profile_pointers")
    op.drop_index(
        "ix_tenant_profile_version_grants_active",
        table_name="tenant_profile_version_grants",
    )
    op.drop_table("tenant_profile_version_grants")
    op.drop_index(
        "ix_agent_profile_versions_scope_key", table_name="agent_profile_versions"
    )
    op.drop_table("agent_profile_versions")
    op.drop_index(
        "ix_agent_profile_validation_results_revision",
        table_name="agent_profile_validation_results",
    )
    op.drop_table("agent_profile_validation_results")
    op.drop_index(
        "ix_agent_profile_draft_revisions_draft",
        table_name="agent_profile_draft_revisions",
    )
    op.drop_table("agent_profile_draft_revisions")
    op.drop_index(
        "ix_agent_profile_drafts_profile_status", table_name="agent_profile_drafts"
    )
    op.drop_table("agent_profile_drafts")
    op.drop_index(
        "ix_agent_runtime_profiles_scope_key", table_name="agent_runtime_profiles"
    )
    op.drop_table("agent_runtime_profiles")
    op.drop_index("ix_prompt_audit_records_lineage", table_name="prompt_audit_records")
    op.drop_index(
        "ix_prompt_audit_records_scope_time", table_name="prompt_audit_records"
    )
    op.drop_table("prompt_audit_records")
    op.drop_index(
        "ix_tenant_prompt_version_grants_active",
        table_name="tenant_prompt_version_grants",
    )
    op.drop_table("tenant_prompt_version_grants")
    op.drop_index("ix_prompt_versions_scope_status", table_name="prompt_versions")
    op.drop_index("ix_prompt_versions_lineage_sequence", table_name="prompt_versions")
    op.drop_table("prompt_versions")
    op.drop_table("prompt_render_tests")
    op.drop_index(
        "ix_prompt_validation_results_revision", table_name="prompt_validation_results"
    )
    op.drop_table("prompt_validation_results")
    op.drop_index(
        "ix_prompt_draft_revisions_draft", table_name="prompt_draft_revisions"
    )
    op.drop_table("prompt_draft_revisions")
    op.drop_index("ix_prompt_drafts_lineage_status", table_name="prompt_drafts")
    op.drop_table("prompt_drafts")
    op.drop_index("ix_prompt_lineages_status", table_name="prompt_lineages")
    op.drop_index("ix_prompt_lineages_scope_slug", table_name="prompt_lineages")
    op.drop_table("prompt_lineages")
