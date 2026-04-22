from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.db.models.queue import JobLease, JobStatus, QueueJob
from multi_agent_platform.runtime.queue.models import (
    QueueEnqueueRequest,
    QueueLeaseResult,
)


class QueueRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def enqueue(self, request: QueueEnqueueRequest) -> QueueJob:
        job = QueueJob(
            tenant_id=request.tenant_id,
            scope_type=request.scope_type,
            job_kind=request.job_kind,
            payload_json=request.payload_json,
            priority=request.priority,
            idempotency_key=request.idempotency_key,
            trace_id=request.trace_id,
            available_at=request.available_at,
        )
        self.session.add(job)
        await self.session.flush()
        return job

    async def lease_next(
        self, worker_id: str, lease_seconds: int
    ) -> QueueLeaseResult | None:
        now = datetime.now(UTC)
        stmt = (
            select(QueueJob)
            .where(QueueJob.status == JobStatus.PENDING, QueueJob.available_at <= now)
            .order_by(QueueJob.priority.asc(), QueueJob.available_at.asc())
            .limit(1)
        )
        job = (await self.session.execute(stmt)).scalar_one_or_none()
        if job is None:
            return None
        job.status = JobStatus.LEASED
        job.attempt_count += 1
        lease = JobLease(
            job_id=job.job_id,
            worker_id=worker_id,
            lease_expires_at=now + timedelta(seconds=lease_seconds),
        )
        self.session.add(lease)
        await self.session.flush()
        return QueueLeaseResult(
            job_id=job.job_id, worker_id=worker_id, trace_id=job.trace_id
        )

    async def complete(self, job_id: object) -> None:
        job = await self.session.get(QueueJob, job_id)
        if job is None:
            raise KeyError(str(job_id))
        job.status = JobStatus.COMPLETED
        await self.session.flush()

    async def get(self, job_id: object) -> QueueJob | None:
        return await self.session.get(QueueJob, job_id)
