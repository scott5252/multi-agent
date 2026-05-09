from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.config.service import ModelSkillConfigService
from multi_agent_platform.config.settings import Settings
from multi_agent_platform.db.models.runtime_orchestration import (
    RuntimeTimelineEventRecord,
)
from multi_agent_platform.db.repositories.runtime_orchestration import (
    RuntimeOrchestrationRepository,
)
from multi_agent_platform.model_providers.gateway import ModelGateway
from multi_agent_platform.reliability.models import RecoveryOutcome
from multi_agent_platform.runtime.orchestration.graph_execution import (
    GraphExecutionService,
    GraphExecutionStatus,
)
from multi_agent_platform.runtime.orchestration.model_backed_roles import (
    ModelSkillConfigRolePinResolver,
    build_role_node_executor,
)
from multi_agent_platform.storage.base import StorageProvider


@dataclass(slots=True, frozen=True)
class OrchestrationWorkerResult:
    claimed: bool
    workflow_run_id: str | None = None
    recovery_outcome: RecoveryOutcome | None = None
    graph_status: GraphExecutionStatus | None = None
    executed_node_count: int = 0
    wave_count: int = 0


class OrchestrationWorker:
    def __init__(
        self,
        *,
        session: AsyncSession,
        settings: Settings,
        worker_id: str,
        model_gateway_factory: Callable[[AsyncSession], ModelGateway] | None = None,
        model_skill_service_factory: Callable[[AsyncSession], ModelSkillConfigService]
        | None = None,
        storage_provider: StorageProvider | None = None,
    ) -> None:
        self.repository = RuntimeOrchestrationRepository(session)
        self.session = session
        self.settings = settings
        self.worker_id = worker_id
        self.model_gateway_factory = model_gateway_factory
        self.model_skill_service_factory = model_skill_service_factory
        self.storage_provider = storage_provider

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
        role_executor = build_role_node_executor(
            model_gateway=self.model_gateway_factory(self.session)
            if self.model_gateway_factory is not None
            else None,
            pin_resolver=ModelSkillConfigRolePinResolver(
                self.model_skill_service_factory(self.session)
            )
            if self.model_skill_service_factory is not None
            else None,
            storage_provider=self.storage_provider,
        )
        graph_result = await GraphExecutionService(
            self.repository,
            role_executor=role_executor,
        ).execute_claimed_run(
            workflow_run_id=lease.workflow_run_id,
            worker_id=self.worker_id,
        )
        return OrchestrationWorkerResult(
            claimed=True,
            workflow_run_id=str(lease.workflow_run_id),
            recovery_outcome=RecoveryOutcome.RESUMED,
            graph_status=graph_result.status,
            executed_node_count=len(graph_result.executed_node_keys),
            wave_count=graph_result.wave_count,
        )
