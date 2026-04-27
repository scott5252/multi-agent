"""reliability scale hardening schema

Revision ID: 0009_reliability_scale_hardening
Revises: 0008_production_audit_debugging
Create Date: 2026-04-26 00:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0009_reliability_scale_hardening"
down_revision = "0008_production_audit_debugging"
branch_labels = None
depends_on = None


def _tenant(nullable: bool = True) -> sa.Column:
    return sa.Column(
        "tenant_id",
        sa.Uuid(),
        sa.ForeignKey("tenants.tenant_id"),
        nullable=nullable,
    )


def upgrade() -> None:
    op.create_table(
        "reliability_policies",
        sa.Column("policy_id", sa.Uuid(), primary_key=True),
        _tenant(),
        sa.Column("scope_type", sa.String(64), nullable=False),
        sa.Column("scope_key", sa.String(255)),
        sa.Column("policy_version", sa.Integer(), nullable=False),
        sa.Column("settings", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(64), nullable=False),
        sa.Column("effective_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("retired_at", sa.DateTime(timezone=True)),
        sa.Column("created_by", sa.String(128), nullable=False),
        sa.Column("created_reason", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "tenant_id",
            "scope_type",
            "scope_key",
            "policy_version",
            name="uq_reliability_policy_scope_version",
        ),
    )
    op.create_index(
        "ix_reliability_policy_scope_active",
        "reliability_policies",
        ["tenant_id", "scope_type", "scope_key", "status"],
    )
    op.create_table(
        "reliability_capacity_snapshots",
        sa.Column("capacity_snapshot_id", sa.Uuid(), primary_key=True),
        sa.Column("snapshot_scope", sa.String(64), nullable=False),
        _tenant(),
        sa.Column("worker_pool", sa.String(128)),
        sa.Column("runnable_depth", sa.Integer(), nullable=False),
        sa.Column("delayed_depth", sa.Integer(), nullable=False),
        sa.Column("active_leases", sa.Integer(), nullable=False),
        sa.Column("recovery_backlog", sa.Integer(), nullable=False),
        sa.Column("retry_backlog", sa.Integer(), nullable=False),
        sa.Column("compensation_backlog", sa.Integer(), nullable=False),
        sa.Column("dead_letter_count", sa.Integer(), nullable=False),
        sa.Column("db_pool_wait_p95_ms", sa.Integer(), nullable=False),
        sa.Column("db_pool_in_use", sa.Integer(), nullable=False),
        sa.Column("db_pool_available", sa.Integer(), nullable=False),
        sa.Column("artifact_inflight", sa.Integer(), nullable=False),
        sa.Column("artifact_wait_p95_ms", sa.Integer(), nullable=False),
        sa.Column("open_breaker_count", sa.Integer(), nullable=False),
        sa.Column("fairness_debt_total", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_reliability_capacity_tenant_time",
        "reliability_capacity_snapshots",
        ["tenant_id", "created_at"],
    )
    op.create_table(
        "reliability_admission_decisions",
        sa.Column("admission_decision_id", sa.Uuid(), primary_key=True),
        _tenant(nullable=False),
        sa.Column("workflow_run_id", sa.Uuid()),
        sa.Column("queue_job_id", sa.Uuid()),
        sa.Column("policy_id", sa.Uuid(), nullable=False),
        sa.Column("policy_version", sa.Integer(), nullable=False),
        sa.Column("decision", sa.String(64), nullable=False),
        sa.Column("reason_code", sa.String(128), nullable=False),
        sa.Column("available_at", sa.DateTime(timezone=True)),
        sa.Column("capacity_snapshot_id", sa.Uuid()),
        sa.Column("trace_id", sa.String(128)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_reliability_admission_tenant_time",
        "reliability_admission_decisions",
        ["tenant_id", "created_at"],
    )
    op.create_index(
        "ix_reliability_admission_tenant_decision_time",
        "reliability_admission_decisions",
        ["tenant_id", "decision", "created_at"],
    )
    op.create_table(
        "reliability_tenant_quota_counters",
        sa.Column("quota_counter_id", sa.Uuid(), primary_key=True),
        _tenant(nullable=False),
        sa.Column("resource_kind", sa.String(64), nullable=False),
        sa.Column("limit_value", sa.Integer(), nullable=False),
        sa.Column("used_value", sa.Integer(), nullable=False),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("window_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("policy_id", sa.Uuid()),
        sa.Column("policy_version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "tenant_id",
            "resource_kind",
            "window_start",
            name="uq_reliability_quota_counter_window",
        ),
    )
    op.create_table(
        "reliability_fairness_windows",
        sa.Column("fairness_window_id", sa.Uuid(), primary_key=True),
        _tenant(nullable=False),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("window_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("weight", sa.Integer(), nullable=False),
        sa.Column("allocated_tokens", sa.Integer(), nullable=False),
        sa.Column("consumed_tokens", sa.Integer(), nullable=False),
        sa.Column("fairness_debt", sa.Integer(), nullable=False),
        sa.Column("burst_debt", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_reliability_fairness_tenant_window",
        "reliability_fairness_windows",
        ["tenant_id", "window_start"],
    )
    op.create_table(
        "reliability_worker_pool_scaling_decisions",
        sa.Column("scaling_decision_id", sa.Uuid(), primary_key=True),
        sa.Column("worker_pool", sa.String(128), nullable=False),
        sa.Column("decision", sa.String(64), nullable=False),
        sa.Column("current_workers", sa.Integer(), nullable=False),
        sa.Column("target_workers", sa.Integer(), nullable=False),
        sa.Column("reason_code", sa.String(128), nullable=False),
        sa.Column("capacity_snapshot_id", sa.Uuid()),
        sa.Column("policy_id", sa.Uuid()),
        sa.Column("policy_version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "reliability_retry_schedules",
        sa.Column("retry_schedule_id", sa.Uuid(), primary_key=True),
        _tenant(nullable=False),
        sa.Column("workflow_run_id", sa.Uuid()),
        sa.Column("run_step_id", sa.Uuid()),
        sa.Column("queue_job_id", sa.Uuid()),
        sa.Column("failure_category", sa.String(64), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column("max_attempts", sa.Integer(), nullable=False),
        sa.Column("next_eligible_at", sa.DateTime(timezone=True)),
        sa.Column("deadline_at", sa.DateTime(timezone=True)),
        sa.Column("status", sa.String(64), nullable=False),
        sa.Column("stop_reason", sa.String(128)),
        sa.Column("policy_id", sa.Uuid()),
        sa.Column("policy_version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_reliability_retry_tenant_status_time",
        "reliability_retry_schedules",
        ["tenant_id", "status", "updated_at"],
    )
    op.create_table(
        "reliability_circuit_breakers",
        sa.Column("circuit_breaker_id", sa.Uuid(), primary_key=True),
        _tenant(),
        sa.Column("scope_type", sa.String(64), nullable=False),
        sa.Column("scope_key", sa.String(255), nullable=False),
        sa.Column("state", sa.String(64), nullable=False),
        sa.Column("reason_code", sa.String(128), nullable=False),
        sa.Column("thresholds", sa.JSON(), nullable=False),
        sa.Column("cooldown_until", sa.DateTime(timezone=True)),
        sa.Column("probe_required", sa.Boolean(), nullable=False),
        sa.Column("half_open_tokens", sa.Integer(), nullable=False),
        sa.Column("policy_id", sa.Uuid()),
        sa.Column("policy_version", sa.Integer(), nullable=False),
        sa.Column("last_transition_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "tenant_id",
            "scope_type",
            "scope_key",
            name="uq_reliability_breaker_scope",
        ),
    )
    op.create_table(
        "reliability_circuit_breaker_events",
        sa.Column("breaker_event_id", sa.Uuid(), primary_key=True),
        sa.Column("circuit_breaker_id", sa.Uuid(), nullable=False),
        _tenant(),
        sa.Column("from_state", sa.String(64), nullable=False),
        sa.Column("to_state", sa.String(64), nullable=False),
        sa.Column("reason_code", sa.String(128), nullable=False),
        sa.Column("probe_result", sa.JSON()),
        sa.Column("actor_id", sa.String(128)),
        sa.Column("override_id", sa.Uuid()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "reliability_compensation_requests",
        sa.Column("compensation_request_id", sa.Uuid(), primary_key=True),
        _tenant(nullable=False),
        sa.Column("workflow_run_id", sa.Uuid(), nullable=False),
        sa.Column("run_step_id", sa.Uuid(), nullable=False),
        sa.Column("side_effect_intent_id", sa.Uuid(), nullable=False),
        sa.Column("hook_ref", sa.String(255), nullable=False),
        sa.Column("status", sa.String(64), nullable=False),
        sa.Column("retry_schedule_id", sa.Uuid()),
        sa.Column("dead_letter_id", sa.Uuid()),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "tenant_id",
            "side_effect_intent_id",
            "hook_ref",
            name="uq_reliability_compensation_intent_hook",
        ),
    )
    op.create_table(
        "reliability_dead_letters",
        sa.Column("dead_letter_id", sa.Uuid(), primary_key=True),
        _tenant(nullable=False),
        sa.Column("source_kind", sa.String(64), nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=False),
        sa.Column("failure_category", sa.String(64), nullable=False),
        sa.Column("latest_state", sa.JSON(), nullable=False),
        sa.Column("recommended_action", sa.String(64), nullable=False),
        sa.Column("artifact_refs", sa.JSON(), nullable=False),
        sa.Column("policy_id", sa.Uuid()),
        sa.Column("policy_version", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(64), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_reliability_dead_letters_tenant_status_time",
        "reliability_dead_letters",
        ["tenant_id", "status", "updated_at"],
    )
    op.create_table(
        "reliability_operational_control_changes",
        sa.Column("control_change_id", sa.Uuid(), primary_key=True),
        _tenant(),
        sa.Column("policy_id", sa.Uuid()),
        sa.Column("actor_id", sa.String(128), nullable=False),
        sa.Column("actor_role", sa.String(64), nullable=False),
        sa.Column("scope_type", sa.String(64), nullable=False),
        sa.Column("scope_key", sa.String(255)),
        sa.Column("previous_value", sa.JSON(), nullable=False),
        sa.Column("new_value", sa.JSON(), nullable=False),
        sa.Column("validation_outcome", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "reliability_artifact_throughput_windows",
        sa.Column("artifact_window_id", sa.Uuid(), primary_key=True),
        _tenant(),
        sa.Column("operation_kind", sa.String(64), nullable=False),
        sa.Column("inflight_count", sa.Integer(), nullable=False),
        sa.Column("limit_value", sa.Integer(), nullable=False),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("window_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("policy_id", sa.Uuid()),
        sa.Column("policy_version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "reliability_failure_injection_records",
        sa.Column("failure_injection_id", sa.Uuid(), primary_key=True),
        _tenant(),
        sa.Column("workflow_run_id", sa.Uuid()),
        sa.Column("injection_point", sa.String(128), nullable=False),
        sa.Column("seed", sa.Integer(), nullable=False),
        sa.Column("outcome", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    for table in (
        "reliability_failure_injection_records",
        "reliability_artifact_throughput_windows",
        "reliability_operational_control_changes",
        "reliability_dead_letters",
        "reliability_compensation_requests",
        "reliability_circuit_breaker_events",
        "reliability_circuit_breakers",
        "reliability_retry_schedules",
        "reliability_worker_pool_scaling_decisions",
        "reliability_fairness_windows",
        "reliability_tenant_quota_counters",
        "reliability_admission_decisions",
        "reliability_capacity_snapshots",
        "reliability_policies",
    ):
        op.drop_table(table)
