from __future__ import annotations

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
    status: Literal["passed", "failed"]
    blocking_issue_count: int = 0
    findings: list[ValidationFinding] = Field(default_factory=list)


class ActivationRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=500)


class ProfileDraftDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    agent_runtime_profile_id: UUID
    agent_profile_draft_id: UUID
    current_revision_number: int


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


class ProfileVersionDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    agent_profile_version_id: UUID
    agent_runtime_profile_id: UUID
    agent_key: str
    agent_kind: str
    display_version: str
    status: str
