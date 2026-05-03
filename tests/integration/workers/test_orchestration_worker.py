from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.db.models.runtime_orchestration import (
    RuntimeExecutionBundleRecord,
    RuntimeRunStatus,
    WorkflowRunRecord,
)
from multi_agent_platform.db.models.workflow_registry import WorkflowVersionBundle
from multi_agent_platform.db.repositories.runtime_orchestration import (
    RuntimeOrchestrationRepository,
)
from multi_agent_platform.runtime.orchestration.graph_execution import (
    GraphExecutionStatus,
)
from multi_agent_platform.workers.orchestration import OrchestrationWorker
from tests.unit.runtime.orchestration.test_graph_execution import simple_graph_document


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


async def test_orchestration_worker_executes_claimed_graph_run(
    session,
    settings,
) -> None:
    tenant_id = uuid4()
    workflow_run_id = uuid4()
    version_id = uuid4()
    document = simple_graph_document()
    session.add(
        WorkflowVersionBundle(
            workflow_version_bundle_id=version_id,
            workflow_lineage_id=uuid4(),
            scope_type="tenant",
            tenant_id=tenant_id,
            version_sequence=1,
            display_version="v1",
            published_from_draft_id=uuid4(),
            published_from_revision_id=uuid4(),
            published_by_principal_id=uuid4(),
            summary_json={"document": document},
        )
    )
    repository = RuntimeOrchestrationRepository(session)
    bundle = RuntimeExecutionBundleRecord(
        tenant_id=tenant_id,
        workflow_run_id=workflow_run_id,
        published_workflow_version_id=version_id,
        bundle_digest="d" * 64,
        workflow_version={"document": document},
    )
    run = WorkflowRunRecord(
        workflow_run_id=workflow_run_id,
        tenant_id=tenant_id,
        scope_type="tenant",
        initiating_principal_id="principal",
        run_bundle_id=bundle.run_bundle_id,
        status=RuntimeRunStatus.RUNNABLE,
        idempotency_key="idem-worker-graph",
        trace_id="trace-worker-graph",
    )
    await repository.create_run(run=run, bundle=bundle)
    worker = OrchestrationWorker(
        session=session,
        settings=settings,
        worker_id="worker-graph-test",
    )

    result = await worker.poll_once()

    assert result.claimed
    assert result.workflow_run_id == str(workflow_run_id)
    assert result.graph_status is GraphExecutionStatus.SUCCEEDED
    assert result.executed_node_count == 3
    assert result.wave_count == 3
    assert run.status is RuntimeRunStatus.SUCCEEDED
