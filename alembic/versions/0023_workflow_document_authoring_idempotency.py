"""workflow document authoring idempotency

Revision ID: 0023_workflow_document_authoring
Revises: 0022_runtime_interactions
Create Date: 2026-05-09 00:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0023_workflow_document_authoring"
down_revision = "0022_runtime_interactions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "workflow_draft_revisions",
        sa.Column("react_save_idempotency_key", sa.String(160), nullable=True),
    )
    op.add_column(
        "workflow_draft_revisions",
        sa.Column("react_save_scope_hash", sa.String(64), nullable=True),
    )
    op.add_column(
        "workflow_draft_revisions",
        sa.Column("react_save_payload_hash", sa.String(64), nullable=True),
    )
    op.create_index(
        "ix_workflow_draft_revisions_react_save_idempotency",
        "workflow_draft_revisions",
        ["workflow_draft_id", "react_save_idempotency_key"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_workflow_draft_revisions_react_save_idempotency",
        table_name="workflow_draft_revisions",
    )
    op.drop_column("workflow_draft_revisions", "react_save_payload_hash")
    op.drop_column("workflow_draft_revisions", "react_save_scope_hash")
    op.drop_column("workflow_draft_revisions", "react_save_idempotency_key")
