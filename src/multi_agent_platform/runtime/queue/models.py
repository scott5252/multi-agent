from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from multi_agent_platform.db.models.queue import JobKind


class QueueEnqueueRequest(BaseModel):
    tenant_id: UUID | None = None
    scope_type: str
    job_kind: JobKind
    payload_json: dict[str, str] = Field(default_factory=dict)
    priority: int = 100
    idempotency_key: str | None = None
    trace_id: str = Field(default_factory=lambda: uuid4().hex)
    available_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class QueueLeaseResult(BaseModel):
    job_id: UUID
    worker_id: str
    trace_id: str
