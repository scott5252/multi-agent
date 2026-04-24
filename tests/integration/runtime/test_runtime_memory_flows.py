from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.db.repositories.memory import SqlAlchemyMemoryRepository
from multi_agent_platform.memory.models import RuntimeMemoryContext
from multi_agent_platform.memory.service import MemoryService
from multi_agent_platform.runtime.orchestration.service import (
    RuntimeOrchestrationService,
)


@pytest.mark.asyncio
async def test_runtime_memory_facade_reads_writes_and_replays_idempotently(
    session,
) -> None:
    tenant_id = uuid4()
    workflow_run_id = uuid4()
    context = RuntimeMemoryContext(
        tenant_id=tenant_id,
        workflow_lineage_id="workflow.demo",
        agent_key="triage",
        memory_key="prefs",
        workflow_run_id=workflow_run_id,
        run_step_id=uuid4(),
        run_bundle_id=uuid4(),
        bundle_digest="a" * 64,
        actor_principal_id="runtime-worker",
        trace_id="trace",
        run_lineage_id=uuid4(),
    )
    memory_service = MemoryService(SqlAlchemyMemoryRepository(session))
    runtime_service = RuntimeOrchestrationService()

    missing = await runtime_service.get_current_memory_head(
        memory_service=memory_service,
        context=context,
    )
    first = await runtime_service.write_memory_version(
        memory_service=memory_service,
        context=context,
        content={"preferred_contact": "sms"},
        expected_current_version_id=None,
        assert_no_current_head=True,
        idempotency_key="runtime-idem-1",
    )
    retry = await memory_service.write_version_for_runtime(
        context=context,
        content={"preferred_contact": "sms"},
        expected_current_version_id=None,
        assert_no_current_head=True,
        idempotency_key="runtime-idem-1",
    )

    assert missing.has_memory is False
    assert first.version.source.workflow_run_id == workflow_run_id
    assert first.version.source.run_lineage_id == context.run_lineage_id
    assert retry.version.memory_version_id == first.version.memory_version_id
