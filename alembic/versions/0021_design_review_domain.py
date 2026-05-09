"""design review domain

Revision ID: 0021_design_review_domain
Revises: 0020_briefing_preferences
Create Date: 2026-05-08 00:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0021_design_review_domain"
down_revision = "0020_briefing_preferences"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "design_review_sessions",
        sa.Column("design_review_session_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), nullable=False
        ),
        sa.Column("status", sa.String(19), nullable=False),
        sa.Column("request_summary", sa.Text(), nullable=False),
        sa.Column("active_revision_number", sa.Integer(), nullable=False),
        sa.Column("quorum_policy_key", sa.String(120), nullable=False),
        sa.Column(
            "workflow_version_bundle_id",
            sa.Uuid(),
            sa.ForeignKey("workflow_version_bundles.workflow_version_bundle_id"),
            nullable=True,
        ),
        sa.Column("owner_principal_id", sa.String(255), nullable=False),
        sa.Column("idempotency_key", sa.String(160), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_design_review_sessions_tenant_idempotency",
        ),
    )
    op.create_index(
        "ix_design_review_sessions_tenant_status",
        "design_review_sessions",
        ["tenant_id", "status"],
    )
    op.create_index(
        "ix_design_review_sessions_tenant_updated",
        "design_review_sessions",
        ["tenant_id", "updated_at"],
    )

    op.create_table(
        "design_revisions",
        sa.Column("design_revision_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "design_review_session_id",
            sa.Uuid(),
            sa.ForeignKey(
                "design_review_sessions.design_review_session_id", ondelete="CASCADE"
            ),
            nullable=False,
        ),
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), nullable=False
        ),
        sa.Column("revision_number", sa.Integer(), nullable=False),
        sa.Column("author_role_key", sa.String(120), nullable=False),
        sa.Column("safe_summary", sa.Text(), nullable=False),
        sa.Column("artifact_id", sa.Uuid(), sa.ForeignKey("artifacts.artifact_id")),
        sa.Column("payload_digest", sa.String(128), nullable=False),
        sa.Column(
            "previous_revision_id",
            sa.Uuid(),
            sa.ForeignKey("design_revisions.design_revision_id"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "design_review_session_id",
            "revision_number",
            name="uq_design_revisions_session_number",
        ),
    )
    op.create_index(
        "ix_design_revisions_tenant_session",
        "design_revisions",
        ["tenant_id", "design_review_session_id"],
    )

    op.create_table(
        "design_review_rounds",
        sa.Column("design_review_round_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "design_review_session_id",
            sa.Uuid(),
            sa.ForeignKey(
                "design_review_sessions.design_review_session_id", ondelete="CASCADE"
            ),
            nullable=False,
        ),
        sa.Column(
            "design_revision_id",
            sa.Uuid(),
            sa.ForeignKey("design_revisions.design_revision_id"),
            nullable=False,
        ),
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), nullable=False
        ),
        sa.Column("round_number", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(19), nullable=False),
        sa.Column("workflow_run_id", sa.Uuid()),
        sa.Column("reviewer_count", sa.Integer(), nullable=False),
        sa.Column("quorum_count", sa.Integer(), nullable=False),
        sa.Column("idempotency_key", sa.String(160)),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "design_review_session_id",
            "round_number",
            name="uq_design_review_rounds_session_number",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_design_review_rounds_tenant_idempotency",
        ),
    )
    op.create_index(
        "ix_design_review_rounds_tenant_status",
        "design_review_rounds",
        ["tenant_id", "status"],
    )
    op.create_index(
        "ix_design_review_rounds_session",
        "design_review_rounds",
        ["design_review_session_id"],
    )

    op.create_table(
        "design_reviewer_assignments",
        sa.Column("design_reviewer_assignment_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "design_review_round_id",
            sa.Uuid(),
            sa.ForeignKey(
                "design_review_rounds.design_review_round_id", ondelete="CASCADE"
            ),
            nullable=False,
        ),
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), nullable=False
        ),
        sa.Column("reviewer_key", sa.String(120), nullable=False),
        sa.Column("role_key", sa.String(120), nullable=False),
        sa.Column(
            "prompt_version_id",
            sa.Uuid(),
            sa.ForeignKey("prompt_versions.prompt_version_id"),
        ),
        sa.Column(
            "profile_version_id",
            sa.Uuid(),
            sa.ForeignKey("agent_profile_versions.agent_profile_version_id"),
        ),
        sa.Column("provider_reference", sa.String(255)),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "design_review_round_id",
            "reviewer_key",
            name="uq_design_reviewer_assignments_round_reviewer",
        ),
    )
    op.create_index(
        "ix_design_reviewer_assignments_tenant_round",
        "design_reviewer_assignments",
        ["tenant_id", "design_review_round_id"],
    )

    op.create_table(
        "design_reviewer_verdicts",
        sa.Column("design_reviewer_verdict_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "design_review_round_id",
            sa.Uuid(),
            sa.ForeignKey(
                "design_review_rounds.design_review_round_id", ondelete="CASCADE"
            ),
            nullable=False,
        ),
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), nullable=False
        ),
        sa.Column("reviewer_key", sa.String(120), nullable=False),
        sa.Column("verdict", sa.String(17), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("blocking_issue_count", sa.Integer(), nullable=False),
        sa.Column("safe_feedback_summary", sa.Text(), nullable=False),
        sa.Column("artifact_id", sa.Uuid(), sa.ForeignKey("artifacts.artifact_id")),
        sa.Column("output_digest", sa.String(128), nullable=False),
        sa.Column("usage_summary", sa.JSON(), nullable=False),
        sa.Column("idempotency_key", sa.String(160)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "design_review_round_id",
            "reviewer_key",
            name="uq_design_reviewer_verdicts_round_reviewer",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_design_reviewer_verdicts_tenant_idempotency",
        ),
    )
    op.create_index(
        "ix_design_reviewer_verdicts_tenant_round",
        "design_reviewer_verdicts",
        ["tenant_id", "design_review_round_id"],
    )

    op.create_table(
        "design_quorum_decisions",
        sa.Column("design_quorum_decision_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "design_review_round_id",
            sa.Uuid(),
            sa.ForeignKey(
                "design_review_rounds.design_review_round_id", ondelete="CASCADE"
            ),
            nullable=False,
        ),
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), nullable=False
        ),
        sa.Column("status", sa.String(19), nullable=False),
        sa.Column("approval_count", sa.Integer(), nullable=False),
        sa.Column("blocking_issue_count", sa.Integer(), nullable=False),
        sa.Column("next_action", sa.String(15), nullable=False),
        sa.Column("policy_version", sa.String(120), nullable=False),
        sa.Column("safe_rationale", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "design_review_round_id",
            name="uq_design_quorum_decisions_round",
        ),
    )
    op.create_index(
        "ix_design_quorum_decisions_tenant_round",
        "design_quorum_decisions",
        ["tenant_id", "design_review_round_id"],
    )

    op.create_table(
        "design_manual_decisions",
        sa.Column("design_manual_decision_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "design_review_session_id",
            sa.Uuid(),
            sa.ForeignKey(
                "design_review_sessions.design_review_session_id", ondelete="CASCADE"
            ),
            nullable=False,
        ),
        sa.Column(
            "design_review_round_id",
            sa.Uuid(),
            sa.ForeignKey("design_review_rounds.design_review_round_id"),
        ),
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), nullable=False
        ),
        sa.Column("decision_type", sa.String(17), nullable=False),
        sa.Column("actor_principal_id", sa.String(255), nullable=False),
        sa.Column("safe_rationale", sa.Text(), nullable=False),
        sa.Column("accepted_risk", sa.Boolean(), nullable=False),
        sa.Column("idempotency_key", sa.String(160)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_design_manual_decisions_tenant_idempotency",
        ),
    )
    op.create_index(
        "ix_design_manual_decisions_tenant_session",
        "design_manual_decisions",
        ["tenant_id", "design_review_session_id"],
    )

    op.create_table(
        "design_development_handoffs",
        sa.Column("design_development_handoff_id", sa.Uuid(), primary_key=True),
        sa.Column(
            "design_review_session_id",
            sa.Uuid(),
            sa.ForeignKey(
                "design_review_sessions.design_review_session_id", ondelete="CASCADE"
            ),
            nullable=False,
        ),
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), nullable=False
        ),
        sa.Column(
            "approved_revision_id",
            sa.Uuid(),
            sa.ForeignKey("design_revisions.design_revision_id"),
            nullable=False,
        ),
        sa.Column("artifact_id", sa.Uuid(), sa.ForeignKey("artifacts.artifact_id")),
        sa.Column("safe_summary", sa.Text(), nullable=False),
        sa.Column("output_digest", sa.String(128), nullable=False),
        sa.Column("status", sa.String(9), nullable=False),
        sa.Column("idempotency_key", sa.String(160)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "design_review_session_id",
            name="uq_design_development_handoffs_session",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_design_development_handoffs_tenant_idempotency",
        ),
    )
    op.create_index(
        "ix_design_development_handoffs_tenant_status",
        "design_development_handoffs",
        ["tenant_id", "status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_design_development_handoffs_tenant_status",
        table_name="design_development_handoffs",
    )
    op.drop_table("design_development_handoffs")
    op.drop_index(
        "ix_design_manual_decisions_tenant_session",
        table_name="design_manual_decisions",
    )
    op.drop_table("design_manual_decisions")
    op.drop_index(
        "ix_design_quorum_decisions_tenant_round",
        table_name="design_quorum_decisions",
    )
    op.drop_table("design_quorum_decisions")
    op.drop_index(
        "ix_design_reviewer_verdicts_tenant_round",
        table_name="design_reviewer_verdicts",
    )
    op.drop_table("design_reviewer_verdicts")
    op.drop_index(
        "ix_design_reviewer_assignments_tenant_round",
        table_name="design_reviewer_assignments",
    )
    op.drop_table("design_reviewer_assignments")
    op.drop_index("ix_design_review_rounds_session", table_name="design_review_rounds")
    op.drop_index(
        "ix_design_review_rounds_tenant_status",
        table_name="design_review_rounds",
    )
    op.drop_table("design_review_rounds")
    op.drop_index("ix_design_revisions_tenant_session", table_name="design_revisions")
    op.drop_table("design_revisions")
    op.drop_index(
        "ix_design_review_sessions_tenant_updated",
        table_name="design_review_sessions",
    )
    op.drop_index(
        "ix_design_review_sessions_tenant_status",
        table_name="design_review_sessions",
    )
    op.drop_table("design_review_sessions")
