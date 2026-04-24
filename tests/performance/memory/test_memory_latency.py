from __future__ import annotations

import time
from uuid import uuid4

import pytest

from multi_agent_platform.db.repositories.memory import SqlAlchemyMemoryRepository
from multi_agent_platform.memory.policy import MemoryAccessPolicy
from multi_agent_platform.memory.service import MemoryService


@pytest.mark.asyncio
@pytest.mark.performance
async def test_current_head_lookup_stays_fast_under_small_history(session) -> None:
    service = MemoryService(SqlAlchemyMemoryRepository(session))
    policy = MemoryAccessPolicy(tenant_id=uuid4(), principal_id="tenant-admin")
    result = await service.write_version(
        policy=policy,
        workflow_lineage_id="workflow.demo",
        agent_key="triage",
        memory_key="prefs",
        content={"sequence": 1},
        expected_current_version_id=None,
        assert_no_current_head=True,
    )
    for sequence in range(2, 25):
        result = await service.write_version(
            policy=policy,
            workflow_lineage_id="workflow.demo",
            agent_key="triage",
            memory_key="prefs",
            content={"sequence": sequence},
            expected_current_version_id=result.version.memory_version_id,
            assert_no_current_head=False,
        )

    started = time.perf_counter()
    head = await service.get_current_head(
        policy=policy,
        workflow_lineage_id="workflow.demo",
        agent_key="triage",
        memory_key="prefs",
    )

    assert head.has_memory is True
    assert (time.perf_counter() - started) < 1
