"""runtime interaction evidence

Revision ID: 0022_runtime_interactions
Revises: 0021_design_review_domain
Create Date: 2026-05-09 00:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0022_runtime_interactions"
down_revision = "0021_design_review_domain"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "runtime_interaction_evidence",
        sa.Column("interaction_evidence_id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column(
            "workflow_run_id",
            sa.Uuid(),
            sa.ForeignKey("runtime_workflow_runs.workflow_run_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("source_node_key", sa.String(128), nullable=False),
        sa.Column("target_node_key", sa.String(128)),
        sa.Column("source_run_step_id", sa.Uuid()),
        sa.Column("target_run_step_id", sa.Uuid()),
        sa.Column("timeline_event_id", sa.Uuid()),
        sa.Column("interaction_kind", sa.String(32), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("safe_summary", sa.Text(), nullable=False),
        sa.Column("classification", sa.String(64), nullable=False),
        sa.Column("payload_digest", sa.String(64), nullable=False),
        sa.Column("artifact_refs", sa.JSON(), nullable=False),
        sa.Column("provenance", sa.JSON(), nullable=False),
        sa.Column("idempotency_key", sa.String(160), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "tenant_id",
            "workflow_run_id",
            "idempotency_key",
            name="uq_runtime_interaction_evidence_tenant_run_idempotency",
        ),
    )
    op.create_index(
        "ix_runtime_interaction_evidence_tenant_run_sequence",
        "runtime_interaction_evidence",
        ["tenant_id", "workflow_run_id", "sequence"],
    )
    op.create_index(
        "ix_runtime_interaction_evidence_tenant_run_edge",
        "runtime_interaction_evidence",
        ["tenant_id", "workflow_run_id", "source_node_key", "target_node_key"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_runtime_interaction_evidence_tenant_run_edge",
        table_name="runtime_interaction_evidence",
    )
    op.drop_index(
        "ix_runtime_interaction_evidence_tenant_run_sequence",
        table_name="runtime_interaction_evidence",
    )
    op.drop_table("runtime_interaction_evidence")
