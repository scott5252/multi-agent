from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.runtime.orchestration.compiler import (
    PublishedWorkflowBundle,
    clone_execution_bundle,
)
from multi_agent_platform.runtime.orchestration.events import (
    RuntimeEventType,
    RuntimeTimelineEvent,
)
from multi_agent_platform.runtime.orchestration.models import WorkflowRun
from multi_agent_platform.runtime.orchestration.repository import (
    InMemoryRuntimeRepository,
)


@pytest.mark.asyncio
async def test_in_memory_repository_is_tenant_scoped() -> None:
    tenant_id = uuid4()
    run_id = uuid4()
    published = PublishedWorkflowBundle(
        published_workflow_version_id=uuid4(),
        workflow={},
        contracts={},
        retry_policy={},
        checkpoint_policy={},
    )
    bundle = clone_execution_bundle(
        tenant_id=tenant_id,
        workflow_run_id=run_id,
        published_bundle=published,
    )
    run = WorkflowRun(
        workflow_run_id=run_id,
        tenant_id=tenant_id,
        scope_type="tenant",
        initiating_principal_id="principal",
        run_bundle_id=bundle.run_bundle_id,
        bundle_digest=bundle.bundle_digest,
        idempotency_key="idem",
        trace_id="trace",
    )
    repository = InMemoryRuntimeRepository()

    await repository.create_run(run, bundle)
    await repository.add_timeline_event(
        RuntimeTimelineEvent(
            tenant_id=tenant_id,
            workflow_run_id=run_id,
            event_type=RuntimeEventType.START,
            trace_id="trace",
        )
    )

    assert await repository.get_run(run_id, tenant_id) == run
    assert await repository.get_run(run_id, uuid4()) is None
    assert len(await repository.list_timeline(run_id, tenant_id)) == 1
    assert await repository.list_timeline(run_id, uuid4()) == []
