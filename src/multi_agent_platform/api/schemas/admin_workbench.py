from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from multi_agent_platform.api.schemas.admin_patterns import (
    AdminAction,
    EvidenceSummary,
    FilterProfile,
    RefreshHint,
    safe_text,
)
from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminScope,
    ReactAdminShellState,
)

WORKBENCH_UNSAFE_MARKERS = (
    "qa029-secret-value",
    "private channel message",
    "telegram update payload",
    "provider authorization",
    "raw provider response",
    "raw tool result",
)


def safe_workbench_text(value: str, *, max_length: int = 220) -> str:
    normalized = safe_text(value, max_length=max_length)
    lowered = normalized.lower()
    if any(marker in lowered for marker in WORKBENCH_UNSAFE_MARKERS):
        raise ValueError("unsafe workbench text cannot be rendered")
    return normalized


class WorkbenchStatus(StrEnum):
    READY = "ready"
    AVAILABLE = "available"
    DEGRADED = "degraded"
    WARNING = "warning"
    CRITICAL = "critical"
    EMPTY = "empty"
    DENIED = "denied"
    QUEUED = "queued"
    VALIDATION = "validation"
    CONFLICT = "conflict"
    NOT_FOUND = "not_found"
    UNAVAILABLE = "unavailable"


class WorkbenchSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class WorkbenchExportStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"
    EXPIRED = "expired"
    EMPTY = "empty"
    DENIED = "denied"
    VALIDATION = "validation"
    CONFLICT = "conflict"
    UNAVAILABLE = "unavailable"


class WorkbenchTimeRange(BaseModel):
    model_config = ConfigDict(extra="forbid")

    preset: str = "60m"
    label: str = "Last 60 minutes"
    start: datetime | None = None
    end: datetime | None = None

    @field_validator("label")
    @classmethod
    def label_is_safe(cls, value: str) -> str:
        return safe_workbench_text(value, max_length=80)


