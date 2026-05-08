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
    ReactAdminEmptyStateMetadata,
    ReactAdminEmptyStateReason,
    ReactAdminPageProvenance,
    ReactAdminScope,
    ReactAdminShellState,
    ReactAdminSourceKind,
)

SKILL_LIFECYCLE_UNSAFE_MARKERS = (
    "qa032-secret-value",
    "raw manifest",
    "resolved credential",
    "authorization header",
    "bearer ",
    "provider token",
    "private message",
    "memory contents",
    "connector request",
    "connector response",
    "connector payload",
    "raw tool output",
    "stack trace",
    "/users/",
    "globex secret",
)


def safe_skill_lifecycle_text(value: str, *, max_length: int = 240) -> str:
    normalized = safe_text(value, max_length=max_length)
    lowered = normalized.lower()
    if any(marker in lowered for marker in SKILL_LIFECYCLE_UNSAFE_MARKERS):
        raise ValueError("unsafe skill lifecycle text cannot be rendered")
    if normalized.startswith("/"):
        raise ValueError("local paths cannot be rendered")
    return normalized


class SkillLifecycleStatus(StrEnum):
    READY = "ready"
    DEGRADED = "degraded"
    WARNING = "warning"
    BLOCKED = "blocked"
    DENIED = "denied"
    UNAVAILABLE = "unavailable"
    QUEUED = "queued"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    STALE = "stale"
    PUBLISHED = "published"
    QUARANTINED = "quarantined"
    WITHDRAWN = "withdrawn"
    SUMMARIZED = "summarized"


def live_skill_lifecycle_provenance(
    *, source_label: str, source_detail: str | None = None
) -> ReactAdminPageProvenance:
    return ReactAdminPageProvenance(
        source_kind=ReactAdminSourceKind.LIVE_REPOSITORY,
        source_label=source_label,
        source_detail=source_detail,
    )


def empty_skill_lifecycle_state(
    *,
    title: str,
    summary: str,
    setup_hint: str | None = None,
    source_label: str = "Skill lifecycle records",
) -> ReactAdminEmptyStateMetadata:
    return ReactAdminEmptyStateMetadata(
        reason=ReactAdminEmptyStateReason.NO_LIVE_ROWS,
        title=title,
        summary=summary,
        setup_hint=setup_hint,
        provenance=ReactAdminPageProvenance(
            source_kind=ReactAdminSourceKind.EMPTY_LIVE_STATE,
            source_label=source_label,
            source_detail=(
                "No authorized live skill lifecycle records exist for this scope."
            ),
        ),
    )


class SkillLifecycleSection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    section_id: str
    label: str
    status: SkillLifecycleStatus
    summary: str
    href: str | None = None

    @field_validator("label", "summary")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_skill_lifecycle_text(value, max_length=180)


class SkillLifecycleWizardStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step_id: str
    label: str
    status: SkillLifecycleStatus
    summary: str

    @field_validator("label", "summary")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_skill_lifecycle_text(value, max_length=180)


class SkillPackageCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate_id: str
    package_slug: str
    candidate_revision: str
    manifest_digest: str
    manifest_source: str
    safe_manifest_summary: str
    validation_status: SkillLifecycleStatus
    validation_findings: tuple[ValidationFieldError, ...] = Field(default_factory=tuple)
    safe_documentation_summary: str
    smoke_evidence_status: SkillLifecycleStatus
    publish_blockers: tuple[str, ...] = Field(default_factory=tuple)
    audit_reference_id: str
    authorized_actions: tuple[AdminAction, ...] = Field(default_factory=tuple)

    @field_validator(
        "package_slug",
        "candidate_revision",
        "manifest_digest",
        "manifest_source",
        "safe_manifest_summary",
        "safe_documentation_summary",
        "audit_reference_id",
    )
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_skill_lifecycle_text(value, max_length=220)

    @field_validator("publish_blockers")
    @classmethod
    def blockers_are_safe(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(safe_skill_lifecycle_text(item, max_length=180) for item in value)


class TenantSkillGrantSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_id: str
    tenant_label: str
    package_slug: str
    version_label: str
    grant_status: SkillLifecycleStatus
    allowed_versions: tuple[str, ...] = Field(default_factory=tuple)
    install_eligibility: SkillLifecycleStatus
    restrictions: tuple[str, ...] = Field(default_factory=tuple)
    authorized_actions: tuple[AdminAction, ...] = Field(default_factory=tuple)

    @field_validator("tenant_label", "package_slug", "version_label")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_skill_lifecycle_text(value, max_length=180)

    @field_validator("allowed_versions", "restrictions")
    @classmethod
    def tuple_text_is_safe(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(safe_skill_lifecycle_text(item, max_length=160) for item in value)


class SkillPackageVersionSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    package_id: str
    package_slug: str
    version_id: str
    version_label: str
    lifecycle_status: SkillLifecycleStatus
    manifest_digest: str
    safe_manifest_summary: str
    tenant_grant_summary: tuple[TenantSkillGrantSummary, ...] = Field(
        default_factory=tuple
    )
    validation_evidence_ref: str
    smoke_evidence_ref: str
    quarantine_summary: str | None = None
    withdrawal_summary: str | None = None
    audit_reference_id: str
    authorized_actions: tuple[AdminAction, ...] = Field(default_factory=tuple)

    @field_validator(
        "package_slug",
        "version_id",
        "version_label",
        "manifest_digest",
        "safe_manifest_summary",
        "validation_evidence_ref",
        "smoke_evidence_ref",
        "quarantine_summary",
        "withdrawal_summary",
        "audit_reference_id",
    )
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_skill_lifecycle_text(value, max_length=220)


class PackagePublicationWorkspace(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate: SkillPackageCandidate
    available_steps: tuple[SkillLifecycleWizardStep, ...] = Field(default_factory=tuple)
    package_versions: tuple[SkillPackageVersionSummary, ...] = Field(
        default_factory=tuple
    )
    validation_summary: str
    grant_preview: tuple[TenantSkillGrantSummary, ...] = Field(default_factory=tuple)
    publish_readiness: SkillLifecycleStatus
    authorized_actions: tuple[AdminAction, ...] = Field(default_factory=tuple)

    @field_validator("validation_summary")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_skill_lifecycle_text(value, max_length=220)


class CredentialReferenceOption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reference_id: str
    label: str
    source_type: str
    readiness: SkillLifecycleStatus
    fingerprint: str | None = None
    policy_reason: str
    last_checked_label: str
    remediation: str

    @field_validator(
        "reference_id",
        "label",
        "source_type",
        "fingerprint",
        "policy_reason",
        "last_checked_label",
        "remediation",
    )
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_skill_lifecycle_text(value, max_length=180)


class ConnectorReadinessSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    connector_id: str
    connector_label: str
    tool_names: tuple[str, ...] = Field(default_factory=tuple)
    readiness: SkillLifecycleStatus
    credential_status: SkillLifecycleStatus
    policy_status: SkillLifecycleStatus
    smoke_test_status: SkillLifecycleStatus
    staging_probe_status: SkillLifecycleStatus
    last_safe_summary: str
    evidence_reference_id: str
    remediation: str
    authorized_actions: tuple[AdminAction, ...] = Field(default_factory=tuple)

    @field_validator(
        "connector_id",
        "connector_label",
        "last_safe_summary",
        "evidence_reference_id",
        "remediation",
    )
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_skill_lifecycle_text(value, max_length=220)

    @field_validator("tool_names")
    @classmethod
    def tool_names_are_safe(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(safe_skill_lifecycle_text(item, max_length=120) for item in value)


class TenantSkillInstallationSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    installation_id: str
    tenant_id: str
    package_slug: str
    installed_version: str
    installation_revision: str
    installation_status: SkillLifecycleStatus
    credential_readiness: SkillLifecycleStatus
    smoke_test_readiness: SkillLifecycleStatus
    connector_readiness: tuple[ConnectorReadinessSummary, ...] = Field(
        default_factory=tuple
    )
    binding_readiness: SkillLifecycleStatus
    upgrade_path: str | None = None
    findings: tuple[str, ...] = Field(default_factory=tuple)
    credential_options: tuple[CredentialReferenceOption, ...] = Field(
        default_factory=tuple
    )
    authorized_actions: tuple[AdminAction, ...] = Field(default_factory=tuple)
    audit_reference_id: str

    @field_validator(
        "package_slug",
        "installed_version",
        "installation_revision",
        "upgrade_path",
        "audit_reference_id",
    )
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_skill_lifecycle_text(value, max_length=180)

    @field_validator("findings")
    @classmethod
    def findings_are_safe(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(safe_skill_lifecycle_text(item, max_length=180) for item in value)


class TenantSkillDiscovery(BaseModel):
    model_config = ConfigDict(extra="forbid")

    grants: tuple[TenantSkillGrantSummary, ...] = Field(default_factory=tuple)
    available_versions: tuple[SkillPackageVersionSummary, ...] = Field(
        default_factory=tuple
    )
    empty_state_summary: str | None = None

    @field_validator("empty_state_summary")
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_skill_lifecycle_text(value, max_length=180)


class SkillExecutionDiagnosticSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    diagnostic_id: str
    skill_package_version: str
    tool_name: str
    gateway_decision: str
    side_effect_posture: str
    outbound_policy_status: SkillLifecycleStatus
    credential_policy_status: SkillLifecycleStatus
    connector_readiness: SkillLifecycleStatus
    safe_attempt_summary: str
    redaction_summary: str
    audit_reference_id: str
    remediation: str

    @field_validator(
        "diagnostic_id",
        "skill_package_version",
        "tool_name",
        "gateway_decision",
        "side_effect_posture",
        "safe_attempt_summary",
        "redaction_summary",
        "audit_reference_id",
        "remediation",
    )
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_skill_lifecycle_text(value, max_length=220)


class BindingContextChoice(BaseModel):
    model_config = ConfigDict(extra="forbid")

    choice_id: str
    label: str
    kind: str
    selected: bool = False

    @field_validator("label", "kind")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_skill_lifecycle_text(value, max_length=160)


class BindingEligibilityPreview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    preview_id: str
    tenant_label: str
    context_choices: tuple[BindingContextChoice, ...] = Field(default_factory=tuple)
    selected_context: str
    eligible_tools: tuple[str, ...] = Field(default_factory=tuple)
    blocked_tools: tuple[str, ...] = Field(default_factory=tuple)
    policy_reasons: tuple[str, ...] = Field(default_factory=tuple)
    missing_requirements: tuple[str, ...] = Field(default_factory=tuple)
    remediation: str
    audit_reference_id: str

    @field_validator(
        "tenant_label",
        "selected_context",
        "remediation",
        "audit_reference_id",
    )
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_skill_lifecycle_text(value, max_length=220)

    @field_validator(
        "eligible_tools",
        "blocked_tools",
        "policy_reasons",
        "missing_requirements",
    )
    @classmethod
    def tuple_text_is_safe(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(safe_skill_lifecycle_text(item, max_length=180) for item in value)


class SkillLifecycleAuditRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    record_id: str
    domain: str
    package_slug: str
    version_label: str
    tenant_scope_label: str
    actor_label: str
    timestamp_label: str
    action: str
    outcome: SkillLifecycleStatus
    safe_diff_summary: str
    audit_reference_id: str
    links: tuple[AdminAction, ...] = Field(default_factory=tuple)

    @field_validator(
        "domain",
        "package_slug",
        "version_label",
        "tenant_scope_label",
        "actor_label",
        "timestamp_label",
        "action",
        "safe_diff_summary",
        "audit_reference_id",
    )
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_skill_lifecycle_text(value, max_length=200)


class SkillLegacyRouteMapping(BaseModel):
    model_config = ConfigDict(extra="forbid")

    legacy_path: str
    react_path: str
    compatibility_status: str
    preserved_params: tuple[str, ...] = Field(default_factory=tuple)
    authorization_behavior: str
    evidence: tuple[str, ...] = Field(default_factory=tuple)
    notes: str

    @field_validator("legacy_path", "react_path")
    @classmethod
    def route_path_is_safe(cls, value: str) -> str:
        normalized = safe_text(value, max_length=240)
        lowered = normalized.lower()
        if any(marker in lowered for marker in SKILL_LIFECYCLE_UNSAFE_MARKERS):
            raise ValueError("unsafe skill lifecycle path cannot be rendered")
        if not normalized.startswith("/admin/"):
            raise ValueError("legacy route mappings must stay on admin routes")
        return normalized

    @field_validator(
        "compatibility_status",
        "authorization_behavior",
        "notes",
    )
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_skill_lifecycle_text(value, max_length=240)

    @field_validator("preserved_params", "evidence")
    @classmethod
    def tuple_text_is_safe(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(safe_skill_lifecycle_text(item, max_length=180) for item in value)


class SkillLifecycleDashboard(BaseModel):
    model_config = ConfigDict(extra="forbid")

    page_id: str
    title: str
    description: str
    scope: ReactAdminScope
    sections: tuple[SkillLifecycleSection, ...] = Field(default_factory=tuple)
    setup_summary: tuple[str, ...] = Field(default_factory=tuple)
    platform_publication: PackagePublicationWorkspace | None = None
    tenant_discovery: TenantSkillDiscovery | None = None
    installations: tuple[TenantSkillInstallationSummary, ...] = Field(
        default_factory=tuple
    )
    connector_diagnostics: tuple[ConnectorReadinessSummary, ...] = Field(
        default_factory=tuple
    )
    skill_execution_diagnostics: tuple[SkillExecutionDiagnosticSummary, ...] = Field(
        default_factory=tuple
    )
    binding_preview: BindingEligibilityPreview
    audit_timeline: tuple[SkillLifecycleAuditRecord, ...] = Field(default_factory=tuple)
    legacy_routes: tuple[SkillLegacyRouteMapping, ...] = Field(default_factory=tuple)
    actions: tuple[AdminAction, ...] = Field(default_factory=tuple)
    state: ReactAdminShellState | None = None
    refresh: RefreshHint | None = None
    provenance: ReactAdminPageProvenance | None = None
    empty_state: ReactAdminEmptyStateMetadata | None = None

    @field_validator("title", "description")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_skill_lifecycle_text(value, max_length=220)

    @field_validator("setup_summary")
    @classmethod
    def summary_is_safe(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(safe_skill_lifecycle_text(item, max_length=180) for item in value)


class SkillPackageCandidateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    manifest_text: str | None = None
    uploaded_fixture_id: str | None = None
    candidate_revision: str | None = None
    idempotency_key: str

    @field_validator("uploaded_fixture_id", "candidate_revision", "idempotency_key")
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_skill_lifecycle_text(value, max_length=160)


class SkillPackagePublishRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate_revision: str
    confirmed: bool = False
    idempotency_key: str

    @field_validator("candidate_revision", "idempotency_key")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_skill_lifecycle_text(value, max_length=160)


class TenantGrantMutationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_id: str
    version_id: str
    grant_enabled: bool
    revision: str
    idempotency_key: str

    @field_validator("version_id", "revision", "idempotency_key")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_skill_lifecycle_text(value, max_length=160)


class TenantSkillInstallRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    package_id: str
    version_id: str
    revision: str
    idempotency_key: str
    upgrade: bool = False

    @field_validator("package_id", "version_id", "revision", "idempotency_key")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_skill_lifecycle_text(value, max_length=160)


class CredentialConfigurationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    selected_reference_id: str
    revision: str
    idempotency_key: str

    @field_validator("selected_reference_id", "revision", "idempotency_key")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_skill_lifecycle_text(value, max_length=160)


class ReadinessRefreshRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    revision: str
    idempotency_key: str

    @field_validator("revision", "idempotency_key")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_skill_lifecycle_text(value, max_length=160)


class BindingEligibilityPreviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workflow_context: str
    profile_id: str
    package_id: str

    @field_validator("workflow_context", "profile_id", "package_id")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_skill_lifecycle_text(value, max_length=180)


class SkillLifecycleMutationResult(MutationResult):
    revision: str | None = None
    publication: SkillPackageVersionSummary | None = None
    installation: TenantSkillInstallationSummary | None = None
    credential: CredentialReferenceOption | None = None
    smoke_test: ConnectorReadinessSummary | None = None
    diagnostic: SkillExecutionDiagnosticSummary | None = None
    binding_preview: BindingEligibilityPreview | None = None
    diagnostics: tuple[str, ...] = Field(default_factory=tuple)

    @field_validator("summary", "audit_reference_id", "revision")
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_skill_lifecycle_text(value, max_length=220)

    @field_validator("diagnostics")
    @classmethod
    def diagnostics_are_safe(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(safe_skill_lifecycle_text(item, max_length=180) for item in value)


class TenantSkillDiscoveryList(BaseModel):
    model_config = ConfigDict(extra="forbid")

    discovery: TenantSkillDiscovery
    provenance: ReactAdminPageProvenance | None = None
    empty_state: ReactAdminEmptyStateMetadata | None = None


class TenantSkillInstallationList(BaseModel):
    model_config = ConfigDict(extra="forbid")

    installations: tuple[TenantSkillInstallationSummary, ...] = Field(
        default_factory=tuple
    )
    provenance: ReactAdminPageProvenance | None = None
    empty_state: ReactAdminEmptyStateMetadata | None = None


class SkillExecutionDiagnosticList(BaseModel):
    model_config = ConfigDict(extra="forbid")

    diagnostics: tuple[SkillExecutionDiagnosticSummary, ...] = Field(
        default_factory=tuple
    )
    provenance: ReactAdminPageProvenance | None = None
    empty_state: ReactAdminEmptyStateMetadata | None = None


class SkillLifecycleAuditList(BaseModel):
    model_config = ConfigDict(extra="forbid")

    audit_timeline: tuple[SkillLifecycleAuditRecord, ...] = Field(default_factory=tuple)
    provenance: ReactAdminPageProvenance | None = None
    empty_state: ReactAdminEmptyStateMetadata | None = None
