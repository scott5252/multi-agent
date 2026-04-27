from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.db.repositories.reliability import ReliabilityRepository
from multi_agent_platform.reliability.admission import decide_admission
from multi_agent_platform.reliability.models import (
    AdmissionDecision,
    CapacitySnapshot,
    ReliabilityPolicy,
    ReliabilityPolicySettings,
    ReliabilityScopeType,
)


class ReliabilityService:
    def __init__(self, session: AsyncSession) -> None:
        self.repository = ReliabilityRepository(session)

    async def dashboard(self, *, tenant_id: UUID | None = None) -> dict[str, object]:
        snapshot = await self.repository.latest_capacity_snapshot(tenant_id=tenant_id)
        return {
            "tenant_id": str(tenant_id) if tenant_id else None,
            "status": "available",
            "capacity": snapshot,
        }

    async def admit(
        self,
        *,
        tenant_id: UUID,
        snapshot: CapacitySnapshot,
        submitted_count: int,
        active_count: int,
        trace_id: str | None = None,
    ) -> AdmissionDecision:
        policy = ReliabilityPolicy(
            tenant_id=tenant_id,
            scope_type=ReliabilityScopeType.TENANT,
            scope_key=None,
            settings=ReliabilityPolicySettings(),
        )
        decision = decide_admission(
            tenant_id=tenant_id,
            policy=policy,
            snapshot=snapshot,
            submitted_count=submitted_count,
            active_count=active_count,
            trace_id=trace_id,
        )
        await self.repository.insert_admission_decision(decision)
        return decision
