from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.db.models.runtime_orchestration import (
    RuntimeExecutionBundleRecord,
    RuntimeRunStatus,
    RuntimeTimelineEventRecord,
    WorkflowRunRecord,
)
from multi_agent_platform.db.repositories.runtime_orchestration import (
    RuntimeOrchestrationRepository,
)


async def test_runtime_repository_persists_tenant_scoped_run_and_timeline(
    session,
) -> None:
    repository = RuntimeOrchestrationRepository(session)
    tenant_id = uuid4()
    workflow_run_id = uuid4()
    bundle = RuntimeExecutionBundleRecord(
        tenant_id=tenant_id,
        workflow_run_id=workflow_run_id,
        published_workflow_version_id=uuid4(),
        bundle_digest="a" * 64,
    )
    run = WorkflowRunRecord(
        workflow_run_id=workflow_run_id,
        tenant_id=tenant_id,
        scope_type="tenant",
        initiating_principal_id="principal",
        run_bundle_id=bundle.run_bundle_id,
        status=RuntimeRunStatus.RUNNABLE,
        idempotency_key="idem-runtime",
        trace_id="trace-runtime",
    )

    await repository.create_run(run=run, bundle=bundle)
    await repository.create_timeline_event(
        RuntimeTimelineEventRecord(
            tenant_id=tenant_id,
            workflow_run_id=workflow_run_id,
            event_type="start",
            severity="info",
            payload={"status": "runnable"},
            trace_id="trace-runtime",
        )
    )

    assert (
        await repository.get_run(workflow_run_id=workflow_run_id, tenant_id=tenant_id)
    ) == run
    assert (
        await repository.get_run(workflow_run_id=workflow_run_id, tenant_id=uuid4())
    ) is None
    assert (
        len(
            await repository.list_timeline(
                workflow_run_id=workflow_run_id, tenant_id=tenant_id
            )
        )
        == 1
    )


async def test_runtime_repository_claims_oldest_runnable_run(session) -> None:
    repository = RuntimeOrchestrationRepository(session)
    workflow_run_id = uuid4()
    bundle = RuntimeExecutionBundleRecord(
        tenant_id=None,
        workflow_run_id=workflow_run_id,
        published_workflow_version_id=uuid4(),
        bundle_digest="b" * 64,
    )
    run = WorkflowRunRecord(
        workflow_run_id=workflow_run_id,
        tenant_id=None,
        scope_type="platform",
        initiating_principal_id="principal",
        run_bundle_id=bundle.run_bundle_id,
        status=RuntimeRunStatus.RUNNABLE,
        idempotency_key="idem-claim",
        trace_id="trace-claim",
    )
    await repository.create_run(run=run, bundle=bundle)

    lease = await repository.claim_next_run(worker_id="worker-1", lease_seconds=30)

    assert lease is not None
    assert lease.workflow_run_id == workflow_run_id
    assert lease.worker_id == "worker-1"
    assert run.status is RuntimeRunStatus.RUNNING


async def test_runtime_repository_creates_default_retention_policy(session) -> None:
    repository = RuntimeOrchestrationRepository(session)
    tenant_id = uuid4()

    first = await repository.get_or_create_retention_policy(tenant_id)
    second = await repository.get_or_create_retention_policy(tenant_id)

    assert first is second
    assert first.checkpoint_retention_days == 90
    assert first.run_payload_ref_retention_days == 90
    assert first.audit_retention == "indefinite"
    assert first.lineage_retention == "indefinite"