class WorkbenchLink(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str
    href: str

    @field_validator("label")
    @classmethod
    def label_is_safe(cls, value: str) -> str:
        return safe_workbench_text(value, max_length=90)


class WorkbenchMetric(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str
    value: str
    status: WorkbenchStatus = WorkbenchStatus.READY
    summary: str | None = None

    @field_validator("label", "value", "summary")
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_workbench_text(value, max_length=140)


class WorkbenchSummaryCard(BaseModel):
    model_config = ConfigDict(extra="forbid")

    card_id: str
    label: str
    value: str
    status: WorkbenchStatus
    severity: WorkbenchSeverity
    summary: str
    freshness_label: str
    trend: str | None = None
    href: str | None = None
    evidence_reference_id: str | None = None

    @field_validator("label", "value", "summary", "freshness_label", "trend")
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_workbench_text(value, max_length=180)


class LikelyCauseSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cause_id: str
    severity: WorkbenchSeverity
    affected_subsystem: str
    symptom: str
    likely_cause_category: str
    recommended_next_step: str
    href: str | None = None
    confidence_label: str = "High confidence"
    evidence_reference_id: str | None = None

    @field_validator(
        "affected_subsystem",
        "symptom",
        "likely_cause_category",
        "recommended_next_step",
        "confidence_label",
    )
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_workbench_text(value, max_length=180)


class HealthPressurePanel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    panel_id: str
    title: str
    status: WorkbenchStatus
    metrics: tuple[WorkbenchMetric, ...] = Field(default_factory=tuple)
    dependencies: tuple[WorkbenchMetric, ...] = Field(default_factory=tuple)
    freshness_label: str
    polling_allowed: bool = False
    partial_reason: str | None = None
    links: tuple[WorkbenchLink, ...] = Field(default_factory=tuple)

    @field_validator("title", "freshness_label", "partial_reason")
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_workbench_text(value, max_length=180)


class TimelineEventSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str
    occurred_at_label: str
    sequence: int | None = None
    category: str
    severity: WorkbenchSeverity
    status: WorkbenchStatus
    summary: str
    details: dict[str, str] = Field(default_factory=dict)
    trace_id: str | None = None
    audit_reference_id: str | None = None
    links: tuple[WorkbenchLink, ...] = Field(default_factory=tuple)

    @field_validator("occurred_at_label", "category", "summary")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_workbench_text(value, max_length=180)

    @field_validator("details")
    @classmethod
    def details_are_safe(cls, value: dict[str, str]) -> dict[str, str]:
        return {
            safe_workbench_text(key, max_length=80): safe_workbench_text(
                detail, max_length=160
            )
            for key, detail in value.items()
        }


class GraphBranchSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    branch_id: str
    label: str
    status: WorkbenchStatus
    node_count: int = Field(default=0, ge=0)
    completed_count: int = Field(default=0, ge=0)
    failed_count: int = Field(default=0, ge=0)
    waiting_count: int = Field(default=0, ge=0)
    join_policy: str | None = None
    join_decision: str | None = None
    manual_resolution_required: bool = False
    summary: str

    @field_validator("label", "join_policy", "join_decision", "summary")
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_workbench_text(value, max_length=180)


class GatewayAttemptSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    attempt_id: str
    provider_label: str
    model_label: str
    status: WorkbenchStatus
    latency_ms: int | None = Field(default=None, ge=0)
    retry_category: str | None = None
    breaker_category: str | None = None
    credential_diagnostic_category: str | None = None
    usage_reference_id: str | None = None
    safe_summary: str
    evidence_reference_id: str | None = None

    @field_validator(
        "provider_label",
        "model_label",
        "retry_category",
        "breaker_category",
        "credential_diagnostic_category",
        "safe_summary",
    )
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_workbench_text(value, max_length=160)


class ToolCallSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool_call_id: str
    tool_label: str
    connector_label: str
    readiness_status: WorkbenchStatus
    policy_outcome: str
    side_effect_classification: str
    result_category: str
    safe_summary: str
    evidence_reference_id: str | None = None

    @field_validator(
        "tool_label",
        "connector_label",
        "policy_outcome",
        "side_effect_classification",
        "result_category",
        "safe_summary",
    )
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_workbench_text(value, max_length=160)


class ChannelDeliverySummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    delivery_id: str
    channel: str
    alias_label: str
    identity_status: WorkbenchStatus
    receipt_status: WorkbenchStatus
    notification_status: WorkbenchStatus
    delivery_status: WorkbenchStatus
    failure_category: str | None = None
    safe_summary: str
    evidence_reference_id: str | None = None

    @field_validator("channel", "alias_label", "failure_category", "safe_summary")
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_workbench_text(value, max_length=160)


class ReliabilityRecoveryItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    item_id: str
    label: str
    status: WorkbenchStatus
    severity: WorkbenchSeverity
    summary: str
    href: str | None = None
    confirmation: str | None = None

    @field_validator("label", "summary", "confirmation")
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_workbench_text(value, max_length=180)


class ReliabilityRecoverySummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    breakers: tuple[ReliabilityRecoveryItem, ...] = Field(default_factory=tuple)
    retries: tuple[ReliabilityRecoveryItem, ...] = Field(default_factory=tuple)
    dead_letters: tuple[ReliabilityRecoveryItem, ...] = Field(default_factory=tuple)
    confirmations: tuple[ReliabilityRecoveryItem, ...] = Field(default_factory=tuple)
    partial_reason: str | None = None

    @field_validator("partial_reason")
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_workbench_text(value, max_length=180)


class WorkbenchLogSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    log_id: str
    occurred_at_label: str
    source: str
    severity: WorkbenchSeverity
    status: WorkbenchStatus
    subsystem: str
    tenant_scope: str | None = None
    run_reference: str | None = None
    correlation_reference: str | None = None
    summary: str
    safe_details: dict[str, str] = Field(default_factory=dict)
    links: tuple[WorkbenchLink, ...] = Field(default_factory=tuple)

    @field_validator(
        "occurred_at_label",
        "source",
        "subsystem",
        "tenant_scope",
        "run_reference",
        "correlation_reference",
        "summary",
    )
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_workbench_text(value, max_length=180)

    @field_validator("safe_details")
    @classmethod
    def details_are_safe(cls, value: dict[str, str]) -> dict[str, str]:
        return {
            safe_workbench_text(key, max_length=80): safe_workbench_text(
                detail, max_length=160
            )
            for key, detail in value.items()
        }


class WorkbenchExportSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    export_id: str
    status: WorkbenchExportStatus
    summary: str
    artifact_reference_id: str | None = None
    progress_label: str | None = None
    expires_at: datetime | None = None
    audit_reference_id: str | None = None
    scope_label: str
    redaction_summary: str
    row_count: int = Field(default=0, ge=0)

    @field_validator(
        "summary",
        "artifact_reference_id",
        "progress_label",
        "audit_reference_id",
    )
    @classmethod
    def inherited_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_workbench_text(value, max_length=180)

    @field_validator("artifact_reference_id")
    @classmethod
    def artifact_reference_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if value.startswith(("/", "file:")) or ".." in value:
            raise ValueError("artifact reference must not expose a filesystem path")
        return value

    @field_validator("scope_label", "redaction_summary")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_workbench_text(value, max_length=180)


class WorkbenchExportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scope_type: str = "active"
    range: str = "60m"
    include_run_debug: bool = True
    included_sections: tuple[str, ...] = (
        "summary",
        "logs",
        "run_debug",
        "reliability",
        "exports",
    )


class RunDebugEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workflow_run_id: str
    tenant_scope: ReactAdminScope | None = None
    run_status: WorkbenchStatus
    safe_title: str
    timeline: tuple[TimelineEventSummary, ...] = Field(default_factory=tuple)
    branches: tuple[GraphBranchSummary, ...] = Field(default_factory=tuple)
    gateway_attempts: tuple[GatewayAttemptSummary, ...] = Field(default_factory=tuple)
    tool_calls: tuple[ToolCallSummary, ...] = Field(default_factory=tuple)
    deliveries: tuple[ChannelDeliverySummary, ...] = Field(default_factory=tuple)
    lineage: tuple[WorkbenchLink, ...] = Field(default_factory=tuple)
    replay_links: tuple[WorkbenchLink, ...] = Field(default_factory=tuple)
    bundle_summary: str
    fallback_links: tuple[WorkbenchLink, ...] = Field(default_factory=tuple)
    state: ReactAdminShellState | None = None

    @field_validator("safe_title", "bundle_summary")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_workbench_text(value, max_length=180)


class OperationsWorkbenchEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    page_id: str
    title: str
    description: str
    scope: ReactAdminScope
    generated_at_label: str
    time_range: WorkbenchTimeRange
    summary_cards: tuple[WorkbenchSummaryCard, ...] = Field(default_factory=tuple)
    likely_causes: tuple[LikelyCauseSummary, ...] = Field(default_factory=tuple)
    health_panels: tuple[HealthPressurePanel, ...] = Field(default_factory=tuple)
    run_debug: RunDebugEnvelope | None = None
    reliability: ReliabilityRecoverySummary
    logs: tuple[WorkbenchLogSummary, ...] = Field(default_factory=tuple)
    filters: FilterProfile
    actions: tuple[AdminAction, ...] = Field(default_factory=tuple)
    exports: WorkbenchExportSnapshot
    fallback_links: tuple[WorkbenchLink, ...] = Field(default_factory=tuple)
    evidence: tuple[EvidenceSummary, ...] = Field(default_factory=tuple)
    state: ReactAdminShellState | None = None
    refresh: RefreshHint | None = None

    @field_validator("title", "description", "generated_at_label")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_workbench_text(value, max_length=180)
