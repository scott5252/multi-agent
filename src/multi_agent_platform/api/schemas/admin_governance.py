from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from multi_agent_platform.api.schemas.admin_patterns import (
    AdminAction,
    MutationResult,
    RefreshHint,
    ValidationFieldError,
    safe_text,
)
from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminScope,
    ReactAdminShellState,
)

GOVERNANCE_UNSAFE_MARKERS = (
    "qa031-secret-value",
    "resolved credential",
    "authorization header",
    "bearer ",
    "api_key",
    "provider token",
    "raw provider request",
    "raw provider response",
    "raw prompt",
    "raw completion",
    "private channel",
    "memory contents",
    "connector payload",
    "stack trace",
    "/users/",
    "globex secret",
)


def safe_governance_text(value: str, *, max_length: int = 240) -> str:
    normalized = safe_text(value, max_length=max_length)
    lowered = normalized.lower()
    if any(marker in lowered for marker in GOVERNANCE_UNSAFE_MARKERS):
        raise ValueError("unsafe governance text cannot be rendered")
    if normalized.startswith("/"):
        raise ValueError("local paths cannot be rendered")
    return normalized


class GovernanceStatus(StrEnum):
    READY = "ready"
    DEGRADED = "degraded"
    WARNING = "warning"
    BLOCKED = "blocked"
    DENIED = "denied"
    UNAVAILABLE = "unavailable"
    RUNNING = "running"
    SUMMARIZED = "summarized"


class GovernanceSection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    section_id: str
    label: str
    status: GovernanceStatus
    summary: str
    href: str | None = None

    @field_validator("label", "summary")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_governance_text(value, max_length=180)


class ProviderCredentialReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reference_id: str
    label: str
    source_type: str
    readiness: GovernanceStatus
    fingerprint: str | None = None
    last_resolution_status: str
    last_checked_label: str
    policy_reason: str
    remediation: str

    @field_validator(
        "label",
        "source_type",
        "fingerprint",
        "last_resolution_status",
        "last_checked_label",
        "policy_reason",
        "remediation",
    )
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_governance_text(value, max_length=180)


class ProviderHealthSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: GovernanceStatus
    latency_bucket: str
    breaker_state: str
    checked_at_label: str
    summary: str

    @field_validator("latency_bucket", "breaker_state", "checked_at_label", "summary")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_governance_text(value, max_length=180)


class ProviderProbeDiagnostic(BaseModel):
    model_config = ConfigDict(extra="forbid")

    probe_id: str
    provider_id: str
    status: GovernanceStatus
    summary: str
    latency_bucket: str
    failure_category: str | None = None
    retry_state: str
    breaker_state: str
    credential_resolution_status: str
    audit_reference_id: str
    redaction_summary: str

    @field_validator(
        "summary",
        "latency_bucket",
        "failure_category",
        "retry_state",
        "breaker_state",
        "credential_resolution_status",
        "audit_reference_id",
        "redaction_summary",
    )
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_governance_text(value, max_length=220)


class ProviderGovernanceSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider_id: str
    provider_key: str
    display_name: str
    provider_type: str
    status: GovernanceStatus
    tenant_availability: str
    model_count: int = Field(ge=0)
    health: ProviderHealthSummary
    credential_reference: ProviderCredentialReference
    local_no_auth_status: str
    direct_call_guardrail: str
    authorized_actions: tuple[AdminAction, ...] = Field(default_factory=tuple)
    links: tuple[AdminAction, ...] = Field(default_factory=tuple)

    @field_validator(
        "display_name",
        "provider_type",
        "tenant_availability",
        "local_no_auth_status",
        "direct_call_guardrail",
    )
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_governance_text(value, max_length=180)


class PromptVersionSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version_id: str
    label: str
    status: GovernanceStatus
    safe_change_summary: str
    audit_reference_id: str

    @field_validator("label", "safe_change_summary", "audit_reference_id")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_governance_text(value, max_length=180)


class PromptLibrarySummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prompt_lineage_id: str
    name: str
    status: GovernanceStatus
    draft_version: str | None = None
    published_version: str | None = None
    tenant_grants: tuple[str, ...] = Field(default_factory=tuple)
    render_test_status: GovernanceStatus
    safe_change_summary: str
    history: tuple[PromptVersionSummary, ...] = Field(default_factory=tuple)
    authorized_actions: tuple[AdminAction, ...] = Field(default_factory=tuple)
    links: tuple[AdminAction, ...] = Field(default_factory=tuple)

    @field_validator(
        "name",
        "draft_version",
        "published_version",
        "safe_change_summary",
    )
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_governance_text(value, max_length=180)

    @field_validator("tenant_grants")
    @classmethod
    def grant_labels_are_safe(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(safe_governance_text(item, max_length=140) for item in value)


class SafePromptPreview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    preview_id: str
    prompt_lineage_id: str
    fixture_label: str
    status: GovernanceStatus
    safe_output: str
    redaction_findings: tuple[str, ...] = Field(default_factory=tuple)
    variable_summary: str
    artifact_reference_id: str | None = None
    audit_reference_id: str

    @field_validator(
        "fixture_label",
        "safe_output",
        "variable_summary",
        "artifact_reference_id",
        "audit_reference_id",
    )
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_governance_text(value, max_length=220)

    @field_validator("redaction_findings")
    @classmethod
    def findings_are_safe(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(safe_governance_text(item, max_length=180) for item in value)


class RuntimeProfileGovernanceSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile_id: str
    profile_lineage_id: str
    name: str
    status: GovernanceStatus
    draft_version: str | None = None
    published_version: str
    model_binding: str
    provider_binding: str
    prompt_binding: str
    skill_requirements: tuple[str, ...] = Field(default_factory=tuple)
    tenant_grants: tuple[str, ...] = Field(default_factory=tuple)
    resolver_status: GovernanceStatus
    authorized_actions: tuple[AdminAction, ...] = Field(default_factory=tuple)
    links: tuple[AdminAction, ...] = Field(default_factory=tuple)

    @field_validator(
        "name",
        "draft_version",
        "published_version",
        "model_binding",
        "provider_binding",
        "prompt_binding",
    )
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_governance_text(value, max_length=180)

    @field_validator("skill_requirements", "tenant_grants")
    @classmethod
    def tuple_text_is_safe(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(safe_governance_text(item, max_length=160) for item in value)


class ProfileResolutionPreview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    preview_id: str
    profile_id: str
    status: GovernanceStatus
    selected_profile_version: str
    model_route: str
    provider_route: str
    prompt_route: str
    skill_route: str
    fallback_reason: str | None = None
    policy_reasons: tuple[str, ...] = Field(default_factory=tuple)
    remediation: str
    audit_reference_id: str

    @field_validator(
        "selected_profile_version",
        "model_route",
        "provider_route",
        "prompt_route",
        "skill_route",
        "fallback_reason",
        "remediation",
        "audit_reference_id",
    )
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_governance_text(value, max_length=200)

    @field_validator("policy_reasons")
    @classmethod
    def reasons_are_safe(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(safe_governance_text(item, max_length=180) for item in value)


class RoutingPreviewResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    preview_id: str
    tenant_label: str
    workflow_context_label: str
    status: GovernanceStatus
    model_decision: str
    provider_decision: str
    skill_decision: str
    policy_reasons: tuple[str, ...] = Field(default_factory=tuple)
    direct_call_guardrail: str
    credential_reference_status: str
    audit_reference_id: str
    remediation: str

    @field_validator(
        "tenant_label",
        "workflow_context_label",
        "model_decision",
        "provider_decision",
        "skill_decision",
        "direct_call_guardrail",
        "credential_reference_status",
        "audit_reference_id",
        "remediation",
    )
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_governance_text(value, max_length=220)

    @field_validator("policy_reasons")
    @classmethod
    def reasons_are_safe(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(safe_governance_text(item, max_length=180) for item in value)


class PolicyHistoryRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    history_id: str
    domain: str
    actor_label: str
    tenant_scope_label: str
    timestamp_label: str
    change_category: str
    outcome: GovernanceStatus
    safe_diff_summary: str
    audit_reference_id: str
    links: tuple[AdminAction, ...] = Field(default_factory=tuple)

    @field_validator(
        "domain",
        "actor_label",
        "tenant_scope_label",
        "timestamp_label",
        "change_category",
        "safe_diff_summary",
        "audit_reference_id",
    )
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_governance_text(value, max_length=180)


class RunProvenanceSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    tenant_label: str
    workflow_label: str
    started_at_label: str
    provider_evidence: str
    model_evidence: str
    prompt_evidence: str
    profile_evidence: str
    routing_evidence: str
    credential_reference_evidence: str
    usage_evidence: str
    audit_reference_id: str
    links: tuple[AdminAction, ...] = Field(default_factory=tuple)

    @field_validator(
        "tenant_label",
        "workflow_label",
        "started_at_label",
        "provider_evidence",
        "model_evidence",
        "prompt_evidence",
        "profile_evidence",
        "routing_evidence",
        "credential_reference_evidence",
        "usage_evidence",
        "audit_reference_id",
    )
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_governance_text(value, max_length=220)


class GovernanceDashboard(BaseModel):
    model_config = ConfigDict(extra="forbid")

    page_id: str
    title: str
    description: str
    scope: ReactAdminScope
    sections: tuple[GovernanceSection, ...] = Field(default_factory=tuple)
    setup_summary: tuple[str, ...] = Field(default_factory=tuple)
    providers: tuple[ProviderGovernanceSummary, ...] = Field(default_factory=tuple)
    prompts: tuple[PromptLibrarySummary, ...] = Field(default_factory=tuple)
    profiles: tuple[RuntimeProfileGovernanceSummary, ...] = Field(default_factory=tuple)
    routing_preview: RoutingPreviewResult
    profile_resolution: ProfileResolutionPreview
    prompt_preview: SafePromptPreview
    policy_history: tuple[PolicyHistoryRecord, ...] = Field(default_factory=tuple)
    run_provenance: tuple[RunProvenanceSummary, ...] = Field(default_factory=tuple)
    actions: tuple[AdminAction, ...] = Field(default_factory=tuple)
    state: ReactAdminShellState | None = None
    refresh: RefreshHint | None = None

    @field_validator("title", "description")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_governance_text(value, max_length=220)

    @field_validator("setup_summary")
    @classmethod
    def summary_is_safe(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(safe_governance_text(item, max_length=180) for item in value)


class ProviderGovernanceList(BaseModel):
    model_config = ConfigDict(extra="forbid")

    providers: tuple[ProviderGovernanceSummary, ...] = Field(default_factory=tuple)


class PromptGovernanceList(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prompts: tuple[PromptLibrarySummary, ...] = Field(default_factory=tuple)


class ProfileGovernanceList(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profiles: tuple[RuntimeProfileGovernanceSummary, ...] = Field(default_factory=tuple)


class PolicyHistoryList(BaseModel):
    model_config = ConfigDict(extra="forbid")

    history: tuple[PolicyHistoryRecord, ...] = Field(default_factory=tuple)


class ProviderCredentialReferenceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    credential_reference_id: str
    revision: str

    @field_validator("credential_reference_id", "revision")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_governance_text(value, max_length=140)


class PromptPreviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fixture_id: str

    @field_validator("fixture_id")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_governance_text(value, max_length=120)


class PromptSaveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    revision: str
    idempotency_key: str
    safe_summary: str
    publish: bool = False

    @field_validator("revision", "idempotency_key", "safe_summary")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_governance_text(value, max_length=180)


class ProfileSaveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    revision: str
    idempotency_key: str
    model_binding: str
    provider_binding: str

    @field_validator("revision", "idempotency_key", "model_binding", "provider_binding")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_governance_text(value, max_length=180)


class RoutingPreviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workflow_context: str
    profile_id: str | None = None
    skill_id: str | None = None

    @field_validator("workflow_context", "profile_id", "skill_id")
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_governance_text(value, max_length=180)


class GovernanceMutationResult(MutationResult):
    revision: str | None = None
    probe: ProviderProbeDiagnostic | None = None
    prompt_preview: SafePromptPreview | None = None
    profile_resolution: ProfileResolutionPreview | None = None
    routing_preview: RoutingPreviewResult | None = None
    diagnostics: tuple[str, ...] = Field(default_factory=tuple)

    @field_validator("summary", "audit_reference_id", "revision")
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_governance_text(value, max_length=220)

    @field_validator("diagnostics")
    @classmethod
    def diagnostics_are_safe(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(safe_governance_text(item, max_length=180) for item in value)


class GovernanceValidationFieldError(ValidationFieldError):
    pass
