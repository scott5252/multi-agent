from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class UsageEventStatus(StrEnum):
    ESTIMATED = "estimated"
    CONFIRMED = "confirmed"
    PARTIAL = "partial"
    UNAVAILABLE = "unavailable"
    MALFORMED = "malformed"


class UsageExportStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    DENIED = "denied"


class UsageScopeType(StrEnum):
    PLATFORM = "platform"
    TENANT = "tenant"


UsageGroupBy = Literal[
    "hour",
    "day",
    "tenant",
    "provider",
    "model",
    "workflow",
    "agent",
    "sub_agent",
    "prompt",
    "execution_mode",
    "principal",
]


class UsageAccessScope(BaseModel):
    scope_type: UsageScopeType
    tenant_id: UUID | None = None
    principal_id: str
    platform_admin: bool = False

    @model_validator(mode="after")
    def validate_tenant_scope(self) -> UsageAccessScope:
        if self.scope_type is UsageScopeType.TENANT and self.tenant_id is None:
            raise ValueError("tenant usage scope requires tenant_id")
        if self.scope_type is UsageScopeType.PLATFORM and not self.platform_admin:
            raise ValueError("platform usage scope requires platform admin")
        return self


class UsageFilters(BaseModel):
    tenant_id: UUID | None = None
    start: datetime | None = None
    end: datetime | None = None
    provider_key: str | None = Field(default=None, max_length=128)
    model_id: str | None = Field(default=None, max_length=128)
    workflow_lineage_id: UUID | None = None
    workflow_version_id: UUID | None = None
    workflow_run_id: UUID | None = None
    workflow_run_step_id: UUID | None = None
    agent_key: str | None = Field(default=None, max_length=128)
    sub_agent_key: str | None = Field(default=None, max_length=128)
    prompt_version_id: UUID | None = None
    execution_mode: str | None = Field(default=None, max_length=64)
    usage_status: UsageEventStatus | None = None
    principal_id: str | None = Field(default=None, max_length=255)
    group_by: UsageGroupBy = "day"

    @model_validator(mode="after")
    def validate_time_range(self) -> UsageFilters:
        if self.start and self.end and self.end <= self.start:
            raise ValueError("usage filter end must be after start")
        return self

    def safe_snapshot(self) -> dict[str, str]:
        data = self.model_dump(mode="json", exclude_none=True)
        return {key: str(value) for key, value in data.items()}


class UsageTotals(BaseModel):
    total_events: int = 0
    total_tokens: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    reasoning_tokens: int = 0
    provider_billable_units: int = 0
    estimated_cost_micros: int = 0
    currency: str = "USD"
    estimated_event_count: int = 0
    confirmed_event_count: int = 0
    unavailable_event_count: int = 0


class UsageRollup(BaseModel):
    label: str
    event_count: int
    total_tokens: int
    estimated_cost_micros: int


class UsageEventView(BaseModel):
    llm_usage_event_id: UUID
    tenant_id: UUID
    principal_id: str | None = None
    provider_key: str
    model_id: str
    workflow_run_id: UUID | None = None
    workflow_run_step_id: UUID | None = None
    workflow_lineage_id: UUID | None = None
    workflow_version_id: UUID | None = None
    agent_key: str | None = None
    sub_agent_key: str | None = None
    prompt_version_id: UUID | None = None
    execution_mode: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cached_tokens: int | None = None
    reasoning_tokens: int | None = None
    total_tokens: int | None = None
    provider_billable_units: int | None = None
    latency_ms: int
    estimated_cost_micros: int | None = None
    currency: str = "USD"
    usage_status: UsageEventStatus
    recorded_at: datetime


class UsageSummary(BaseModel):
    totals: UsageTotals = Field(default_factory=UsageTotals)
    rollups: tuple[UsageRollup, ...] = ()
    events: tuple[UsageEventView, ...] = ()


SENSITIVE_ATTRIBUTION_KEYS = frozenset(
    {
        "prompt",
        "completion",
        "content",
        "message",
        "messages",
        "secret",
        "password",
        "api_key",
        "authorization",
        "credential",
        "memory",
        "payload",
        "transcript",
    }
)


def utc_now() -> datetime:
    return datetime.now(UTC)


def sanitize_safe_attribution(value: object) -> object:
    if isinstance(value, dict):
        sanitized: dict[str, object] = {}
        for key, item in value.items():
            lowered = str(key).lower()
            if any(marker in lowered for marker in SENSITIVE_ATTRIBUTION_KEYS):
                sanitized[str(key)] = "[redacted]"
            else:
                sanitized[str(key)] = sanitize_safe_attribution(item)
        return sanitized
    if isinstance(value, list | tuple):
        return [sanitize_safe_attribution(item) for item in value[:20]]
    if isinstance(value, str):
        lowered = value.lower()
        if any(marker in lowered for marker in SENSITIVE_ATTRIBUTION_KEYS):
            return "[redacted]"
        return value[:500]
    if value is None or isinstance(value, bool | int | float):
        return value
    return str(value)[:500]
