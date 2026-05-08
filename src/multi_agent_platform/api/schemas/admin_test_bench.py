from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from multi_agent_platform.api.schemas.admin_patterns import (
    AdminAction,
    AdminMutationStatus,
    RefreshHint,
    RevisionConflict,
    ToastHint,
    ValidationFieldError,
    safe_text,
)
from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminEmptyStateMetadata,
    ReactAdminEmptyStateReason,
    ReactAdminPageProvenance,
    ReactAdminScope,
    ReactAdminSourceKind,
)

TEST_BENCH_UNSAFE_MARKERS = (
    "qa033-secret-value",
    "raw prompt",
    "raw completion",
    "raw transcript",
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
    "storage path",
    "/users/",
    "globex secret",
)


def safe_test_bench_text(value: str, *, max_length: int = 240) -> str:
    normalized = safe_text(value, max_length=max_length)
    lowered = normalized.lower()
    if any(marker in lowered for marker in TEST_BENCH_UNSAFE_MARKERS):
        raise ValueError("unsafe test bench text cannot be rendered")
    if normalized.startswith("/"):
        raise ValueError("local paths cannot be rendered")
    return normalized


class TestBenchStatus(StrEnum):
    READY = "ready"
    WARNING = "warning"
    BLOCKED = "blocked"
    DENIED = "denied"
    UNAVAILABLE = "unavailable"
    MISSING = "missing"
    STALE = "stale"
    QUEUED = "queued"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    FAILED_ASSERTION = "failed_assertion"
    CONTRACT_FAILURE = "contract_failure"
    EVALUATOR_FAILURE = "evaluator_failure"
    SAFE_MODE_BLOCK = "safe_mode_block"
    RUNTIME_ERROR = "runtime_error"
    CANCELED = "canceled"
    TIMED_OUT = "timed_out"
    PARTIAL = "partial"
    SUMMARIZED = "summarized"
    ARTIFACT_UNAVAILABLE = "artifact_unavailable"
    AUDIT_UNAVAILABLE = "audit_unavailable"
    REDACTION_UNAVAILABLE = "redaction_unavailable"


def live_test_bench_provenance(
    *, source_label: str, source_detail: str | None = None
) -> ReactAdminPageProvenance:
    return ReactAdminPageProvenance(
        source_kind=ReactAdminSourceKind.LIVE_REPOSITORY,
        source_label=source_label,
        source_detail=source_detail,
    )


def empty_test_bench_state(
    *,
    title: str,
    summary: str,
    setup_hint: str | None = None,
    source_label: str = "Agent test bench records",
) -> ReactAdminEmptyStateMetadata:
    return ReactAdminEmptyStateMetadata(
        reason=ReactAdminEmptyStateReason.NO_LIVE_ROWS,
        title=title,
        summary=summary,
        setup_hint=setup_hint,
        provenance=ReactAdminPageProvenance(
            source_kind=ReactAdminSourceKind.EMPTY_LIVE_STATE,
            source_label=source_label,
            source_detail="No authorized live test bench records exist for this scope.",
        ),
    )


class TestBenchSection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    section_id: str
    label: str
    status: TestBenchStatus
    summary: str
    href: str | None = None

    @field_validator("label", "summary")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_test_bench_text(value, max_length=180)


class TestBenchSummaryMetric(BaseModel):
    model_config = ConfigDict(extra="forbid")

    metric_id: str
    label: str
    value: str
    status: TestBenchStatus
    summary: str

    @field_validator("label", "value", "summary")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_test_bench_text(value, max_length=180)


class TargetOption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_type: str
    target_id: str
    label: str
    current_revision: str
    revision_status: TestBenchStatus
    safe_summary: str
    authorized: bool = True

    @field_validator(
        "target_type",
        "target_id",
        "label",
        "current_revision",
        "safe_summary",
    )
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_test_bench_text(value, max_length=200)


class AssertionDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    assertion_id: str
    label: str
    kind: str
    path_summary: str
    comparator: str
    expected_summary: str
    severity: str
    threshold_weight: float = Field(ge=0, le=1)
    validation_status: TestBenchStatus
    field_errors: tuple[ValidationFieldError, ...] = Field(default_factory=tuple)

    @field_validator(
        "assertion_id",
        "label",
        "kind",
        "path_summary",
        "comparator",
        "expected_summary",
        "severity",
    )
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_test_bench_text(value, max_length=200)


class TestCaseSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str
    case_name: str
    case_status: TestBenchStatus
    case_revision: str
    fixture_summary: str
    expected_contract_summary: str
    assertions: tuple[AssertionDefinition, ...] = Field(default_factory=tuple)
    evaluator_summary: str
    threshold_contribution: float = Field(ge=0, le=1)
    order: int = Field(ge=0)
    audit_reference_id: str
    authorized_actions: tuple[AdminAction, ...] = Field(default_factory=tuple)

    @field_validator(
        "case_id",
        "case_name",
        "case_revision",
        "fixture_summary",
        "expected_contract_summary",
        "evaluator_summary",
        "audit_reference_id",
    )
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_test_bench_text(value, max_length=220)


class TargetRevisionBinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_type: str
    target_id: str
    target_label: str
    current_revision: str
    selected_revision: str
    revision_status: TestBenchStatus
    source_links: tuple[AdminAction, ...] = Field(default_factory=tuple)
    stale_reason: str | None = None
    remediation: str

    @field_validator(
        "target_type",
        "target_id",
        "target_label",
        "current_revision",
        "selected_revision",
        "stale_reason",
        "remediation",
    )
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_test_bench_text(value, max_length=220)


class SafeExecutionModeOption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mode_id: str
    label: str
    side_effect_posture: str
    model_behavior: str
    tool_behavior: str
    credential_behavior: str
    allowed_status: TestBenchStatus
    policy_reason: str
    requires_approval: bool = False
    approval_reference_id: str | None = None
    audit_reference_id: str | None = None

    @field_validator(
        "mode_id",
        "label",
        "side_effect_posture",
        "model_behavior",
        "tool_behavior",
        "credential_behavior",
        "policy_reason",
        "approval_reference_id",
        "audit_reference_id",
    )
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_test_bench_text(value, max_length=220)


class TestBenchFormMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_options: tuple[TargetOption, ...] = Field(default_factory=tuple)
    safe_modes: tuple[SafeExecutionModeOption, ...] = Field(default_factory=tuple)
    assertion_templates: tuple[AssertionDefinition, ...] = Field(default_factory=tuple)
    run_reason_options: tuple[str, ...] = Field(default_factory=tuple)
    default_safe_mode: str
    default_pass_threshold: float = Field(ge=0, le=1)

    @field_validator("run_reason_options")
    @classmethod
    def reasons_are_safe(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(safe_test_bench_text(item, max_length=140) for item in value)

    @field_validator("default_safe_mode")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_test_bench_text(value, max_length=120)


class TestRunProgressSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: TestBenchStatus
    summary: str
    completed_cases: int = Field(ge=0)
    total_cases: int = Field(ge=0)
    next_poll_seconds: int = Field(ge=0)
    sse_href: str | None = None
    audit_reference_id: str

    @field_validator("summary", "audit_reference_id")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_test_bench_text(value, max_length=220)


class TestRunSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    suite_id: str
    suite_name: str
    target_revision: str
    safe_mode: str
    status: TestBenchStatus
    pass_rate: float = Field(ge=0, le=1)
    failure_category: TestBenchStatus | None = None
    started_label: str
    finished_label: str | None = None
    actor_label: str
    case_total: int = Field(ge=0)
    case_passed: int = Field(ge=0)
    case_failed: int = Field(ge=0)
    usage_summary: str
    latency_summary: str
    audit_reference_id: str
    authorized_actions: tuple[AdminAction, ...] = Field(default_factory=tuple)

    @field_validator(
        "run_id",
        "suite_id",
        "suite_name",
        "target_revision",
        "safe_mode",
        "started_label",
        "finished_label",
        "actor_label",
        "usage_summary",
        "latency_summary",
        "audit_reference_id",
    )
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_test_bench_text(value, max_length=220)


class DiagnosticFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    finding_id: str
    category: TestBenchStatus
    label: str
    expected_summary: str
    actual_summary: str
    comparator: str
    path_summary: str
    severity: str
    remediation: str

    @field_validator(
        "finding_id",
        "label",
        "expected_summary",
        "actual_summary",
        "comparator",
        "path_summary",
        "severity",
        "remediation",
    )
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_test_bench_text(value, max_length=220)


class TraceStepSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step_id: str
    case_id: str
    step_label: str
    runtime_role: str
    status: TestBenchStatus
    latency_ms: int = Field(ge=0)
    token_usage: str
    model_label: str
    provider_label: str
    prompt_version_label: str
    profile_version_label: str
    skill_version_labels: tuple[str, ...] = Field(default_factory=tuple)
    safe_transcript_excerpt: str
    blocked_side_effects: tuple[str, ...] = Field(default_factory=tuple)
    gateway_decision: str
    redaction_class: str
    artifact_reference_ids: tuple[str, ...] = Field(default_factory=tuple)

    @field_validator(
        "step_id",
        "case_id",
        "step_label",
        "runtime_role",
        "token_usage",
        "model_label",
        "provider_label",
        "prompt_version_label",
        "profile_version_label",
        "safe_transcript_excerpt",
        "gateway_decision",
        "redaction_class",
    )
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_test_bench_text(value, max_length=220)

    @field_validator("skill_version_labels", "blocked_side_effects")
    @classmethod
    def tuple_text_is_safe(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(safe_test_bench_text(item, max_length=160) for item in value)


class ArtifactReferenceSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_reference_id: str
    label: str
    content_class: str
    checksum: str
    size_label: str
    retention_state: TestBenchStatus
    redaction_class: str
    access_status: TestBenchStatus
    safe_summary: str
    authorized_href: str | None = None
    audit_reference_id: str

    @field_validator(
        "artifact_reference_id",
        "label",
        "content_class",
        "checksum",
        "size_label",
        "redaction_class",
        "safe_summary",
        "audit_reference_id",
    )
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_test_bench_text(value, max_length=220)


class PublishGateEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    gate_id: str
    target_type: str
    target_label: str
    target_revision: str
    required_suite_id: str
    required_suite_label: str
    evidence_status: TestBenchStatus
    latest_run_id: str | None = None
    latest_run_revision: str | None = None
    latest_run_status: TestBenchStatus | None = None
    reason: str
    remediation: str
    audit_reference_id: str
    artifact_references: tuple[ArtifactReferenceSummary, ...] = Field(
        default_factory=tuple
    )
    authorized_actions: tuple[AdminAction, ...] = Field(default_factory=tuple)

    @field_validator(
        "gate_id",
        "target_type",
        "target_label",
        "target_revision",
        "required_suite_id",
        "required_suite_label",
        "latest_run_id",
        "latest_run_revision",
        "reason",
        "remediation",
        "audit_reference_id",
    )
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_test_bench_text(value, max_length=220)


class TestSuiteSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    suite_id: str
    suite_slug: str
    suite_name: str
    tenant_id: str
    tenant_label: str
    target_type: str
    target_label: str
    target_revision: str
    target_status: TestBenchStatus
    default_safe_mode: str
    pass_threshold: float = Field(ge=0, le=1)
    required_for_publish: bool
    case_count: int = Field(ge=0)
    latest_run_status: TestBenchStatus
    latest_run_id: str | None = None
    publish_gate_status: TestBenchStatus
    suite_revision: str
    archive_status: TestBenchStatus
    audit_reference_id: str
    authorized_actions: tuple[AdminAction, ...] = Field(default_factory=tuple)

    @field_validator(
        "suite_id",
        "suite_slug",
        "suite_name",
        "tenant_id",
        "tenant_label",
        "target_type",
        "target_label",
        "target_revision",
        "default_safe_mode",
        "latest_run_id",
        "suite_revision",
        "audit_reference_id",
    )
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_test_bench_text(value, max_length=220)


class TestSuiteDetail(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: TestSuiteSummary
    cases: tuple[TestCaseSummary, ...] = Field(default_factory=tuple)
    target_binding: TargetRevisionBinding
    run_launcher: TestBenchFormMetadata
    recent_runs: tuple[TestRunSummary, ...] = Field(default_factory=tuple)
    publish_gate: PublishGateEvidence
    audit_reference_id: str

    @field_validator("audit_reference_id")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_test_bench_text(value, max_length=180)


class TestRunDetail(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: TestRunSummary
    progress: TestRunProgressSnapshot
    case_results: tuple[TestCaseSummary, ...] = Field(default_factory=tuple)
    trace_steps: tuple[TraceStepSummary, ...] = Field(default_factory=tuple)
    assertion_diagnostics: tuple[DiagnosticFinding, ...] = Field(default_factory=tuple)
    artifacts: tuple[ArtifactReferenceSummary, ...] = Field(default_factory=tuple)
    publish_gate: PublishGateEvidence
    redaction_summary: str
    blocked_side_effects: tuple[str, ...] = Field(default_factory=tuple)
    audit_reference_id: str

    @field_validator("redaction_summary", "audit_reference_id")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_test_bench_text(value, max_length=220)

    @field_validator("blocked_side_effects")
    @classmethod
    def tuple_text_is_safe(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(safe_test_bench_text(item, max_length=160) for item in value)


class TestBenchAuditRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    record_id: str
    domain: str
    tenant_scope_label: str
    actor_label: str
    target_label: str
    timestamp_label: str
    action: str
    outcome: TestBenchStatus
    safe_diff_summary: str
    redaction_class: str
    audit_reference_id: str
    links: tuple[AdminAction, ...] = Field(default_factory=tuple)

    @field_validator(
        "record_id",
        "domain",
        "tenant_scope_label",
        "actor_label",
        "target_label",
        "timestamp_label",
        "action",
        "safe_diff_summary",
        "redaction_class",
        "audit_reference_id",
    )
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_test_bench_text(value, max_length=220)


class TestBenchDashboard(BaseModel):
    model_config = ConfigDict(extra="forbid")

    page_id: str
    title: str
    description: str
    scope: ReactAdminScope
    sections: tuple[TestBenchSection, ...] = Field(default_factory=tuple)
    summary_cards: tuple[TestBenchSummaryMetric, ...] = Field(default_factory=tuple)
    gate_alerts: tuple[PublishGateEvidence, ...] = Field(default_factory=tuple)
    suites: tuple[TestSuiteSummary, ...] = Field(default_factory=tuple)
    selected_suite: TestSuiteDetail | None = None
    recent_runs: tuple[TestRunSummary, ...] = Field(default_factory=tuple)
    audit_timeline: tuple[TestBenchAuditRecord, ...] = Field(default_factory=tuple)
    refresh: RefreshHint | None = None
    actions: tuple[AdminAction, ...] = Field(default_factory=tuple)
    provenance: ReactAdminPageProvenance | None = None
    empty_state: ReactAdminEmptyStateMetadata | None = None

    @field_validator("page_id", "title", "description")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_test_bench_text(value, max_length=240)


class TestSuiteList(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scope: ReactAdminScope
    suites: tuple[TestSuiteSummary, ...] = Field(default_factory=tuple)
    form_metadata: TestBenchFormMetadata
    provenance: ReactAdminPageProvenance | None = None
    empty_state: ReactAdminEmptyStateMetadata | None = None


class TestRunList(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scope: ReactAdminScope
    runs: tuple[TestRunSummary, ...] = Field(default_factory=tuple)
    provenance: ReactAdminPageProvenance | None = None
    empty_state: ReactAdminEmptyStateMetadata | None = None


class PublishGateEvidenceList(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scope: ReactAdminScope
    gates: tuple[PublishGateEvidence, ...] = Field(default_factory=tuple)
    provenance: ReactAdminPageProvenance | None = None
    empty_state: ReactAdminEmptyStateMetadata | None = None


class TestBenchAuditList(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scope: ReactAdminScope
    audit_timeline: tuple[TestBenchAuditRecord, ...] = Field(default_factory=tuple)
    provenance: ReactAdminPageProvenance | None = None
    empty_state: ReactAdminEmptyStateMetadata | None = None


class TestBenchMutationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: AdminMutationStatus
    summary: str
    revision: str | None = None
    toast: ToastHint | None = None
    suite: TestSuiteDetail | None = None
    case: TestCaseSummary | None = None
    run: TestRunDetail | None = None
    gate: PublishGateEvidence | None = None
    artifact: ArtifactReferenceSummary | None = None
    audit_reference_id: str | None = None
    field_errors: tuple[ValidationFieldError, ...] = Field(default_factory=tuple)
    stale_conflict: RevisionConflict | None = None
    diagnostics: tuple[str, ...] = Field(default_factory=tuple)

    @field_validator("summary", "revision", "audit_reference_id")
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_test_bench_text(value, max_length=220)

    @field_validator("diagnostics")
    @classmethod
    def tuple_text_is_safe(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(safe_test_bench_text(item, max_length=220) for item in value)


class TestSuiteSaveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    description: str | None = None
    target_type: str
    target_id: str
    target_revision: str
    default_safe_mode: str
    pass_threshold: float = Field(ge=0, le=1)
    required_for_publish: bool = True
    revision: str | None = None
    idempotency_key: str

    @field_validator(
        "name",
        "description",
        "target_type",
        "target_id",
        "target_revision",
        "default_safe_mode",
        "revision",
        "idempotency_key",
    )
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_test_bench_text(value, max_length=220)


class TestCaseSaveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    fixture_summary: str
    expected_contract_summary: str
    assertions: tuple[AssertionDefinition, ...] = Field(default_factory=tuple)
    evaluator_reference_id: str | None = None
    revision: str | None = None
    idempotency_key: str

    @field_validator(
        "name",
        "fixture_summary",
        "expected_contract_summary",
        "evaluator_reference_id",
        "revision",
        "idempotency_key",
    )
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_test_bench_text(value, max_length=220)


class TestRunLaunchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_revision: str
    safe_mode: str
    run_reason: str = "Release confidence"
    idempotency_key: str

    @field_validator("target_revision", "safe_mode", "run_reason", "idempotency_key")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_test_bench_text(value, max_length=220)


class GateEvidenceRefreshRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_revision: str
    idempotency_key: str

    @field_validator("target_revision", "idempotency_key")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_test_bench_text(value, max_length=180)
