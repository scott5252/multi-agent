from __future__ import annotations

from multi_agent_platform.db.models.queue import JobKind
from multi_agent_platform.runtime.queue.models import QueueEnqueueRequest
from multi_agent_platform.runtime.queue.service import QueueService
from multi_agent_platform.tenancy.context import ScopeContext, ScopeType


async def test_queue_service_enqueues_and_leases(session) -> None:
    service = QueueService(session)
    scope = ScopeContext(scope_type=ScopeType.PLATFORM, trace_id="trace")
    job = await service.enqueue(
        scope,
        QueueEnqueueRequest(
            scope_type="platform", job_kind=JobKind.RUNTIME_TASK, trace_id="trace"
        ),
    )
    lease = await service.lease_next("worker-1", 30)
    assert job.job_id == lease.job_id
