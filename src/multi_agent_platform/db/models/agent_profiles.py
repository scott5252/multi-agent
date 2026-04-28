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


class AgentRuntimeProfile(Base, TimestampMixin):
    __tablename__ = "agent_runtime_profiles"
    __table_args__ = (
        CheckConstraint(
            "(scope_type = 'platform' AND tenant_id IS NULL) OR "
            "(scope_type = 'tenant' AND tenant_id IS NOT NULL)",
            name="ck_agent_runtime_profiles_scope_tenant",
        ),
        Index(
            "ix_agent_runtime_profiles_scope_key",
            "scope_type",
            "tenant_id",
            "agent_kind",
            "agent_key",
            unique=True,
        ),
    )

    agent_runtime_profile_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    scope_type: Mapped[str] = mapped_column(String(32))
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    agent_key: Mapped[str] = mapped_column(String(128))
    agent_kind: Mapped[str] = mapped_column(String(32))
    display_name: Mapped[str] = mapped_column(String(255))
    purpose: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(32), default="active")
    latest_draft_id: Mapped[UUID | None] = mapped_column(nullable=True)
    active_profile_version_id: Mapped[UUID | None] = mapped_column(nullable=True)
    created_by_principal_id: Mapped[str] = mapped_column(String(128))


class AgentProfileDraft(Base, TimestampMixin):
    __tablename__ = "agent_profile_drafts"
    __table_args__ = (
        Index(
            "ix_agent_profile_drafts_profile_status",
            "agent_runtime_profile_id",
            "status",
        ),
    )

    agent_profile_draft_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    agent_runtime_profile_id: Mapped[UUID] = mapped_column(
        ForeignKey("agent_runtime_profiles.agent_runtime_profile_id")
    )
    scope_type: Mapped[str] = mapped_column(String(32))
    tenant_id: Mapped[UUID | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="active")
    current_revision_number: Mapped[int] = mapped_column(Integer, default=0)
    latest_revision_id: Mapped[UUID | None] = mapped_column(nullable=True)
    created_from_profile_version_id: Mapped[UUID | None] = mapped_column(nullable=True)
    last_validation_result_id: Mapped[UUID | None] = mapped_column(nullable=True)
    created_by_principal_id: Mapped[str] = mapped_column(String(128))
    last_edited_by_principal_id: Mapped[str] = mapped_column(String(128))


