from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from multi_agent_platform.api.schemas.admin_patterns import safe_text
from multi_agent_platform.api.schemas.admin_react import ReactAdminScope

MIGRATION_HARDENING_UNSAFE_MARKERS = (
    "qa037-secret-value",
    "bot token",
    "webhook secret",
    "credential value",
    "authorization header",
    "bearer ",
    "provider token",
    "raw prompt",
    "raw completion",
    "memory content",
    "private message",
    "raw run",
    "run result",
    "raw tool payload",
    "raw package payload",
    "raw test transcript",
    "private briefing",
    "full telegram",
    "telegram user id",
    "telegram chat id",
    "link token",
    "pair-code",
    "stack trace",
    "unauthorized tenant label",
    "/users/",
    "/Users/",
)


def safe_migration_text(value: str, *, max_length: int = 320) -> str:
    normalized = safe_text(value, max_length=max_length)
    lowered = normalized.lower()
    if any(marker.lower() in lowered for marker in MIGRATION_HARDENING_UNSAFE_MARKERS):
        raise ValueError("unsafe migration hardening text cannot be rendered")
    return normalized


def _validate_strings(value: object) -> None:
    if isinstance(value, str):
        safe_migration_text(value)
        return
    if isinstance(value, dict):
        for item in value.values():
            _validate_strings(item)
        return
    if isinstance(value, list | tuple):
        for item in value:
            _validate_strings(item)


class SafeMigrationHardeningModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def safe_string_payload(self) -> SafeMigrationHardeningModel:
        _validate_strings(self.model_dump(mode="python"))
        return self


class MigrationOverallStatus(StrEnum):
    READY = "ready"
    PARTIAL = "partial"
    BLOCKED = "blocked"
    ROLLBACK = "rollback"


class MigrationRouteDecision(StrEnum):
    REACT_PRIMARY = "react_primary"
    REDIRECT = "redirect"
    ALIAS = "alias"
    RETAINED_FALLBACK = "retained_fallback"
    RETIREMENT_CANDIDATE = "retirement_candidate"
    BLOCKED = "blocked"


class MigrationScopeRequirement(StrEnum):
    PLATFORM = "platform"
    TENANT_ADMIN = "tenant_admin"
    TENANT_USER = "tenant_user"
    AUDITOR = "auditor"
    MIXED = "mixed"


class MigrationEvidenceStatus(StrEnum):
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"


class MigrationProblemSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    BLOCKING = "blocking"


class MigrationHardeningSummary(SafeMigrationHardeningModel):
    total_destinations: int = Field(ge=0)
    react_primary_count: int = Field(ge=0)
    redirect_count: int = Field(ge=0)
    retained_fallback_count: int = Field(ge=0)
    retirement_candidate_count: int = Field(ge=0)
    blocked_count: int = Field(ge=0)
    overall_status: MigrationOverallStatus
    next_step: str


class MigrationRouteEntry(SafeMigrationHardeningModel):
    entry_id: str
    admin_area: str
    legacy_route: str | None = None
    react_route: str | None = None
    decision: MigrationRouteDecision
    scope_requirement: MigrationScopeRequirement
    auth_modes: tuple[str, ...] = Field(default_factory=tuple, max_length=4)
    parity_evidence: tuple[str, ...] = Field(default_factory=tuple, max_length=10)
    redirect_preserves: tuple[str, ...] = Field(default_factory=tuple, max_length=8)
    fallback_notice: str | None = None
    retirement_allowed: bool = False
    rollback_reference: str
    audit_reference: str

    @model_validator(mode="after")
    def retirement_requires_evidence(self) -> MigrationRouteEntry:
        if self.retirement_allowed and (
            not self.parity_evidence
            or self.decision
            not in {
                MigrationRouteDecision.REACT_PRIMARY,
                MigrationRouteDecision.RETIREMENT_CANDIDATE,
                MigrationRouteDecision.REDIRECT,
                MigrationRouteDecision.ALIAS,
            }
        ):
            raise ValueError("retirement requires approved parity evidence")
        return self


class MigrationRouteGroup(SafeMigrationHardeningModel):
    group_id: str
    label: str
    spec_refs: tuple[str, ...] = Field(default_factory=tuple, max_length=12)
    group_status: MigrationOverallStatus
    entries: tuple[MigrationRouteEntry, ...] = Field(
        default_factory=tuple,
        max_length=40,
    )


class MigrationRollbackPlan(SafeMigrationHardeningModel):
    plan_id: str
    status: MigrationOverallStatus
    feature_flag_label: str
    asset_version_label: str
    steps: tuple[str, ...] = Field(default_factory=tuple, max_length=12)
    verification_steps: tuple[str, ...] = Field(default_factory=tuple, max_length=12)
    owner_label: str
    last_reviewed_at: datetime
    audit_reference: str


class MigrationPerformanceMeasurement(SafeMigrationHardeningModel):
    measurement_id: str
    label: str
    value: float = Field(ge=0)
    unit: str
    limit: float = Field(ge=0)
    status: MigrationEvidenceStatus
    evidence_reference: str


class MigrationPerformanceBudget(SafeMigrationHardeningModel):
    budget_id: str
    route_bootstrap_ms_limit: int = Field(ge=1)
    primary_interactive_ms_limit: int = Field(ge=1)
    compressed_asset_kb_limit: int = Field(ge=1)
    status: MigrationEvidenceStatus
    mitigation: str | None = None
    measurements: tuple[MigrationPerformanceMeasurement, ...] = Field(
        default_factory=tuple,
        max_length=12,
    )


class MigrationAccessibilityAudit(SafeMigrationHardeningModel):
    audit_id: str
    status: MigrationEvidenceStatus
    viewport_coverage: tuple[str, ...] = Field(default_factory=tuple, max_length=8)
    keyboard_status: MigrationEvidenceStatus
    focus_status: MigrationEvidenceStatus
    landmark_status: MigrationEvidenceStatus
    label_status: MigrationEvidenceStatus
    contrast_state_status: MigrationEvidenceStatus
    text_overlap_status: MigrationEvidenceStatus
    evidence_references: tuple[str, ...] = Field(default_factory=tuple, max_length=12)


class MigrationSweepSummary(SafeMigrationHardeningModel):
    sweep_id: str
    status: MigrationEvidenceStatus
    checked_artifacts: int = Field(ge=0)
    unsafe_match_count: int = Field(ge=0)
    safe_summary: str
    evidence_reference: str

    @model_validator(mode="after")
    def failed_sweep_requires_match(self) -> MigrationSweepSummary:
        if self.status == MigrationEvidenceStatus.FAIL and self.unsafe_match_count == 0:
            raise ValueError("failed sweep requires unsafe matches")
        return self


class MigrationProblem(SafeMigrationHardeningModel):
    reason: str
    title: str
    detail: str
    next_action: str
    severity: MigrationProblemSeverity
    audit_reference: str | None = None


class AdminMigrationHardeningDashboard(SafeMigrationHardeningModel):
    page_id: str
    title: str
    description: str
    scope: ReactAdminScope
    updated_at: datetime
    summary: MigrationHardeningSummary
    route_groups: tuple[MigrationRouteGroup, ...] = Field(
        default_factory=tuple,
        max_length=20,
    )
    rollback_plan: MigrationRollbackPlan
    performance_budget: MigrationPerformanceBudget
    accessibility_audit: MigrationAccessibilityAudit
    redaction_sweep: MigrationSweepSummary
    tenant_isolation_sweep: MigrationSweepSummary
    states: tuple[MigrationProblem, ...] = Field(default_factory=tuple, max_length=12)
