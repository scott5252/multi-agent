from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from multi_agent_platform.db.base import Base, TimestampMixin, utcnow


class ModelSkillProviderStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    RETIRED = "retired"


class ModelSkillVersionStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ROLLED_BACK_FROM = "rolled_back_from"
    ARCHIVED = "archived"


class ModelSkillConfigKind(StrEnum):
    MODEL_ROUTING = "model_routing"
    PROMPT_REFERENCE = "prompt_reference"
    SKILL_BINDING = "skill_binding"
    ALLOWED_TOOL_POLICY = "allowed_tool_policy"
    OUTBOUND_DOMAIN_POLICY = "outbound_domain_policy"
    SECRET_REFERENCE = "secret_reference"
    CREDENTIAL_REQUIREMENT = "credential_requirement"


class RuntimeDecisionOutcome(StrEnum):
    ALLOW = "allow"
    DENY = "deny"


class ModelProviderCatalogEntry(Base, TimestampMixin):
    __tablename__ = "model_provider_catalog_entries"
    __table_args__ = (
        Index(
            "ix_model_provider_entries_tenant_provider_model",
            "tenant_id",
            "provider_key",
            "model_id",
            unique=True,
        ),
    )

    model_provider_entry_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    provider_key: Mapped[str] = mapped_column(String(64))
    model_id: Mapped[str] = mapped_column(String(128))
    display_name: Mapped[str] = mapped_column(String(255))
    capabilities: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    cost_metadata: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    status: Mapped[ModelSkillProviderStatus] = mapped_column(
        Enum(ModelSkillProviderStatus, native_enum=False),
        default=ModelSkillProviderStatus.ACTIVE,
    )
    retired_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class ModelRoutingVersion(Base):
    __tablename__ = "model_routing_versions"

    model_routing_version_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.tenant_id"))
    scope_type: Mapped[str] = mapped_column(String(32))
    workflow_lineage_id: Mapped[UUID | None] = mapped_column(nullable=True)
    workflow_version_bundle_id: Mapped[UUID | None] = mapped_column(nullable=True)
    agent_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    step_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    scope_hash: Mapped[str] = mapped_column(String(64), index=True)
    model_provider_entry_id: Mapped[UUID] = mapped_column(
        ForeignKey("model_provider_catalog_entries.model_provider_entry_id")
    )
    routing_parameters: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    status: Mapped[ModelSkillVersionStatus] = mapped_column(
        Enum(ModelSkillVersionStatus, native_enum=False),
        default=ModelSkillVersionStatus.DRAFT,
    )
    version_sequence: Mapped[int] = mapped_column(Integer, default=1)
    previous_version_id: Mapped[UUID | None] = mapped_column(nullable=True)
    created_by_principal_id: Mapped[UUID] = mapped_column(
        ForeignKey("principal_identities.principal_identity_id")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    activation_reason: Mapped[str] = mapped_column(Text())
    effective_from: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    effective_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    redacted_summary: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)


class PromptReferenceVersion(Base):
    __tablename__ = "prompt_reference_versions"

    prompt_reference_version_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.tenant_id"))
    scope_type: Mapped[str] = mapped_column(String(32))
    workflow_lineage_id: Mapped[UUID | None] = mapped_column(nullable=True)
    workflow_version_bundle_id: Mapped[UUID | None] = mapped_column(nullable=True)
    agent_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    step_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    scope_hash: Mapped[str] = mapped_column(String(64), index=True)
    prompt_id: Mapped[UUID] = mapped_column()
    prompt_version_id: Mapped[UUID] = mapped_column()
    prompt_digest: Mapped[str] = mapped_column(String(128))
    status: Mapped[ModelSkillVersionStatus] = mapped_column(
        Enum(ModelSkillVersionStatus, native_enum=False),
        default=ModelSkillVersionStatus.DRAFT,
    )
    version_sequence: Mapped[int] = mapped_column(Integer, default=1)
    previous_version_id: Mapped[UUID | None] = mapped_column(nullable=True)
    created_by_principal_id: Mapped[UUID] = mapped_column(
        ForeignKey("principal_identities.principal_identity_id")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    activation_reason: Mapped[str] = mapped_column(Text())
    redacted_summary: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)


