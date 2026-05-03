from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class OperationsRole(StrEnum):
    PLATFORM_ADMIN = "platform_admin"
    AUDITOR = "auditor"


class OperationsAuthorizationError(PermissionError):
    """Raised when a principal is not allowed to use platform operations data."""


class OperationsAccessScope(BaseModel):
    principal_id: str
    role: OperationsRole
    can_export: bool = False
    trace_id: str | None = None


class OperationsLogFilters(BaseModel):
    trace_id: str | None = Field(default=None, max_length=128)
    tenant_id: UUID | None = None
    run_id: UUID | None = None
    component: str | None = Field(default=None, max_length=64)
    severity: str | None = Field(default=None, max_length=64)
    status: str | None = Field(default=None, max_length=64)
    dependency: str | None = Field(default=None, max_length=128)
    start: datetime | None = None
    end: datetime | None = None
    limit: int = Field(default=100, ge=1, le=500)

    @model_validator(mode="after")
    def validate_time_range(self) -> OperationsLogFilters:
        if self.start is not None and self.end is not None and self.end <= self.start:
            raise ValueError("operations log filter end must be after start")
        return self

    def safe_snapshot(self) -> dict[str, str]:
        data = self.model_dump(mode="json", exclude_none=True)
        return {key: str(value) for key, value in data.items()}

    def candidate_limit(self) -> int:
        return min(max(self.limit * 5, self.limit), 2_000)


class OperationsLink(BaseModel):
    label: str
    href: str


class OperationsStatusCard(BaseModel):
    label: str
    value: str
    status: str
    summary: str
    href: str | None = None


class OperationsDependencyView(BaseModel):
    name: str
    required: bool
    status: str
    detail: str | None = None
    checked_at: str | None = None


class OperationsCapacitySummary(BaseModel):
    runnable_depth: int = 0
    delayed_depth: int = 0
    active_leases: int = 0
    retry_backlog: int = 0
    compensation_backlog: int = 0
    dead_letter_count: int = 0
    db_pool_wait_p95_ms: int = 0
    db_pool_in_use: int = 0
    db_pool_available: int = 0
    artifact_inflight: int = 0
    artifact_wait_p95_ms: int = 0
    open_breaker_count: int = 0
    fairness_debt_total: float = 0.0
    recorded_at: datetime | None = None


class OperationsProviderSummary(BaseModel):
    provider_connection_id: UUID
    display_name: str
    provider_type: str
    active: bool
    health_state: str
    model_count: int
    last_test_outcome: str | None = None
    href: str


class OperationsUsageSummary(BaseModel):
    total_events: int = 0
    total_tokens: int = 0
    estimated_cost_micros: int = 0
    model_latency_ms: int = 0
    token_throughput: int = 0
    usage_status: str = "available"


class OperationalLogEvent(BaseModel):
    event_id: str
    source: str
    occurred_at: datetime
    tenant_id: UUID | None = None
    trace_id: str | None = None
    run_id: UUID | None = None
    component: str
    severity: str
    status: str
    dependency: str | None = None
    summary: str
    details: dict[str, str] = Field(default_factory=dict)
    links: tuple[OperationsLink, ...] = ()
    latency_ms: int | None = None


class OperationsDashboardSnapshot(BaseModel):
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    health_status: str
    status_cards: tuple[OperationsStatusCard, ...]
    dependencies: tuple[OperationsDependencyView, ...]
    capacity: OperationsCapacitySummary
    providers: tuple[OperationsProviderSummary, ...] = ()
    usage: OperationsUsageSummary = Field(default_factory=OperationsUsageSummary)
    logs: tuple[OperationalLogEvent, ...] = ()
    filters: OperationsLogFilters = Field(default_factory=OperationsLogFilters)
    redaction_notice: str

    @property
    def has_logs(self) -> bool:
        return bool(self.logs)


class OperationsExportResult(BaseModel):
    export_id: UUID
    artifact_uri: str
    artifact_sha256: str
    artifact_size_bytes: int
    row_count: int
    filters: dict[str, str]
    requested_by: str
    audit_event_id: UUID | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
