from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from multi_agent_platform.api.schemas.admin_patterns import safe_text
from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminScope,
    ReactAdminScopeOption,
    ReactAdminShellState,
)

USAGE_UNSAFE_MARKERS = (
    "qa035-secret-value",
    "raw prompt",
    "raw completion",
    "memory content",
    "authorization header",
    "bearer ",
    "provider token",
    "credential value",
    "credential reference",
    "raw tool payload",
    "private message",
    "unauthorized tenant label",
    "/users/",
    "/Users/",
)


def safe_usage_text(value: str, *, max_length: int = 320) -> str:
    normalized = safe_text(value, max_length=max_length)
    lowered = normalized.lower()
    if any(marker.lower() in lowered for marker in USAGE_UNSAFE_MARKERS):
        raise ValueError("unsafe usage text cannot be rendered")
    return normalized


def _validate_strings(value: object) -> None:
    if isinstance(value, str):
        safe_usage_text(value)
        return
    if isinstance(value, dict):
        for item in value.values():
            _validate_strings(item)
        return
    if isinstance(value, list | tuple):
        for item in value:
            _validate_strings(item)


class SafeUsageModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def safe_string_payload(self) -> SafeUsageModel:
        _validate_strings(self.model_dump(mode="python"))
        return self


class UsageReactConfidenceStatus(StrEnum):
    CONFIRMED = "confirmed"
    ESTIMATED = "estimated"
    PARTIAL = "partial"
    UNAVAILABLE = "unavailable"


class UsageReactTone(StrEnum):
    NEUTRAL = "neutral"
    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"


class UsageReactGroupBy(StrEnum):
    DAY = "day"
    TENANT = "tenant"
    PROVIDER = "provider"
    MODEL = "model"
    WORKFLOW = "workflow"
    AGENT = "agent"
    SUB_AGENT = "sub_agent"
    PROMPT = "prompt"
    EXECUTION_MODE = "execution_mode"
    PRINCIPAL = "principal"
    GRAPH_NODE = "graph_node"
    GATEWAY_OPERATION = "gateway_operation"
    PHYSICAL_ATTEMPT = "physical_attempt"
    GOVERNED_TOOL = "governed_tool"


class UsageReactProblemReason(StrEnum):
    DENIED = "denied"
    EMPTY = "empty"
    PARTIAL = "partial"
    UNAVAILABLE = "unavailable"
    STALE_PRICING = "stale_pricing"
    EXPORT_PENDING = "export_pending"
    AUDIT_UNAVAILABLE = "audit_unavailable"
    UNSUPPORTED_FILTER = "unsupported_filter"
    INVALID_RANGE = "invalid_range"


class UsageReactExportStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    DENIED = "denied"


class UsageReactRange(SafeUsageModel):
    label: str
    start: datetime
    end: datetime

    @model_validator(mode="after")
    def end_after_start(self) -> UsageReactRange:
        if self.end <= self.start:
            raise ValueError("usage range end must be after start")
        return self


class UsageReactFilterOption(SafeUsageModel):
    value: str
    label: str
    selected: bool = False
    disabled: bool = False
    disabled_reason: str | None = None


class UsageReactFilterMetadata(SafeUsageModel):
    selected_range: UsageReactRange
    range_options: tuple[UsageReactFilterOption, ...] = Field(default_factory=tuple)
    selected_group_by: UsageReactGroupBy = UsageReactGroupBy.DAY
    group_by_options: tuple[UsageReactFilterOption, ...] = Field(default_factory=tuple)
    tenant_options: tuple[UsageReactFilterOption, ...] = Field(default_factory=tuple)
    provider_options: tuple[UsageReactFilterOption, ...] = Field(default_factory=tuple)
    model_options: tuple[UsageReactFilterOption, ...] = Field(default_factory=tuple)
    workflow_options: tuple[UsageReactFilterOption, ...] = Field(default_factory=tuple)
    agent_options: tuple[UsageReactFilterOption, ...] = Field(default_factory=tuple)
    prompt_options: tuple[UsageReactFilterOption, ...] = Field(default_factory=tuple)
    confidence_options: tuple[UsageReactFilterOption, ...] = Field(
        default_factory=tuple
    )
    availability_options: tuple[UsageReactFilterOption, ...] = Field(
        default_factory=tuple
    )
    disabled_reasons: dict[str, str] = Field(default_factory=dict)


class UsageReactSummaryCard(SafeUsageModel):
    card_id: str
    label: str
    value: str
    unit: str
    status: UsageReactConfidenceStatus
    tone: UsageReactTone = UsageReactTone.NEUTRAL
    comparison: str | None = None
    detail: str
    audit_reference: str | None = None


