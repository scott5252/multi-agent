"""token usage cost analytics

Revision ID: 0016_token_usage_cost_analytics
Revises: 0015_agent_workflow_test_bench
Create Date: 2026-05-03 00:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0016_token_usage_cost_analytics"
down_revision = "0015_agent_workflow_test_bench"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "llm_pricing_versions",
        sa.Column("llm_pricing_version_id", sa.Uuid(), primary_key=True),
        sa.Column("provider_key", sa.String(128), nullable=False),
        sa.Column("model_id", sa.String(128), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("input_token_micros", sa.Integer(), nullable=False),
        sa.Column("output_token_micros", sa.Integer(), nullable=False),
        sa.Column("cached_token_micros", sa.Integer(), nullable=False),
        sa.Column("reasoning_token_micros", sa.Integer(), nullable=False),
        sa.Column("billable_unit_micros", sa.Integer()),
        sa.Column("calculation_method", sa.String(64), nullable=False),
        sa.Column("effective_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("effective_to", sa.DateTime(timezone=True)),
        sa.Column("source_note", sa.String(255), nullable=False),
        sa.Column("created_by_principal_id", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_llm_pricing_versions_lookup",
        "llm_pricing_versions",
        ["provider_key", "model_id", "currency", "effective_from"],
    )

    op.create_table(
        "llm_usage_events",
        sa.Column("llm_usage_event_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), nullable=False
        ),
        sa.Column("principal_id", sa.String(255)),
        sa.Column("workflow_run_id", sa.Uuid()),
        sa.Column("workflow_run_step_id", sa.Uuid()),
        sa.Column("workflow_lineage_id", sa.Uuid()),
        sa.Column("workflow_version_id", sa.Uuid()),
        sa.Column("agent_key", sa.String(128)),
        sa.Column("sub_agent_key", sa.String(128)),
        sa.Column("provider_key", sa.String(128), nullable=False),
        sa.Column("provider_connection_id", sa.Uuid()),
        sa.Column("model_id", sa.String(128), nullable=False),
        sa.Column("prompt_version_id", sa.Uuid()),
        sa.Column("agent_profile_version_id", sa.Uuid()),
        sa.Column("execution_mode", sa.String(64), nullable=False),
        sa.Column("operation_identity", sa.String(255)),
        sa.Column("idempotency_key", sa.String(255)),
        sa.Column("trace_id", sa.String(128)),
        sa.Column("input_tokens", sa.Integer()),
        sa.Column("output_tokens", sa.Integer()),
        sa.Column("cached_tokens", sa.Integer()),
        sa.Column("reasoning_tokens", sa.Integer()),
        sa.Column("total_tokens", sa.Integer()),
        sa.Column("provider_billable_units", sa.Integer()),
        sa.Column("input_status", sa.String(64), nullable=False),
        sa.Column("output_status", sa.String(64), nullable=False),
        sa.Column("cached_status", sa.String(64), nullable=False),
        sa.Column("reasoning_status", sa.String(64), nullable=False),
        sa.Column("total_status", sa.String(64), nullable=False),
        sa.Column("billable_status", sa.String(64), nullable=False),
        sa.Column("cost_status", sa.String(64), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("estimated_cost_micros", sa.Integer()),
        sa.Column(
            "pricing_version_id",
            sa.Uuid(),
            sa.ForeignKey("llm_pricing_versions.llm_pricing_version_id"),
        ),
        sa.Column("usage_status", sa.String(64), nullable=False),
        sa.Column("source_gateway_attempt_id", sa.Uuid()),
        sa.Column("safe_attribution", sa.JSON(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_llm_usage_events_tenant_time",
        "llm_usage_events",
        ["tenant_id", "recorded_at"],
    )
    op.create_index(
        "ix_llm_usage_events_provider_model",
        "llm_usage_events",
        ["provider_key", "model_id"],
    )
    op.create_index(
        "ix_llm_usage_events_workflow",
        "llm_usage_events",
        ["tenant_id", "workflow_lineage_id", "workflow_version_id"],
    )
    op.create_index(
        "ix_llm_usage_events_agent",
        "llm_usage_events",
        ["tenant_id", "agent_key", "sub_agent_key"],
    )
    op.create_index(
        "ix_llm_usage_events_principal",
        "llm_usage_events",
        ["tenant_id", "principal_id"],
    )
    op.create_index(
        "ix_llm_usage_events_idempotency",
        "llm_usage_events",
        ["tenant_id", "idempotency_key", "provider_key", "model_id"],
        unique=True,
    )

    op.create_table(
        "llm_usage_rollups",
        sa.Column("llm_usage_rollup_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), nullable=False
        ),
        sa.Column("bucket_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("bucket_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("bucket_granularity", sa.String(32), nullable=False),
        sa.Column("provider_key", sa.String(128)),
        sa.Column("model_id", sa.String(128)),
        sa.Column("workflow_lineage_id", sa.Uuid()),
        sa.Column("agent_key", sa.String(128)),
        sa.Column("sub_agent_key", sa.String(128)),
        sa.Column("prompt_version_id", sa.Uuid()),
        sa.Column("execution_mode", sa.String(64)),
        sa.Column("principal_id", sa.String(255)),
        sa.Column("event_count", sa.Integer(), nullable=False),
        sa.Column("total_tokens", sa.Integer(), nullable=False),
        sa.Column("estimated_cost_micros", sa.Integer(), nullable=False),
        sa.Column("estimated_event_count", sa.Integer(), nullable=False),
        sa.Column("confirmed_event_count", sa.Integer(), nullable=False),
        sa.Column("computed_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_llm_usage_rollups_bucket",
        "llm_usage_rollups",
        ["tenant_id", "bucket_start", "bucket_end"],
    )

    op.create_table(
        "usage_export_requests",
        sa.Column("usage_export_request_id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column("requested_by_principal_id", sa.String(255), nullable=False),
        sa.Column("scope_type", sa.String(64), nullable=False),
        sa.Column("filters", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(64), nullable=False),
        sa.Column("row_count", sa.Integer(), nullable=False),
        sa.Column("artifact_uri", sa.String(512)),
        sa.Column("artifact_sha256", sa.String(128)),
        sa.Column("artifact_size_bytes", sa.Integer()),
        sa.Column("denial_reason", sa.String(255)),
        sa.Column("failure_reason", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
    )
    op.create_index(
        "ix_usage_export_requests_scope",
        "usage_export_requests",
        ["scope_type", "tenant_id", "created_at"],
    )

    op.create_table(
        "usage_reconciliation_records",
        sa.Column("usage_reconciliation_record_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "llm_usage_event_id",
            sa.Uuid(),
            sa.ForeignKey("llm_usage_events.llm_usage_event_id"),
            nullable=False,
        ),
        sa.Column("source", sa.String(128), nullable=False),
        sa.Column("previous_values", sa.JSON(), nullable=False),
        sa.Column("confirmed_values", sa.JSON(), nullable=False),
        sa.Column("reconciled_by_principal_id", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_usage_reconciliation_event",
        "usage_reconciliation_records",
        ["llm_usage_event_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_usage_reconciliation_event",
        table_name="usage_reconciliation_records",
    )
    op.drop_table("usage_reconciliation_records")
    op.drop_index("ix_usage_export_requests_scope", table_name="usage_export_requests")
    op.drop_table("usage_export_requests")
    op.drop_index("ix_llm_usage_rollups_bucket", table_name="llm_usage_rollups")
    op.drop_table("llm_usage_rollups")
    op.drop_index("ix_llm_usage_events_idempotency", table_name="llm_usage_events")
    op.drop_index("ix_llm_usage_events_principal", table_name="llm_usage_events")
    op.drop_index("ix_llm_usage_events_agent", table_name="llm_usage_events")
    op.drop_index("ix_llm_usage_events_workflow", table_name="llm_usage_events")
    op.drop_index("ix_llm_usage_events_provider_model", table_name="llm_usage_events")
    op.drop_index("ix_llm_usage_events_tenant_time", table_name="llm_usage_events")
    op.drop_table("llm_usage_events")
    op.drop_index("ix_llm_pricing_versions_lookup", table_name="llm_pricing_versions")
    op.drop_table("llm_pricing_versions")
