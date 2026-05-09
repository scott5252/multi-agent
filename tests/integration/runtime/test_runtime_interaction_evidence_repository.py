from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.db.models.runtime_orchestration import (
    RuntimeExecutionBundleRecord,
    RuntimeInteractionKind,
    RuntimeInteractionStatus,
    RuntimeRunStatus,
    WorkflowRunRecord,
)
from multi_agent_platform.db.repositories.runtime_orchestration import (
    RuntimeOrchestrationRepository,
)


async def test_runtime_interaction_evidence_is_idempotent_and_ordered(session) -> None:
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
        initiating_principal_id="tenant-admin-acme",
        run_bundle_id=bundle.run_bundle_id,
        status=RuntimeRunStatus.RUNNING,
        idempotency_key=f"run-{workflow_run_id}",
        trace_id=f"trace-{workflow_run_id}",
    )
    await repository.create_run(run=run, bundle=bundle)

    first = await repository.record_interaction_evidence(
        tenant_id=tenant_id,
        workflow_run_id=workflow_run_id,
        source_node_key="coordinator",
        target_node_key="specialist",
        interaction_kind=RuntimeInteractionKind.HANDOFF,
        status=RuntimeInteractionStatus.SENT,
        safe_summary="Coordinator sent safe context.",
        classification="safe-summary",
        payload_digest="b" * 64,
        provenance={"edge_key": "coordinator-specialist"},
        idempotency_key="same-interaction",
    )
    replay = await repository.record_interaction_evidence(
        tenant_id=tenant_id,
        workflow_run_id=workflow_run_id,
        source_node_key="coordinator",
        target_node_key="specialist",
        interaction_kind=RuntimeInteractionKind.HANDOFF,
        status=RuntimeInteractionStatus.SENT,
        safe_summary="Coordinator sent safe context again.",
        classification="safe-summary",
        payload_digest="c" * 64,
        provenance={"edge_key": "coordinator-specialist"},
        idempotency_key="same-interaction",
    )
    second = await repository.record_interaction_evidence(
        tenant_id=tenant_id,
        workflow_run_id=workflow_run_id,
        source_node_key="specialist",
        target_node_key="done",
        interaction_kind=RuntimeInteractionKind.RESULT_RETURN,
        status=RuntimeInteractionStatus.COMPLETED,
        safe_summary="Specialist returned a safe result.",
        classification="safe-summary",
        payload_digest="d" * 64,
        provenance={"edge_key": "specialist-done"},
        idempotency_key="second-interaction",
    )

    records = await repository.list_interaction_evidence(
        workflow_run_id=workflow_run_id,
        tenant_id=tenant_id,
    )

    assert replay is first
    assert [record.sequence for record in records] == [1, 2]
    assert second.sequence == 2
    assert records[0].safe_summary == "Coordinator sent safe context."


async def test_runtime_interaction_evidence_is_tenant_filtered(session) -> None:
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
        initiating_principal_id="tenant-admin-acme",
        run_bundle_id=bundle.run_bundle_id,
        status=RuntimeRunStatus.RUNNING,
        idempotency_key=f"run-{workflow_run_id}",
        trace_id=f"trace-{workflow_run_id}",
    )
    await repository.create_run(run=run, bundle=bundle)
    await repository.record_interaction_evidence(
        tenant_id=tenant_id,
        workflow_run_id=workflow_run_id,
        source_node_key="coordinator",
        target_node_key="specialist",
        interaction_kind=RuntimeInteractionKind.HANDOFF,
        status=RuntimeInteractionStatus.SENT,
        safe_summary="Coordinator sent safe context.",
        classification="safe-summary",
        payload_digest="b" * 64,
        provenance={},
        idempotency_key="tenant-filtered",
    )

    assert (
        await repository.list_interaction_evidence(
            workflow_run_id=workflow_run_id,
            tenant_id=uuid4(),
        )
        == []
    )
