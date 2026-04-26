"""model skill routing schema

Revision ID: 0007_model_skill_routing
Revises: 0006_user_interaction_channels
Create Date: 2026-04-26 00:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0007_model_skill_routing"
down_revision = "0006_user_interaction_channels"
branch_labels = None
depends_on = None


def _version_columns(*, include_step: bool = True) -> list[sa.Column]:
    columns = [
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), nullable=False
        ),
        sa.Column("workflow_lineage_id", sa.Uuid()),
        sa.Column("workflow_version_bundle_id", sa.Uuid()),
        sa.Column("agent_key", sa.String(128)),
    ]
    if include_step:
        columns.append(sa.Column("step_key", sa.String(128)))
    columns.extend(
        [
            sa.Column("scope_hash", sa.String(64), nullable=False),
            sa.Column("status", sa.String(32), nullable=False),
            sa.Column("version_sequence", sa.Integer(), nullable=False),
            sa.Column("previous_version_id", sa.Uuid()),
            sa.Column(
                "created_by_principal_id",
                sa.Uuid(),
                sa.ForeignKey("principal_identities.principal_identity_id"),
                nullable=False,
            ),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("activation_reason", sa.Text(), nullable=False),
            sa.Column("redacted_summary", sa.JSON(), nullable=False),
        ]
    )
    return columns


def upgrade() -> None:
    op.create_table(
        "model_provider_catalog_entries",
        sa.Column("model_provider_entry_id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column("provider_key", sa.String(64), nullable=False),
        sa.Column("model_id", sa.String(128), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("capabilities", sa.JSON(), nullable=False),
        sa.Column("cost_metadata", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("retired_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_model_provider_entries_tenant_provider_model",
        "model_provider_catalog_entries",
        ["tenant_id", "provider_key", "model_id"],
        unique=True,
    )
    op.create_table(
        "model_routing_versions",
        sa.Column("model_routing_version_id", sa.Uuid(), primary_key=True),
        sa.Column("scope_type", sa.String(32), nullable=False),
        *_version_columns(),
        sa.Column(
            "model_provider_entry_id",
            sa.Uuid(),
            sa.ForeignKey("model_provider_catalog_entries.model_provider_entry_id"),
            nullable=False,
        ),
        sa.Column("routing_parameters", sa.JSON(), nullable=False),
        sa.Column("effective_from", sa.DateTime(timezone=True)),
        sa.Column("effective_until", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "prompt_reference_versions",
        sa.Column("prompt_reference_version_id", sa.Uuid(), primary_key=True),
        sa.Column("scope_type", sa.String(32), nullable=False),
        *_version_columns(),
        sa.Column("prompt_id", sa.Uuid(), nullable=False),
        sa.Column("prompt_version_id", sa.Uuid(), nullable=False),
        sa.Column("prompt_digest", sa.String(128), nullable=False),
    )
    op.create_table(
        "skill_binding_versions",
        sa.Column("skill_binding_version_id", sa.Uuid(), primary_key=True),
        *_version_columns(include_step=False),
        sa.Column("skill_slug", sa.String(128), nullable=False),
        sa.Column("skill_version", sa.String(64), nullable=False),
        sa.Column("allowed_contexts", sa.JSON(), nullable=False),
        sa.Column("runtime_ref_constraints", sa.JSON(), nullable=False),
    )
    op.create_table(
        "allowed_tool_policy_versions",
        sa.Column("allowed_tool_policy_version_id", sa.Uuid(), primary_key=True),
        *_version_columns(),
        sa.Column("skill_slug", sa.String(128)),
        sa.Column("tool_id", sa.String(128), nullable=False),
        sa.Column("allowed_action_categories", sa.JSON(), nullable=False),
        sa.Column("constraints", sa.JSON(), nullable=False),
    )
    op.create_table(
        "outbound_domain_policy_versions",
        sa.Column("outbound_domain_policy_version_id", sa.Uuid(), primary_key=True),
        *_version_columns(),
        sa.Column("tool_id", sa.String(128), nullable=False),
        sa.Column("action_category", sa.String(64)),
        sa.Column("allowed_domain_patterns", sa.JSON(), nullable=False),
        sa.Column("allowed_schemes", sa.JSON(), nullable=False),
        sa.Column("allowed_ports", sa.JSON(), nullable=False),
    )
    op.create_table(
        "model_skill_secret_reference_versions",
        sa.Column("secret_reference_version_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), nullable=False
        ),
        sa.Column("scope_hash", sa.String(64), nullable=False),
        sa.Column("secret_reference_id", sa.String(255), nullable=False),
        sa.Column("provider_key", sa.String(64), nullable=False),
        sa.Column("external_reference", sa.String(512), nullable=False),
        sa.Column("allowed_scopes", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("version_sequence", sa.Integer(), nullable=False),
        sa.Column("previous_version_id", sa.Uuid()),
        sa.Column(
            "created_by_principal_id",
            sa.Uuid(),
            sa.ForeignKey("principal_identities.principal_identity_id"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("activation_reason", sa.Text(), nullable=False),
        sa.Column("rotation_metadata", sa.JSON(), nullable=False),
        sa.Column("redacted_summary", sa.JSON(), nullable=False),
    )
    op.create_table(
        "tool_credential_requirement_versions",
        sa.Column(
            "tool_credential_requirement_version_id", sa.Uuid(), primary_key=True
        ),
        *_version_columns(),
        sa.Column("tool_id", sa.String(128), nullable=False),
        sa.Column("action_category", sa.String(64)),
        sa.Column("credential_kind", sa.String(64), nullable=False),
        sa.Column("secret_reference_version_id", sa.Uuid()),
        sa.Column("delegated_credential_link_id", sa.Uuid()),
        sa.Column("allowed_credential_scope", sa.JSON(), nullable=False),
        sa.Column("expiry_policy", sa.JSON(), nullable=False),
    )
    op.create_table(
        "active_configuration_pointers",
        sa.Column("active_configuration_pointer_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), nullable=False
        ),
        sa.Column("config_kind", sa.String(64), nullable=False),
        sa.Column("scope_hash", sa.String(64), nullable=False),
        sa.Column("scope_selectors", sa.JSON(), nullable=False),
        sa.Column("active_version_id", sa.Uuid(), nullable=False),
        sa.Column(
            "activated_by_principal_id",
            sa.Uuid(),
            sa.ForeignKey("principal_identities.principal_identity_id"),
            nullable=False,
        ),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("activation_reason", sa.Text(), nullable=False),
        sa.Column("expected_previous_version_id", sa.Uuid()),
    )
    op.create_index(
        "ix_active_configuration_pointer_singleton",
        "active_configuration_pointers",
        ["tenant_id", "config_kind", "scope_hash"],
        unique=True,
    )
    op.create_table(
        "resolved_execution_configurations",
        sa.Column("resolved_execution_configuration_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), nullable=False
        ),
        sa.Column("workflow_run_id", sa.Uuid(), nullable=False),
        sa.Column("run_bundle_id", sa.Uuid(), nullable=False),
        sa.Column("bundle_digest", sa.String(128), nullable=False),
        sa.Column("workflow_version_bundle_id", sa.Uuid(), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_by_principal_id", sa.Uuid()),
        sa.Column("model_routing_version_ids", sa.JSON(), nullable=False),
        sa.Column("prompt_reference_version_ids", sa.JSON(), nullable=False),
        sa.Column("skill_binding_version_ids", sa.JSON(), nullable=False),
        sa.Column("allowed_tool_policy_version_ids", sa.JSON(), nullable=False),
        sa.Column("outbound_domain_policy_version_ids", sa.JSON(), nullable=False),
        sa.Column("secret_reference_version_ids", sa.JSON(), nullable=False),
        sa.Column("credential_requirement_version_ids", sa.JSON(), nullable=False),
        sa.Column("resolution_digest", sa.String(64), nullable=False),
        sa.Column("trace_id", sa.String(128)),
        sa.Column("redacted_summary", sa.JSON(), nullable=False),
    )
    op.create_index(
        "ix_resolved_execution_configuration_run",
        "resolved_execution_configurations",
        ["tenant_id", "workflow_run_id"],
        unique=True,
    )
    op.create_table(
        "runtime_policy_decisions",
        sa.Column("runtime_policy_decision_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), nullable=False
        ),
        sa.Column("workflow_run_id", sa.Uuid(), nullable=False),
        sa.Column("run_step_id", sa.Uuid()),
        sa.Column("run_bundle_id", sa.Uuid()),
        sa.Column("agent_key", sa.String(128)),
        sa.Column("step_key", sa.String(128)),
        sa.Column("decision_category", sa.String(64), nullable=False),
        sa.Column("requested_resource", sa.String(255), nullable=False),
        sa.Column("requested_action", sa.String(128)),
        sa.Column("destination_host", sa.String(255)),
        sa.Column("outcome", sa.String(16), nullable=False),
        sa.Column("denial_category", sa.String(64)),
        sa.Column("safe_reason", sa.Text(), nullable=False),
        sa.Column("evaluated_version_ids", sa.JSON(), nullable=False),
        sa.Column("winning_version_ids", sa.JSON(), nullable=False),
        sa.Column("source_scopes", sa.JSON(), nullable=False),
        sa.Column("idempotency_key", sa.String(128)),
        sa.Column("trace_id", sa.String(128)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("redacted_metadata", sa.JSON(), nullable=False),
    )
    op.create_index(
        "ix_runtime_policy_decisions_idempotency",
        "runtime_policy_decisions",
        ["tenant_id", "workflow_run_id", "decision_category", "idempotency_key"],
        unique=True,
    )
    op.create_table(
        "configuration_audit_records",
        sa.Column("configuration_audit_record_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), nullable=False
        ),
        sa.Column("actor_principal_id", sa.Uuid()),
        sa.Column("actor_role", sa.String(64)),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("config_kind", sa.String(64), nullable=False),
        sa.Column("affected_scope", sa.JSON(), nullable=False),
        sa.Column("prior_version_id", sa.Uuid()),
        sa.Column("new_version_id", sa.Uuid()),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("request_id", sa.String(128)),
        sa.Column("trace_id", sa.String(128)),
        sa.Column("redacted_diff_summary", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "configuration_rollback_records",
        sa.Column("configuration_rollback_record_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), nullable=False
        ),
        sa.Column("config_kind", sa.String(64), nullable=False),
        sa.Column("scope_hash", sa.String(64), nullable=False),
        sa.Column("from_version_id", sa.Uuid(), nullable=False),
        sa.Column("to_version_id", sa.Uuid(), nullable=False),
        sa.Column("actor_principal_id", sa.Uuid()),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("configuration_audit_record_id", sa.Uuid()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "run_configuration_migration_records",
        sa.Column("run_configuration_migration_record_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), nullable=False
        ),
        sa.Column("workflow_run_id", sa.Uuid(), nullable=False),
        sa.Column("from_resolution_digest", sa.String(64), nullable=False),
        sa.Column("to_resolution_digest", sa.String(64), nullable=False),
        sa.Column("old_version_ids", sa.JSON(), nullable=False),
        sa.Column("new_version_ids", sa.JSON(), nullable=False),
        sa.Column("compatibility_status", sa.String(64), nullable=False),
        sa.Column("approval_record_id", sa.Uuid()),
        sa.Column("actor_principal_id", sa.Uuid()),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("trace_id", sa.String(128)),
        sa.Column("redacted_summary", sa.JSON(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("run_configuration_migration_records")
    op.drop_table("configuration_rollback_records")
    op.drop_table("configuration_audit_records")
    op.drop_index(
        "ix_runtime_policy_decisions_idempotency", table_name="runtime_policy_decisions"
    )
    op.drop_table("runtime_policy_decisions")
    op.drop_index(
        "ix_resolved_execution_configuration_run",
        table_name="resolved_execution_configurations",
    )
    op.drop_table("resolved_execution_configurations")
    op.drop_index(
        "ix_active_configuration_pointer_singleton",
        table_name="active_configuration_pointers",
    )
    op.drop_table("active_configuration_pointers")
    op.drop_table("tool_credential_requirement_versions")
    op.drop_table("model_skill_secret_reference_versions")
    op.drop_table("outbound_domain_policy_versions")
    op.drop_table("allowed_tool_policy_versions")
    op.drop_table("skill_binding_versions")
    op.drop_table("prompt_reference_versions")
    op.drop_table("model_routing_versions")
    op.drop_index(
        "ix_model_provider_entries_tenant_provider_model",
        table_name="model_provider_catalog_entries",
    )
    op.drop_table("model_provider_catalog_entries")
