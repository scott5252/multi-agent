"""production audit debugging schema

Revision ID: 0008_production_audit_debugging
Revises: 0007_model_skill_routing
Create Date: 2026-04-26 00:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0008_production_audit_debugging"
down_revision = "0007_model_skill_routing"
branch_labels = None
depends_on = None


def _tenant_column() -> sa.Column:
    return sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"))


def _timestamps() -> tuple[sa.Column, sa.Column]:
    return (
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
    )


def upgrade() -> None:
    op.create_table(
        "audit_timeline_events",
        sa.Column("timeline_event_id", sa.Uuid(), primary_key=True),
        _tenant_column(),
        sa.Column("workflow_run_id", sa.Uuid(), nullable=False),
        sa.Column("parent_run_id", sa.Uuid()),
        sa.Column("run_step_id", sa.Uuid()),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("event_category", sa.String(64), nullable=False),
        sa.Column("run_status_after", sa.String(64), nullable=False),
        sa.Column("origin_type", sa.String(64), nullable=False),
        sa.Column("origin_ref", sa.String(255)),
        sa.Column("actor_principal_id", sa.String(128)),
        sa.Column("trace_id", sa.String(128), nullable=False),
        sa.Column("correlation_id", sa.String(128)),
        sa.Column("source_event_id", sa.String(255), nullable=False),
        *_timestamps(),
        sa.Column("criticality", sa.String(64), nullable=False),
        sa.Column("safe_summary", sa.Text(), nullable=False),
        sa.Column("safe_details", sa.JSON(), nullable=False),
        sa.Column("classification_version", sa.String(64), nullable=False),
        sa.Column("supersedes_event_id", sa.Uuid()),
        sa.UniqueConstraint("tenant_id", "workflow_run_id", "sequence"),
        sa.UniqueConstraint(
            "tenant_id",
            "workflow_run_id",
            "event_category",
            "source_event_id",
            name="uq_audit_timeline_idempotency",
        ),
    )
    op.create_index(
        "ix_audit_timeline_tenant_run_time",
        "audit_timeline_events",
        ["tenant_id", "workflow_run_id", "occurred_at"],
    )
    op.create_index(
        "ix_audit_timeline_tenant_category_time",
        "audit_timeline_events",
        ["tenant_id", "event_category", "occurred_at"],
    )
    op.create_table(
        "audit_runtime_trace_records",
        sa.Column("trace_record_id", sa.Uuid(), primary_key=True),
        _tenant_column(),
        sa.Column("workflow_run_id", sa.Uuid(), nullable=False),
        sa.Column(
            "timeline_event_id",
            sa.Uuid(),
            sa.ForeignKey(
                "audit_timeline_events.timeline_event_id", ondelete="CASCADE"
            ),
            nullable=False,
        ),
        sa.Column("run_step_id", sa.Uuid()),
        sa.Column("trace_type", sa.String(64), nullable=False),
        sa.Column("trace_id", sa.String(128), nullable=False),
        sa.Column("correlation_id", sa.String(128)),
        sa.Column("status", sa.String(64), nullable=False),
        sa.Column("outcome", sa.String(64), nullable=False),
        sa.Column("duration_ms", sa.Integer()),
        sa.Column("policy_outcome", sa.String(64), nullable=False),
        sa.Column("subject_ref", sa.String(255)),
        sa.Column("safe_input_summary", sa.JSON(), nullable=False),
        sa.Column("safe_output_summary", sa.JSON(), nullable=False),
        sa.Column("safe_error_summary", sa.JSON(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        *_timestamps(),
    )
    op.create_index(
        "ix_audit_trace_tenant_run",
        "audit_runtime_trace_records",
        ["tenant_id", "workflow_run_id"],
    )
    op.create_index(
        "ix_audit_trace_timeline", "audit_runtime_trace_records", ["timeline_event_id"]
    )
    op.create_index(
        "ix_audit_trace_type",
        "audit_runtime_trace_records",
        ["tenant_id", "trace_type"],
    )
    op.create_table(
        "audit_agent_handoff_traces",
        sa.Column(
            "trace_record_id",
            sa.Uuid(),
            sa.ForeignKey(
                "audit_runtime_trace_records.trace_record_id", ondelete="CASCADE"
            ),
            primary_key=True,
        ),
        sa.Column("source_agent_key", sa.String(128), nullable=False),
        sa.Column("destination_agent_key", sa.String(128), nullable=False),
        sa.Column("handoff_reason", sa.String(255), nullable=False),
        sa.Column("handoff_outcome", sa.String(64), nullable=False),
        sa.Column("handoff_contract_ref", sa.String(255)),
        sa.Column("payload_schema_ref", sa.String(255)),
        sa.Column("payload_digest", sa.String(128)),
        sa.Column("safe_payload_metadata", sa.JSON(), nullable=False),
    )
    op.create_table(
        "audit_contract_validation_traces",
        sa.Column(
            "trace_record_id",
            sa.Uuid(),
            sa.ForeignKey(
                "audit_runtime_trace_records.trace_record_id", ondelete="CASCADE"
            ),
            primary_key=True,
        ),
        sa.Column("contract_name", sa.String(128), nullable=False),
        sa.Column("contract_version", sa.String(64), nullable=False),
        sa.Column("validation_target", sa.String(128), nullable=False),
        sa.Column("validation_outcome", sa.String(64), nullable=False),
        sa.Column("error_count", sa.Integer(), nullable=False),
        sa.Column("safe_error_summary", sa.JSON(), nullable=False),
        sa.Column("prioritized_error_codes", sa.JSON(), nullable=False),
    )
    op.create_table(
        "audit_memory_write_traces",
        sa.Column(
            "trace_record_id",
            sa.Uuid(),
            sa.ForeignKey(
                "audit_runtime_trace_records.trace_record_id", ondelete="CASCADE"
            ),
            primary_key=True,
        ),
        sa.Column("memory_scope_id", sa.Uuid()),
        sa.Column("write_intent", sa.String(128), nullable=False),
        sa.Column("requested_version_ref", sa.String(255)),
        sa.Column("effective_version_ref", sa.String(255)),
        sa.Column("projection_ref", sa.String(255)),
        sa.Column("write_outcome", sa.String(64), nullable=False),
        sa.Column("superseded_by_ref", sa.String(255)),
        sa.Column("safe_memory_summary", sa.JSON(), nullable=False),
    )
    op.create_table(
        "audit_tool_usage_traces",
        sa.Column(
            "trace_record_id",
            sa.Uuid(),
            sa.ForeignKey(
                "audit_runtime_trace_records.trace_record_id", ondelete="CASCADE"
            ),
            primary_key=True,
        ),
        sa.Column("tool_id", sa.String(128), nullable=False),
        sa.Column("tool_name", sa.String(128), nullable=False),
        sa.Column("action_category", sa.String(128), nullable=False),
        sa.Column("policy_decision_id", sa.String(255)),
        sa.Column("policy_outcome", sa.String(64), nullable=False),
        sa.Column("execution_outcome", sa.String(64), nullable=False),
        sa.Column("duration_ms", sa.Integer()),
        sa.Column("destination_category", sa.String(128)),
        sa.Column("safe_input_summary", sa.JSON(), nullable=False),
        sa.Column("safe_output_summary", sa.JSON(), nullable=False),
        sa.Column("safe_failure_reason", sa.Text()),
    )
    op.create_table(
        "audit_model_selection_traces",
        sa.Column(
            "trace_record_id",
            sa.Uuid(),
            sa.ForeignKey(
                "audit_runtime_trace_records.trace_record_id", ondelete="CASCADE"
            ),
            primary_key=True,
        ),
        sa.Column("model_provider_key", sa.String(128), nullable=False),
        sa.Column("model_id", sa.String(128), nullable=False),
        sa.Column("selection_source", sa.String(128), nullable=False),
        sa.Column("model_routing_version_id", sa.Uuid()),
        sa.Column("prompt_reference_version_id", sa.Uuid()),
        sa.Column("workflow_bundle_ref", sa.String(255)),
        sa.Column("agent_key", sa.String(128)),
        sa.Column("step_key", sa.String(128)),
        sa.Column("selection_outcome", sa.String(64), nullable=False),
        sa.Column("safe_trace_metadata", sa.JSON(), nullable=False),
    )
    op.create_table(
        "audit_notification_delivery_traces",
        sa.Column(
            "trace_record_id",
            sa.Uuid(),
            sa.ForeignKey(
                "audit_runtime_trace_records.trace_record_id", ondelete="CASCADE"
            ),
            primary_key=True,
        ),
        sa.Column("notification_delivery_attempt_id", sa.Uuid()),
        sa.Column("destination_category", sa.String(128), nullable=False),
        sa.Column("delivery_status", sa.String(64), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column("latest_attempt_at", sa.DateTime(timezone=True)),
        sa.Column("safe_failure_reason", sa.Text()),
        sa.Column("triggering_timeline_event_id", sa.Uuid()),
        sa.Column("provider_correlation_ref", sa.String(255)),
    )
    op.create_table(
        "audit_capture_gaps",
        sa.Column("capture_gap_id", sa.Uuid(), primary_key=True),
        _tenant_column(),
        sa.Column("workflow_run_id", sa.Uuid(), nullable=False),
        sa.Column("timeline_event_id", sa.Uuid()),
        sa.Column("trace_id", sa.String(128), nullable=False),
        sa.Column("gap_type", sa.String(128), nullable=False),
        sa.Column("affected_trace_type", sa.String(64)),
        sa.Column("criticality", sa.String(64), nullable=False),
        sa.Column("safe_reason", sa.Text(), nullable=False),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("recovery_status", sa.String(64), nullable=False),
    )
    op.create_index(
        "ix_audit_capture_gaps_tenant_run",
        "audit_capture_gaps",
        ["tenant_id", "workflow_run_id"],
    )
    op.create_table(
        "audit_version_bundle_snapshots",
        sa.Column("version_bundle_snapshot_id", sa.Uuid(), primary_key=True),
        _tenant_column(),
        sa.Column("workflow_run_id", sa.Uuid(), nullable=False),
        sa.Column("workflow_lineage_id", sa.Uuid()),
        sa.Column("workflow_version_bundle_id", sa.Uuid()),
        sa.Column("execution_bundle_id", sa.Uuid()),
        sa.Column("bundle_digest", sa.String(128), nullable=False),
        sa.Column("workflow_version", sa.JSON(), nullable=False),
        sa.Column("contract_version_refs", sa.JSON(), nullable=False),
        sa.Column("prompt_version_refs", sa.JSON(), nullable=False),
        sa.Column("model_config_version_refs", sa.JSON(), nullable=False),
        sa.Column("tool_policy_version_refs", sa.JSON(), nullable=False),
        sa.Column("activation_state_at_acceptance", sa.String(64), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("migration_record_refs", sa.JSON(), nullable=False),
        sa.Column("safe_summary", sa.JSON(), nullable=False),
        sa.UniqueConstraint("tenant_id", "workflow_run_id"),
    )
    op.create_table(
        "audit_run_lineage_links",
        sa.Column("run_lineage_link_id", sa.Uuid(), primary_key=True),
        _tenant_column(),
        sa.Column("source_run_id", sa.Uuid(), nullable=False),
        sa.Column("target_run_id", sa.Uuid(), nullable=False),
        sa.Column("relationship_type", sa.String(64), nullable=False),
        sa.Column("source_timeline_event_id", sa.Uuid()),
        sa.Column("source_trace_record_id", sa.Uuid()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(64), nullable=False),
        sa.Column("safe_reason", sa.Text(), nullable=False),
    )
    op.create_index(
        "ix_audit_lineage_tenant_source",
        "audit_run_lineage_links",
        ["tenant_id", "source_run_id"],
    )
    op.create_table(
        "audit_secret_access_records",
        sa.Column("secret_access_audit_record_id", sa.Uuid(), primary_key=True),
        _tenant_column(),
        sa.Column("workflow_run_id", sa.Uuid(), nullable=False),
        sa.Column("timeline_event_id", sa.Uuid()),
        sa.Column("trace_record_id", sa.Uuid()),
        sa.Column("requester_type", sa.String(64), nullable=False),
        sa.Column("requester_ref", sa.String(255), nullable=False),
        sa.Column("secret_reference_id", sa.String(255), nullable=False),
        sa.Column("secret_reference_version", sa.String(128)),
        sa.Column("credential_scope", sa.String(128)),
        sa.Column("policy_outcome", sa.String(64), nullable=False),
        sa.Column("access_outcome", sa.String(64), nullable=False),
        sa.Column("reason_code", sa.String(128)),
        sa.Column("safe_reason", sa.Text(), nullable=False),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("trace_id", sa.String(128), nullable=False),
    )
    op.create_index(
        "ix_audit_secret_access_tenant_run",
        "audit_secret_access_records",
        ["tenant_id", "workflow_run_id"],
    )
    op.create_table(
        "audit_inspection_access_events",
        sa.Column("inspection_access_audit_event_id", sa.Uuid(), primary_key=True),
        _tenant_column(),
        sa.Column("actor_principal_id", sa.String(128), nullable=False),
        sa.Column("actor_role", sa.String(64), nullable=False),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("target_run_id", sa.Uuid()),
        sa.Column("target_trace_record_id", sa.Uuid()),
        sa.Column("authorization_outcome", sa.String(64), nullable=False),
        sa.Column("denial_category", sa.String(128)),
        sa.Column("filters_digest", sa.String(128)),
        sa.Column("export_id", sa.Uuid()),
        sa.Column("trace_id", sa.String(128)),
        sa.Column("safe_metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_audit_inspection_tenant_target",
        "audit_inspection_access_events",
        ["tenant_id", "target_run_id", "created_at"],
    )
    op.create_table(
        "audit_debug_exports",
        sa.Column("debug_evidence_export_id", sa.Uuid(), primary_key=True),
        _tenant_column(),
        sa.Column("requested_by", sa.String(128), nullable=False),
        sa.Column("workflow_run_id", sa.Uuid(), nullable=False),
        sa.Column("lineage_scope", sa.String(64), nullable=False),
        sa.Column("recipient_scope", sa.String(64), nullable=False),
        sa.Column("redaction_profile", sa.String(64), nullable=False),
        sa.Column("status", sa.String(64), nullable=False),
        sa.Column("artifact_id", sa.Uuid()),
        sa.Column("artifact_ref", sa.String(512)),
        sa.Column("included_sections", sa.JSON(), nullable=False),
        sa.Column("excluded_sections", sa.JSON(), nullable=False),
        sa.Column("safe_failure_reason", sa.Text()),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
    )
    op.create_index(
        "ix_audit_debug_exports_tenant_run",
        "audit_debug_exports",
        ["tenant_id", "workflow_run_id"],
    )
    op.create_index(
        "ix_audit_debug_exports_status",
        "audit_debug_exports",
        ["tenant_id", "status"],
    )
    op.create_table(
        "audit_redaction_classification_records",
        sa.Column("redaction_classification_record_id", sa.Uuid(), primary_key=True),
        _tenant_column(),
        sa.Column("source_record_type", sa.String(64), nullable=False),
        sa.Column("source_record_id", sa.String(128), nullable=False),
        sa.Column("classification_version", sa.String(64), nullable=False),
        sa.Column("field_name", sa.String(128), nullable=False),
        sa.Column("sensitivity_label", sa.String(64), nullable=False),
        sa.Column("redaction_action", sa.String(64), nullable=False),
        sa.Column("viewer_role", sa.String(64), nullable=False),
        sa.Column("decision_reason", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_audit_redaction_source",
        "audit_redaction_classification_records",
        ["tenant_id", "source_record_type", "source_record_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_audit_redaction_source", table_name="audit_redaction_classification_records"
    )
    op.drop_table("audit_redaction_classification_records")
    op.drop_index("ix_audit_debug_exports_status", table_name="audit_debug_exports")
    op.drop_index("ix_audit_debug_exports_tenant_run", table_name="audit_debug_exports")
    op.drop_table("audit_debug_exports")
    op.drop_index(
        "ix_audit_inspection_tenant_target", table_name="audit_inspection_access_events"
    )
    op.drop_table("audit_inspection_access_events")
    op.drop_index(
        "ix_audit_secret_access_tenant_run", table_name="audit_secret_access_records"
    )
    op.drop_table("audit_secret_access_records")
    op.drop_index(
        "ix_audit_lineage_tenant_source", table_name="audit_run_lineage_links"
    )
    op.drop_table("audit_run_lineage_links")
    op.drop_table("audit_version_bundle_snapshots")
    op.drop_index("ix_audit_capture_gaps_tenant_run", table_name="audit_capture_gaps")
    op.drop_table("audit_capture_gaps")
    op.drop_table("audit_notification_delivery_traces")
    op.drop_table("audit_model_selection_traces")
    op.drop_table("audit_tool_usage_traces")
    op.drop_table("audit_memory_write_traces")
    op.drop_table("audit_contract_validation_traces")
    op.drop_table("audit_agent_handoff_traces")
    op.drop_index("ix_audit_trace_type", table_name="audit_runtime_trace_records")
    op.drop_index("ix_audit_trace_timeline", table_name="audit_runtime_trace_records")
    op.drop_index("ix_audit_trace_tenant_run", table_name="audit_runtime_trace_records")
    op.drop_table("audit_runtime_trace_records")
    op.drop_index(
        "ix_audit_timeline_tenant_category_time", table_name="audit_timeline_events"
    )
    op.drop_index(
        "ix_audit_timeline_tenant_run_time", table_name="audit_timeline_events"
    )
    op.drop_table("audit_timeline_events")
