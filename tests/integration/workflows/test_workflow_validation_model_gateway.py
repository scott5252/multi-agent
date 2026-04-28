from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.admin.workflow_registry.validation import (
    execute_model_backed_validation,
)
from multi_agent_platform.model_providers.models import GatewayResult, TestOutcome


class RecordingGateway:
    def __init__(self) -> None:
        self.context = None

    async def invoke(self, **kwargs):
        self.context = kwargs["context"]
        return GatewayResult(outcome=TestOutcome.SUCCESS)


async def test_model_backed_workflow_validation_uses_model_gateway() -> None:
    gateway = RecordingGateway()
    validation_id = uuid4()
    result = await execute_model_backed_validation(
        model_gateway=gateway,
        connection_id=uuid4(),
        model_id="gpt-test",
        workflow_validation_id=validation_id,
        tenant_id=uuid4(),
        trace_id="trace",
        agent_key="planner",
        agent_kind="agent",
        agent_profile_version_id=uuid4(),
        prompt_version_ids=(uuid4(),),
        prompt_reference_version_ids=(uuid4(),),
        model_routing_provenance={"resolver": "model_skill_config"},
    )

    assert result.outcome is TestOutcome.SUCCESS
    assert gateway.context.workflow_validation_id == validation_id
    assert gateway.context.operation_identity.startswith("workflow-validation:")
    assert gateway.context.safe_summary()["side_effect_boundary"] == (
        "before_provider_invocation"
    )
