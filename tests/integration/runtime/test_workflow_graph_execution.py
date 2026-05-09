from __future__ import annotations

import json
from uuid import UUID, uuid4

from sqlalchemy import select

from multi_agent_platform.db.models.runtime_orchestration import (
    ApprovalGateRecord,
    RunStepRecord,
    RuntimeExecutionBundleRecord,
    RuntimeInteractionEvidenceRecord,
    RuntimeRunStatus,
    RuntimeStepStatus,
    RuntimeTimelineEventRecord,
    SideEffectIntentRecord,
    WorkflowRunRecord,
)
from multi_agent_platform.db.models.workflow_registry import WorkflowVersionBundle
from multi_agent_platform.db.repositories.runtime_orchestration import (
    RuntimeOrchestrationRepository,
)
from multi_agent_platform.runtime.orchestration.graph_execution import (
    GraphExecutionService,
    GraphExecutionStatus,
)
from multi_agent_platform.runtime.orchestration.graph_roles import (
    DeterministicRoleNodeExecutor,
)
from tests.unit.runtime.orchestration.test_graph_execution import (
    daily_briefing_graph_document,
    simple_graph_document,
)


async def _create_graph_run(
    session,
    *,
    document: dict[str, object],
    run_tenant_id: UUID | None,
    version_tenant_id: UUID | None,
    status: RuntimeRunStatus = RuntimeRunStatus.RUNNING,
) -> tuple[RuntimeOrchestrationRepository, WorkflowRunRecord]:
    workflow_run_id = uuid4()
    version_id = uuid4()
    session.add(
        WorkflowVersionBundle(
            workflow_version_bundle_id=version_id,
            workflow_lineage_id=uuid4(),
            scope_type="tenant" if version_tenant_id is not None else "platform",
            tenant_id=version_tenant_id,
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
        tenant_id=run_tenant_id,
        workflow_run_id=workflow_run_id,
        published_workflow_version_id=version_id,
        bundle_digest="c" * 64,
        workflow_version={"document": document},
    )
    run = WorkflowRunRecord(
        workflow_run_id=workflow_run_id,
        tenant_id=run_tenant_id,
        scope_type="tenant" if run_tenant_id is not None else "platform",
        initiating_principal_id="principal",
        run_bundle_id=bundle.run_bundle_id,
        status=status,
        idempotency_key=f"idem-{workflow_run_id}",
        trace_id=f"trace-{workflow_run_id}",
    )
    await repository.create_run(run=run, bundle=bundle)
    return repository, run


async def test_graph_execution_completes_simple_published_bundle(session) -> None:
    tenant_id = uuid4()
    repository, run = await _create_graph_run(
        session,
        document=simple_graph_document(),
        run_tenant_id=tenant_id,
        version_tenant_id=tenant_id,
    )

    result = await GraphExecutionService(repository).execute_claimed_run(
        workflow_run_id=run.workflow_run_id,
        worker_id="worker-graph",
    )

    steps = await repository.list_run_steps(
        workflow_run_id=run.workflow_run_id,
        tenant_id=tenant_id,
    )
    timeline = await repository.list_timeline(
        workflow_run_id=run.workflow_run_id,
        tenant_id=tenant_id,
        limit=50,
    )

    assert result.status is GraphExecutionStatus.SUCCEEDED
    assert run.status is RuntimeRunStatus.SUCCEEDED
    assert {step.step_key for step in steps} == {"entry", "writer", "terminal"}
    assert all(step.status is RuntimeStepStatus.SUCCEEDED for step in steps)
    assert result.final_output_ref is not None
    assert "graph_run_succeeded" in {event.event_type for event in timeline}
    interactions = await repository.list_interaction_evidence(
        workflow_run_id=run.workflow_run_id,
        tenant_id=tenant_id,
    )
    assert {interaction.interaction_kind.value for interaction in interactions} >= {
        "handoff",
        "result_return",
        "run_completion",
    }
    assert [interaction.sequence for interaction in interactions] == list(
        range(1, len(interactions) + 1)
    )


async def test_daily_briefing_graph_schedules_four_scouts_in_one_wave(session) -> None:
    tenant_id = uuid4()
    repository, run = await _create_graph_run(
        session,
        document=daily_briefing_graph_document(),
        run_tenant_id=tenant_id,
        version_tenant_id=tenant_id,
    )

    result = await GraphExecutionService(repository).execute_claimed_run(
        workflow_run_id=run.workflow_run_id,
        worker_id="worker-daily",
    )

    timeline = await repository.list_timeline(
        workflow_run_id=run.workflow_run_id,
        tenant_id=tenant_id,
        limit=100,
    )
    wave_payloads = [
        event.payload
        for event in timeline
        if event.event_type == "graph_wave_scheduled"
    ]
    side_effects = list(
        (await session.execute(select(SideEffectIntentRecord))).scalars()
    )

    assert result.status is GraphExecutionStatus.SUCCEEDED
    assert any(payload["parallel_role_node_count"] == 4 for payload in wave_payloads)
    assert {"focus-node", "synthesis-node", "terminal"} <= set(
        result.executed_node_keys
    )
    assert side_effects
    assert all(effect.tool_policy_ref.startswith("mock:") for effect in side_effects)


async def test_graph_execution_resumes_without_reexecuting_succeeded_step(
    session,
) -> None:
    tenant_id = uuid4()
    repository, run = await _create_graph_run(
        session,
        document=simple_graph_document(),
        run_tenant_id=tenant_id,
        version_tenant_id=tenant_id,
    )
    await repository.create_run_step(
        workflow_run_id=run.workflow_run_id,
        tenant_id=tenant_id,
        step_key="entry",
        step_type="agent",
        status=RuntimeStepStatus.SUCCEEDED,
        input_ref={"node_key": "entry"},
    )
    entry = await repository.get_latest_run_step(
        workflow_run_id=run.workflow_run_id,
        step_key="entry",
    )
    assert entry is not None
    await repository.update_run_step(
        run_step_id=entry.run_step_id,
        status=RuntimeStepStatus.SUCCEEDED,
        output_ref={"safe_summary": "preexisting entry output"},
    )

    result = await GraphExecutionService(repository).execute_claimed_run(
        workflow_run_id=run.workflow_run_id,
        worker_id="worker-resume",
    )

    steps = await repository.list_run_steps(
        workflow_run_id=run.workflow_run_id,
        tenant_id=tenant_id,
    )

    assert result.status is GraphExecutionStatus.SUCCEEDED
    assert result.skipped_node_keys == ("entry",)
    assert [step.step_key for step in steps].count("entry") == 1
    assert {"writer", "terminal"} <= {step.step_key for step in steps}


async def test_manual_resolution_join_pauses_and_persists_approval(session) -> None:
    tenant_id = uuid4()
    repository, run = await _create_graph_run(
        session,
        document=daily_briefing_graph_document(),
        run_tenant_id=tenant_id,
        version_tenant_id=tenant_id,
    )

    result = await GraphExecutionService(
        repository,
        role_executor=DeterministicRoleNodeExecutor(
            fail_node_keys={"calendar-scout-node"}
        ),
    ).execute_claimed_run(
        workflow_run_id=run.workflow_run_id,
        worker_id="worker-manual",
    )

    approvals = list((await session.execute(select(ApprovalGateRecord))).scalars())
    timeline = await repository.list_timeline(
        workflow_run_id=run.workflow_run_id,
        tenant_id=tenant_id,
        limit=100,
    )

    assert result.status is GraphExecutionStatus.PAUSED
    assert run.status is RuntimeRunStatus.PAUSED
    assert approvals
    assert "graph_manual_resolution_required" in {
        event.event_type for event in timeline
    }
    interactions = await repository.list_interaction_evidence(
        workflow_run_id=run.workflow_run_id,
        tenant_id=tenant_id,
    )
    assert "join_contribution" in {
        interaction.interaction_kind.value for interaction in interactions
    }
    assert "manual_resolution" in {
        interaction.interaction_kind.value for interaction in interactions
    }


async def test_cross_tenant_bundle_execution_fails_closed(session) -> None:
    repository, run = await _create_graph_run(
        session,
        document=simple_graph_document(),
        run_tenant_id=uuid4(),
        version_tenant_id=uuid4(),
    )

    result = await GraphExecutionService(repository).execute_claimed_run(
        workflow_run_id=run.workflow_run_id,
        worker_id="worker-denied",
    )

    steps = await repository.list_run_steps(
        workflow_run_id=run.workflow_run_id,
        tenant_id=run.tenant_id,
    )

    assert result.status is GraphExecutionStatus.FAILED
    assert "tenant mismatch" in (result.failure_reason or "")
    assert run.status is RuntimeRunStatus.FAILED
    assert steps == []


async def test_graph_execution_redacts_sensitive_step_and_timeline_values(
    session,
) -> None:
    tenant_id = uuid4()
    repository, run = await _create_graph_run(
        session,
        document=simple_graph_document(),
        run_tenant_id=tenant_id,
        version_tenant_id=tenant_id,
    )

    await GraphExecutionService(
        repository,
        role_executor=DeterministicRoleNodeExecutor(
            output_overrides={
                "writer": {
                    "secret_token": "real-secret-token",
                    "raw_payload": {"message": "private raw text"},
                }
            }
        ),
    ).execute_claimed_run(
        workflow_run_id=run.workflow_run_id,
        worker_id="worker-redaction",
    )

    steps = list((await session.execute(select(RunStepRecord))).scalars())
    interactions = list(
        (await session.execute(select(RuntimeInteractionEvidenceRecord))).scalars()
    )
    timeline = list(
        (await session.execute(select(RuntimeTimelineEventRecord))).scalars()
    )
    encoded = json.dumps(
        {
            "steps": [
                {
                    "input_ref": step.input_ref,
                    "output_ref": step.output_ref,
                    "error_ref": step.error_ref,
                }
                for step in steps
            ],
            "interactions": [
                {
                    "safe_summary": interaction.safe_summary,
                    "provenance": interaction.provenance,
                    "classification": interaction.classification,
                    "payload_digest": interaction.payload_digest,
                }
                for interaction in interactions
            ],
            "timeline": [event.payload for event in timeline],
        },
        default=str,
    )

    assert "real-secret-token" not in encoded
    assert "private raw text" not in encoded
    assert "payload_digest" in encoded