class AgentProfileDraftRevision(Base):
    __tablename__ = "agent_profile_draft_revisions"
    __table_args__ = (
        UniqueConstraint(
            "agent_profile_draft_id",
            "revision_number",
            name="uq_agent_profile_draft_revisions_draft_number",
        ),
        Index(
            "ix_agent_profile_draft_revisions_draft",
            "agent_profile_draft_id",
            "revision_number",
        ),
    )

    agent_profile_draft_revision_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    agent_profile_draft_id: Mapped[UUID] = mapped_column(
        ForeignKey("agent_profile_drafts.agent_profile_draft_id")
    )
    revision_number: Mapped[int] = mapped_column(Integer)
    agent_key: Mapped[str] = mapped_column(String(128))
    agent_kind: Mapped[str] = mapped_column(String(32))
    purpose: Mapped[str] = mapped_column(String(500))
    prompt_references_json: Mapped[list[dict[str, object]]] = mapped_column(
        JSON, default=list
    )
    model_routing_hints_json: Mapped[dict[str, object]] = mapped_column(
        JSON, default=dict
    )
    memory_scope_policy_json: Mapped[dict[str, object]] = mapped_column(
        JSON, default=dict
    )
    skill_requirements_json: Mapped[list[dict[str, object]]] = mapped_column(
        JSON, default=list
    )
    tool_policy_expectations_json: Mapped[list[dict[str, object]]] = mapped_column(
        JSON, default=list
    )
    output_contract_expectations_json: Mapped[dict[str, object]] = mapped_column(
        JSON, default=dict
    )
    test_suite_requirements_json: Mapped[list[dict[str, object]]] = mapped_column(
        JSON, default=list
    )
    safe_summary_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    created_by_principal_id: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class AgentProfileValidationResult(Base):
    __tablename__ = "agent_profile_validation_results"
    __table_args__ = (
        Index(
            "ix_agent_profile_validation_results_revision",
            "agent_profile_draft_revision_id",
            "executed_at",
        ),
    )

    agent_profile_validation_result_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    agent_profile_draft_revision_id: Mapped[UUID] = mapped_column(
        ForeignKey("agent_profile_draft_revisions.agent_profile_draft_revision_id")
    )
    rule_set_version: Mapped[str] = mapped_column(
        String(64), default="profile-runtime-v1"
    )
    status: Mapped[str] = mapped_column(String(32))
    blocking_issue_count: Mapped[int] = mapped_column(Integer, default=0)
    advisory_issue_count: Mapped[int] = mapped_column(Integer, default=0)
    findings_json: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list)
    referenced_prompt_version_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    referenced_model_routing_scope_ids: Mapped[list[str]] = mapped_column(
        JSON, default=list
    )
    referenced_memory_policy_hash: Mapped[str | None] = mapped_column(
        String(128), nullable=True
    )
    referenced_skill_requirement_hash: Mapped[str | None] = mapped_column(
        String(128), nullable=True
    )
    executed_by_principal_id: Mapped[str] = mapped_column(String(128))
    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class AgentProfileVersion(Base):
    __tablename__ = "agent_profile_versions"
    __table_args__ = (
        UniqueConstraint(
            "agent_runtime_profile_id",
            "version_sequence",
            name="uq_agent_profile_versions_profile_sequence",
        ),
        Index(
            "ix_agent_profile_versions_scope_key",
            "scope_type",
            "tenant_id",
            "agent_kind",
            "agent_key",
            "status",
        ),
    )

    agent_profile_version_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    agent_runtime_profile_id: Mapped[UUID] = mapped_column(
        ForeignKey("agent_runtime_profiles.agent_runtime_profile_id")
    )
    scope_type: Mapped[str] = mapped_column(String(32))
    tenant_id: Mapped[UUID | None] = mapped_column(nullable=True)
    agent_key: Mapped[str] = mapped_column(String(128))
    agent_kind: Mapped[str] = mapped_column(String(32))
    version_sequence: Mapped[int] = mapped_column(Integer)
    display_version: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), default="active")
    activated_from_draft_id: Mapped[UUID] = mapped_column(
        ForeignKey("agent_profile_drafts.agent_profile_draft_id")
    )
    activated_from_revision_id: Mapped[UUID] = mapped_column(
        ForeignKey("agent_profile_draft_revisions.agent_profile_draft_revision_id")
    )
    validation_result_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "agent_profile_validation_results.agent_profile_validation_result_id"
        )
    )
    purpose: Mapped[str] = mapped_column(String(500))
    prompt_references_json: Mapped[list[dict[str, object]]] = mapped_column(
        JSON, default=list
    )
    model_routing_hints_json: Mapped[dict[str, object]] = mapped_column(
        JSON, default=dict
    )
    memory_scope_policy_json: Mapped[dict[str, object]] = mapped_column(
        JSON, default=dict
    )
    skill_requirements_json: Mapped[list[dict[str, object]]] = mapped_column(
        JSON, default=list
    )
    tool_policy_expectations_json: Mapped[list[dict[str, object]]] = mapped_column(
        JSON, default=list
    )
    output_contract_expectations_json: Mapped[dict[str, object]] = mapped_column(
        JSON, default=dict
    )
    test_suite_requirements_json: Mapped[list[dict[str, object]]] = mapped_column(
        JSON, default=list
    )
    safe_summary_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    activated_by_principal_id: Mapped[str] = mapped_column(String(128))
    activated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    activation_reason: Mapped[str] = mapped_column(String(500))
    retired_by_principal_id: Mapped[str | None] = mapped_column(
        String(128), nullable=True
    )
    retired_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    retirement_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)


class TenantProfileVersionGrant(Base):
    __tablename__ = "tenant_profile_version_grants"
    __table_args__ = (
        Index(
            "ix_tenant_profile_version_grants_active",
            "agent_profile_version_id",
            "grantee_tenant_id",
            "status",
        ),
    )

    tenant_profile_version_grant_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    agent_profile_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("agent_profile_versions.agent_profile_version_id")
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


class ActiveAgentProfilePointer(Base):
    __tablename__ = "active_agent_profile_pointers"
    __table_args__ = (
        Index(
            "ix_active_agent_profile_pointer_lookup",
            "scope_type",
            "tenant_id",
            "agent_kind",
            "agent_key",
            unique=True,
        ),
    )

    active_agent_profile_pointer_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    scope_type: Mapped[str] = mapped_column(String(32))
    tenant_id: Mapped[UUID | None] = mapped_column(nullable=True)
    agent_kind: Mapped[str] = mapped_column(String(32))
    agent_key: Mapped[str] = mapped_column(String(128))
    active_profile_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("agent_profile_versions.agent_profile_version_id")
    )
    activated_by_principal_id: Mapped[str] = mapped_column(String(128))
    activated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    activation_reason: Mapped[str] = mapped_column(Text, default="")
    expected_previous_version_id: Mapped[UUID | None] = mapped_column(nullable=True)
