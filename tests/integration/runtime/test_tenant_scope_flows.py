from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.db.models.artifact import ArtifactRecord
from multi_agent_platform.db.models.queue import JobKind
from multi_agent_platform.db.models.tenant import Tenant
from multi_agent_platform.db.repositories.artifact import ArtifactRepository
from multi_agent_platform.runtime.queue.models import QueueEnqueueRequest
from multi_agent_platform.runtime.queue.service import QueueService
from multi_agent_platform.tenancy.context import ScopeContext, ScopeType
from multi_agent_platform.tenancy.guards import ScopeError


async def test_tenant_scope_blocks_cross_tenant_queue_requests(session) -> None:
    service = QueueService(session)
    tenant_id = uuid4()
    scope = ScopeContext(
        scope_type=ScopeType.TENANT, tenant_id=tenant_id, trace_id="trace"
    )
    with pytest.raises(ScopeError):
        await service.enqueue(
            scope,
            QueueEnqueueRequest(
                tenant_id=uuid4(),
                scope_type="tenant",
                job_kind=JobKind.RUNTIME_TASK,
                trace_id="trace",
            ),
        )


async def test_artifact_repository_lists_records_by_tenant(session) -> None:
    tenant = Tenant(slug="acme", display_name="Acme")
    session.add(tenant)
    await session.flush()
    repository = ArtifactRepository(session)
    await repository.create(
        ArtifactRecord(
            tenant_id=tenant.tenant_id,
            scope_type="tenant",
            provider="filesystem",
            storage_key="artifact.txt",
        )
    )
    records = await repository.list_for_tenant(tenant.tenant_id)
    assert len(records) == 1