class SkillBindingVersion(Base):
    __tablename__ = "skill_binding_versions"

    skill_binding_version_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.tenant_id"))
    workflow_lineage_id: Mapped[UUID | None] = mapped_column(nullable=True)
    workflow_version_bundle_id: Mapped[UUID | None] = mapped_column(nullable=True)
    agent_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    scope_hash: Mapped[str] = mapped_column(String(64), index=True)
    skill_slug: Mapped[str] = mapped_column(String(128))
    skill_version: Mapped[str] = mapped_column(String(64))
    allowed_contexts: Mapped[list[str]] = mapped_column(JSON, default=list)
    runtime_ref_constraints: Mapped[dict[str, object]] = mapped_column(
        JSON, default=dict
    )
    status: Mapped[ModelSkillVersionStatus] = mapped_column(
        Enum(ModelSkillVersionStatus, native_enum=False),
        default=ModelSkillVersionStatus.DRAFT,
    )
    version_sequence: Mapped[int] = mapped_column(Integer, default=1)
    previous_version_id: Mapped[UUID | None] = mapped_column(nullable=True)
    created_by_principal_id: Mapped[UUID] = mapped_column(
        ForeignKey("principal_identities.principal_identity_id")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    activation_reason: Mapped[str] = mapped_column(Text())
    redacted_summary: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)


class AllowedToolPolicyVersion(Base):
    __tablename__ = "allowed_tool_policy_versions"

    allowed_tool_policy_version_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.tenant_id"))
    workflow_lineage_id: Mapped[UUID | None] = mapped_column(nullable=True)
    workflow_version_bundle_id: Mapped[UUID | None] = mapped_column(nullable=True)
    agent_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    step_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    scope_hash: Mapped[str] = mapped_column(String(64), index=True)
    skill_slug: Mapped[str | None] = mapped_column(String(128), nullable=True)
    tool_id: Mapped[str] = mapped_column(String(128))
    allowed_action_categories: Mapped[list[str]] = mapped_column(JSON, default=list)
    constraints: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    status: Mapped[ModelSkillVersionStatus] = mapped_column(
        Enum(ModelSkillVersionStatus, native_enum=False),
        default=ModelSkillVersionStatus.DRAFT,
    )
    version_sequence: Mapped[int] = mapped_column(Integer, default=1)
    previous_version_id: Mapped[UUID | None] = mapped_column(nullable=True)
    created_by_principal_id: Mapped[UUID] = mapped_column(
        ForeignKey("principal_identities.principal_identity_id")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    activation_reason: Mapped[str] = mapped_column(Text())
    redacted_summary: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)


class OutboundDomainPolicyVersion(Base):
    __tablename__ = "outbound_domain_policy_versions"

    outbound_domain_policy_version_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.tenant_id"))
    workflow_lineage_id: Mapped[UUID | None] = mapped_column(nullable=True)
    workflow_version_bundle_id: Mapped[UUID | None] = mapped_column(nullable=True)
    agent_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    step_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    scope_hash: Mapped[str] = mapped_column(String(64), index=True)
    tool_id: Mapped[str] = mapped_column(String(128))
    action_category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    allowed_domain_patterns: Mapped[list[str]] = mapped_column(JSON, default=list)
    allowed_schemes: Mapped[list[str]] = mapped_column(JSON, default=list)
    allowed_ports: Mapped[list[int]] = mapped_column(JSON, default=list)
    status: Mapped[ModelSkillVersionStatus] = mapped_column(
        Enum(ModelSkillVersionStatus, native_enum=False),
        default=ModelSkillVersionStatus.DRAFT,
    )
    version_sequence: Mapped[int] = mapped_column(Integer, default=1)
    previous_version_id: Mapped[UUID | None] = mapped_column(nullable=True)
    created_by_principal_id: Mapped[UUID] = mapped_column(
        ForeignKey("principal_identities.principal_identity_id")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    activation_reason: Mapped[str] = mapped_column(Text())
    redacted_summary: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)


