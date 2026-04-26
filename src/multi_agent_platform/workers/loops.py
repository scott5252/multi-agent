from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from multi_agent_platform.bootstrap.worker import WorkerBootstrap
from multi_agent_platform.db.session import session_scope
from multi_agent_platform.runtime.queue.service import QueueService
from multi_agent_platform.workers.orchestration import OrchestrationWorker

JobHandler = Callable[[object], Awaitable[None]]


@dataclass(slots=True)
class ChannelDeliveryBudget:
    tenant_id: str | None
    delivery_kind: str
    limit: int
    in_flight: int = 0

    @property
    def remaining(self) -> int:
        return max(self.limit - self.in_flight, 0)

    def try_claim(self) -> bool:
        if self.remaining <= 0:
            return False
        self.in_flight += 1
        return True

    def release(self) -> None:
        self.in_flight = max(self.in_flight - 1, 0)


class ChannelDeliveryLeaseManager:
    def __init__(self, default_limit: int = 4) -> None:
        self.default_limit = default_limit
        self._budgets: dict[tuple[str | None, str], ChannelDeliveryBudget] = {}

    def budget_for(
        self, *, tenant_id: str | None, delivery_kind: str
    ) -> ChannelDeliveryBudget:
        key = (tenant_id, delivery_kind)
        if key not in self._budgets:
            self._budgets[key] = ChannelDeliveryBudget(
                tenant_id=tenant_id,
                delivery_kind=delivery_kind,
                limit=self.default_limit,
            )
        return self._budgets[key]


async def run_channel_delivery_once(
    manager: ChannelDeliveryLeaseManager,
    *,
    tenant_id: str | None,
    delivery_kind: str,
) -> bool:
    budget = manager.budget_for(tenant_id=tenant_id, delivery_kind=delivery_kind)
    if not budget.try_claim():
        return False
    budget.release()
    return True


async def poll_once(
    bootstrap: WorkerBootstrap, handler: JobHandler | None = None
) -> object | None:
    async with session_scope(bootstrap.container.session_factory) as session:
        service = QueueService(session)
        lease = await service.lease_next(
            worker_id=bootstrap.worker_id,
            lease_seconds=bootstrap.container.settings.worker_lease_seconds,
        )
        if lease is None:
            return None
        if handler is not None:
            await handler(lease)
        await service.repository.complete(lease.job_id)
        return lease


async def poll_orchestration_once(bootstrap: WorkerBootstrap) -> object | None:
    async with session_scope(bootstrap.container.session_factory) as session:
        worker = OrchestrationWorker(
            session=session,
            settings=bootstrap.container.settings,
            worker_id=bootstrap.worker_id,
        )
        result = await worker.poll_once()
        return result if result.claimed else None


async def run_polling_loop(
    bootstrap: WorkerBootstrap,
    iterations: int | None = None,
    handler: JobHandler | None = None,
) -> None:
    completed = 0
    while iterations is None or completed < iterations:
        await poll_once(bootstrap, handler=handler)
        completed += 1
        await asyncio.sleep(bootstrap.container.settings.worker_poll_interval_seconds)


async def run_orchestration_polling_loop(
    bootstrap: WorkerBootstrap,
    iterations: int | None = None,
) -> None:
    completed = 0
    while iterations is None or completed < iterations:
        await poll_orchestration_once(bootstrap)
        completed += 1
        await asyncio.sleep(
            bootstrap.container.settings.runtime_worker_poll_interval_seconds
        )
