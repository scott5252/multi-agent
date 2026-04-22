"""platform foundation schema

Revision ID: 0001_platform_foundation
Revises:
Create Date: 2026-04-22 00:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001_platform_foundation"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tenants",
        sa.Column("tenant_id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column(
            "status",
            sa.Enum("active", "suspended", name="tenantstatus", native_enum=False),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("slug"),
    )
    op.create_table(
        "tenant_limit_policies",
        sa.Column("policy_id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column(
            "tenant_id",
            sa.Uuid(),
            sa.ForeignKey("tenants.tenant_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("max_concurrent_jobs", sa.Integer(), nullable=False),
        sa.Column("max_api_rps", sa.Integer(), nullable=False),
        sa.Column("max_artifact_bytes", sa.Integer(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("effective_from", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("tenant_id", "effective_from"),
    )
    op.create_table(
        "artifacts",
        sa.Column("artifact_id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), nullable=True
        ),
        sa.Column("scope_type", sa.String(length=32), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("storage_key", sa.String(length=255), nullable=False),
        sa.Column("media_type", sa.String(length=128), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("checksum", sa.String(length=128), nullable=True),
        sa.Column("retention_class", sa.String(length=32), nullable=False),
        sa.Column(
            "status",
            sa.Enum("active", "deleted", name="artifactstatus", native_enum=False),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "secret_references",
        sa.Column("secret_reference_id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), nullable=True
        ),
        sa.Column("scope_type", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("provider_key", sa.String(length=255), nullable=False),
        sa.Column("access_policy", sa.JSON(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "active", "revoked", name="secretreferencestatus", native_enum=False
            ),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "audit_events",
        sa.Column("audit_event_id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), nullable=True
        ),
        sa.Column("scope_type", sa.String(length=32), nullable=False),
        sa.Column(
            "actor_type",
            sa.Enum(
                "system", "service", "user", name="auditactortype", native_enum=False
            ),
            nullable=False,
        ),
        sa.Column("actor_id", sa.String(length=128), nullable=False),
        sa.Column("action", sa.String(length=128), nullable=False),
        sa.Column("entity_type", sa.String(length=128), nullable=False),
        sa.Column("entity_id", sa.String(length=128), nullable=False),
        sa.Column("trace_id", sa.String(length=64), nullable=False),
        sa.Column("request_id", sa.String(length=64), nullable=True),
        sa.Column("payload_redacted", sa.JSON(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "queue_jobs",
        sa.Column("job_id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column(
            "tenant_id", sa.Uuid(), sa.ForeignKey("tenants.tenant_id"), nullable=True
        ),
        sa.Column("scope_type", sa.String(length=32), nullable=False),
        sa.Column(
            "job_kind",
            sa.Enum(
                "bootstrap_task",
                "migration_task",
                "runtime_task",
                name="jobkind",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column(
            "artifact_id",
            sa.Uuid(),
            sa.ForeignKey("artifacts.artifact_id"),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "leased",
                "completed",
                "failed",
                "dead_letter",
                name="jobstatus",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column("max_attempts", sa.Integer(), nullable=False),
        sa.Column("idempotency_key", sa.String(length=255), nullable=True),
        sa.Column("trace_id", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "job_leases",
        sa.Column("lease_id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column(
            "job_id",
            sa.Uuid(),
            sa.ForeignKey("queue_jobs.job_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("worker_id", sa.String(length=128), nullable=False),
        sa.Column("lease_expires_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("job_leases")
    op.drop_table("queue_jobs")
    op.drop_table("audit_events")
    op.drop_table("secret_references")
    op.drop_table("artifacts")
    op.drop_table("tenant_limit_policies")
    op.drop_table("tenants")
