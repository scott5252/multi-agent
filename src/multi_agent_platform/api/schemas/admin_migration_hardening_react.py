from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from multi_agent_platform.api.schemas.admin_patterns import safe_text
from multi_agent_platform.api.schemas.admin_react import ReactAdminScope

MIGRATION_HARDENING_UNSAFE_MARKERS = (
    "qa038-secret-value",
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


class JinjaInventoryItemType(StrEnum):
    TEMPLATE = "template"
    TEMPLATE_INCLUDE = "template_include"
    TEMPLATE_RESPONSE = "template_response"
    JINJA_IMPORT = "jinja_import"
    TEMPLATE_HELPER = "template_helper"
    STATIC_ASSET = "static_asset"
    ROUTE = "route"
    DIRECT_LINK = "direct_link"
    FORM_ACTION = "form_action"
    EXPORT = "export"
    UPLOAD = "upload"
    FILTER = "filter"
    SSE_PROGRESS = "sse_progress"
    MUTATION = "mutation"
    DENIED_STATE = "denied_state"
    REACT_HOST = "react_host"


class JinjaInventoryClassification(StrEnum):
    REACT_PARITY_PROVEN = "react_parity_proven"
    REACT_PARITY_MISSING = "react_parity_missing"
    REDIRECTABLE = "redirectable"
    NON_JINJA_COMPATIBILITY_NEEDED = "non_jinja_compatibility_needed"
    SAFE_TO_DELETE = "safe_to_delete"
    BLOCKED_WITH_REASON = "blocked_with_reason"


class JinjaInventoryEvidenceType(StrEnum):
    SCANNER = "scanner"
    CONTRACT_TEST = "contract_test"
    BACKEND_ROUTE_TEST = "backend_route_test"
    FRONTEND_TEST = "frontend_test"
    PLAYWRIGHT = "playwright"
    QA_DOC = "qa_doc"
    REDACTION = "redaction"
    TENANT_ISOLATION = "tenant_isolation"
    REVIEWER_NOTE = "reviewer_note"


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


class JinjaInventorySummary(SafeMigrationHardeningModel):
    generated_at: datetime
    total_items: int = Field(ge=0)
    template_count: int = Field(ge=0)
    route_count: int = Field(ge=0)
    static_asset_count: int = Field(ge=0)
    direct_link_count: int = Field(ge=0)
    blocked_count: int = Field(ge=0)
    safe_to_delete_count: int = Field(ge=0)
    reviewer_signoff_required: bool = True


class JinjaInventoryItem(SafeMigrationHardeningModel):
    item_id: str
    item_type: JinjaInventoryItemType
    label: str
    source_path: str | None = None
    source_line: int | None = Field(default=None, ge=1)
    legacy_route: str | None = None
    react_path: str | None = None
    methods: tuple[str, ...] = Field(default_factory=tuple, max_length=8)
    owner_category: str
    planned_removal_spec: str
    classification: JinjaInventoryClassification
    evidence_refs: tuple[str, ...] = Field(default_factory=tuple, max_length=12)
    blocker_refs: tuple[str, ...] = Field(default_factory=tuple, max_length=12)
    redirect_preserves: tuple[str, ...] = Field(default_factory=tuple, max_length=8)
    behaviors: tuple[str, ...] = Field(default_factory=tuple, max_length=12)
    reviewer_signoff_required: bool = True
    notes: str

    @model_validator(mode="after")
    def safe_delete_requires_evidence(self) -> JinjaInventoryItem:
        if self.classification == JinjaInventoryClassification.SAFE_TO_DELETE:
            if not self.evidence_refs or not self.reviewer_signoff_required:
                raise ValueError(
                    "safe-to-delete inventory requires evidence and signoff"
                )
            if not self.planned_removal_spec:
                raise ValueError("safe-to-delete inventory requires removal spec")
        if self.source_path and self.source_path.startswith("/"):
            raise ValueError("inventory source paths must be repository-relative")
        return self


class JinjaInventoryGroup(SafeMigrationHardeningModel):
    group_id: str
    label: str
    planned_removal_spec: str
    blocked_count: int = Field(ge=0)
    safe_to_delete_count: int = Field(ge=0)
    items: tuple[JinjaInventoryItem, ...] = Field(default_factory=tuple)


class JinjaInventoryEvidence(SafeMigrationHardeningModel):
    evidence_id: str
    evidence_type: JinjaInventoryEvidenceType
    reference: str
    status: MigrationEvidenceStatus

    @model_validator(mode="after")
    def reference_must_be_relative_or_safe_id(self) -> JinjaInventoryEvidence:
        if self.reference.startswith("/"):
            raise ValueError(
                "inventory evidence references must be repository-relative"
            )
        return self


class JinjaInventoryDashboard(SafeMigrationHardeningModel):
    summary: JinjaInventorySummary
    groups: tuple[JinjaInventoryGroup, ...] = Field(default_factory=tuple)
    evidence: tuple[JinjaInventoryEvidence, ...] = Field(default_factory=tuple)


class LiveDataInventorySeverity(StrEnum):
    BLOCKING = "blocking"
    WARNING = "warning"
    INFO = "info"


class LiveDataInventoryStatus(StrEnum):
    MAPPED_LEGACY = "mapped_legacy"
    ALLOWED_COMPUTED_METADATA = "allowed_computed_metadata"
    NEW_REGRESSION = "new_regression"
    TEST_ONLY = "test_only"


class LiveDataMarkerKind(StrEnum):
    QA_MARKER = "qa_marker"
    FAKE_AUDIT_REFERENCE = "fake_audit_reference"
    FAKE_ARTIFACT_REFERENCE = "fake_artifact_reference"
    FAKE_RUN_ID = "fake_run_id"
    FAKE_LINK_TOKEN = "fake_link_token"
    FIXTURE_COLLECTION = "fixture_collection"
    FAKE_MUTATION_SUCCESS = "fake_mutation_success"
    HARDCODED_DOMAIN_ENTITY = "hardcoded_domain_entity"
    TEST_FIXTURE_IMPORT = "test_fixture_import"


class LiveDataReachability(StrEnum):
    PRODUCTION_RESPONSE = "production_response"
    PRODUCTION_SOURCE = "production_source"
    GENERATED_CONTRACT = "generated_contract"
    BUILT_ASSET = "built_asset"
    COMPUTED_METADATA = "computed_metadata"
    TEST_ONLY = "test_only"


class LiveDataCiStatus(StrEnum):
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"


class LiveDataInventoryEvidenceType(StrEnum):
    SCANNER = "scanner"
    ROUTE_RESPONSE_SCAN = "route_response_scan"
    CONTRACT_TEST = "contract_test"
    BACKEND_ROUTE_TEST = "backend_route_test"
    FRONTEND_TEST = "frontend_test"
    PLAYWRIGHT = "playwright"
    QA_DOC = "qa_doc"
    REVIEWER_NOTE = "reviewer_note"
    CURL_TEST = "curl_test"


class LiveDataInventoryFinding(SafeMigrationHardeningModel):
    finding_id: str
    severity: LiveDataInventorySeverity
    status: LiveDataInventoryStatus
    marker_kind: LiveDataMarkerKind
    source_path: str
    route_path: str | None = None
    owner_spec: str | None = None
    replacement_spec: str | None = None
    durable_source: str
    reachability: LiveDataReachability
    safe_excerpt: str

    @model_validator(mode="after")
    def source_paths_must_be_relative(self) -> LiveDataInventoryFinding:
        if self.source_path.startswith("/"):
            raise ValueError("live-data inventory paths must be repository-relative")
        if self.status == LiveDataInventoryStatus.NEW_REGRESSION and (
            self.severity != LiveDataInventorySeverity.BLOCKING
        ):
            raise ValueError("new live-data regressions must be blocking")
        return self


class LiveDataAllowlistEntry(SafeMigrationHardeningModel):
    allowlist_id: str
    scope: str
    marker_kind: LiveDataMarkerKind
    reason: str
    derivation_source: str
    owner: str
    expires_with_spec: str | None = None

    @model_validator(mode="after")
    def allowlist_must_be_narrow(self) -> LiveDataAllowlistEntry:
        if self.scope in {"src", "src/", "frontend", "frontend/"}:
            raise ValueError("live-data allowlist scope is too broad")
        if not self.reason or not self.derivation_source:
            raise ValueError("live-data allowlist requires reason and source")
        return self


class LiveDataRouteTarget(SafeMigrationHardeningModel):
    target_id: str
    method: str
    path: str
    principal: str
    tenant_scope: str
    empty_state_required: bool
    seeded_state_required: bool
    computed_metadata_only: bool
    replacement_spec: str | None = None

    @model_validator(mode="after")
    def route_target_must_be_admin_app_json(self) -> LiveDataRouteTarget:
        if self.method not in {"GET", "POST"}:
            raise ValueError("live-data route targets use GET or POST")
        if not self.path.startswith("/admin/app"):
            raise ValueError("live-data route target must be under /admin/app")
        return self


class LiveDataScanSummary(SafeMigrationHardeningModel):
    total_findings: int = Field(ge=0)
    blocking_findings: int = Field(ge=0)
    mapped_legacy_findings: int = Field(ge=0)
    allowed_computed_metadata: int = Field(ge=0)
    test_only_markers: int = Field(ge=0)
    route_targets: int = Field(ge=0)
    empty_state_scans: int = Field(ge=0)
    seeded_state_scans: int = Field(ge=0)
    ci_status: LiveDataCiStatus
    next_step: str

    @model_validator(mode="after")
    def ci_status_matches_blocking_findings(self) -> LiveDataScanSummary:
        if self.ci_status == LiveDataCiStatus.FAIL and self.blocking_findings == 0:
            raise ValueError("failed live-data scan requires blocking findings")
        if self.empty_state_scans > self.route_targets:
            raise ValueError("empty scan count cannot exceed route targets")
        if self.seeded_state_scans > self.route_targets:
            raise ValueError("seeded scan count cannot exceed route targets")
        return self


class LiveDataInventoryEvidence(SafeMigrationHardeningModel):
    evidence_id: str
    evidence_type: LiveDataInventoryEvidenceType
    reference: str
    status: MigrationEvidenceStatus

    @model_validator(mode="after")
    def evidence_reference_must_be_relative(self) -> LiveDataInventoryEvidence:
        if self.reference.startswith("/"):
            raise ValueError("live-data evidence references must be relative")
        return self


class LiveDataInventoryDashboard(SafeMigrationHardeningModel):
    page_id: str
    generated_at: datetime
    summary: LiveDataScanSummary
    findings: tuple[LiveDataInventoryFinding, ...] = Field(default_factory=tuple)
    allowlist: tuple[LiveDataAllowlistEntry, ...] = Field(default_factory=tuple)
    route_targets: tuple[LiveDataRouteTarget, ...] = Field(default_factory=tuple)
    evidence: tuple[LiveDataInventoryEvidence, ...] = Field(default_factory=tuple)
    states: tuple[MigrationProblem, ...] = Field(default_factory=tuple, max_length=12)

    @model_validator(mode="after")
    def summary_matches_payload(self) -> LiveDataInventoryDashboard:
        if self.summary.total_findings != len(self.findings):
            raise ValueError("live-data summary total must match findings")
        if self.summary.route_targets != len(self.route_targets):
            raise ValueError("live-data summary route count must match targets")
        return self


class TransitionalLabelSeverity(StrEnum):
    BLOCKING = "blocking"
    WARNING = "warning"
    INFO = "info"


class TransitionalLabelClassification(StrEnum):
    BLOCKING_TRANSITIONAL_LABEL = "blocking_transitional_label"
    ALLOWED_IMPLEMENTATION_REFERENCE = "allowed_implementation_reference"
    TECHNICAL_QA_CONTEXT = "technical_qa_context"
    HISTORICAL_REFERENCE = "historical_reference"
    INTERNAL_GENERATED_IDENTIFIER = "internal_generated_identifier"


class TransitionalLabelEvidenceType(StrEnum):
    SCANNER = "scanner"
    ROUTE_RESPONSE = "route_response"
    PLAYWRIGHT = "playwright"
    DOCS = "docs"
    CURL = "curl"


class TransitionalLabelFinding(SafeMigrationHardeningModel):
    finding_id: str
    surface_id: str
    matched_text: str
    classification: TransitionalLabelClassification
    severity: TransitionalLabelSeverity
    rationale: str
    owner: str
    remediation: str | None = None

    @model_validator(mode="after")
    def blocking_labels_require_blocking_severity(
        self,
    ) -> TransitionalLabelFinding:
        if (
            self.classification
            == TransitionalLabelClassification.BLOCKING_TRANSITIONAL_LABEL
            and self.severity != TransitionalLabelSeverity.BLOCKING
        ):
            raise ValueError("blocking transitional labels must be blocking")
        if self.severity == TransitionalLabelSeverity.BLOCKING and not self.remediation:
            raise ValueError("blocking transitional labels require remediation")
        return self


class TransitionalLabelGateSummary(SafeMigrationHardeningModel):
    blocked_count: int = Field(ge=0)
    allowed_reference_count: int = Field(ge=0)
    surfaces_scanned: int = Field(ge=0)
    routes_scanned: int = Field(ge=0)
    screenshots_checked: int = Field(ge=0)
    ci_status: LiveDataCiStatus
    next_step: str

    @model_validator(mode="after")
    def ci_status_matches_blockers(self) -> TransitionalLabelGateSummary:
        if self.ci_status == LiveDataCiStatus.FAIL and self.blocked_count == 0:
            raise ValueError("failed transitional label gate requires blockers")
        if self.ci_status == LiveDataCiStatus.PASS and self.blocked_count:
            raise ValueError("passing transitional label gate cannot have blockers")
        return self


class TransitionalLabelEvidence(SafeMigrationHardeningModel):
    evidence_id: str
    evidence_type: TransitionalLabelEvidenceType
    reference: str
    status: MigrationEvidenceStatus

    @model_validator(mode="after")
    def evidence_reference_must_be_relative(self) -> TransitionalLabelEvidence:
        if self.reference.startswith("/"):
            raise ValueError("transitional label evidence references must be relative")
        return self


class TransitionalLabelGate(SafeMigrationHardeningModel):
    page_id: str
    generated_at: datetime
    summary: TransitionalLabelGateSummary
    findings: tuple[TransitionalLabelFinding, ...] = Field(default_factory=tuple)
    evidence: tuple[TransitionalLabelEvidence, ...] = Field(default_factory=tuple)
    states: tuple[MigrationProblem, ...] = Field(default_factory=tuple, max_length=12)

    @model_validator(mode="after")
    def summary_matches_findings(self) -> TransitionalLabelGate:
        blocked = sum(
            finding.classification
            == TransitionalLabelClassification.BLOCKING_TRANSITIONAL_LABEL
            for finding in self.findings
        )
        allowed = sum(
            finding.classification
            != TransitionalLabelClassification.BLOCKING_TRANSITIONAL_LABEL
            for finding in self.findings
        )
        if self.summary.blocked_count != blocked:
            raise ValueError("transitional label blocked count must match findings")
        if self.summary.allowed_reference_count != allowed:
            raise ValueError("transitional label allowed count must match findings")
        return self


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
    jinja_inventory: JinjaInventoryDashboard
    live_data_inventory: LiveDataInventoryDashboard | None = None
    transitional_label_gate: TransitionalLabelGate | None = None
    states: tuple[MigrationProblem, ...] = Field(default_factory=tuple, max_length=12)
