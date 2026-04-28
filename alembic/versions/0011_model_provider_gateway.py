"""model provider gateway schema

Revision ID: 0011_model_provider_gateway
Revises: 0010_admin_console_shell
Create Date: 2026-04-28 00:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0011_model_provider_gateway"
down_revision = "0010_admin_console_shell"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "model_provider_connections",
        sa.Column("provider_connection_id", sa.Uuid(), primary_key=True),
        sa.Column("provider_type", sa.String(64), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("base_url_safe", sa.String(512)),
        sa.Column("timeout_policy", sa.JSON(), nullable=False),
        sa.Column("visibility_mode", sa.String(64), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("health_state", sa.String(64), nullable=False),
        sa.Column("credential_secret_reference_ids", sa.JSON(), nullable=False),
        sa.Column("safe_metadata", sa.JSON(), nullable=False),
        sa.Column("allowlist_decision_hash", sa.String(128)),
        sa.Column("created_by_principal_id", sa.String(128), nullable=False),
        sa.Column("updated_by_principal_id", sa.String(128), nullable=False),
        sa.Column("deactivated_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_model_provider_connections_status",
        "model_provider_connections",
        ["active", "health_state"],
    )
    op.create_index(
        "ix_model_provider_connections_type",
        "model_provider_connections",
        ["provider_type"],
    )
    op.create_table(
        "provider_model_definitions",
        sa.Column("provider_model_definition_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "provider_connection_id",
            sa.Uuid(),
            sa.ForeignKey("model_provider_connections.provider_connection_id"),
            nullable=False,
        ),
        sa.Column("model_id", sa.String(128), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("capability_metadata", sa.JSON(), nullable=False),
        sa.Column("cost_metadata", sa.JSON(), nullable=False),
        sa.Column("default_parameters", sa.JSON(), nullable=False),
        sa.Column("available", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_provider_model_definitions_connection_model",
        "provider_model_definitions",
        ["provider_connection_id", "model_id"],
        unique=True,
    )
    op.create_table(
        "connection_tenant_visibility",
        sa.Column("connection_tenant_visibility_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "provider_connection_id",
            sa.Uuid(),
            sa.ForeignKey("model_provider_connections.provider_connection_id"),
            nullable=False,
        ),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column("visible", sa.Boolean(), nullable=False),
        sa.Column("created_by_principal_id", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
    )
    op.create_index(
        "ix_connection_tenant_visibility_scope",
        "connection_tenant_visibility",
        ["provider_connection_id", "tenant_id", "visible"],
    )
    op.create_table(
        "connection_test_results",
        sa.Column("connection_test_result_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "provider_connection_id",
            sa.Uuid(),
            sa.ForeignKey("model_provider_connections.provider_connection_id"),
            nullable=False,
        ),
        sa.Column(
            "provider_model_definition_id",
            sa.Uuid(),
            sa.ForeignKey("provider_model_definitions.provider_model_definition_id"),
        ),
        sa.Column("actor_principal_id", sa.String(128), nullable=False),
        sa.Column("source", sa.String(64), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("outcome", sa.String(64), nullable=False),
        sa.Column("normalized_reason", sa.String(64), nullable=False),
        sa.Column("tested_model_id", sa.String(128)),
        sa.Column("safe_diagnostic_summary", sa.String(500), nullable=False),
        sa.Column("safe_provider_request_id", sa.String(255)),
        sa.Column("http_status_class", sa.String(16)),
        sa.Column("timeout_policy", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_connection_test_results_latest",
        "connection_test_results",
        ["provider_connection_id", "completed_at"],
    )
    op.create_table(
        "connection_health_snapshots",
        sa.Column("connection_health_snapshot_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "provider_connection_id",
            sa.Uuid(),
            sa.ForeignKey("model_provider_connections.provider_connection_id"),
            nullable=False,
        ),
        sa.Column("health_state", sa.String(64), nullable=False),
        sa.Column(
            "latest_test_result_id",
            sa.Uuid(),
            sa.ForeignKey("connection_test_results.connection_test_result_id"),
        ),
        sa.Column("derived_reason", sa.String(255), nullable=False),
        sa.Column("derived_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("selectable", sa.Boolean(), nullable=False),
    )
    op.create_index(
        "ix_connection_health_snapshots_latest",
        "connection_health_snapshots",
        ["provider_connection_id", "derived_at"],
    )
    op.create_table(
        "catalog_sync_records",
        sa.Column("catalog_sync_record_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "provider_connection_id",
            sa.Uuid(),
            sa.ForeignKey("model_provider_connections.provider_connection_id"),
            nullable=False,
        ),
        sa.Column(
            "provider_model_definition_id",
            sa.Uuid(),
            sa.ForeignKey("provider_model_definitions.provider_model_definition_id"),
        ),
        sa.Column("model_provider_entry_id", sa.Uuid()),
        sa.Column("tenant_id", sa.Uuid()),
        sa.Column("sync_action", sa.String(64), nullable=False),
        sa.Column("outcome", sa.String(64), nullable=False),
        sa.Column("normalized_reason", sa.String(64), nullable=False),
        sa.Column("safe_summary", sa.String(500), nullable=False),
        sa.Column("actor_principal_id", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_catalog_sync_records_connection",
        "catalog_sync_records",
        ["provider_connection_id"],
    )
    op.create_table(
        "gateway_invocation_attempts",
        sa.Column("gateway_invocation_attempt_id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid()),
        sa.Column("workflow_run_id", sa.Uuid()),
        sa.Column("test_bench_run_id", sa.Uuid()),
        sa.Column("trace_id", sa.String(128)),
        sa.Column("idempotency_key", sa.String(255)),
        sa.Column("model_provider_entry_id", sa.Uuid()),
        sa.Column("provider_connection_id", sa.Uuid()),
        sa.Column("provider_model_definition_id", sa.Uuid()),
        sa.Column("provider_type", sa.String(64), nullable=False),
        sa.Column("model_id", sa.String(128), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("outcome", sa.String(64), nullable=False),
        sa.Column("normalized_error_category", sa.String(64), nullable=False),
        sa.Column("retry_attempt_number", sa.Integer(), nullable=False),
        sa.Column("retry_decision_summary", sa.JSON(), nullable=False),
        sa.Column("breaker_scope", sa.String(255)),
        sa.Column("breaker_decision_summary", sa.JSON(), nullable=False),
        sa.Column("usage_metadata", sa.JSON(), nullable=False),
        sa.Column("usage_available", sa.Boolean(), nullable=False),
        sa.Column("safe_audit_summary", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_gateway_invocation_attempts_tenant_time",
        "gateway_invocation_attempts",
        ["tenant_id", "created_at"],
    )
    op.create_index(
        "ix_gateway_invocation_attempts_run",
        "gateway_invocation_attempts",
        ["workflow_run_id", "test_bench_run_id"],
    )

    op.add_column(
        "model_provider_catalog_entries",
        sa.Column("provider_connection_id", sa.Uuid()),
    )
    op.add_column(
        "model_provider_catalog_entries",
        sa.Column("provider_model_definition_id", sa.Uuid()),
    )
    op.add_column(
        "model_provider_catalog_entries",
        sa.Column("health_state", sa.String(64), server_default="untested"),
    )
    op.add_column(
        "model_provider_catalog_entries",
        sa.Column("availability_status", sa.String(64), server_default="unavailable"),
    )
    op.add_column(
        "model_provider_catalog_entries",
        sa.Column("visibility_mode", sa.String(64), server_default="platform_default"),
    )
    op.add_column(
        "model_provider_catalog_entries",
        sa.Column("tenant_visibility_hash", sa.String(128)),
    )
    op.add_column(
        "model_provider_catalog_entries",
        sa.Column("last_synced_at", sa.DateTime(timezone=True)),
    )
    op.add_column(
        "model_provider_catalog_entries",
        sa.Column("gateway_governed", sa.Boolean(), server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("model_provider_catalog_entries", "gateway_governed")
    op.drop_column("model_provider_catalog_entries", "last_synced_at")
    op.drop_column("model_provider_catalog_entries", "tenant_visibility_hash")
    op.drop_column("model_provider_catalog_entries", "visibility_mode")
    op.drop_column("model_provider_catalog_entries", "availability_status")
    op.drop_column("model_provider_catalog_entries", "health_state")
    op.drop_column("model_provider_catalog_entries", "provider_model_definition_id")
    op.drop_column("model_provider_catalog_entries", "provider_connection_id")
    op.drop_index(
        "ix_gateway_invocation_attempts_run",
        table_name="gateway_invocation_attempts",
    )
    op.drop_index(
        "ix_gateway_invocation_attempts_tenant_time",
        table_name="gateway_invocation_attempts",
    )
    op.drop_table("gateway_invocation_attempts")
    op.drop_index(
        "ix_catalog_sync_records_connection",
        table_name="catalog_sync_records",
    )
    op.drop_table("catalog_sync_records")
    op.drop_index(
        "ix_connection_health_snapshots_latest",
        table_name="connection_health_snapshots",
    )
    op.drop_table("connection_health_snapshots")
    op.drop_index(
        "ix_connection_test_results_latest",
        table_name="connection_test_results",
    )
    op.drop_table("connection_test_results")
    op.drop_index(
        "ix_connection_tenant_visibility_scope",
        table_name="connection_tenant_visibility",
    )
    op.drop_table("connection_tenant_visibility")
    op.drop_index(
        "ix_provider_model_definitions_connection_model",
        table_name="provider_model_definitions",
    )
    op.drop_table("provider_model_definitions")
    op.drop_index(
        "ix_model_provider_connections_type",
        table_name="model_provider_connections",
    )
    op.drop_index(
        "ix_model_provider_connections_status",
        table_name="model_provider_connections",
    )
    op.drop_table("model_provider_connections")
