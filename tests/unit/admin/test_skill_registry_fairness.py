from __future__ import annotations

from multi_agent_platform.admin.skill_registry.fairness import (
    QueuedLifecycleJob,
    TenantFairnessController,
    TenantLifecycleQuota,
)


def test_fairness_blocks_artifact_throughput_excess() -> None:
    controller = TenantFairnessController(
        TenantLifecycleQuota(max_artifact_bytes_per_window=10)
    )

    decision = controller.admit(
        tenant_id="tenant-1",
        job_kind="smoke",
        artifact_bytes=11,
    )

    assert decision.allowed is False
    assert decision.reason == "artifact_throughput_limit"


def test_fair_scheduler_selects_oldest_queued_job() -> None:
    controller = TenantFairnessController()
    first = QueuedLifecycleJob(job_id="first", tenant_id="tenant-1", kind="smoke")
    second = QueuedLifecycleJob(job_id="second", tenant_id="tenant-2", kind="smoke")
    controller.enqueue(second)
    controller.enqueue(first)

    assert controller.next_job() == first
