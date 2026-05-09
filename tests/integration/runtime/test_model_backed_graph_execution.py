from __future__ import annotations

import json
from uuid import UUID, uuid4

from sqlalchemy import select

from multi_agent_platform.db.models.runtime_orchestration import (
    RunStepRecord,
    RuntimeExecutionBundleRecord,
    RuntimeRunStatus,
    WorkflowRunRecord,
)
from multi_agent_platform.db.models.workflow_registry import WorkflowVersionBundle
from multi_agent_platform.db.repositories.runtime_orchestration import (
    RuntimeOrchestrationRepository,
)
from multi_agent_platform.model_providers.models import (
    GatewayResult,
    GatewayUsage,
    TestOutcome,
)
from multi_agent_platform.runtime.orchestration.graph_execution import (
    GraphExecutionService,
    GraphExecutionStatus,
)
from multi_agent_platform.runtime.orchestration.model_backed_roles import (
    ResolvedModelBackedRolePins,
    build_role_node_executor,
)

PROFILE_ID = UUID("bbbbbbbb-bbbb-4bbb-bbbb-bbbbbbbbbbbb")


def _model_graph_document(*, execution_mode: str | None) -> dict[str, object]:
    role: dict[str, object] = {
        "role_key": "ux-reviewer",
        "role_kind": "agent",
        "profile_reference_key": "ux-profile",
        "output_contract_key": "reviewer-output-v1",
        "agent_profile_version_id": str(PROFILE_ID),
    }
    if execution_mode is not None:
        role["execution_mode"] = execution_mode
    return {
        "workflow_key": "model-backed-review",
        "entry_node_key": "reviewer",
        "roles": [role],
        "nodes": [
            {
                "node_key": "reviewer",
                "node_type": "role",
                "role_key": "ux-reviewer",
            },
            {"node_key": "terminal", "node_type": "terminal"},
        ],
        "edges": [
            {
                "edge_key": "reviewer-terminal",
                "source_node_key": "reviewer",
                "target_node_key": "terminal",
            }
        ],
        "contracts": [
            {
                "contract_key": "reviewer-output-v1",
                "json_schema": {"required": ["summary", "status"]},
            }
        ],
    }


async def _create_graph_run(
    session,
    *,
    document: dict[str, object],
    tenant_id: UUID,
) -> tuple[RuntimeOrchestrationRepository, WorkflowRunRecord]:
    workflow_run_id = uuid4()
    version_id = uuid4()
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
        status=RuntimeRunStatus.RUNNING,
        idempotency_key=f"idem-{workflow_run_id}",
        trace_id=f"trace-{workflow_run_id}",
    )
    await repository.create_run(run=run, bundle=bundle)
    return repository, run


class FakeResolver:
    async def resolve(self, context) -> ResolvedModelBackedRolePins:
        return ResolvedModelBackedRolePins(
            provider_connection_id=uuid4(),
            model_id="gpt-safe-fixture",
            model_provider_key="local",
            model_routing_version_id=uuid4(),
            prompt_reference_version_id=uuid4(),
            prompt_version_id=uuid4(),
            prompt_digest="sha256:prompt",
            agent_profile_version_id=PROFILE_ID,
            evaluated_version_ids=(uuid4(),),
            safe_reason="model and prompt resolved from pinned candidates",
        )


class FakeGateway:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    async def invoke(self, **kwargs: object) -> GatewayResult:
        self.calls.append(dict(kwargs))
        return GatewayResult(
            outcome=TestOutcome.SUCCESS,
            content=json.dumps(
                {
                    "summary": "Safe reviewer summary.",
                    "status": "approved",
                    "findings": [],
                }
            ),
            usage=GatewayUsage(input_tokens=7, output_tokens=5, total_tokens=12),
            safe_audit_summary={"outcome": "success"},
        )


async def test_graph_execution_runs_model_backed_role_with_mocked_gateway(
    session,
) -> None:
    tenant_id = uuid4()
    repository, run = await _create_graph_run(
        session,
        document=_model_graph_document(execution_mode="model_gateway"),
        tenant_id=tenant_id,
    )
    gateway = FakeGateway()

    result = await GraphExecutionService(
        repository,
        role_executor=build_role_node_executor(
            model_gateway=gateway,
            pin_resolver=FakeResolver(),
        ),
    ).execute_claimed_run(
        workflow_run_id=run.workflow_run_id,
        worker_id="worker-model-backed",
    )

    steps = list((await session.execute(select(RunStepRecord))).scalars())
    reviewer_step = next(step for step in steps if step.step_key == "reviewer")

    assert result.status is GraphExecutionStatus.SUCCEEDED
    assert gateway.calls
    assert gateway.calls[0]["context"].workflow_run_step_id == reviewer_step.run_step_id
    assert reviewer_step.output_ref["usage_summary"]["total_tokens"] == 12
    assert reviewer_step.output_ref["provenance"]["model_id"] == "gpt-safe-fixture"


async def test_graph_execution_keeps_deterministic_default(session) -> None:
    tenant_id = uuid4()
    repository, run = await _create_graph_run(
        session,
        document=_model_graph_document(execution_mode=None),
        tenant_id=tenant_id,
    )
    gateway = FakeGateway()

    result = await GraphExecutionService(
        repository,
        role_executor=build_role_node_executor(
            model_gateway=gateway,
            pin_resolver=FakeResolver(),
        ),
    ).execute_claimed_run(
        workflow_run_id=run.workflow_run_id,
        worker_id="worker-deterministic",
    )

    steps = list((await session.execute(select(RunStepRecord))).scalars())
    reviewer_step = next(step for step in steps if step.step_key == "reviewer")

    assert result.status is GraphExecutionStatus.SUCCEEDED
    assert gateway.calls == []
    assert reviewer_step.output_ref["structured_output"]["result"] == (
        "safe deterministic output for ux-reviewer"
    )
