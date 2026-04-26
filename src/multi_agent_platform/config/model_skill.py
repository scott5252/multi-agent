from __future__ import annotations

import json
from collections.abc import Mapping
from enum import StrEnum
from hashlib import sha256
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ModelSkillErrorCategory(StrEnum):
    MISSING_GLOBAL_DEFAULT = "missing_global_default"
    INVALID_MODEL_REFERENCE = "invalid_model_reference"
    MISSING_PROMPT_VERSION = "missing_prompt_version"
    SKILL_NOT_BOUND = "skill_not_bound"
    TOOL_DENIED = "tool_denied"
    DOMAIN_DENIED = "domain_denied"
    CREDENTIAL_UNSATISFIED = "credential_unsatisfied"
    SECRET_REFERENCE_INVALID = "secret_reference_invalid"
    RESOLUTION_CONFLICT = "resolution_conflict"
    AUTHORIZATION_FAILED = "authorization_failed"
    STALE_CONFIGURATION = "stale_configuration"
    VALIDATION_FAILED = "validation_failed"
    NOT_FOUND = "not_found"


class ConfigKind(StrEnum):
    MODEL_ROUTING = "model_routing"
    PROMPT_REFERENCE = "prompt_reference"
    SKILL_BINDING = "skill_binding"
    ALLOWED_TOOL_POLICY = "allowed_tool_policy"
    OUTBOUND_DOMAIN_POLICY = "outbound_domain_policy"
    SECRET_REFERENCE = "secret_reference"
    CREDENTIAL_REQUIREMENT = "credential_requirement"


class ScopeType(StrEnum):
    TENANT_DEFAULT = "tenant_default"
    WORKFLOW = "workflow"
    AGENT = "agent"
    STEP = "step"


class VersionStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ROLLED_BACK_FROM = "rolled_back_from"
    ARCHIVED = "archived"


class ProviderStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    RETIRED = "retired"


class PolicyOutcome(StrEnum):
    ALLOW = "allow"
    DENY = "deny"


class DecisionCategory(StrEnum):
    MODEL_PROMPT = "model_prompt"
    SKILL = "skill"
    TOOL = "tool"
    OUTBOUND_DOMAIN = "outbound_domain"
    CREDENTIAL = "credential"
    SECRET_REFERENCE = "secret_reference"


class ScopeSelector(BaseModel):
    model_config = ConfigDict(frozen=True)

    tenant_id: UUID
    workflow_lineage_id: UUID | None = None
    workflow_version_bundle_id: UUID | None = None
    agent_key: str | None = None
    step_key: str | None = None

    @property
    def scope_type(self) -> ScopeType:
        if self.step_key:
            return ScopeType.STEP
        if self.agent_key:
            return ScopeType.AGENT
        if self.workflow_lineage_id or self.workflow_version_bundle_id:
            return ScopeType.WORKFLOW
        return ScopeType.TENANT_DEFAULT

    def canonical_json(self) -> str:
        return json.dumps(
            self.model_dump(mode="json", exclude_none=True),
            sort_keys=True,
            separators=(",", ":"),
        )

    def scope_hash(self) -> str:
        return sha256(self.canonical_json().encode("utf-8")).hexdigest()

    def contains(self, request: ScopeSelector) -> bool:
        if self.tenant_id != request.tenant_id:
            return False
        for field_name in (
            "workflow_lineage_id",
            "workflow_version_bundle_id",
            "agent_key",
            "step_key",
        ):
            value = getattr(self, field_name)
            if value is not None and value != getattr(request, field_name):
                return False
        return True

    def specificity(self) -> int:
        return {
            ScopeType.TENANT_DEFAULT: 0,
            ScopeType.WORKFLOW: 1,
            ScopeType.AGENT: 2,
            ScopeType.STEP: 3,
        }[self.scope_type]


class VersionedRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    version_id: UUID
    tenant_id: UUID
    scope: ScopeSelector
    status: VersionStatus = VersionStatus.ACTIVE
    version_sequence: int = 1
    activation_reason: str
    redacted_summary: dict[str, Any] = Field(default_factory=dict)


class ModelProviderSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    model_provider_entry_id: UUID
    tenant_id: UUID | None
    provider_key: str
    model_id: str
    display_name: str
    status: ProviderStatus = ProviderStatus.ACTIVE
    capabilities: dict[str, Any] = Field(default_factory=dict)


class ModelRoutingCandidate(VersionedRecord):
    model_provider_entry_id: UUID
    provider_key: str
    model_id: str
    routing_parameters: dict[str, Any] = Field(default_factory=dict)


class PromptReferenceCandidate(VersionedRecord):
    prompt_id: UUID
    prompt_version_id: UUID
    prompt_digest: str


class SkillBindingCandidate(VersionedRecord):
    skill_slug: str
    skill_version: str
    allowed_contexts: tuple[str, ...] = Field(default_factory=tuple)
    runtime_ref_constraints: dict[str, Any] = Field(default_factory=dict)


class ToolPolicyCandidate(VersionedRecord):
    skill_slug: str | None = None
    tool_id: str
    allowed_action_categories: tuple[str, ...] = Field(default_factory=tuple)
    constraints: dict[str, Any] = Field(default_factory=dict)


class OutboundPolicyCandidate(VersionedRecord):
    tool_id: str
    action_category: str | None = None
    allowed_domain_patterns: tuple[str, ...] = Field(default_factory=tuple)
    allowed_schemes: tuple[str, ...] = Field(default_factory=tuple)
    allowed_ports: tuple[int, ...] = Field(default_factory=tuple)


class SecretReferenceCandidate(VersionedRecord):
    secret_reference_id: str
    provider_key: str
    external_reference: str
    allowed_scopes: dict[str, Any] = Field(default_factory=dict)
    rotation_metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def is_usable(self) -> bool:
        return (
            self.status is VersionStatus.ACTIVE
            and not bool(self.rotation_metadata.get("revoked"))
            and not bool(self.rotation_metadata.get("expired"))
        )


class CredentialRequirementCandidate(VersionedRecord):
    tool_id: str
    action_category: str | None = None
    credential_kind: str
    secret_reference_version_id: UUID | None = None
    delegated_credential_link_id: UUID | None = None
    allowed_credential_scope: dict[str, Any] = Field(default_factory=dict)
    expiry_policy: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_reference_shape(self) -> CredentialRequirementCandidate:
        if self.credential_kind == "secret_reference" and (
            self.secret_reference_version_id is None
        ):
            raise ValueError(
                "secret_reference credential requirements need a version id"
            )
        if self.credential_kind == "delegated_credential" and (
            self.delegated_credential_link_id is None
        ):
            raise ValueError(
                "delegated_credential requirements need a delegated credential link id"
            )
        return self


class SafeError(BaseModel):
    category: ModelSkillErrorCategory
    message: str
    trace_id: str | None = None
    remediation_hint: str | None = None
    safe_identifiers: dict[str, str] = Field(default_factory=dict)


def stable_digest(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return sha256(encoded.encode("utf-8")).hexdigest()
