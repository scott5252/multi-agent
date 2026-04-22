from __future__ import annotations

from multi_agent_platform.bootstrap.container import build_container
from multi_agent_platform.bootstrap.worker import build_worker_bootstrap
from multi_agent_platform.db.models.queue import JobKind
from multi_agent_platform.db.session import session_scope
from multi_agent_platform.runtime.queue.models import QueueEnqueueRequest
from multi_agent_platform.runtime.queue.service import QueueService
from multi_agent_platform.workers.loops import poll_once


async def test_worker_bootstrap_processes_a_queued_job(settings, engine) -> None:
    container = build_container(settings)
    bootstrap = build_worker_bootstrap(container)
    try:
        async with session_scope(container.session_factory) as session:
            await QueueService(session).enqueue(
                scope=type(
                    "Scope", (), {"scope_type": "platform", "tenant_id": None}
                )(),
                request=QueueEnqueueRequest(
                    scope_type="platform",
                    job_kind=JobKind.RUNTIME_TASK,
                    trace_id="trace",
                ),
            )
        lease = await poll_once(bootstrap)
        assert lease is not None
    finally:
        await container.dispose()
