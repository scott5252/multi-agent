from __future__ import annotations

from pydantic import BaseModel, Field

from multi_agent_platform.operations.models import (
    OperationalLogEvent,
    OperationsDashboardSnapshot,
    OperationsExportResult,
    OperationsLogFilters,
)


class OperationsDashboardResponse(OperationsDashboardSnapshot):
    pass


class OperationsLogResponse(BaseModel):
    items: tuple[OperationalLogEvent, ...]
    filters: dict[str, str] = Field(default_factory=dict)


class OperationsExportCreateRequest(BaseModel):
    filters: OperationsLogFilters = Field(default_factory=OperationsLogFilters)


class OperationsExportResponse(OperationsExportResult):
    pass
