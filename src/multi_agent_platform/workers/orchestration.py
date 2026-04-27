from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.config.settings import Settings
from multi_agent_platform.db.models.runtime_orchestration import (
    RuntimeTimelineEventRecord,
)
from multi_agent_platform.db.repositories.runtime_orchestration import (
    RuntimeOrchestrationRepository,
)
from multi_agent_platform.reliability.models import RecoveryOutcome


@dataclass(slots=True, frozen=True)
class OrchestrationWorkerResult:
    claimed: bool
    workflow_run_id: str | None = None
    recovery_outcome: RecoveryOutcome | None = None


class OrchestrationWorker:
    def __init__(
        self,
        *,
        session: AsyncSession,
        settings: Settings,
        worker_id: str,
    ) -> None:
        self.repository = RuntimeOrchestrationRepository(session)
        self.settings = settings
        self.worker_id = worker_id

    async def poll_once(self) -> OrchestrationWorkerResult:
        lease = await self.repository.claim_next_run(
            worker_id=self.worker_id,
            lease_seconds=self.settings.runtime_worker_lease_seconds,
        )
        if lease is None:
            return OrchestrationWorkerResult(claimed=False)
        await self.repository.create_timeline_event(
            RuntimeTimelineEventRecord(
                tenant_id=lease.tenant_id,
                workflow_run_id=lease.workflow_run_id,
                event_type="claim",
                severity="info",
                payload={"worker_id": self.worker_id},
                trace_id=self.worker_id,
            )
        )
        return OrchestrationWorkerResult(
            claimed=True,
            workflow_run_id=str(lease.workflow_run_id),
            recovery_outcome=RecoveryOutcome.RESUMED,
        )
