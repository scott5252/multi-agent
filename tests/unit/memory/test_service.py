from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.db.repositories.memory import SqlAlchemyMemoryRepository
from multi_agent_platform.memory.models import (
    MemoryAuditAction,
    MemoryAuditOutcome,
    MemoryConflictError,
)
from multi_agent_platform.memory.policy import MemoryAccessPolicy
from multi_agent_platform.memory.service import MemoryService


@pytest.mark.asyncio
async def test_service_writes_versions_rejects_stale_head_and_audits(session) -> None:
    tenant_id = uuid4()
    service = MemoryService(SqlAlchemyMemoryRepository(session))
    policy = MemoryAccessPolicy(tenant_id=tenant_id, principal_id="tenant-admin")

    first = await service.write_version(
        policy=policy,
        workflow_lineage_id="workflow.demo",
        agent_key="triage",
        memory_key="prefs",
        content={"preferred_contact": "sms"},
        expected_current_version_id=None,
        assert_no_current_head=True,
        change_summary_redacted="Captured preference",
    )
    second = await service.write_version(
        policy=policy,
        workflow_lineage_id="workflow.demo",
        agent_key="triage",
        memory_key="prefs",
        content={"preferred_contact": "email"},
        expected_current_version_id=first.version.memory_version_id,
        assert_no_current_head=False,
    )

    with pytest.raises(MemoryConflictError):
        await service.write_version(
            policy=policy,
            workflow_lineage_id="workflow.demo",
            agent_key="triage",
            memory_key="prefs",
            content={"preferred_contact": "phone"},
            expected_current_version_id=first.version.memory_version_id,
            assert_no_current_head=False,
        )

    head = await service.get_current_head(
        policy=policy,
        workflow_lineage_id="workflow.demo",
        agent_key="triage",
        memory_key="prefs",
    )
    original = await service.get_version(
        policy=policy,
        memory_version_id=first.version.memory_version_id,
    )
    audit = await service.list_audit(policy=policy)

    assert second.version.previous_memory_version_id == first.version.memory_version_id
    assert head.version
    assert head.version.memory_version_id == second.version.memory_version_id
    assert original.content == {"preferred_contact": "sms"}
    assert any(event.action_type is MemoryAuditAction.CREATE_VERSION for event in audit)
    assert any(event.outcome is MemoryAuditOutcome.CONFLICT for event in audit)
    assert all(not hasattr(event, "content") for event in audit)


@pytest.mark.asyncio
async def test_service_replays_and_diffs_versions(session) -> None:
    tenant_id = uuid4()
    service = MemoryService(SqlAlchemyMemoryRepository(session))
    policy = MemoryAccessPolicy(tenant_id=tenant_id, principal_id="tenant-admin")
    first = await service.write_version(
        policy=policy,
        workflow_lineage_id="workflow.demo",
        agent_key="triage",
        memory_key="prefs",
        content={"preferred_contact": "sms"},
        expected_current_version_id=None,
        assert_no_current_head=True,
    )
    second = await service.write_version(
        policy=policy,
        workflow_lineage_id="workflow.demo",
        agent_key="triage",
        memory_key="prefs",
        content={"preferred_contact": "email", "timezone": "ET"},
        expected_current_version_id=first.version.memory_version_id,
        assert_no_current_head=False,
    )

    replay = await service.replay_version(
        policy=policy, memory_version_id=first.version.memory_version_id
    )
    diff = await service.diff_versions(
        policy=policy,
        base_memory_version_id=first.version.memory_version_id,
        compare_memory_version_id=second.version.memory_version_id,
    )

    assert replay.content == {"preferred_contact": "sms"}
    assert [entry.path for entry in diff.additions] == ["/timezone"]
    assert [entry.path for entry in diff.changes] == ["/preferred_contact"]
