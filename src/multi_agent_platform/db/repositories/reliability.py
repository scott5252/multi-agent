from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.db.models.reliability import (
    AdmissionDecisionRecord,
    CapacitySnapshotRecord,
    CircuitBreakerRecord,
    DeadLetterRecordModel,
    ReliabilityDecisionRecord,
    ReliabilityPolicyRecord,
    ReliabilityPolicyStatusRecord,
    RetryScheduleRecord,
    TenantQuotaCounterRecord,
)
from multi_agent_platform.reliability.models import AdmissionDecision


class ReliabilityRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def active_policy_head(
        self, *, tenant_id: UUID | None, scope_type: str, scope_key: str | None
    ) -> ReliabilityPolicyRecord | None:
        stmt = (
            select(ReliabilityPolicyRecord)
            .where(
                ReliabilityPolicyRecord.tenant_id == tenant_id,
                ReliabilityPolicyRecord.scope_type == scope_type,
                ReliabilityPolicyRecord.scope_key == scope_key,
                ReliabilityPolicyRecord.status == ReliabilityPolicyStatusRecord.ACTIVE,
            )
            .order_by(ReliabilityPolicyRecord.policy_version.desc())
            .limit(1)
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def insert_admission_decision(
        self, decision: AdmissionDecision
    ) -> AdmissionDecisionRecord:
        record = AdmissionDecisionRecord(
            admission_decision_id=decision.admission_decision_id,
            tenant_id=decision.tenant_id,
            workflow_run_id=decision.workflow_run_id,
            queue_job_id=decision.queue_job_id,
            policy_id=decision.policy_id,
            policy_version=decision.policy_version,
            decision=ReliabilityDecisionRecord(decision.decision.value),
            reason_code=decision.reason_code,
            available_at=decision.available_at,
            capacity_snapshot_id=decision.capacity_snapshot_id,
            trace_id=decision.trace_id,
            created_at=decision.created_at,
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def update_quota_counter(
        self,
        *,
        tenant_id: UUID,
        resource_kind: str,
        window_start: datetime,
        amount: int,
    ) -> TenantQuotaCounterRecord | None:
        stmt = select(TenantQuotaCounterRecord).where(
            TenantQuotaCounterRecord.tenant_id == tenant_id,
            TenantQuotaCounterRecord.resource_kind == resource_kind,
            TenantQuotaCounterRecord.window_start == window_start,
        )
        record = (await self.session.execute(stmt)).scalar_one_or_none()
        if record is None:
            return None
        record.used_value = max(record.used_value + amount, 0)
        await self.session.flush()
        return record

    async def latest_capacity_snapshot(
        self, *, tenant_id: UUID | None
    ) -> CapacitySnapshotRecord | None:
        stmt = (
            select(CapacitySnapshotRecord)
            .where(CapacitySnapshotRecord.tenant_id == tenant_id)
            .order_by(CapacitySnapshotRecord.created_at.desc())
            .limit(1)
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def breaker_head(
        self, *, tenant_id: UUID | None, scope_type: str, scope_key: str
    ) -> CircuitBreakerRecord | None:
        stmt = select(CircuitBreakerRecord).where(
            CircuitBreakerRecord.tenant_id == tenant_id,
            CircuitBreakerRecord.scope_type == scope_type,
            CircuitBreakerRecord.scope_key == scope_key,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def list_retry_schedules(
        self, *, tenant_id: UUID | None, limit: int = 100
    ) -> list[RetryScheduleRecord]:
        stmt = (
            select(RetryScheduleRecord)
            .where(RetryScheduleRecord.tenant_id == tenant_id)
            .order_by(RetryScheduleRecord.updated_at.desc())
            .limit(limit)
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def list_dead_letters(
        self, *, tenant_id: UUID | None, limit: int = 100
    ) -> list[DeadLetterRecordModel]:
        stmt = (
            select(DeadLetterRecordModel)
            .where(DeadLetterRecordModel.tenant_id == tenant_id)
            .order_by(DeadLetterRecordModel.updated_at.desc())
            .limit(limit)
        )
        return list((await self.session.execute(stmt)).scalars().all())
