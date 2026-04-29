from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from multi_agent_platform.db.base import Base, TimestampMixin, utcnow


class SkillPackageLifecycleState(StrEnum):
    DRAFT = "draft"
    APPROVED = "approved"
    RETIRED = "retired"
    QUARANTINED = "quarantined"


class SkillVersionLifecycleState(StrEnum):
    CANDIDATE = "candidate"
    VALIDATED = "validated"
    PUBLISHED = "published"
    WITHDRAWN = "withdrawn_from_new_installs"
    QUARANTINED = "quarantined"


class SkillInstallationState(StrEnum):
    INSTALLED = "installed"
    CONFIGURING = "configuring"
    TESTING = "testing"
    READY = "ready"
    BLOCKED = "blocked"
    QUARANTINED = "quarantined"
    RETIRED = "retired"


class SkillJobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERRORED = "errored"
    BLOCKED = "blocked"


class SkillPackage(Base, TimestampMixin):
    __tablename__ = "skill_packages"
    __table_args__ = (Index("ix_skill_packages_slug", "slug", unique=True),)

    skill_package_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    slug: Mapped[str] = mapped_column(String(128), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text(), nullable=False)
    owner_principal_id: Mapped[str] = mapped_column(String(255), nullable=False)
    approval_status: Mapped[str] = mapped_column(String(64), default="approved")
    lifecycle_state: Mapped[SkillPackageLifecycleState] = mapped_column(
        Enum(SkillPackageLifecycleState, native_enum=False),
        default=SkillPackageLifecycleState.APPROVED,
    )
    safe_documentation_summary: Mapped[dict[str, object]] = mapped_column(
        JSON,
        default=dict,
    )
    latest_published_version: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )
    created_by_principal_id: Mapped[str] = mapped_column(String(255), nullable=False)
    retired_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    quarantined_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class SkillPackageVersion(Base):
    __tablename__ = "skill_package_versions"
    __table_args__ = (
        Index(
            "ix_skill_package_versions_package_semver",
            "skill_package_id",
            "semantic_version",
            unique=True,
        ),
        Index("ix_skill_package_versions_slug_semver", "slug", "semantic_version"),
    )

    skill_package_version_id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    skill_package_id: Mapped[UUID] = mapped_column(
        ForeignKey("skill_packages.skill_package_id"),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(String(128), nullable=False)
    semantic_version: Mapped[str] = mapped_column(String(64), nullable=False)
    manifest_digest: Mapped[str] = mapped_column(String(128), nullable=False)
    manifest_snapshot: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    safe_manifest_summary: Mapped[dict[str, object]] = mapped_column(
        JSON,
        default=dict,
    )
    artifact_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("artifacts.artifact_id"),
        nullable=True,
    )
    artifact_digest: Mapped[str] = mapped_column(String(128), nullable=False)
    documentation_artifact_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("artifacts.artifact_id"),
        nullable=True,
    )
    documentation_digest: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )
    fixture_artifact_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("artifacts.artifact_id"),
        nullable=True,
    )
    fixture_digest: Mapped[str | None] = mapped_column(String(128), nullable=True)
    compatibility_metadata: Mapped[dict[str, object]] = mapped_column(
        JSON,
        default=dict,
    )
    validation_status: Mapped[str] = mapped_column(String(64), default="pending")
    validation_summary: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    lifecycle_state: Mapped[SkillVersionLifecycleState] = mapped_column(
        Enum(SkillVersionLifecycleState, native_enum=False),
        default=SkillVersionLifecycleState.CANDIDATE,
    )
    availability_mode: Mapped[str] = mapped_column(
        String(64),
        default="selected_tenants",
    )
    published_by_principal_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    withdrawn_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    quarantined_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    runtime_blocked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
    )


class SkillPackageTenantGrant(Base):
    __tablename__ = "skill_package_tenant_grants"
    __table_args__ = (
        Index(
            "ix_skill_package_tenant_grants_version_tenant",
            "skill_package_version_id",
            "tenant_id",
            unique=True,
        ),
    )

    tenant_grant_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    skill_package_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("skill_package_versions.skill_package_version_id"),
        nullable=False,
    )
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"),
        nullable=True,
    )
    grant_mode: Mapped[str] = mapped_column(String(64), default="selected_tenant")
    status: Mapped[str] = mapped_column(String(64), default="active")
    granted_by_principal_id: Mapped[str] = mapped_column(String(255), nullable=False)
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    reason: Mapped[str | None] = mapped_column(Text(), nullable=True)
    audit_record_id: Mapped[UUID | None] = mapped_column(nullable=True)


class SkillInstallation(Base):
    __tablename__ = "skill_installations"
    __table_args__ = (
        Index(
            "ix_skill_installations_tenant_slug_version",
            "tenant_id",
            "slug",
            "installation_version",
            unique=True,
        ),
        Index("ix_skill_installations_tenant_state", "tenant_id", "readiness_state"),
    )

    skill_installation_id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.tenant_id"))
    skill_package_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("skill_package_versions.skill_package_version_id"),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(String(128), nullable=False)
    semantic_version: Mapped[str] = mapped_column(String(64), nullable=False)
    installation_version: Mapped[int] = mapped_column(Integer, nullable=False)
    previous_installation_id: Mapped[UUID | None] = mapped_column(nullable=True)
    manifest_digest: Mapped[str] = mapped_column(String(128), nullable=False)
    manifest_summary: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    artifact_digest: Mapped[str] = mapped_column(String(128), nullable=False)
    readiness_state: Mapped[SkillInstallationState] = mapped_column(
        Enum(SkillInstallationState, native_enum=False),
        default=SkillInstallationState.INSTALLED,
    )
    credential_status: Mapped[str] = mapped_column(String(64), default="pending")
    compatibility_status: Mapped[str] = mapped_column(String(64), default="pending")
    permission_status: Mapped[str] = mapped_column(String(64), default="pending")
    smoke_test_status: Mapped[str] = mapped_column(String(64), default="pending")
    binding_eligibility_status: Mapped[str] = mapped_column(
        String(64),
        default="denied",
    )
    policy_summary: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    findings: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list)
    quarantine_state: Mapped[str] = mapped_column(String(64), default="clear")
    runtime_blocked: Mapped[bool] = mapped_column(default=False)
    installed_by_principal_id: Mapped[str] = mapped_column(String(255), nullable=False)
    installed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    ready_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    retired_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    revision_token: Mapped[str] = mapped_column(String(128), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
    )


