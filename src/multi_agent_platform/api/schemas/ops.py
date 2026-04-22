from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from multi_agent_platform.runtime.health.models import DependencyHealthCheck


class LiveResponse(BaseModel):
    service: str
    status: str = "live"
    version: str
    checked_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class ReadyResponse(BaseModel):
    service: str
    status: str
    checks: list[DependencyHealthCheck]
    checked_at: str


class VersionResponse(BaseModel):
    service: str
    version: str
    commit_sha: str
    build_time: str
    python_version: str


class DependencyStatusResponse(BaseModel):
    service: str
    status: str
    dependencies: list[DependencyHealthCheck]
    checked_at: str
