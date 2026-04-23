from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from multi_agent_platform.db.base import Base, TimestampMixin


class WorkflowKind(StrEnum):
    MAIN_WORKFLOW = "main_workflow"
    SUBWORKFLOW = "subworkflow"


class WorkflowLineageStatus(StrEnum):
    DRAFTING = "drafting"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class WorkflowDraftStatus(StrEnum):
    ACTIVE = "active"
    PUBLISHED_SOURCE = "published_source"
    ARCHIVED = "archived"
    REPLACED = "replaced"


class ValidationResultStatus(StrEnum):
    PASSED = "passed"
    FAILED = "failed"
    SUPERSEDED = "superseded"


class WorkflowVersionStatus(StrEnum):
    PUBLISHED = "published"
    HIDDEN = "hidden"
    RETIRED = "retired"


class RegistrySharingGrantStatus(StrEnum):
    ACTIVE = "active"
    REVOKED = "revoked"


class WorkflowLineage(Base, TimestampMixin):
    __tablename__ = "workflow_lineages"
    __table_args__ = (UniqueConstraint("scope_type", "tenant_id", "slug"),)

    workflow_lineage_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    scope_type: Mapped[str] = mapped_column(String(32))
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    slug: Mapped[str] = mapped_column(String(128))
    display_name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    workflow_kind: Mapped[WorkflowKind] = mapped_column(
        Enum(WorkflowKind, native_enum=False)
    )
    status: Mapped[WorkflowLineageStatus] = mapped_column(
        Enum(WorkflowLineageStatus, native_enum=False),
        default=WorkflowLineageStatus.DRAFTING,
    )
    latest_published_version_id: Mapped[UUID | None] = mapped_column(nullable=True)
    created_by_principal_id: Mapped[UUID] = mapped_column(
        ForeignKey("principal_identities.principal_identity_id")
    )


class WorkflowDraft(Base, TimestampMixin):
    __tablename__ = "workflow_drafts"

    workflow_draft_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    workflow_lineage_id: Mapped[UUID] = mapped_column(
        ForeignKey("workflow_lineages.workflow_lineage_id", ondelete="CASCADE")
    )
    scope_type: Mapped[str] = mapped_column(String(32))
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    status: Mapped[WorkflowDraftStatus] = mapped_column(
        Enum(WorkflowDraftStatus, native_enum=False),
        default=WorkflowDraftStatus.ACTIVE,
    )
    current_revision_number: Mapped[int] = mapped_column(Integer, default=1)
    latest_revision_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("workflow_draft_revisions.workflow_draft_revision_id"),
        nullable=True,
    )
    created_from_version_id: Mapped[UUID | None] = mapped_column(nullable=True)
    created_by_principal_id: Mapped[UUID] = mapped_column(
        ForeignKey("principal_identities.principal_identity_id")
    )
    last_edited_by_principal_id: Mapped[UUID] = mapped_column(
        ForeignKey("principal_identities.principal_identity_id")
    )


class WorkflowDraftRevision(Base):
    __tablename__ = "workflow_draft_revisions"
    __table_args__ = (UniqueConstraint("workflow_draft_id", "revision_number"),)

    workflow_draft_revision_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    workflow_draft_id: Mapped[UUID] = mapped_column(
        ForeignKey("workflow_drafts.workflow_draft_id", ondelete="CASCADE")
    )
    revision_number: Mapped[int] = mapped_column(Integer)
    authoring_document_json: Mapped[dict[str, object]] = mapped_column(JSON)
    document_sha256: Mapped[str] = mapped_column(String(64))
    change_summary: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_by_principal_id: Mapped[UUID] = mapped_column(
        ForeignKey("principal_identities.principal_identity_id")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


class ValidationResult(Base):
    __tablename__ = "validation_results"

    validation_result_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    workflow_draft_revision_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "workflow_draft_revisions.workflow_draft_revision_id", ondelete="CASCADE"
        )
    )
    rule_set_version: Mapped[str] = mapped_column(String(64))
    status: Mapped[ValidationResultStatus] = mapped_column(
        Enum(ValidationResultStatus, native_enum=False)
    )
    blocking_issue_count: Mapped[int] = mapped_column(Integer, default=0)
    advisory_issue_count: Mapped[int] = mapped_column(Integer, default=0)
    findings_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    report_artifact_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("artifacts.artifact_id"), nullable=True
    )
    executed_by_principal_id: Mapped[UUID] = mapped_column(
        ForeignKey("principal_identities.principal_identity_id")
    )
    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


class WorkflowVersionBundle(Base, TimestampMixin):
    __tablename__ = "workflow_version_bundles"
    __table_args__ = (UniqueConstraint("workflow_lineage_id", "version_sequence"),)

    workflow_version_bundle_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    workflow_lineage_id: Mapped[UUID] = mapped_column(
        ForeignKey("workflow_lineages.workflow_lineage_id", ondelete="CASCADE")
    )
    scope_type: Mapped[str] = mapped_column(String(32))
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    version_sequence: Mapped[int] = mapped_column(Integer)
    display_version: Mapped[str] = mapped_column(String(32))
    status: Mapped[WorkflowVersionStatus] = mapped_column(
        Enum(WorkflowVersionStatus, native_enum=False),
        default=WorkflowVersionStatus.PUBLISHED,
    )
    published_from_draft_id: Mapped[UUID] = mapped_column(
        ForeignKey("workflow_drafts.workflow_draft_id")
    )
    published_from_revision_id: Mapped[UUID] = mapped_column(
        ForeignKey("workflow_draft_revisions.workflow_draft_revision_id")
    )
    validation_result_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("validation_results.validation_result_id"), nullable=True
    )
    previous_version_bundle_id: Mapped[UUID | None] = mapped_column(nullable=True)
    compiled_bundle_artifact_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("artifacts.artifact_id"), nullable=True
    )
    compiled_bundle_digest: Mapped[str | None] = mapped_column(
        String(64), nullable=True
    )
    compiler_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    summary_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    published_by_principal_id: Mapped[UUID] = mapped_column(
        ForeignKey("principal_identities.principal_identity_id")
    )
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


class RegistrySharingGrant(Base):
    __tablename__ = "registry_sharing_grants"
    __table_args__ = (
        UniqueConstraint("workflow_version_bundle_id", "grantee_tenant_id"),
    )

    registry_sharing_grant_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    workflow_version_bundle_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "workflow_version_bundles.workflow_version_bundle_id", ondelete="CASCADE"
        )
    )
    grantee_tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.tenant_id"))
    status: Mapped[RegistrySharingGrantStatus] = mapped_column(
        Enum(RegistrySharingGrantStatus, native_enum=False),
        default=RegistrySharingGrantStatus.ACTIVE,
    )
    granted_by_principal_id: Mapped[UUID] = mapped_column(
        ForeignKey("principal_identities.principal_identity_id")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