class SkillInstallationCredential(Base):
    __tablename__ = "skill_installation_credentials"
    __table_args__ = (
        Index(
            "ix_skill_installation_credentials_installation_requirement",
            "skill_installation_id",
            "requirement_key",
            unique=True,
        ),
    )

    credential_readiness_id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    skill_installation_id: Mapped[UUID] = mapped_column(
        ForeignKey("skill_installations.skill_installation_id"),
        nullable=False,
    )
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.tenant_id"))
    requirement_key: Mapped[str] = mapped_column(String(128), nullable=False)
    credential_kind: Mapped[str] = mapped_column(String(64), nullable=False)
    secret_reference_id: Mapped[UUID | None] = mapped_column(nullable=True)
    secret_reference_version_id: Mapped[UUID | None] = mapped_column(nullable=True)
    delegated_credential_link_id: Mapped[UUID | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(64), default="pending")
    failure_reason: Mapped[str | None] = mapped_column(Text(), nullable=True)
    safe_summary: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    configured_by_principal_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    configured_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_checked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    audit_record_id: Mapped[UUID | None] = mapped_column(nullable=True)


class SkillInstallationTest(Base):
    __tablename__ = "skill_installation_tests"
    __table_args__ = (
        Index(
            "ix_skill_installation_tests_installation_idempotency",
            "skill_installation_id",
            "idempotency_key",
            unique=True,
        ),
        Index("ix_skill_installation_tests_tenant_run", "tenant_id", "test_run_id"),
    )

    skill_installation_test_id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    skill_installation_id: Mapped[UUID] = mapped_column(
        ForeignKey("skill_installations.skill_installation_id"),
        nullable=False,
    )
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.tenant_id"))
    skill_package_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("skill_package_versions.skill_package_version_id"),
        nullable=False,
    )
    installation_version: Mapped[int] = mapped_column(Integer, nullable=False)
    fixture_key: Mapped[str] = mapped_column(String(128), nullable=False)
    test_run_id: Mapped[str] = mapped_column(String(128), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False)
    runner_status: Mapped[SkillJobStatus] = mapped_column(
        Enum(SkillJobStatus, native_enum=False),
        default=SkillJobStatus.QUEUED,
    )
    outcome: Mapped[str] = mapped_column(String(64), default="queued")
    credential_readiness_summary: Mapped[dict[str, object]] = mapped_column(
        JSON,
        default=dict,
    )
    policy_decision_summary: Mapped[dict[str, object]] = mapped_column(
        JSON,
        default=dict,
    )
    failure_reasons: Mapped[list[str]] = mapped_column(JSON, default=list)
    safe_output_summary: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    evidence_artifact_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("artifacts.artifact_id"),
        nullable=True,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    trace_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    audit_record_id: Mapped[UUID | None] = mapped_column(nullable=True)


class SkillQuarantineDecision(Base):
    __tablename__ = "skill_quarantine_decisions"
    __table_args__ = (
        Index("ix_skill_quarantine_decisions_target", "target_type", "target_id"),
    )

    quarantine_decision_id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    target_type: Mapped[str] = mapped_column(String(64), nullable=False)
    target_id: Mapped[str] = mapped_column(String(128), nullable=False)
    state: Mapped[str] = mapped_column(String(64), default="quarantined")
    reason: Mapped[str] = mapped_column(Text(), nullable=False)
    actor_principal_id: Mapped[str] = mapped_column(String(255), nullable=False)
    blocks_new_installs: Mapped[bool] = mapped_column(default=True)
    blocks_readiness: Mapped[bool] = mapped_column(default=True)
    blocks_bindings: Mapped[bool] = mapped_column(default=True)
    blocks_runtime: Mapped[bool] = mapped_column(default=True)
    safe_summary: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class SkillAuditRecord(Base):
    __tablename__ = "skill_audit_records"
    __table_args__ = (
        Index("ix_skill_audit_records_package", "package_slug", "package_version"),
        Index("ix_skill_audit_records_tenant_created", "tenant_id", "created_at"),
        Index("ix_skill_audit_records_installation", "skill_installation_id"),
    )

    skill_audit_record_id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    event_type: Mapped[str] = mapped_column(String(128), nullable=False)
    actor_principal_id: Mapped[str] = mapped_column(String(255), nullable=False)
    outcome: Mapped[str] = mapped_column(String(64), nullable=False)
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"),
        nullable=True,
    )
    skill_package_id: Mapped[UUID | None] = mapped_column(nullable=True)
    skill_package_version_id: Mapped[UUID | None] = mapped_column(nullable=True)
    skill_installation_id: Mapped[UUID | None] = mapped_column(nullable=True)
    package_slug: Mapped[str | None] = mapped_column(String(128), nullable=True)
    package_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    safe_summary: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    redaction_metadata: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    trace_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
