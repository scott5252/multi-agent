"""agent workflow test bench

Revision ID: 0015_agent_workflow_test_bench
Revises: 0014_skill_registry_lifecycle
Create Date: 2026-05-02 00:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0015_agent_workflow_test_bench"
down_revision = "0014_skill_registry_lifecycle"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "agent_test_suites",
        sa.Column("agent_test_suite_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), nullable=False
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("target_type", sa.String(64), nullable=False),
        sa.Column("target_id", sa.String(255), nullable=False),
        sa.Column("target_version", sa.String(128)),
        sa.Column("default_safe_mode", sa.String(64), nullable=False),
        sa.Column("model_mode", sa.String(64), nullable=False),
        sa.Column("tool_mode", sa.String(64), nullable=False),
        sa.Column("pass_threshold", sa.Float(), nullable=False),
        sa.Column("is_required_for_publish", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(64), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("created_by_principal_id", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint(
            "tenant_id", "name", name="uq_agent_test_suites_tenant_name"
        ),
    )
    op.create_index(
        "ix_agent_test_suites_tenant_target",
        "agent_test_suites",
        ["tenant_id", "target_type", "target_id"],
    )
    op.create_index(
        "ix_agent_test_suites_required",
        "agent_test_suites",
        ["tenant_id", "is_required_for_publish"],
    )

    op.create_table(
        "agent_test_cases",
        sa.Column("agent_test_case_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "agent_test_suite_id",
            sa.Uuid(),
            sa.ForeignKey("agent_test_suites.agent_test_suite_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), nullable=False
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("fixture_summary", sa.JSON(), nullable=False),
        sa.Column(
            "fixture_artifact_id", sa.Uuid(), sa.ForeignKey("artifacts.artifact_id")
        ),
        sa.Column("expected_contract_shape", sa.JSON(), nullable=False),
        sa.Column("model_mode", sa.String(64), nullable=False),
        sa.Column("tool_mode", sa.String(64), nullable=False),
        sa.Column("evaluator_prompt_ref", sa.String(255)),
        sa.Column("pass_threshold", sa.Float(), nullable=False),
        sa.Column("case_order", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(64), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True)),
    )
    op.create_index(
        "ix_agent_test_cases_suite_order",
        "agent_test_cases",
        ["agent_test_suite_id", "case_order"],
    )

    op.create_table(
        "agent_test_assertions",
        sa.Column("agent_test_assertion_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "agent_test_case_id",
            sa.Uuid(),
            sa.ForeignKey("agent_test_cases.agent_test_case_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), nullable=False
        ),
        sa.Column("kind", sa.String(64), nullable=False),
        sa.Column("path", sa.String(255)),
        sa.Column("comparator", sa.String(64)),
        sa.Column("expected_value", sa.JSON()),
        sa.Column("expected_schema", sa.JSON(), nullable=False),
        sa.Column("threshold", sa.Float()),
        sa.Column("severity", sa.String(64), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_agent_test_assertions_case",
        "agent_test_assertions",
        ["agent_test_case_id"],
    )

    op.create_table(
        "agent_test_runs",
        sa.Column("agent_test_run_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), nullable=False
        ),
        sa.Column(
            "agent_test_suite_id",
            sa.Uuid(),
            sa.ForeignKey("agent_test_suites.agent_test_suite_id"),
            nullable=False,
        ),
        sa.Column("target_type", sa.String(64), nullable=False),
        sa.Column("target_id", sa.String(255), nullable=False),
        sa.Column("target_version", sa.String(128)),
        sa.Column("safe_mode", sa.String(64), nullable=False),
        sa.Column("status", sa.String(64), nullable=False),
        sa.Column("pass_status", sa.String(64), nullable=False),
        sa.Column("triggered_by_principal_id", sa.String(255), nullable=False),
        sa.Column("idempotency_key", sa.String(255), nullable=False),
        sa.Column("trace_id", sa.String(255)),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("usage_summary", sa.JSON(), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("redaction_summary", sa.JSON(), nullable=False),
        sa.Column("artifact_summary", sa.JSON(), nullable=False),
        sa.Column("blocked_side_effect_count", sa.Integer(), nullable=False),
        sa.Column("failure_summary", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_agent_test_runs_tenant_suite_status",
        "agent_test_runs",
        ["tenant_id", "agent_test_suite_id", "status"],
    )
    op.create_index(
        "ix_agent_test_runs_target_version",
        "agent_test_runs",
        ["tenant_id", "target_type", "target_id", "target_version"],
    )
    op.create_index(
        "ix_agent_test_runs_idempotency",
        "agent_test_runs",
        ["tenant_id", "idempotency_key"],
        unique=True,
    )

    op.create_table(
        "agent_test_run_steps",
        sa.Column("agent_test_run_step_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "agent_test_run_id",
            sa.Uuid(),
            sa.ForeignKey("agent_test_runs.agent_test_run_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), nullable=False
        ),
        sa.Column(
            "agent_test_case_id",
            sa.Uuid(),
            sa.ForeignKey("agent_test_cases.agent_test_case_id"),
        ),
        sa.Column("step_name", sa.String(255), nullable=False),
        sa.Column("status", sa.String(64), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("model_provider", sa.String(128)),
        sa.Column("model_id", sa.String(128)),
        sa.Column("prompt_version_id", sa.String(128)),
        sa.Column("profile_version_id", sa.String(128)),
        sa.Column("skill_version_refs", sa.JSON(), nullable=False),
        sa.Column("workflow_version_ref", sa.String(128)),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("token_usage", sa.JSON(), nullable=False),
        sa.Column("contract_validation", sa.JSON(), nullable=False),
        sa.Column("assertion_results", sa.JSON(), nullable=False),
        sa.Column("blocked_side_effects", sa.JSON(), nullable=False),
        sa.Column("redacted_transcript", sa.JSON(), nullable=False),
        sa.Column("artifact_refs", sa.JSON(), nullable=False),
        sa.Column("failure_reason", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_agent_test_run_steps_run_sequence",
        "agent_test_run_steps",
        ["agent_test_run_id", "sequence"],
    )

    op.create_table(
        "agent_test_artifacts",
        sa.Column("agent_test_artifact_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), nullable=False
        ),
        sa.Column(
            "agent_test_run_id",
            sa.Uuid(),
            sa.ForeignKey("agent_test_runs.agent_test_run_id"),
        ),
        sa.Column(
            "agent_test_case_id",
            sa.Uuid(),
            sa.ForeignKey("agent_test_cases.agent_test_case_id"),
        ),
        sa.Column("artifact_type", sa.String(64), nullable=False),
        sa.Column("storage_uri", sa.String(512)),
        sa.Column("checksum_sha256", sa.String(128)),
        sa.Column("size_bytes", sa.Integer()),
        sa.Column("content_type", sa.String(128)),
        sa.Column("redaction_classification", sa.String(64), nullable=False),
        sa.Column("retention_state", sa.String(64), nullable=False),
        sa.Column("safe_summary", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
    )
    op.create_index(
        "ix_agent_test_artifacts_run",
        "agent_test_artifacts",
        ["agent_test_run_id"],
    )

    op.create_table(
        "agent_test_publication_requirements",
        sa.Column("agent_test_publication_requirement_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), nullable=False
        ),
        sa.Column("target_type", sa.String(64), nullable=False),
        sa.Column("target_id", sa.String(255), nullable=False),
        sa.Column(
            "agent_test_suite_id",
            sa.Uuid(),
            sa.ForeignKey("agent_test_suites.agent_test_suite_id"),
            nullable=False,
        ),
        sa.Column("required", sa.Boolean(), nullable=False),
        sa.Column("minimum_pass_status", sa.String(64), nullable=False),
        sa.Column("created_by_principal_id", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint(
            "tenant_id",
            "target_type",
            "target_id",
            "agent_test_suite_id",
            name="uq_agent_test_publication_requirement",
        ),
    )
    op.create_index(
        "ix_agent_test_pub_req_target",
        "agent_test_publication_requirements",
        ["tenant_id", "target_type", "target_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_agent_test_pub_req_target", table_name="agent_test_publication_requirements"
    )
    op.drop_table("agent_test_publication_requirements")
    op.drop_index("ix_agent_test_artifacts_run", table_name="agent_test_artifacts")
    op.drop_table("agent_test_artifacts")
    op.drop_index(
        "ix_agent_test_run_steps_run_sequence", table_name="agent_test_run_steps"
    )
    op.drop_table("agent_test_run_steps")
    op.drop_index("ix_agent_test_runs_idempotency", table_name="agent_test_runs")
    op.drop_index("ix_agent_test_runs_target_version", table_name="agent_test_runs")
    op.drop_index(
        "ix_agent_test_runs_tenant_suite_status", table_name="agent_test_runs"
    )
    op.drop_table("agent_test_runs")
    op.drop_index("ix_agent_test_assertions_case", table_name="agent_test_assertions")
    op.drop_table("agent_test_assertions")
    op.drop_index("ix_agent_test_cases_suite_order", table_name="agent_test_cases")
    op.drop_table("agent_test_cases")
    op.drop_index("ix_agent_test_suites_required", table_name="agent_test_suites")
    op.drop_index("ix_agent_test_suites_tenant_target", table_name="agent_test_suites")
    op.drop_table("agent_test_suites")
