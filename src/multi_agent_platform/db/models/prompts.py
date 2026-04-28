from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from multi_agent_platform.db.base import Base, TimestampMixin, utcnow


class PromptLineage(Base, TimestampMixin):
    __tablename__ = "prompt_lineages"
    __table_args__ = (
        CheckConstraint(
            "(scope_type = 'platform' AND tenant_id IS NULL) OR "
            "(scope_type = 'tenant' AND tenant_id IS NOT NULL)",
            name="ck_prompt_lineages_scope_tenant",
        ),
        Index(
            "ix_prompt_lineages_scope_slug",
            "scope_type",
            "tenant_id",
            "slug",
            unique=True,
        ),
        Index("ix_prompt_lineages_status", "status"),
    )

    prompt_lineage_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    scope_type: Mapped[str] = mapped_column(String(32))
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    slug: Mapped[str] = mapped_column(String(128))
    display_name: Mapped[str] = mapped_column(String(255))
    purpose: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(32), default="active")
    latest_draft_id: Mapped[UUID | None] = mapped_column(nullable=True)
    latest_published_prompt_version_id: Mapped[UUID | None] = mapped_column(
        nullable=True
    )
    created_by_principal_id: Mapped[str] = mapped_column(String(128))


class PromptDraft(Base, TimestampMixin):
    __tablename__ = "prompt_drafts"
    __table_args__ = (
        Index("ix_prompt_drafts_lineage_status", "prompt_lineage_id", "status"),
    )

    prompt_draft_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    prompt_lineage_id: Mapped[UUID] = mapped_column(
        ForeignKey("prompt_lineages.prompt_lineage_id")
    )
    scope_type: Mapped[str] = mapped_column(String(32))
    tenant_id: Mapped[UUID | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="active")
    current_revision_number: Mapped[int] = mapped_column(Integer, default=0)
    latest_revision_id: Mapped[UUID | None] = mapped_column(nullable=True)
    created_from_prompt_version_id: Mapped[UUID | None] = mapped_column(nullable=True)
    last_validation_result_id: Mapped[UUID | None] = mapped_column(nullable=True)
    created_by_principal_id: Mapped[str] = mapped_column(String(128))
    last_edited_by_principal_id: Mapped[str] = mapped_column(String(128))


