from __future__ import annotations

from multi_agent_platform.bootstrap.container import build_container
from multi_agent_platform.bootstrap.worker import build_worker_bootstrap
from multi_agent_platform.db.models.queue import JobKind
from multi_agent_platform.db.session import session_scope
from multi_agent_platform.runtime.queue.models import QueueEnqueueRequest
from multi_agent_platform.runtime.queue.service import QueueService
from multi_agent_platform.workers.loops import poll_once, run_polling_loop


async def test_poll_once_returns_none_when_queue_is_empty(settings, engine) -> None:
    container = build_container(settings)
    bootstrap = build_worker_bootstrap(container)
    try:
        assert await poll_once(bootstrap) is None
    finally:
        await container.dispose()


async def test_run_polling_loop_invokes_handler(settings, engine) -> None:
    container = build_container(settings)
    bootstrap = build_worker_bootstrap(container)
    observed: list[str] = []
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
        await run_polling_loop(
            bootstrap,
            iterations=1,
            handler=lambda lease: _record(observed, lease.trace_id),
        )
        assert observed == ["trace"]
    finally:
        await container.dispose()


async def _record(observed: list[str], trace_id: str) -> None:
    observed.append(trace_id)
