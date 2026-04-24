from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.db.models.runtime_orchestration import (
    RuntimeExecutionBundleRecord,
    RuntimeRetentionPolicyRecord,
    RuntimeRunStatus,
    RuntimeTimelineEventRecord,
    RuntimeWorkerLeaseStatus,
    WorkerLeaseRecord,
    WorkflowRunRecord,
)


class RuntimeOrchestrationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_run(
        self,
        *,
        run: WorkflowRunRecord,
        bundle: RuntimeExecutionBundleRecord,
    ) -> WorkflowRunRecord:
        self.session.add(bundle)
        await self.session.flush()
        run.run_bundle_id = bundle.run_bundle_id
        self.session.add(run)
        await self.session.flush()
        return run

    async def get_run(
        self, *, workflow_run_id: UUID, tenant_id: UUID | None
    ) -> WorkflowRunRecord | None:
        stmt = select(WorkflowRunRecord).where(
            WorkflowRunRecord.workflow_run_id == workflow_run_id,
            WorkflowRunRecord.tenant_id == tenant_id,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def list_timeline(
        self, *, workflow_run_id: UUID, tenant_id: UUID | None, limit: int = 100
    ) -> list[RuntimeTimelineEventRecord]:
        stmt = (
            select(RuntimeTimelineEventRecord)
            .where(
                RuntimeTimelineEventRecord.workflow_run_id == workflow_run_id,
                RuntimeTimelineEventRecord.tenant_id == tenant_id,
            )
            .order_by(RuntimeTimelineEventRecord.created_at.desc())
            .limit(limit)
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def create_timeline_event(
        self, event: RuntimeTimelineEventRecord
    ) -> RuntimeTimelineEventRecord:
        self.session.add(event)
        await self.session.flush()
        return event

    async def claim_next_run(
        self, *, worker_id: str, lease_seconds: int = 120
    ) -> WorkerLeaseRecord | None:
        stmt = (
            select(WorkflowRunRecord)
            .where(WorkflowRunRecord.status == RuntimeRunStatus.RUNNABLE)
            .order_by(WorkflowRunRecord.created_at.asc())
            .limit(1)
        )
        run = (await self.session.execute(stmt)).scalar_one_or_none()
        if run is None:
            return None
        run.status = RuntimeRunStatus.RUNNING
        now = datetime.now(UTC)
        lease = WorkerLeaseRecord(
            tenant_id=run.tenant_id,
            workflow_run_id=run.workflow_run_id,
            worker_id=worker_id,
            lease_status=RuntimeWorkerLeaseStatus.ACTIVE,
            claimed_at=now,
            expires_at=now + timedelta(seconds=lease_seconds),
        )
        self.session.add(lease)
        await self.session.flush()
        return lease

    async def get_or_create_retention_policy(
        self, tenant_id: UUID | None
    ) -> RuntimeRetentionPolicyRecord:
        stmt = select(RuntimeRetentionPolicyRecord).where(
            RuntimeRetentionPolicyRecord.tenant_id == tenant_id
        )
        policy = (await self.session.execute(stmt)).scalar_one_or_none()
        if policy is not None:
            return policy
        policy = RuntimeRetentionPolicyRecord(tenant_id=tenant_id)
        self.session.add(policy)
        await self.session.flush()
        return policy