class PromptDraftRevision(Base):
    __tablename__ = "prompt_draft_revisions"
    __table_args__ = (
        UniqueConstraint(
            "prompt_draft_id",
            "revision_number",
            name="uq_prompt_draft_revisions_draft_number",
        ),
        Index("ix_prompt_draft_revisions_draft", "prompt_draft_id", "revision_number"),
    )

    prompt_draft_revision_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    prompt_draft_id: Mapped[UUID] = mapped_column(
        ForeignKey("prompt_drafts.prompt_draft_id")
    )
    revision_number: Mapped[int] = mapped_column(Integer)
    prompt_title: Mapped[str] = mapped_column(String(255))
    purpose: Mapped[str] = mapped_column(String(500))
    usage_notes: Mapped[str] = mapped_column(Text, default="")
    template_content: Mapped[str] = mapped_column(Text)
    template_content_sha256: Mapped[str] = mapped_column(String(64))
    variable_declarations_json: Mapped[list[dict[str, object]]] = mapped_column(
        JSON, default=list
    )
    fixture_value_sets_json: Mapped[list[dict[str, object]]] = mapped_column(
        JSON, default=list
    )
    safe_summary_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    created_by_principal_id: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class PromptValidationResult(Base):
    __tablename__ = "prompt_validation_results"
    __table_args__ = (
        Index(
            "ix_prompt_validation_results_revision",
            "prompt_draft_revision_id",
            "executed_at",
        ),
    )

    prompt_validation_result_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    prompt_draft_revision_id: Mapped[UUID] = mapped_column(
        ForeignKey("prompt_draft_revisions.prompt_draft_revision_id")
    )
    rule_set_version: Mapped[str] = mapped_column(
        String(64), default="prompt-runtime-v1"
    )
    status: Mapped[str] = mapped_column(String(32))
    blocking_issue_count: Mapped[int] = mapped_column(Integer, default=0)
    advisory_issue_count: Mapped[int] = mapped_column(Integer, default=0)
    findings_json: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list)
    template_content_sha256: Mapped[str] = mapped_column(String(64))
    validated_fixture_set_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    executed_by_principal_id: Mapped[str] = mapped_column(String(128))
    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class PromptRenderTest(Base):
    __tablename__ = "prompt_render_tests"

    prompt_render_test_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    prompt_draft_revision_id: Mapped[UUID] = mapped_column(
        ForeignKey("prompt_draft_revisions.prompt_draft_revision_id")
    )
    fixture_set_id: Mapped[str] = mapped_column(String(128))
    viewer_principal_id: Mapped[str] = mapped_column(String(128))
    outcome: Mapped[str] = mapped_column(String(32))
    missing_variables: Mapped[list[str]] = mapped_column(JSON, default=list)
    redaction_categories: Mapped[list[str]] = mapped_column(JSON, default=list)
    rendered_preview_sha256: Mapped[str | None] = mapped_column(
        String(64), nullable=True
    )
    safe_preview_summary: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class PromptVersion(Base):
    __tablename__ = "prompt_versions"
    __table_args__ = (
        UniqueConstraint(
            "prompt_lineage_id",
            "version_sequence",
            name="uq_prompt_versions_lineage_sequence",
        ),
        Index(
            "ix_prompt_versions_lineage_sequence",
            "prompt_lineage_id",
            "version_sequence",
        ),
        Index("ix_prompt_versions_scope_status", "scope_type", "tenant_id", "status"),
    )

    prompt_version_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    prompt_lineage_id: Mapped[UUID] = mapped_column(
        ForeignKey("prompt_lineages.prompt_lineage_id")
    )
    scope_type: Mapped[str] = mapped_column(String(32))
    tenant_id: Mapped[UUID | None] = mapped_column(nullable=True)
    version_sequence: Mapped[int] = mapped_column(Integer)
    display_version: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), default="active")
    published_from_draft_id: Mapped[UUID] = mapped_column(
        ForeignKey("prompt_drafts.prompt_draft_id")
    )
    published_from_revision_id: Mapped[UUID] = mapped_column(
        ForeignKey("prompt_draft_revisions.prompt_draft_revision_id")
    )
    validation_result_id: Mapped[UUID] = mapped_column(
        ForeignKey("prompt_validation_results.prompt_validation_result_id")
    )
    template_content: Mapped[str] = mapped_column(Text)
    template_content_sha256: Mapped[str] = mapped_column(String(64))
    variable_declarations_json: Mapped[list[dict[str, object]]] = mapped_column(
        JSON, default=list
    )
    purpose: Mapped[str] = mapped_column(String(500))
    usage_notes: Mapped[str] = mapped_column(Text, default="")
    safe_summary_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    published_by_principal_id: Mapped[str] = mapped_column(String(128))
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    publication_reason: Mapped[str] = mapped_column(String(500))
    retired_by_principal_id: Mapped[str | None] = mapped_column(
        String(128), nullable=True
    )
    retired_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    retirement_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)


class TenantPromptVersionGrant(Base):
    __tablename__ = "tenant_prompt_version_grants"
    __table_args__ = (
        Index(
            "ix_tenant_prompt_version_grants_active",
            "prompt_version_id",
            "grantee_tenant_id",
            "status",
        ),
    )

    tenant_prompt_version_grant_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    prompt_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("prompt_versions.prompt_version_id")
    )
    grantee_tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.tenant_id"))
    status: Mapped[str] = mapped_column(String(32), default="active")
    granted_by_principal_id: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    revoked_by_principal_id: Mapped[str | None] = mapped_column(
        String(128), nullable=True
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    reason: Mapped[str] = mapped_column(String(500), default="")


class PromptAuditRecord(Base):
    __tablename__ = "prompt_audit_records"
    __table_args__ = (
        Index("ix_prompt_audit_records_scope_time", "tenant_id", "created_at"),
        Index("ix_prompt_audit_records_lineage", "prompt_lineage_id"),
    )

    prompt_audit_record_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    prompt_lineage_id: Mapped[UUID | None] = mapped_column(nullable=True)
    prompt_version_id: Mapped[UUID | None] = mapped_column(nullable=True)
    agent_runtime_profile_id: Mapped[UUID | None] = mapped_column(nullable=True)
    agent_profile_version_id: Mapped[UUID | None] = mapped_column(nullable=True)
    tenant_id: Mapped[UUID | None] = mapped_column(nullable=True)
    actor_principal_id: Mapped[str] = mapped_column(String(128))
    action: Mapped[str] = mapped_column(String(64))
    outcome: Mapped[str] = mapped_column(String(32))
    safe_summary_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    trace_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
