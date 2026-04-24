from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable

from multi_agent_platform.bootstrap.worker import WorkerBootstrap
from multi_agent_platform.db.session import session_scope
from multi_agent_platform.runtime.queue.service import QueueService
from multi_agent_platform.workers.orchestration import OrchestrationWorker

JobHandler = Callable[[object], Awaitable[None]]


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