class SecretReferenceVersion(Base):
    __tablename__ = "model_skill_secret_reference_versions"

    secret_reference_version_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.tenant_id"))
    scope_hash: Mapped[str] = mapped_column(String(64), index=True)
    secret_reference_id: Mapped[str] = mapped_column(String(255))
    provider_key: Mapped[str] = mapped_column(String(64))
    external_reference: Mapped[str] = mapped_column(String(512))
    allowed_scopes: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    status: Mapped[ModelSkillVersionStatus] = mapped_column(
        Enum(ModelSkillVersionStatus, native_enum=False),
        default=ModelSkillVersionStatus.DRAFT,
    )
    version_sequence: Mapped[int] = mapped_column(Integer, default=1)
    previous_version_id: Mapped[UUID | None] = mapped_column(nullable=True)
    created_by_principal_id: Mapped[UUID] = mapped_column(
        ForeignKey("principal_identities.principal_identity_id")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    activation_reason: Mapped[str] = mapped_column(Text())
    rotation_metadata: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    redacted_summary: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)


class ToolCredentialRequirementVersion(Base):
    __tablename__ = "tool_credential_requirement_versions"

    tool_credential_requirement_version_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.tenant_id"))
    workflow_lineage_id: Mapped[UUID | None] = mapped_column(nullable=True)
    workflow_version_bundle_id: Mapped[UUID | None] = mapped_column(nullable=True)
    agent_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    step_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    scope_hash: Mapped[str] = mapped_column(String(64), index=True)
    tool_id: Mapped[str] = mapped_column(String(128))
    action_category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    credential_kind: Mapped[str] = mapped_column(String(64))
    secret_reference_version_id: Mapped[UUID | None] = mapped_column(nullable=True)
    delegated_credential_link_id: Mapped[UUID | None] = mapped_column(nullable=True)
    allowed_credential_scope: Mapped[dict[str, object]] = mapped_column(
        JSON, default=dict
    )
    expiry_policy: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    status: Mapped[ModelSkillVersionStatus] = mapped_column(
        Enum(ModelSkillVersionStatus, native_enum=False),
        default=ModelSkillVersionStatus.DRAFT,
    )
    version_sequence: Mapped[int] = mapped_column(Integer, default=1)
    previous_version_id: Mapped[UUID | None] = mapped_column(nullable=True)
    created_by_principal_id: Mapped[UUID] = mapped_column(
        ForeignKey("principal_identities.principal_identity_id")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    activation_reason: Mapped[str] = mapped_column(Text())
    redacted_summary: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)


class ActiveConfigurationPointer(Base):
    __tablename__ = "active_configuration_pointers"
    __table_args__ = (
        Index(
            "ix_active_configuration_pointer_singleton",
            "tenant_id",
            "config_kind",
            "scope_hash",
            unique=True,
        ),
    )

    active_configuration_pointer_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.tenant_id"))
    config_kind: Mapped[ModelSkillConfigKind] = mapped_column(
        Enum(ModelSkillConfigKind, native_enum=False)
    )
    scope_hash: Mapped[str] = mapped_column(String(64))
    scope_selectors: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    active_version_id: Mapped[UUID] = mapped_column()
    activated_by_principal_id: Mapped[UUID] = mapped_column(
        ForeignKey("principal_identities.principal_identity_id")
    )
    activated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    activation_reason: Mapped[str] = mapped_column(Text())
    expected_previous_version_id: Mapped[UUID | None] = mapped_column(nullable=True)


class ResolvedExecutionConfiguration(Base):
    __tablename__ = "resolved_execution_configurations"
    __table_args__ = (
        Index(
            "ix_resolved_execution_configuration_run",
            "tenant_id",
            "workflow_run_id",
            unique=True,
        ),
    )

    resolved_execution_configuration_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.tenant_id"))
    workflow_run_id: Mapped[UUID] = mapped_column()
    run_bundle_id: Mapped[UUID] = mapped_column()
    bundle_digest: Mapped[str] = mapped_column(String(128))
    workflow_version_bundle_id: Mapped[UUID] = mapped_column()
    accepted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    resolved_by_principal_id: Mapped[UUID | None] = mapped_column(nullable=True)
    model_routing_version_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    prompt_reference_version_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    skill_binding_version_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    allowed_tool_policy_version_ids: Mapped[list[str]] = mapped_column(
        JSON, default=list
    )
    outbound_domain_policy_version_ids: Mapped[list[str]] = mapped_column(
        JSON, default=list
    )
    secret_reference_version_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    credential_requirement_version_ids: Mapped[list[str]] = mapped_column(
        JSON, default=list
    )
    resolution_digest: Mapped[str] = mapped_column(String(64))
    trace_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    redacted_summary: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)


