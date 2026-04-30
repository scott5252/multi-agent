from __future__ import annotations

import pytest

from multi_agent_platform.admin.skill_registry.jobs import (
    LifecycleJobError,
    SkillLifecycleJobStore,
)


def test_jobs_are_idempotent_by_key() -> None:
    store = SkillLifecycleJobStore()

    first = store.accept(kind="validation", idempotency_key="key", tenant_id="t1")
    second = store.accept(kind="validation", idempotency_key="key", tenant_id="t1")

    assert first.job_id == second.job_id


def test_terminal_jobs_cannot_be_released() -> None:
    store = SkillLifecycleJobStore()
    job = store.accept(kind="validation", idempotency_key="key", tenant_id="t1")
    store.complete(job_id=job.job_id, status="passed")

    with pytest.raises(LifecycleJobError):
        store.lease(job_id=job.job_id, owner="worker")


def test_active_lease_blocks_duplicate_worker() -> None:
    store = SkillLifecycleJobStore()
    job = store.accept(kind="validation", idempotency_key="key", tenant_id="t1")
    store.lease(job_id=job.job_id, owner="worker-a")

    with pytest.raises(LifecycleJobError):
        store.lease(job_id=job.job_id, owner="worker-b")
