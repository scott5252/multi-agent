from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from multi_agent_platform.usage.models import (
    UsageEventStatus,
    UsageEventView,
    UsageFilters,
    UsageRollup,
    UsageTotals,
)


class UsageFilterParams(BaseModel):
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
    group_by: str = "day"

    def to_filters(self) -> UsageFilters:
        return UsageFilters.model_validate(self.model_dump())


class UsageSummaryResponse(BaseModel):
    total_events: int
    total_tokens: int
    input_tokens: int
    output_tokens: int
    cached_tokens: int
    reasoning_tokens: int
    provider_billable_units: int
    estimated_cost_micros: int
    currency: str
    estimated_event_count: int
    confirmed_event_count: int
    unavailable_event_count: int
    rollups: tuple[UsageRollup, ...]

    @classmethod
    def from_parts(
        cls,
        *,
        totals: UsageTotals,
        rollups: tuple[UsageRollup, ...],
    ) -> UsageSummaryResponse:
        return cls(**totals.model_dump(), rollups=rollups)


class UsageEventsResponse(BaseModel):
    events: tuple[UsageEventView, ...]


class UsageExportCreateRequest(BaseModel):
    tenant_id: UUID | None = None
    filters: dict[str, object] = Field(default_factory=dict)


class UsageExportResponse(BaseModel):
    usage_export_request_id: UUID
    status: str
    row_count: int
    artifact_uri: str | None = None
    artifact_sha256: str | None = None
    artifact_size_bytes: int | None = None
    denial_reason: str | None = None
    failure_reason: str | None = None
    created_at: datetime
    completed_at: datetime | None = None
