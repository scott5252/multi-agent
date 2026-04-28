from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

ScopeType = Literal["platform", "tenant"]
AgentKind = Literal["agent", "sub_agent"]


class SafeError(BaseModel):
    code: str
    message: str
    trace_id: str | None = None
    details: dict[str, object] = Field(default_factory=dict)


class ScopedPayload(BaseModel):
    scope_type: ScopeType
    tenant_id: UUID | None = None

    @model_validator(mode="after")
    def validate_scope(self) -> ScopedPayload:
        if self.scope_type == "tenant" and self.tenant_id is None:
            raise ValueError("tenant_id is required for tenant scope")
        if self.scope_type == "platform" and self.tenant_id is not None:
            raise ValueError("tenant_id must be omitted for platform scope")
        return self


class ProfileCreate(ScopedPayload):
    agent_key: str = Field(min_length=1, max_length=128)
    agent_kind: AgentKind
    display_name: str = Field(min_length=1, max_length=255)
    purpose: str = Field(min_length=1, max_length=500)


class ProfileDraftSave(BaseModel):
    expected_revision_number: int = Field(ge=0)
    purpose: str = Field(min_length=1, max_length=500)
    prompt_references: list[dict[str, object]] = Field(default_factory=list)
    model_routing_hints: dict[str, object] = Field(default_factory=dict)
    memory_scope_policy: dict[str, object] = Field(default_factory=dict)
    skill_requirements: list[dict[str, object]] = Field(default_factory=list)
    tool_policy_expectations: list[dict[str, object]] = Field(default_factory=list)
    output_contract_expectations: dict[str, object] = Field(default_factory=dict)
    test_suite_requirements: list[dict[str, object]] = Field(default_factory=list)


class ValidationFinding(BaseModel):
    code: str
    severity: Literal["blocking", "advisory"]
    message: str
    section: str


class ValidationResult(BaseModel):
    validation_result_id: UUID | None = None
    status: Literal["passed", "failed"]
    blocking_issue_count: int = 0
    advisory_issue_count: int = 0
    findings: list[ValidationFinding] = Field(default_factory=list)


class ActivationRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=500)


class RetireRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=500)


class TenantGrantRequest(BaseModel):
    tenant_ids: list[UUID] = Field(min_length=1)
    reason: str = Field(default="", max_length=500)


class TenantGrantResponse(BaseModel):
    granted_tenant_ids: list[UUID]
    revoked_tenant_ids: list[UUID] = Field(default_factory=list)


class ProfileDraftDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    agent_runtime_profile_id: UUID
    agent_profile_draft_id: UUID
    current_revision_number: int
    purpose: str | None = None
    prompt_references: list[dict[str, object]] = Field(default_factory=list)
    model_routing_hints: dict[str, object] = Field(default_factory=dict)
    memory_scope_policy: dict[str, object] = Field(default_factory=dict)
    skill_requirements: list[dict[str, object]] = Field(default_factory=list)
    tool_policy_expectations: list[dict[str, object]] = Field(default_factory=list)
    output_contract_expectations: dict[str, object] = Field(default_factory=dict)
    test_suite_requirements: list[dict[str, object]] = Field(default_factory=list)
    latest_validation: ValidationResult | None = None


class ProfileSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    agent_runtime_profile_id: UUID
    scope_type: str
    tenant_id: UUID | None
    agent_key: str
    agent_kind: str
    display_name: str
    purpose: str
    status: str
    active_profile_version_id: UUID | None = None
    validation_status: str | None = None


class ProfileVersionDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    agent_profile_version_id: UUID
    agent_runtime_profile_id: UUID
    agent_key: str
    agent_kind: str
    display_version: str
    status: str
    safe_summary: dict[str, object] = Field(default_factory=dict)


class ProfileResolveRequest(BaseModel):
    tenant_id: UUID
    agent_key: str = Field(min_length=1, max_length=128)
    agent_kind: AgentKind


class ProfileResolveResponse(BaseModel):
    resolved: bool
    selected_profile_version_id: UUID | None = None
    source_scope: ScopeType | None = None
    considered_profile_version_ids: list[UUID] = Field(default_factory=list)
    blocking_issues: list[ValidationFinding] = Field(default_factory=list)


class AuditEventSummary(BaseModel):
    action: str
    actor_principal_id: str
    created_at: datetime
    outcome: str = "recorded"
    reason: str = ""
    redacted_diff_summary: dict[str, object] = Field(default_factory=dict)


class HistoryResponse(BaseModel):
    items: list[AuditEventSummary] = Field(default_factory=list)
