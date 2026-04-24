"""immutable memory schema

Revision ID: 0005_immutable_memory
Revises: 0004_durable_runtime
Create Date: 2026-04-24 00:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0005_immutable_memory"
down_revision = "0004_durable_runtime"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "memory_scopes",
        sa.Column("memory_scope_id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column("workflow_lineage_id", sa.String(128), nullable=False),
        sa.Column("agent_key", sa.String(128), nullable=False),
        sa.Column("memory_key", sa.String(128), nullable=False),
        sa.Column("created_by_principal_id", sa.String(128), nullable=False),
        sa.Column("created_by_workflow_run_id", sa.Uuid()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "tenant_id",
            "workflow_lineage_id",
            "agent_key",
            "memory_key",
            name="uq_memory_scopes_natural_scope",
        ),
    )
    op.create_index(
        "ix_memory_scopes_tenant_lineage",
        "memory_scopes",
        ["tenant_id", "workflow_lineage_id"],
    )
    op.create_table(
        "memory_versions",
        sa.Column("memory_version_id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column(
            "memory_scope_id",
            sa.Uuid(),
            sa.ForeignKey("memory_scopes.memory_scope_id"),
            nullable=False,
        ),
        sa.Column(
            "previous_memory_version_id",
            sa.Uuid(),
            sa.ForeignKey("memory_versions.memory_version_id"),
        ),
        sa.Column("version_sequence", sa.Integer(), nullable=False),
        sa.Column("content", sa.JSON(), nullable=False),
        sa.Column("content_sha256", sa.String(64), nullable=False),
        sa.Column("content_size_bytes", sa.Integer(), nullable=False),
        sa.Column("change_summary_redacted", sa.String(1000)),
        sa.Column("change_reason", sa.String(500)),
        sa.Column("actor_principal_id", sa.String(128), nullable=False),
        sa.Column("source_type", sa.String(32), nullable=False),
        sa.Column("workflow_run_id", sa.Uuid()),
        sa.Column("run_step_id", sa.Uuid()),
        sa.Column("run_bundle_id", sa.Uuid()),
        sa.Column("bundle_digest", sa.String(64)),
        sa.Column("run_lineage_id", sa.Uuid()),
        sa.Column("idempotency_key", sa.String(128)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "tenant_id",
            "memory_scope_id",
            "version_sequence",
            name="uq_memory_versions_scope_sequence",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "memory_scope_id",
            "idempotency_key",
            name="uq_memory_versions_scope_idempotency",
        ),
    )
    op.create_index(
        "ix_memory_versions_scope_sequence",
        "memory_versions",
        ["memory_scope_id", "version_sequence"],
    )
    op.create_index(
        "ix_memory_versions_previous",
        "memory_versions",
        ["tenant_id", "previous_memory_version_id"],
    )
    op.create_table(
        "memory_heads",
        sa.Column(
            "memory_scope_id",
            sa.Uuid(),
            sa.ForeignKey("memory_scopes.memory_scope_id"),
            primary_key=True,
        ),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column("workflow_lineage_id", sa.String(128), nullable=False),
        sa.Column("agent_key", sa.String(128), nullable=False),
        sa.Column("memory_key", sa.String(128), nullable=False),
        sa.Column(
            "current_memory_version_id",
            sa.Uuid(),
            sa.ForeignKey("memory_versions.memory_version_id"),
            nullable=False,
        ),
        sa.Column("version_sequence", sa.Integer(), nullable=False),
        sa.Column("content_sha256", sa.String(64), nullable=False),
        sa.Column("updated_by_principal_id", sa.String(128), nullable=False),
        sa.Column("updated_by_workflow_run_id", sa.Uuid()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_memory_heads_natural_scope",
        "memory_heads",
        ["tenant_id", "workflow_lineage_id", "agent_key", "memory_key"],
    )
    op.create_table(
        "memory_audit_events",
        sa.Column("memory_audit_event_id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column(
            "memory_scope_id",
            sa.Uuid(),
            sa.ForeignKey("memory_scopes.memory_scope_id"),
        ),
        sa.Column("memory_version_id", sa.Uuid()),
        sa.Column("previous_memory_version_id", sa.Uuid()),
        sa.Column("current_memory_version_id", sa.Uuid()),
        sa.Column("workflow_lineage_id", sa.String(128)),
        sa.Column("agent_key", sa.String(128)),
        sa.Column("memory_key", sa.String(128)),
        sa.Column("workflow_run_id", sa.Uuid()),
        sa.Column("run_step_id", sa.Uuid()),
        sa.Column("run_bundle_id", sa.Uuid()),
        sa.Column("bundle_digest", sa.String(64)),
        sa.Column("run_lineage_id", sa.Uuid()),
        sa.Column("actor_principal_id", sa.String(128)),
        sa.Column("action_type", sa.String(64), nullable=False),
        sa.Column("outcome", sa.String(32), nullable=False),
        sa.Column("content_sha256", sa.String(64)),
        sa.Column("base_memory_version_id", sa.Uuid()),
        sa.Column("compare_memory_version_id", sa.Uuid()),
        sa.Column("compared_content_sha256", sa.String(64)),
        sa.Column("change_summary_redacted", sa.String(1000)),
        sa.Column("denial_reason", sa.Text()),
        sa.Column("trace_id", sa.String(64)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_memory_audit_tenant_scope",
        "memory_audit_events",
        ["tenant_id", "memory_scope_id"],
    )
    op.create_index(
        "ix_memory_audit_tenant_version",
        "memory_audit_events",
        ["tenant_id", "memory_version_id"],
    )
    op.create_index(
        "ix_memory_audit_tenant_run",
        "memory_audit_events",
        ["tenant_id", "workflow_run_id"],
    )
    op.create_index(
        "ix_memory_audit_tenant_created",
        "memory_audit_events",
        ["tenant_id", "created_at"],
    )
    op.create_table(
        "memory_archive_events",
        sa.Column("memory_archive_event_id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id")),
        sa.Column(
            "memory_version_id",
            sa.Uuid(),
            sa.ForeignKey("memory_versions.memory_version_id"),
            nullable=False,
        ),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("archive_reason", sa.Text(), nullable=False),
        sa.Column("actor_principal_id", sa.String(128), nullable=False),
        sa.Column(
            "memory_audit_event_id",
            sa.Uuid(),
            sa.ForeignKey("memory_audit_events.memory_audit_event_id"),
            nullable=False,
        ),
    )
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            """
            CREATE OR REPLACE FUNCTION reject_memory_version_mutation()
            RETURNS trigger AS $$
            BEGIN
                RAISE EXCEPTION 'memory_versions are immutable';
            END;
            $$ LANGUAGE plpgsql;
            """
        )
        op.execute(
            """
            CREATE TRIGGER trg_memory_versions_immutable
            BEFORE UPDATE OR DELETE ON memory_versions
            FOR EACH ROW EXECUTE FUNCTION reject_memory_version_mutation();
            """
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            "DROP TRIGGER IF EXISTS trg_memory_versions_immutable ON memory_versions"
        )
        op.execute("DROP FUNCTION IF EXISTS reject_memory_version_mutation()")
    op.drop_table("memory_archive_events")
    op.drop_index("ix_memory_audit_tenant_created", table_name="memory_audit_events")
    op.drop_index("ix_memory_audit_tenant_run", table_name="memory_audit_events")
    op.drop_index("ix_memory_audit_tenant_version", table_name="memory_audit_events")
    op.drop_index("ix_memory_audit_tenant_scope", table_name="memory_audit_events")
    op.drop_table("memory_audit_events")
    op.drop_index("ix_memory_heads_natural_scope", table_name="memory_heads")
    op.drop_table("memory_heads")
    op.drop_index("ix_memory_versions_previous", table_name="memory_versions")
    op.drop_index("ix_memory_versions_scope_sequence", table_name="memory_versions")
    op.drop_table("memory_versions")
    op.drop_index("ix_memory_scopes_tenant_lineage", table_name="memory_scopes")
    op.drop_table("memory_scopes")
