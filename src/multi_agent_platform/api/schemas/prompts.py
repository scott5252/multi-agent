from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

ScopeType = Literal["platform", "tenant"]
PromptVersionStatus = Literal["active", "retired", "historical_only"]


class SafeError(BaseModel):
    code: str
    message: str
    trace_id: str | None = None
    details: dict[str, object] = Field(default_factory=dict)


class ValidationFinding(BaseModel):
    code: str
    severity: Literal["blocking", "advisory"]
    message: str
    field: str | None = None


class ValidationResult(BaseModel):
    status: Literal["passed", "failed"]
    blocking_issue_count: int = 0
    advisory_issue_count: int = 0
    findings: list[ValidationFinding] = Field(default_factory=list)


class PromptVariableDeclaration(BaseModel):
    name: str = Field(pattern=r"^[A-Za-z_][A-Za-z0-9_]*$")
    purpose: str = Field(min_length=1, max_length=500)
    required: bool = True
    allowed_value_category: str = Field(default="synthetic", max_length=64)
    safety_classification: str = Field(default="safe_fixture", max_length=64)
    sample_guidance: str = Field(default="", max_length=500)
    display_order: int = 0


class FixtureValueSet(BaseModel):
    fixture_set_id: str = Field(min_length=1, max_length=128)
    label: str = Field(min_length=1, max_length=128)
    values_by_variable: dict[str, str] = Field(default_factory=dict)


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


class PromptLineageCreate(ScopedPayload):
    slug: str = Field(min_length=1, max_length=128, pattern=r"^[a-z0-9][a-z0-9_-]*$")
    display_name: str = Field(min_length=1, max_length=255)
    purpose: str = Field(min_length=1, max_length=500)


class PromptDraftSave(BaseModel):
    expected_revision_number: int = Field(ge=0)
    prompt_title: str = Field(min_length=1, max_length=255)
    purpose: str = Field(min_length=1, max_length=500)
    usage_notes: str = Field(default="", max_length=5000)
    template_content: str = Field(min_length=1, max_length=65536)
    variables: list[PromptVariableDeclaration] = Field(default_factory=list)
    fixture_sets: list[FixtureValueSet] = Field(default_factory=list)


class PromptPreviewRequest(BaseModel):
    fixture_set_id: str = Field(min_length=1, max_length=128)


class PromptPreviewResponse(BaseModel):
    rendered_preview: str
    redaction_categories: list[str] = Field(default_factory=list)
    missing_variables: list[str] = Field(default_factory=list)


class PublishRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=500)


class RetireRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=500)


class TenantGrantRequest(BaseModel):
    tenant_ids: list[UUID] = Field(min_length=1)
    reason: str = Field(default="", max_length=500)


class TenantGrantResponse(BaseModel):
    granted_tenant_ids: list[UUID]


class PromptDraftDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    prompt_lineage_id: UUID
    prompt_draft_id: UUID
    current_revision_number: int


class PromptLineageSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    prompt_lineage_id: UUID
    scope_type: str
    tenant_id: UUID | None
    slug: str
    display_name: str
    purpose: str
    status: str


class PromptVersionDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    prompt_version_id: UUID
    prompt_lineage_id: UUID
    display_version: str
    status: str
    template_content_sha256: str
