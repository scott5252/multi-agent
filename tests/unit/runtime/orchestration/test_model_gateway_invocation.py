from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.model_providers.models import GatewayResult, TestOutcome
from multi_agent_platform.runtime.orchestration.service import (
    RuntimeOrchestrationService,
)


class RecordingGateway:
    def __init__(self) -> None:
        self.context = None

    async def invoke(self, **kwargs):
        self.context = kwargs["context"]
        return GatewayResult(outcome=TestOutcome.SUCCESS)


async def test_runtime_orchestration_invokes_model_gateway_with_complete_context() -> (
    None
):
    tenant_id = uuid4()
    workflow_run_id = uuid4()
    step_id = uuid4()
    profile_id = uuid4()
    prompt_id = uuid4()
    prompt_reference_id = uuid4()
    gateway = RecordingGateway()

    result = await RuntimeOrchestrationService().invoke_model_gateway_step(
        model_gateway=gateway,
        connection_id=uuid4(),
        model_id="gpt-test",
        messages=({"role": "user", "content": "safe fixture"},),
        tenant_id=tenant_id,
        workflow_run_id=workflow_run_id,
        workflow_run_step_id=step_id,
        trace_id="trace-1",
        idempotency_key="idem-1",
        agent_key="planner",
        agent_kind="agent",
        agent_profile_version_id=profile_id,
        prompt_version_ids=(prompt_id,),
        prompt_reference_version_ids=(prompt_reference_id,),
        model_routing_provenance={"resolver": "model_skill_config"},
    )

    assert result.outcome is TestOutcome.SUCCESS
    assert gateway.context.tenant_id == tenant_id
    assert gateway.context.workflow_run_id == workflow_run_id
    assert gateway.context.workflow_run_step_id == step_id
    assert gateway.context.trace_id == "trace-1"
    assert gateway.context.idempotency_key == "idem-1"
    assert gateway.context.prompt_version_ids == (prompt_id,)
    assert gateway.context.prompt_reference_version_ids == (prompt_reference_id,)
    assert gateway.context.agent_profile_version_id == profile_id
    assert gateway.context.operation_identity.startswith("runtime:")
    assert gateway.context.side_effect_boundary == "before_provider_invocation"
