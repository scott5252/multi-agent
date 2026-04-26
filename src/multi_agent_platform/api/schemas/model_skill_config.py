from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from multi_agent_platform.config.model_skill import (
    ConfigKind,
    ModelSkillErrorCategory,
    PolicyOutcome,
    ScopeSelector,
)


class ModelSkillErrorResponse(BaseModel):
    category: ModelSkillErrorCategory
    message: str
    trace_id: str | None = None
    remediation_hint: str | None = None
    safe_identifiers: dict[str, str] = Field(default_factory=dict)


class ModelRoutingCreateRequest(BaseModel):
    scope: ScopeSelector
    provider_key: str
    model_id: str
    routing_parameters: dict[str, object] = Field(default_factory=dict)
    activate: bool = False
    expected_active_version_id: UUID | None = None
    reason: str


class PromptReferenceCreateRequest(BaseModel):
    scope: ScopeSelector
    prompt_id: UUID
    prompt_version_id: UUID
    prompt_digest: str
    activate: bool = False
    expected_active_version_id: UUID | None = None
    reason: str


class SkillBindingCreateRequest(BaseModel):
    scope: ScopeSelector
    skill_slug: str
    skill_version: str
    allowed_contexts: list[str] = Field(default_factory=list)
    runtime_ref_constraints: dict[str, object] = Field(default_factory=dict)
    activate: bool = False
    expected_active_version_id: UUID | None = None
    reason: str


class ToolPolicyCreateRequest(BaseModel):
    scope: ScopeSelector
    skill_slug: str | None = None
    tool_id: str
    allowed_action_categories: list[str]
    constraints: dict[str, object] = Field(default_factory=dict)
    activate: bool = False
    expected_active_version_id: UUID | None = None
    reason: str


class OutboundDomainPolicyCreateRequest(BaseModel):
    scope: ScopeSelector
    tool_id: str
    action_category: str | None = None
    allowed_domain_patterns: list[str]
    allowed_schemes: list[str] = Field(default_factory=list)
    allowed_ports: list[int] = Field(default_factory=list)
    activate: bool = False
    expected_active_version_id: UUID | None = None
    reason: str


class SecretReferenceCreateRequest(BaseModel):
    scope: ScopeSelector
    secret_reference_id: str
    provider_key: str
    external_reference: str
    allowed_scopes: dict[str, object] = Field(default_factory=dict)
    rotation_metadata: dict[str, object] = Field(default_factory=dict)
    activate: bool = False
    expected_active_version_id: UUID | None = None
    reason: str


class CredentialRequirementCreateRequest(BaseModel):
    scope: ScopeSelector
    tool_id: str
    action_category: str | None = None
    credential_kind: str
    secret_reference_version_id: UUID | None = None
    delegated_credential_link_id: UUID | None = None
    allowed_credential_scope: dict[str, object] = Field(default_factory=dict)
    expiry_policy: dict[str, object] = Field(default_factory=dict)
    activate: bool = False
    expected_active_version_id: UUID | None = None
    reason: str


class ConfigVersionResponse(BaseModel):
    config_kind: ConfigKind
    version_id: UUID
    tenant_id: UUID
    scope: ScopeSelector
    status: str
    active: bool
    version_sequence: int
    activation_reason: str
    redacted_summary: dict[str, object] = Field(default_factory=dict)


class ActivationRequest(BaseModel):
    expected_active_version_id: UUID | None = None
    reason: str


class ActivationResponse(BaseModel):
    active_configuration_pointer_id: UUID
    active_version_id: UUID
    prior_version_id: UUID | None = None
    config_kind: ConfigKind
    scope_hash: str


class ModelPreviewRequest(ScopeSelector):
    pass


class ModelPreviewResponse(BaseModel):
    model_routing_version_id: UUID
    model_provider_key: str
    model_id: str
    model_source_scope: str
    prompt_reference_version_id: UUID
    prompt_id: UUID
    prompt_version_id: UUID
    prompt_digest: str
    prompt_source_scope: str
    evaluated_version_ids: list[UUID]


class ToolPreviewRequest(ScopeSelector):
    skill_slug: str | None = None
    skill_version: str | None = None
    use_context: str = "runtime_step"
    tool_id: str
    action_category: str
    destination_url: str | None = None
    credential_context: dict[str, object] = Field(default_factory=dict)


class ToolPreviewResponse(BaseModel):
    outcome: PolicyOutcome
    denial_category: ModelSkillErrorCategory | None = None
    safe_reason: str
    evaluated_version_ids: list[UUID] = Field(default_factory=list)
    winning_version_ids: list[UUID] = Field(default_factory=list)
    authorized_secret_reference_ids: list[str] = Field(default_factory=list)
    authorized_delegated_credential_link_ids: list[UUID] = Field(default_factory=list)


class HistoryRecordResponse(BaseModel):
    configuration_audit_record_id: UUID
    actor_principal_id: UUID | None
    action: str
    config_kind: ConfigKind
    affected_scope: dict[str, object]
    prior_version_id: UUID | None
    new_version_id: UUID | None
    reason: str
    created_at: datetime
    redacted_diff_summary: dict[str, object] = Field(default_factory=dict)


class HistoryResponse(BaseModel):
    items: list[HistoryRecordResponse]


class RollbackRequest(BaseModel):
    target_version_id: UUID
    expected_active_version_id: UUID | None = None
    reason: str


class RollbackResponse(BaseModel):
    rollback_record_id: UUID
    active_version_id: UUID
    audit_record_id: UUID


class RunProvenanceResponse(BaseModel):
    workflow_run_id: UUID
    resolved_execution_configuration_id: UUID | None = None
    resolution_digest: str | None = None
    decisions: list[dict[str, object]] = Field(default_factory=list)
    migrations: list[dict[str, object]] = Field(default_factory=list)
