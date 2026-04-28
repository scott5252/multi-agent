"""prompt runtime profiles v2 gateway operation identities

Revision ID: 0013_prp_v2_gateway_ops
Revises: 0012_prompt_runtime_profiles
Create Date: 2026-04-28 00:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0013_prp_v2_gateway_ops"
down_revision = "0012_prompt_runtime_profiles"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "gateway_operations",
        sa.Column("gateway_operation_id", sa.Uuid(), primary_key=True),
        sa.Column("operation_identity", sa.String(255), nullable=False),
        sa.Column("tenant_id", sa.Uuid()),
        sa.Column("workflow_run_id", sa.Uuid()),
        sa.Column("workflow_run_step_id", sa.Uuid()),
        sa.Column("test_bench_run_id", sa.Uuid()),
        sa.Column("workflow_validation_id", sa.Uuid()),
        sa.Column("trace_id", sa.String(128)),
        sa.Column("idempotency_key", sa.String(255), nullable=False),
        sa.Column("agent_profile_version_id", sa.Uuid()),
        sa.Column("prompt_version_ids", sa.JSON(), nullable=False),
        sa.Column("prompt_reference_version_ids", sa.JSON(), nullable=False),
        sa.Column("model_routing_provenance_json", sa.JSON(), nullable=False),
        sa.Column("provider_connection_id", sa.Uuid()),
        sa.Column("provider_model_definition_id", sa.Uuid()),
        sa.Column("model_provider_entry_id", sa.Uuid()),
        sa.Column("model_id", sa.String(128), nullable=False),
        sa.Column("status", sa.String(64), nullable=False),
        sa.Column("authoritative_attempt_id", sa.Uuid()),
        sa.Column("authoritative_outcome", sa.String(64)),
        sa.Column("normalized_error_category", sa.String(64), nullable=False),
        sa.Column("usage_available", sa.Boolean(), nullable=False),
        sa.Column("safe_summary_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
    )
    op.create_index(
        "ix_gateway_operations_identity",
        "gateway_operations",
        ["operation_identity"],
        unique=True,
    )
    op.create_index(
        "ix_gateway_operations_run",
        "gateway_operations",
        ["tenant_id", "workflow_run_id", "workflow_run_step_id"],
    )
    op.create_index(
        "ix_gateway_operations_provider",
        "gateway_operations",
        ["provider_connection_id", "model_id", "status"],
    )
    op.create_table(
        "gateway_physical_attempts",
        sa.Column("gateway_physical_attempt_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "gateway_operation_id",
            sa.Uuid(),
            sa.ForeignKey("gateway_operations.gateway_operation_id"),
            nullable=False,
        ),
        sa.Column("gateway_invocation_attempt_id", sa.Uuid()),
        sa.Column("physical_attempt_number", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("outcome", sa.String(64), nullable=False),
        sa.Column("normalized_error_category", sa.String(64), nullable=False),
        sa.Column("retry_category", sa.String(64), nullable=False),
        sa.Column("retry_decision_summary_json", sa.JSON(), nullable=False),
        sa.Column("retry_budget_snapshot_json", sa.JSON(), nullable=False),
        sa.Column("breaker_scope", sa.String(255)),
        sa.Column("breaker_decision_summary_json", sa.JSON(), nullable=False),
        sa.Column("provider_request_id_safe", sa.String(255)),
        sa.Column("usage_metadata_json", sa.JSON(), nullable=False),
        sa.Column("usage_available", sa.Boolean(), nullable=False),
        sa.Column("duplicate_suppressed", sa.Boolean(), nullable=False),
        sa.Column("recovered_from_attempt_id", sa.Uuid()),
        sa.Column("safe_audit_summary_json", sa.JSON(), nullable=False),
    )
    op.create_index(
        "ix_gateway_physical_attempts_operation_number",
        "gateway_physical_attempts",
        ["gateway_operation_id", "physical_attempt_number"],
        unique=True,
    )
    op.create_table(
        "provider_probe_operations",
        sa.Column("provider_probe_operation_id", sa.Uuid(), primary_key=True),
        sa.Column("operation_identity", sa.String(255), nullable=False),
        sa.Column(
            "provider_connection_id",
            sa.Uuid(),
            sa.ForeignKey("model_provider_connections.provider_connection_id"),
            nullable=False,
        ),
        sa.Column("provider_model_definition_id", sa.Uuid()),
        sa.Column("tenant_id", sa.Uuid()),
        sa.Column("actor_principal_id", sa.String(128), nullable=False),
        sa.Column("status", sa.String(64), nullable=False),
        sa.Column("rate_limit_scope_json", sa.JSON(), nullable=False),
        sa.Column("bounded_operation_decision_json", sa.JSON(), nullable=False),
        sa.Column("authoritative_test_result_id", sa.Uuid()),
        sa.Column("authoritative_outcome", sa.String(64)),
        sa.Column("normalized_reason", sa.String(64), nullable=False),
        sa.Column("safe_summary_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
    )
    op.create_index(
        "ix_provider_probe_operations_identity",
        "provider_probe_operations",
        ["actor_principal_id", "provider_connection_id", "operation_identity"],
        unique=True,
    )
    op.create_index(
        "ix_provider_probe_operations_status",
        "provider_probe_operations",
        ["provider_connection_id", "status"],
    )
    op.create_table(
        "catalog_sync_operations",
        sa.Column("catalog_sync_operation_id", sa.Uuid(), primary_key=True),
        sa.Column("operation_identity", sa.String(255), nullable=False),
        sa.Column(
            "provider_connection_id",
            sa.Uuid(),
            sa.ForeignKey("model_provider_connections.provider_connection_id"),
            nullable=False,
        ),
        sa.Column("tenant_id", sa.Uuid()),
        sa.Column("actor_principal_id", sa.String(128), nullable=False),
        sa.Column("status", sa.String(64), nullable=False),
        sa.Column("checkpoint_json", sa.JSON(), nullable=False),
        sa.Column("authoritative_result_json", sa.JSON(), nullable=False),
        sa.Column("last_attempt_id", sa.Uuid()),
        sa.Column("normalized_reason", sa.String(64), nullable=False),
        sa.Column("safe_summary_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
    )
    op.create_index(
        "ix_catalog_sync_operations_identity",
        "catalog_sync_operations",
        ["provider_connection_id", "operation_identity"],
        unique=True,
    )
    op.create_index(
        "ix_catalog_sync_operations_status",
        "catalog_sync_operations",
        ["provider_connection_id", "status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_catalog_sync_operations_status",
        table_name="catalog_sync_operations",
    )
    op.drop_index(
        "ix_catalog_sync_operations_identity",
        table_name="catalog_sync_operations",
    )
    op.drop_table("catalog_sync_operations")
    op.drop_index(
        "ix_provider_probe_operations_status",
        table_name="provider_probe_operations",
    )
    op.drop_index(
        "ix_provider_probe_operations_identity",
        table_name="provider_probe_operations",
    )
    op.drop_table("provider_probe_operations")
    op.drop_index(
        "ix_gateway_physical_attempts_operation_number",
        table_name="gateway_physical_attempts",
    )
    op.drop_table("gateway_physical_attempts")
    op.drop_index("ix_gateway_operations_provider", table_name="gateway_operations")
    op.drop_index("ix_gateway_operations_run", table_name="gateway_operations")
    op.drop_index("ix_gateway_operations_identity", table_name="gateway_operations")
    op.drop_table("gateway_operations")
