"""durable orchestration runtime schema

Revision ID: 0004_durable_runtime
Revises: 0003_workflow_registry
Create Date: 2026-04-24 00:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0004_durable_runtime"
down_revision = "0003_workflow_registry"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "runtime_execution_bundles",
        sa.Column("run_bundle_id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column("workflow_run_id", sa.Uuid(), nullable=False, unique=True),
        sa.Column(
            "published_workflow_version_id",
            sa.Uuid(),
            sa.ForeignKey("workflow_version_bundles.workflow_version_bundle_id"),
            nullable=False,
        ),
        sa.Column("bundle_digest", sa.String(64), nullable=False),
        sa.Column("workflow_version", sa.JSON(), nullable=False),
        sa.Column("subworkflow_versions", sa.JSON(), nullable=False),
        sa.Column("contract_versions", sa.JSON(), nullable=False),
        sa.Column("prompt_versions", sa.JSON(), nullable=False),
        sa.Column("model_config_versions", sa.JSON(), nullable=False),
        sa.Column("tool_policy_versions", sa.JSON(), nullable=False),
        sa.Column("retry_policy", sa.JSON(), nullable=False),
        sa.Column("checkpoint_policy", sa.JSON(), nullable=False),
        sa.Column("approval_timeout_policy", sa.JSON(), nullable=False),
        sa.Column("child_cancellation_policy", sa.String(64), nullable=False),
        sa.Column("compiled_graph_ref", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "runtime_workflow_runs",
        sa.Column("workflow_run_id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column("scope_type", sa.String(32), nullable=False),
        sa.Column("initiating_principal_id", sa.String(128), nullable=False),
        sa.Column(
            "run_bundle_id",
            sa.Uuid(),
            sa.ForeignKey("runtime_execution_bundles.run_bundle_id"),
            nullable=False,
        ),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("current_step_id", sa.Uuid()),
        sa.Column("current_checkpoint_id", sa.String(128)),
        sa.Column("pause_reason", sa.String(255)),
        sa.Column("terminal_reason", sa.Text()),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.Column("trace_id", sa.String(64), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "runtime_run_steps",
        sa.Column("run_step_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "workflow_run_id",
            sa.Uuid(),
            sa.ForeignKey("runtime_workflow_runs.workflow_run_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column("step_key", sa.String(128), nullable=False),
        sa.Column("step_type", sa.String(32), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("attempt", sa.Integer(), nullable=False),
        sa.Column("max_attempts", sa.Integer(), nullable=False),
        sa.Column("next_retry_at", sa.DateTime(timezone=True)),
        sa.Column("input_ref", sa.JSON()),
        sa.Column("output_ref", sa.JSON()),
        sa.Column("error_ref", sa.JSON()),
        sa.Column("checkpoint_before_id", sa.String(128)),
        sa.Column("checkpoint_after_id", sa.String(128)),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("workflow_run_id", "step_key", "attempt"),
    )
    op.create_table(
        "runtime_worker_leases",
        sa.Column("worker_lease_id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column(
            "workflow_run_id",
            sa.Uuid(),
            sa.ForeignKey("runtime_workflow_runs.workflow_run_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "run_step_id", sa.Uuid(), sa.ForeignKey("runtime_run_steps.run_step_id")
        ),
        sa.Column("worker_id", sa.String(128), nullable=False),
        sa.Column("lease_status", sa.String(32), nullable=False),
        sa.Column("claimed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_renewed_at", sa.DateTime(timezone=True)),
        sa.Column("released_at", sa.DateTime(timezone=True)),
        sa.Column("claim_attempt", sa.Integer(), nullable=False),
    )
    op.create_table(
        "runtime_checkpoint_refs",
        sa.Column("runtime_checkpoint_ref_id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column(
            "workflow_run_id",
            sa.Uuid(),
            sa.ForeignKey("runtime_workflow_runs.workflow_run_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("run_step_id", sa.Uuid()),
        sa.Column("langgraph_thread_id", sa.String(128), nullable=False),
        sa.Column("langgraph_checkpoint_id", sa.String(128), nullable=False),
        sa.Column("checkpoint_kind", sa.String(64), nullable=False),
        sa.Column("bundle_digest", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("retention_expires_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "runtime_handoff_envelopes",
        sa.Column("handoff_envelope_id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column(
            "workflow_run_id",
            sa.Uuid(),
            sa.ForeignKey("runtime_workflow_runs.workflow_run_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("sender_step_id", sa.Uuid(), nullable=False),
        sa.Column("receiver_step_key", sa.String(128), nullable=False),
        sa.Column("contract_id", sa.String(128), nullable=False),
        sa.Column("contract_version", sa.String(64), nullable=False),
        sa.Column("contract_digest", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("payload_hash", sa.String(64), nullable=False),
        sa.Column("payload_ref", sa.JSON(), nullable=False),
        sa.Column("validation_errors", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("validated_at", sa.DateTime(timezone=True)),
        sa.Column("consumed_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "runtime_side_effect_intents",
        sa.Column("side_effect_intent_id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column(
            "workflow_run_id",
            sa.Uuid(),
            sa.ForeignKey("runtime_workflow_runs.workflow_run_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("run_step_id", sa.Uuid(), nullable=False),
        sa.Column("intent_kind", sa.String(64), nullable=False),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("tool_policy_ref", sa.String(255), nullable=False),
        sa.Column("delegated_credential_ref", sa.String(255)),
        sa.Column("request_ref", sa.JSON()),
        sa.Column("result_ref", sa.JSON()),
        sa.Column("error_ref", sa.JSON()),
        sa.Column("compensation_hook_ref", sa.String(255)),
        sa.Column("executed_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "tenant_id", "workflow_run_id", "run_step_id", "idempotency_key"
        ),
    )
    op.create_table(
        "runtime_approval_gates",
        sa.Column("approval_gate_id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column(
            "workflow_run_id",
            sa.Uuid(),
            sa.ForeignKey("runtime_workflow_runs.workflow_run_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("run_step_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("approval_key", sa.String(128), nullable=False),
        sa.Column("requested_action", sa.JSON(), nullable=False),
        sa.Column("approver_policy", sa.JSON(), nullable=False),
        sa.Column("timeout_behavior", sa.JSON(), nullable=False),
        sa.Column("decision_id", sa.Uuid()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("decided_at", sa.DateTime(timezone=True)),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "runtime_approval_decisions",
        sa.Column("approval_decision_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "approval_gate_id",
            sa.Uuid(),
            sa.ForeignKey(
                "runtime_approval_gates.approval_gate_id", ondelete="CASCADE"
            ),
            nullable=False,
        ),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column("principal_id", sa.String(128), nullable=False),
        sa.Column("decision", sa.String(32), nullable=False),
        sa.Column("decision_payload_hash", sa.String(64), nullable=False),
        sa.Column("decision_payload_ref", sa.JSON()),
        sa.Column("accepted", sa.Boolean(), nullable=False),
        sa.Column("rejection_reason", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "runtime_run_lineage",
        sa.Column("run_lineage_id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column("parent_run_id", sa.Uuid(), nullable=False),
        sa.Column("parent_step_id", sa.Uuid(), nullable=False),
        sa.Column("child_run_id", sa.Uuid(), nullable=False),
        sa.Column("relationship_reason", sa.String(64), nullable=False),
        sa.Column("join_policy", sa.String(64), nullable=False),
        sa.Column("child_cancellation_policy", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "runtime_timeline_events",
        sa.Column("runtime_timeline_event_id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column("workflow_run_id", sa.Uuid(), nullable=False),
        sa.Column("run_step_id", sa.Uuid()),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("severity", sa.String(32), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("trace_id", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "runtime_retention_policies",
        sa.Column("runtime_retention_policy_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), unique=True
        ),
        sa.Column("checkpoint_retention_days", sa.Integer(), nullable=False),
        sa.Column("run_payload_ref_retention_days", sa.Integer(), nullable=False),
        sa.Column("audit_retention", sa.String(32), nullable=False),
        sa.Column("lineage_retention", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    for table_name in (
        "runtime_retention_policies",
        "runtime_timeline_events",
        "runtime_run_lineage",
        "runtime_approval_decisions",
        "runtime_approval_gates",
        "runtime_side_effect_intents",
        "runtime_handoff_envelopes",
        "runtime_checkpoint_refs",
        "runtime_worker_leases",
        "runtime_run_steps",
        "runtime_workflow_runs",
        "runtime_execution_bundles",
    ):
        op.drop_table(table_name)
