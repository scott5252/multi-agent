from __future__ import annotations

from multi_agent_platform.workers.orchestration import OrchestrationWorker


async def test_orchestration_worker_reports_no_claim_when_queue_empty(
    session, settings
) -> None:
    worker = OrchestrationWorker(
        session=session,
        settings=settings,
        worker_id="worker-test",
    )

    result = await worker.poll_once()

    assert not result.claimed