class RuntimePolicyDecision(Base):
    __tablename__ = "runtime_policy_decisions"
    __table_args__ = (
        Index(
            "ix_runtime_policy_decisions_idempotency",
            "tenant_id",
            "workflow_run_id",
            "decision_category",
            "idempotency_key",
            unique=True,
        ),
    )

    runtime_policy_decision_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.tenant_id"))
    workflow_run_id: Mapped[UUID] = mapped_column()
    run_step_id: Mapped[UUID | None] = mapped_column(nullable=True)
    run_bundle_id: Mapped[UUID | None] = mapped_column(nullable=True)
    agent_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    step_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    decision_category: Mapped[str] = mapped_column(String(64))
    requested_resource: Mapped[str] = mapped_column(String(255))
    requested_action: Mapped[str | None] = mapped_column(String(128), nullable=True)
    destination_host: Mapped[str | None] = mapped_column(String(255), nullable=True)
    outcome: Mapped[RuntimeDecisionOutcome] = mapped_column(
        Enum(RuntimeDecisionOutcome, native_enum=False)
    )
    denial_category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    safe_reason: Mapped[str] = mapped_column(Text())
    evaluated_version_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    winning_version_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    source_scopes: Mapped[list[str]] = mapped_column(JSON, default=list)
    idempotency_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    trace_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    redacted_metadata: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)


class ConfigurationAuditRecord(Base):
    __tablename__ = "configuration_audit_records"

    configuration_audit_record_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.tenant_id"))
    actor_principal_id: Mapped[UUID | None] = mapped_column(nullable=True)
    actor_role: Mapped[str | None] = mapped_column(String(64), nullable=True)
    action: Mapped[str] = mapped_column(String(64))
    config_kind: Mapped[ModelSkillConfigKind] = mapped_column(
        Enum(ModelSkillConfigKind, native_enum=False)
    )
    affected_scope: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    prior_version_id: Mapped[UUID | None] = mapped_column(nullable=True)
    new_version_id: Mapped[UUID | None] = mapped_column(nullable=True)
    reason: Mapped[str] = mapped_column(Text())
    request_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    trace_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    redacted_diff_summary: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class ConfigurationRollbackRecord(Base):
    __tablename__ = "configuration_rollback_records"

    configuration_rollback_record_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.tenant_id"))
    config_kind: Mapped[ModelSkillConfigKind] = mapped_column(
        Enum(ModelSkillConfigKind, native_enum=False)
    )
    scope_hash: Mapped[str] = mapped_column(String(64))
    from_version_id: Mapped[UUID] = mapped_column()
    to_version_id: Mapped[UUID] = mapped_column()
    actor_principal_id: Mapped[UUID | None] = mapped_column(nullable=True)
    reason: Mapped[str] = mapped_column(Text())
    configuration_audit_record_id: Mapped[UUID | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class RunConfigurationMigrationRecord(Base):
    __tablename__ = "run_configuration_migration_records"

    run_configuration_migration_record_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.tenant_id"))
    workflow_run_id: Mapped[UUID] = mapped_column()
    from_resolution_digest: Mapped[str] = mapped_column(String(64))
    to_resolution_digest: Mapped[str] = mapped_column(String(64))
    old_version_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    new_version_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    compatibility_status: Mapped[str] = mapped_column(String(64))
    approval_record_id: Mapped[UUID | None] = mapped_column(nullable=True)
    actor_principal_id: Mapped[UUID | None] = mapped_column(nullable=True)
    reason: Mapped[str] = mapped_column(Text())
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    trace_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    redacted_summary: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
