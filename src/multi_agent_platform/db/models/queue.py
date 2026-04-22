from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from multi_agent_platform.db.base import Base, TimestampMixin


class JobStatus(StrEnum):
    PENDING = "pending"
    LEASED = "leased"
    COMPLETED = "completed"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"


class JobKind(StrEnum):
    BOOTSTRAP_TASK = "bootstrap_task"
    MIGRATION_TASK = "migration_task"
    RUNTIME_TASK = "runtime_task"


class QueueJob(Base, TimestampMixin):
    __tablename__ = "queue_jobs"

    job_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    scope_type: Mapped[str] = mapped_column(String(32))
    job_kind: Mapped[JobKind] = mapped_column(Enum(JobKind, native_enum=False))
    payload_json: Mapped[dict[str, str]] = mapped_column(JSON, default=dict)
    artifact_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("artifacts.artifact_id"), nullable=True
    )
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, native_enum=False),
        default=JobStatus.PENDING,
    )
    priority: Mapped[int] = mapped_column(Integer, default=100)
    available_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3)
    idempotency_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    trace_id: Mapped[str] = mapped_column(String(64))


class JobLease(Base):
    __tablename__ = "job_leases"

    lease_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    job_id: Mapped[UUID] = mapped_column(
        ForeignKey("queue_jobs.job_id", ondelete="CASCADE")
    )
    worker_id: Mapped[str] = mapped_column(String(128))
    lease_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
