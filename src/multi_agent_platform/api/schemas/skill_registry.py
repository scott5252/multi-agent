from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SkillRegistryFindingResponse(BaseModel):
    code: str
    message: str
    severity: str = "blocking"
    field_path: str | None = None
    blocking: bool = True
    remediation: str | None = None


class SkillPackageCreateRequest(BaseModel):
    slug: str
    display_name: str
    description: str
    owner_principal_id: str


class SkillPackageResponse(BaseModel):
    slug: str
    display_name: str
    description: str
    lifecycle_state: str
    latest_published_version: str | None = None


class SkillVersionValidateRequest(BaseModel):
    manifest: dict[str, Any]
    approved_integration_refs: set[str] = Field(default_factory=set)


class SkillVersionValidationResponse(BaseModel):
    status: str
    manifest_digest: str | None = None
    findings: list[SkillRegistryFindingResponse] = Field(default_factory=list)
    safe_summary: dict[str, Any] = Field(default_factory=dict)


class SkillVersionPublishRequest(SkillVersionValidateRequest):
    artifact_digest: str


class SkillPackageVersionResponse(BaseModel):
    package_version_id: str
    slug: str
    semantic_version: str
    manifest_digest: str
    artifact_digest: str
    validation_status: str
    lifecycle_state: str
    tenant_grants: list[str] = Field(default_factory=list)
    quarantined: bool = False
    runtime_blocked: bool = False


class TenantAvailabilityGrantRequest(BaseModel):
    tenant_id: str


class SkillInstallationCreateRequest(BaseModel):
    tenant_id: str
    slug: str
    semantic_version: str
    previous_installation_id: str | None = None


class CredentialReferenceRequest(BaseModel):
    requirement_key: str
    credential_kind: Literal["secret_reference", "delegated_credential"]
    reference_id: str | None
    status: str = "ready"
    safe_summary: dict[str, Any] = Field(default_factory=dict)


class ConfigureCredentialsRequest(BaseModel):
    revision_token: str
    credentials: list[CredentialReferenceRequest]


class SkillInstallationResponse(BaseModel):
    installation_id: str
    tenant_id: str
    slug: str
    semantic_version: str
    installation_version: int
    manifest_digest: str
    artifact_digest: str
    revision_token: str
    readiness_state: str
    credential_status: str
    compatibility_status: str
    permission_status: str
    smoke_test_status: str
    binding_eligibility_status: str
    findings: list[dict[str, Any]] = Field(default_factory=list)
    runtime_blocked: bool = False
    quarantined: bool = False


class BindingEligibilityResponse(BaseModel):
    allowed: bool
    reason_codes: list[str]
    evidence: dict[str, Any]


class SkillAuditEventResponse(BaseModel):
    audit_record_id: UUID | str
    event_type: str
    actor_principal_id: str
    outcome: str
    safe_summary: dict[str, Any] = Field(default_factory=dict)
    tenant_id: str | None = None
    package_slug: str | None = None
    package_version: str | None = None
    installation_id: str | None = None
    trace_id: str | None = None


class SkillRegistrySafeError(BaseModel):
    model_config = ConfigDict(frozen=True)

    category: str
    message: str
    safe_identifiers: dict[str, str] = Field(default_factory=dict)