class UsageReactTrendPoint(SafeUsageModel):
    bucket_start: datetime
    bucket_end: datetime
    label: str
    confirmed_tokens: int = Field(ge=0)
    estimated_tokens: int = Field(ge=0)
    unavailable_events: int = Field(ge=0)
    estimated_cost_display: str
    estimated_cost_micros: int = Field(default=0, ge=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    average_latency_ms: int = Field(ge=0)
    event_count: int = Field(ge=0)
    confidence_status: UsageReactConfidenceStatus


class UsageReactRollupRow(SafeUsageModel):
    row_id: str
    group_by: UsageReactGroupBy
    safe_label: str
    safe_summary: str
    event_count: int = Field(ge=0)
    total_tokens: int = Field(ge=0)
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    estimated_cost_display: str
    estimated_cost_micros: int = Field(default=0, ge=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    average_latency_ms: int = Field(ge=0)
    unavailable_event_count: int = Field(ge=0)
    confidence_status: UsageReactConfidenceStatus
    attempt_summary: str | None = None
    tool_summary: str | None = None
    drilldown_href: str


class UsageReactRollupSection(SafeUsageModel):
    group_by: UsageReactGroupBy
    rows: tuple[UsageReactRollupRow, ...] = Field(default_factory=tuple, max_length=25)
    limit: int = Field(default=25, ge=1, le=25)
    total_rows: int = Field(ge=0)


class UsageReactEventRow(SafeUsageModel):
    event_id: UUID
    recorded_at: datetime
    tenant_label: str
    provider_label: str
    model_label: str
    workflow_label: str | None = None
    agent_label: str | None = None
    prompt_label: str | None = None
    graph_node_label: str | None = None
    gateway_operation_label: str | None = None
    physical_attempt_label: str | None = None
    tool_label: str | None = None
    total_tokens: int = Field(ge=0)
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    estimated_cost_display: str
    latency_ms: int = Field(ge=0)
    usage_status: UsageReactConfidenceStatus
    cost_status: UsageReactConfidenceStatus
    safe_attribution_summary: str
    audit_reference: str | None = None
    trace_reference: str | None = None


class UsageReactEventDrilldown(SafeUsageModel):
    rows: tuple[UsageReactEventRow, ...] = Field(default_factory=tuple, max_length=100)
    limit: int = Field(default=100, ge=1, le=100)
    total_rows: int = Field(ge=0)
    truncated: bool = False


class UsageReactExportCreateRequest(SafeUsageModel):
    filters: dict[str, str] = Field(default_factory=dict)
    requested_group_by: UsageReactGroupBy | None = None
    idempotency_key: str | None = Field(default=None, max_length=128)


class UsageReactExportSummary(SafeUsageModel):
    usage_export_request_id: UUID
    status: UsageReactExportStatus
    scope_label: str
    requested_by_label: str
    filter_snapshot: dict[str, str] = Field(default_factory=dict)
    row_count: int = Field(ge=0)
    artifact_reference: str | None = None
    artifact_size_label: str | None = None
    checksum_prefix: str | None = None
    created_at: datetime
    completed_at: datetime | None = None
    expires_at: datetime | None = None
    audit_reference: str
    denial_reason: str | None = None
    failure_reason: str | None = None
    next_step: str


class UsageReactProblem(SafeUsageModel):
    reason: UsageReactProblemReason
    title: str
    detail: str
    next_action: str
    audit_reference: str | None = None


class UsageReactDashboardQuery(SafeUsageModel):
    tenant_id: str | None = None
    start: datetime | None = None
    end: datetime | None = None
    group_by: UsageReactGroupBy = UsageReactGroupBy.DAY
    provider_key: str | None = Field(default=None, max_length=128)
    model_id: str | None = Field(default=None, max_length=128)
    usage_status: UsageReactConfidenceStatus | None = None

    @field_validator("tenant_id", "provider_key", "model_id")
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_usage_text(value, max_length=160)

    @model_validator(mode="after")
    def validate_range(self) -> UsageReactDashboardQuery:
        if self.start and self.end and self.end <= self.start:
            raise ValueError("usage filter end must be after start")
        return self


class UsageReactEventQuery(UsageReactDashboardQuery):
    rollup_key: str | None = Field(default=None, max_length=255)


class UsageReactDashboard(SafeUsageModel):
    page_id: str
    title: str
    description: str
    scope: ReactAdminScope
    allowed_scope_options: tuple[ReactAdminScopeOption, ...] = Field(
        default_factory=tuple
    )
    filters: UsageReactFilterMetadata
    summary_cards: tuple[UsageReactSummaryCard, ...] = Field(
        default_factory=tuple,
        max_length=8,
    )
    trend: tuple[UsageReactTrendPoint, ...] = Field(
        default_factory=tuple,
        max_length=31,
    )
    rollup: UsageReactRollupSection
    drilldown: UsageReactEventDrilldown
    exports: tuple[UsageReactExportSummary, ...] = Field(default_factory=tuple)
    states: tuple[UsageReactProblem, ...] = Field(default_factory=tuple)
    common_states: tuple[ReactAdminShellState, ...] = Field(default_factory=tuple)
    updated_at: datetime
