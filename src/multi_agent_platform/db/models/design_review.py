from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from multi_agent_platform.db.base import Base, TimestampMixin, utcnow


class DesignReviewSessionStatus(StrEnum):
    DRAFT = "draft"
    REVIEWING = "reviewing"
    REVISION_REQUIRED = "revision_required"
    MANUAL_RESOLUTION = "manual_resolution"
    APPROVED = "approved"
    CANCELLED = "cancelled"
    FAILED = "failed"


class DesignReviewRoundStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    REVISION_REQUIRED = "revision_required"
    MANUAL_RESOLUTION = "manual_resolution"
    FAILED = "failed"


class DesignReviewerVerdictValue(StrEnum):
    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    BLOCKED = "blocked"
    SKIPPED = "skipped"
    FAILED = "failed"


class DesignQuorumDecisionStatus(StrEnum):
    PENDING = "pending"
    PASSED = "passed"
    REVISION_REQUIRED = "revision_required"
    MANUAL_RESOLUTION = "manual_resolution"
    FAILED = "failed"


class DesignQuorumNextAction(StrEnum):
    HANDOFF = "handoff"
    REVISE = "revise"
    MANUAL_DECISION = "manual_decision"
    RETRY = "retry"
    NONE = "none"


class DesignManualDecisionType(StrEnum):
    REVISE = "revise"
    APPROVE_EXCEPTION = "approve_exception"
    RETRY = "retry"
    CANCEL = "cancel"


class DesignDevelopmentHandoffStatus(StrEnum):
    PENDING = "pending"
    READY = "ready"
    EXPORTED = "exported"
    CANCELLED = "cancelled"


class DesignReviewSession(Base, TimestampMixin):
    __tablename__ = "design_review_sessions"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_design_review_sessions_tenant_idempotency",
        ),
        Index("ix_design_review_sessions_tenant_status", "tenant_id", "status"),
        Index(
            "ix_design_review_sessions_tenant_updated",
            "tenant_id",
            "updated_at",
        ),
    )

    design_review_session_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=False
    )
    status: Mapped[DesignReviewSessionStatus] = mapped_column(
        Enum(DesignReviewSessionStatus, native_enum=False),
        default=DesignReviewSessionStatus.DRAFT,
        nullable=False,
    )
    request_summary: Mapped[str] = mapped_column(Text(), nullable=False)
    active_revision_number: Mapped[int] = mapped_column(Integer, default=1)
    quorum_policy_key: Mapped[str] = mapped_column(String(120), nullable=False)
    workflow_version_bundle_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("workflow_version_bundles.workflow_version_bundle_id"),
        nullable=True,
    )
    owner_principal_id: Mapped[str] = mapped_column(String(255), nullable=False)
    idempotency_key: Mapped[str | None] = mapped_column(String(160), nullable=True)


