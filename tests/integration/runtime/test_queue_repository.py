from __future__ import annotations

from multi_agent_platform.db.models.queue import JobKind
from multi_agent_platform.db.repositories.queue import QueueRepository
from multi_agent_platform.runtime.queue.models import QueueEnqueueRequest


async def test_queue_repository_startup_flow(session) -> None:
    repository = QueueRepository(session)
    job = await repository.enqueue(
        QueueEnqueueRequest(
            scope_type="platform", job_kind=JobKind.BOOTSTRAP_TASK, trace_id="trace"
        )
    )
    lease = await repository.lease_next("worker-1", 30)
    assert lease is not None
    await repository.complete(job.job_id)
    completed = await repository.get(job.job_id)
    assert completed.status == "completed"
