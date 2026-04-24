from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.runtime.orchestration.compiler import clone_execution_bundle
from multi_agent_platform.runtime.orchestration.models import (
    RunStatus,
    RunStep,
    StepType,
    WorkflowRun,
)
from multi_agent_platform.runtime.orchestration.service import (
    RuntimeOrchestrationService,
)


def test_terminal_run_cannot_be_mutated() -> None:
    run = WorkflowRun(
        tenant_id=uuid4(),
        scope_type="tenant",
        initiating_principal_id="principal",
        run_bundle_id=uuid4(),
        bundle_digest="digest",
        idempotency_key="idem",
        trace_id="trace",
    )
    run.transition(RunStatus.SUCCEEDED, reason="done")

    with pytest.raises(ValueError, match="terminal"):
        run.transition(RunStatus.RUNNING)


def test_execution_bundle_clone_pins_digest(published_workflow_bundle) -> None:
    workflow_run_id = uuid4()
    bundle = clone_execution_bundle(
        tenant_id=uuid4(),
        workflow_run_id=workflow_run_id,
        published_bundle=published_workflow_bundle,
    )

    assert bundle.workflow_run_id == workflow_run_id
    assert bundle.bundle_digest == published_workflow_bundle.digest


@pytest.mark.asyncio
async def test_start_run_persists_runnable_run() -> None:
    tenant_id = uuid4()
    service = RuntimeOrchestrationService()

    run = await service.start_run(
        tenant_id=tenant_id,
        scope_type="tenant",
        principal_id="principal",
        published_workflow_version_id=uuid4(),
        input_payload={"prompt": "hello"},
        idempotency_key="idempotency-key",
    )

    assert run.status is RunStatus.RUNNABLE
    assert run.tenant_id == tenant_id
    assert await service.inspect_run(
        workflow_run_id=run.workflow_run_id, tenant_id=tenant_id
    )


@pytest.mark.asyncio
async def test_cancel_missing_run_raises_lookup() -> None:
    service = RuntimeOrchestrationService()

    with pytest.raises(LookupError):
        await service.cancel_run(
            workflow_run_id=uuid4(),
            tenant_id=uuid4(),
            reason="missing",
        )


def test_run_step_retry_budget() -> None:
    step = RunStep(
        workflow_run_id=uuid4(),
        tenant_id=uuid4(),
        step_key="tool",
        step_type=StepType.TOOL,
        max_attempts=1,
    )

    assert step.record_attempt() == 1
    with pytest.raises(ValueError, match="retry budget"):
        step.record_attempt()