class DesignRevision(Base):
    __tablename__ = "design_revisions"
    __table_args__ = (
        UniqueConstraint(
            "design_review_session_id",
            "revision_number",
            name="uq_design_revisions_session_number",
        ),
        Index(
            "ix_design_revisions_tenant_session",
            "tenant_id",
            "design_review_session_id",
        ),
    )

    design_revision_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    design_review_session_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "design_review_sessions.design_review_session_id", ondelete="CASCADE"
        ),
        nullable=False,
    )
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=False
    )
    revision_number: Mapped[int] = mapped_column(Integer, nullable=False)
    author_role_key: Mapped[str] = mapped_column(String(120), nullable=False)
    safe_summary: Mapped[str] = mapped_column(Text(), nullable=False)
    artifact_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("artifacts.artifact_id"), nullable=True
    )
    payload_digest: Mapped[str] = mapped_column(String(128), nullable=False)
    previous_revision_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("design_revisions.design_revision_id"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class DesignReviewRound(Base):
    __tablename__ = "design_review_rounds"
    __table_args__ = (
        UniqueConstraint(
            "design_review_session_id",
            "round_number",
            name="uq_design_review_rounds_session_number",
        ),
        UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_design_review_rounds_tenant_idempotency",
        ),
        Index("ix_design_review_rounds_tenant_status", "tenant_id", "status"),
        Index("ix_design_review_rounds_session", "design_review_session_id"),
    )

    design_review_round_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    design_review_session_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "design_review_sessions.design_review_session_id", ondelete="CASCADE"
        ),
        nullable=False,
    )
    design_revision_id: Mapped[UUID] = mapped_column(
        ForeignKey("design_revisions.design_revision_id"),
        nullable=False,
    )
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=False
    )
    round_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[DesignReviewRoundStatus] = mapped_column(
        Enum(DesignReviewRoundStatus, native_enum=False),
        default=DesignReviewRoundStatus.PENDING,
        nullable=False,
    )
    workflow_run_id: Mapped[UUID | None] = mapped_column(nullable=True)
    reviewer_count: Mapped[int] = mapped_column(Integer, default=0)
    quorum_count: Mapped[int] = mapped_column(Integer, default=0)
    idempotency_key: Mapped[str | None] = mapped_column(String(160), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class DesignReviewerAssignment(Base):
    __tablename__ = "design_reviewer_assignments"
    __table_args__ = (
        UniqueConstraint(
            "design_review_round_id",
            "reviewer_key",
            name="uq_design_reviewer_assignments_round_reviewer",
        ),
        Index(
            "ix_design_reviewer_assignments_tenant_round",
            "tenant_id",
            "design_review_round_id",
        ),
    )

    design_reviewer_assignment_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    design_review_round_id: Mapped[UUID] = mapped_column(
        ForeignKey("design_review_rounds.design_review_round_id", ondelete="CASCADE"),
        nullable=False,
    )
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=False
    )
    reviewer_key: Mapped[str] = mapped_column(String(120), nullable=False)
    role_key: Mapped[str] = mapped_column(String(120), nullable=False)
    prompt_version_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("prompt_versions.prompt_version_id"), nullable=True
    )
    profile_version_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("agent_profile_versions.agent_profile_version_id"), nullable=True
    )
    provider_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class DesignReviewerVerdict(Base):
    __tablename__ = "design_reviewer_verdicts"
    __table_args__ = (
        UniqueConstraint(
            "design_review_round_id",
            "reviewer_key",
            name="uq_design_reviewer_verdicts_round_reviewer",
        ),
        UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_design_reviewer_verdicts_tenant_idempotency",
        ),
        Index(
            "ix_design_reviewer_verdicts_tenant_round",
            "tenant_id",
            "design_review_round_id",
        ),
    )

    design_reviewer_verdict_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    design_review_round_id: Mapped[UUID] = mapped_column(
        ForeignKey("design_review_rounds.design_review_round_id", ondelete="CASCADE"),
        nullable=False,
    )
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=False
    )
    reviewer_key: Mapped[str] = mapped_column(String(120), nullable=False)
    verdict: Mapped[DesignReviewerVerdictValue] = mapped_column(
        Enum(DesignReviewerVerdictValue, native_enum=False),
        nullable=False,
    )
    score: Mapped[int] = mapped_column(Integer, default=0)
    blocking_issue_count: Mapped[int] = mapped_column(Integer, default=0)
    safe_feedback_summary: Mapped[str] = mapped_column(Text(), nullable=False)
    artifact_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("artifacts.artifact_id"), nullable=True
    )
    output_digest: Mapped[str] = mapped_column(String(128), nullable=False)
    usage_summary: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    idempotency_key: Mapped[str | None] = mapped_column(String(160), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class DesignQuorumDecision(Base):
    __tablename__ = "design_quorum_decisions"
    __table_args__ = (
        UniqueConstraint(
            "design_review_round_id",
            name="uq_design_quorum_decisions_round",
        ),
        Index(
            "ix_design_quorum_decisions_tenant_round",
            "tenant_id",
            "design_review_round_id",
        ),
    )

    design_quorum_decision_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    design_review_round_id: Mapped[UUID] = mapped_column(
        ForeignKey("design_review_rounds.design_review_round_id", ondelete="CASCADE"),
        nullable=False,
    )
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=False
    )
    status: Mapped[DesignQuorumDecisionStatus] = mapped_column(
        Enum(DesignQuorumDecisionStatus, native_enum=False),
        nullable=False,
    )
    approval_count: Mapped[int] = mapped_column(Integer, default=0)
    blocking_issue_count: Mapped[int] = mapped_column(Integer, default=0)
    next_action: Mapped[DesignQuorumNextAction] = mapped_column(
        Enum(DesignQuorumNextAction, native_enum=False),
        default=DesignQuorumNextAction.NONE,
        nullable=False,
    )
    policy_version: Mapped[str] = mapped_column(String(120), nullable=False)
    safe_rationale: Mapped[str] = mapped_column(Text(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class DesignManualDecision(Base):
    __tablename__ = "design_manual_decisions"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_design_manual_decisions_tenant_idempotency",
        ),
        Index(
            "ix_design_manual_decisions_tenant_session",
            "tenant_id",
            "design_review_session_id",
        ),
    )

    design_manual_decision_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    design_review_session_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "design_review_sessions.design_review_session_id", ondelete="CASCADE"
        ),
        nullable=False,
    )
    design_review_round_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("design_review_rounds.design_review_round_id"),
        nullable=True,
    )
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=False
    )
    decision_type: Mapped[DesignManualDecisionType] = mapped_column(
        Enum(DesignManualDecisionType, native_enum=False),
        nullable=False,
    )
    actor_principal_id: Mapped[str] = mapped_column(String(255), nullable=False)
    safe_rationale: Mapped[str] = mapped_column(Text(), nullable=False)
    accepted_risk: Mapped[bool] = mapped_column(Boolean, default=False)
    idempotency_key: Mapped[str | None] = mapped_column(String(160), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class DesignDevelopmentHandoff(Base):
    __tablename__ = "design_development_handoffs"
    __table_args__ = (
        UniqueConstraint(
            "design_review_session_id",
            name="uq_design_development_handoffs_session",
        ),
        UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_design_development_handoffs_tenant_idempotency",
        ),
        Index("ix_design_development_handoffs_tenant_status", "tenant_id", "status"),
    )

    design_development_handoff_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    design_review_session_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "design_review_sessions.design_review_session_id", ondelete="CASCADE"
        ),
        nullable=False,
    )
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=False
    )
    approved_revision_id: Mapped[UUID] = mapped_column(
        ForeignKey("design_revisions.design_revision_id"),
        nullable=False,
    )
    artifact_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("artifacts.artifact_id"), nullable=True
    )
    safe_summary: Mapped[str] = mapped_column(Text(), nullable=False)
    output_digest: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[DesignDevelopmentHandoffStatus] = mapped_column(
        Enum(DesignDevelopmentHandoffStatus, native_enum=False),
        default=DesignDevelopmentHandoffStatus.READY,
        nullable=False,
    )
    idempotency_key: Mapped[str | None] = mapped_column(String(160), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
