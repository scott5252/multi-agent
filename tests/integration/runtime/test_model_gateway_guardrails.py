from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.model_providers.models import GatewayResult, TestOutcome
from multi_agent_platform.runtime.orchestration.service import (
    RuntimeOrchestrationService,
)


class RequiredGateway:
    def __init__(self) -> None:
        self.called = False

    async def invoke(self, **kwargs):
        self.called = True
        assert kwargs["context"].operation_identity.startswith("runtime:")
        return GatewayResult(outcome=TestOutcome.SUCCESS)


async def test_runtime_model_backed_execution_requires_gateway_path() -> None:
    gateway = RequiredGateway()

    await RuntimeOrchestrationService().invoke_model_gateway_step(
        model_gateway=gateway,
        connection_id=uuid4(),
        model_id="gpt-test",
        messages=({"role": "user", "content": "health"},),
        tenant_id=uuid4(),
        workflow_run_id=uuid4(),
        workflow_run_step_id=uuid4(),
        trace_id="trace",
        idempotency_key="idem",
        agent_key="planner",
        agent_kind="agent",
        agent_profile_version_id=uuid4(),
        prompt_version_ids=(uuid4(),),
        prompt_reference_version_ids=(uuid4(),),
        model_routing_provenance={"resolver": "model_skill_config"},
    )

    assert gateway.called is True
