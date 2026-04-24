from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from multi_agent_platform.db.base import Base, utcnow


class MemorySourceTypeRecord(StrEnum):
    API = "api"
    RUNTIME = "runtime"
    MIGRATION = "migration"
    SUPPORT = "support"


class MemoryAuditActionRecord(StrEnum):
    CREATE_VERSION = "create_version"
    GET_HEAD = "get_head"
    GET_VERSION = "get_version"
    LIST_HISTORY = "list_history"
    REPLAY = "replay"
    DIFF = "diff"
    ARCHIVE_MARK = "archive_mark"


class MemoryAuditOutcomeRecord(StrEnum):
    ALLOWED = "allowed"
    DENIED = "denied"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    INVALID = "invalid"


class MemoryScopeRecord(Base):
    __tablename__ = "memory_scopes"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "workflow_lineage_id",
            "agent_key",
            "memory_key",
            name="uq_memory_scopes_natural_scope",
        ),
        Index("ix_memory_scopes_tenant_lineage", "tenant_id", "workflow_lineage_id"),
    )

    memory_scope_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    workflow_lineage_id: Mapped[str] = mapped_column(String(128))
    agent_key: Mapped[str] = mapped_column(String(128))
    memory_key: Mapped[str] = mapped_column(String(128))
    created_by_principal_id: Mapped[str] = mapped_column(String(128))
    created_by_workflow_run_id: Mapped[UUID | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class MemoryVersionRecord(Base):
    __tablename__ = "memory_versions"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "memory_scope_id",
            "version_sequence",
            name="uq_memory_versions_scope_sequence",
        ),
        UniqueConstraint(
            "tenant_id",
            "memory_scope_id",
            "idempotency_key",
            name="uq_memory_versions_scope_idempotency",
        ),
        Index(
            "ix_memory_versions_scope_sequence",
            "memory_scope_id",
            "version_sequence",
        ),
        Index(
            "ix_memory_versions_previous",
            "tenant_id",
            "previous_memory_version_id",
        ),
    )

    memory_version_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    memory_scope_id: Mapped[UUID] = mapped_column(
        ForeignKey("memory_scopes.memory_scope_id"), nullable=False
    )
    previous_memory_version_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("memory_versions.memory_version_id"), nullable=True
    )
    version_sequence: Mapped[int] = mapped_column(Integer)
    content: Mapped[
        dict[str, object] | list[object] | str | int | float | bool | None
    ] = mapped_column(JSON)
    content_sha256: Mapped[str] = mapped_column(String(64))
    content_size_bytes: Mapped[int] = mapped_column(Integer)
    change_summary_redacted: Mapped[str | None] = mapped_column(
        String(1000), nullable=True
    )
    change_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    actor_principal_id: Mapped[str] = mapped_column(String(128))
    source_type: Mapped[str] = mapped_column(String(32))
    workflow_run_id: Mapped[UUID | None] = mapped_column(nullable=True)
    run_step_id: Mapped[UUID | None] = mapped_column(nullable=True)
    run_bundle_id: Mapped[UUID | None] = mapped_column(nullable=True)
    bundle_digest: Mapped[str | None] = mapped_column(String(64), nullable=True)
    run_lineage_id: Mapped[UUID | None] = mapped_column(nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class MemoryHeadRecord(Base):
    __tablename__ = "memory_heads"
    __table_args__ = (
        Index(
            "ix_memory_heads_natural_scope",
            "tenant_id",
            "workflow_lineage_id",
            "agent_key",
            "memory_key",
        ),
    )

    memory_scope_id: Mapped[UUID] = mapped_column(
        ForeignKey("memory_scopes.memory_scope_id"), primary_key=True
    )
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    workflow_lineage_id: Mapped[str] = mapped_column(String(128))
    agent_key: Mapped[str] = mapped_column(String(128))
    memory_key: Mapped[str] = mapped_column(String(128))
    current_memory_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("memory_versions.memory_version_id")
    )
    version_sequence: Mapped[int] = mapped_column(Integer)
    content_sha256: Mapped[str] = mapped_column(String(64))
    updated_by_principal_id: Mapped[str] = mapped_column(String(128))
    updated_by_workflow_run_id: Mapped[UUID | None] = mapped_column(nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class MemoryAuditEventRecord(Base):
    __tablename__ = "memory_audit_events"
    __table_args__ = (
        Index("ix_memory_audit_tenant_scope", "tenant_id", "memory_scope_id"),
        Index("ix_memory_audit_tenant_version", "tenant_id", "memory_version_id"),
        Index("ix_memory_audit_tenant_run", "tenant_id", "workflow_run_id"),
        Index("ix_memory_audit_tenant_created", "tenant_id", "created_at"),
    )

    memory_audit_event_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    memory_scope_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("memory_scopes.memory_scope_id"), nullable=True
    )
    memory_version_id: Mapped[UUID | None] = mapped_column(nullable=True)
    previous_memory_version_id: Mapped[UUID | None] = mapped_column(nullable=True)
    current_memory_version_id: Mapped[UUID | None] = mapped_column(nullable=True)
    workflow_lineage_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    agent_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    memory_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    workflow_run_id: Mapped[UUID | None] = mapped_column(nullable=True)
    run_step_id: Mapped[UUID | None] = mapped_column(nullable=True)
    run_bundle_id: Mapped[UUID | None] = mapped_column(nullable=True)
    bundle_digest: Mapped[str | None] = mapped_column(String(64), nullable=True)
    run_lineage_id: Mapped[UUID | None] = mapped_column(nullable=True)
    actor_principal_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    action_type: Mapped[str] = mapped_column(String(64))
    outcome: Mapped[str] = mapped_column(String(32))
    content_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    base_memory_version_id: Mapped[UUID | None] = mapped_column(nullable=True)
    compare_memory_version_id: Mapped[UUID | None] = mapped_column(nullable=True)
    compared_content_sha256: Mapped[str | None] = mapped_column(
        String(64), nullable=True
    )
    change_summary_redacted: Mapped[str | None] = mapped_column(
        String(1000), nullable=True
    )
    denial_reason: Mapped[str | None] = mapped_column(Text(), nullable=True)
    trace_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class MemoryArchiveEventRecord(Base):
    __tablename__ = "memory_archive_events"

    memory_archive_event_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    memory_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("memory_versions.memory_version_id"), nullable=False
    )
    archived_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    archive_reason: Mapped[str] = mapped_column(Text())
    actor_principal_id: Mapped[str] = mapped_column(String(128))
    memory_audit_event_id: Mapped[UUID] = mapped_column(
        ForeignKey("memory_audit_events.memory_audit_event_id")
    )
