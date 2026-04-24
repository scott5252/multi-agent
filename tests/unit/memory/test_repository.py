from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.db.repositories.memory import SqlAlchemyMemoryRepository
from multi_agent_platform.memory.canonical import content_sha256, content_size_bytes
from multi_agent_platform.memory.models import (
    MemoryScopeIdentity,
    MemorySourceType,
    RuntimeSourceRef,
)


@pytest.mark.asyncio
async def test_repository_returns_idempotent_retry_without_new_version(session) -> None:
    tenant_id = uuid4()
    repository = SqlAlchemyMemoryRepository(session)
    scope = MemoryScopeIdentity(
        tenant_id=tenant_id,
        workflow_lineage_id="workflow.demo",
        agent_key="triage",
        memory_key="prefs",
    )
    content = {"preferred_contact": "sms"}

    first = await repository.write_version(
        scope=scope,
        content=content,
        content_sha256=content_sha256(content),
        content_size_bytes=content_size_bytes(content),
        actor_principal_id="tenant-admin",
        source_type=MemorySourceType.API,
        source=RuntimeSourceRef(),
        expected_current_version_id=None,
        assert_no_current_head=True,
        idempotency_key="idem-1",
        change_reason=None,
        change_summary_redacted=None,
        trace_id="trace",
    )
    retry = await repository.write_version(
        scope=scope,
        content=content,
        content_sha256=content_sha256(content),
        content_size_bytes=content_size_bytes(content),
        actor_principal_id="tenant-admin",
        source_type=MemorySourceType.API,
        source=RuntimeSourceRef(),
        expected_current_version_id=None,
        assert_no_current_head=True,
        idempotency_key="idem-1",
        change_reason=None,
        change_summary_redacted=None,
        trace_id="trace",
    )

    assert retry.version.memory_version_id == first.version.memory_version_id
    assert retry.head_advanced is False
