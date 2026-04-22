from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class DependencyStatus(StrEnum):
    READY = "ready"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


class ReadinessStatus(StrEnum):
    READY = "ready"
    NOT_READY = "not_ready"


class DependencyHealthCheck(BaseModel):
    name: str
    required: bool
    status: DependencyStatus
    detail: str | None = None
    checked_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class ReadinessReport(BaseModel):
    service: str
    status: ReadinessStatus
    checks: list[DependencyHealthCheck]
    checked_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class DependencyStatusReport(BaseModel):
    service: str
    status: str
    dependencies: list[DependencyHealthCheck]
    checked_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
