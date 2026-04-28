from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.agents.test_bench import run_profile_test_bench
from multi_agent_platform.model_providers.models import GatewayResult, TestOutcome


class RecordingGateway:
    def __init__(self) -> None:
        self.context = None

    async def invoke(self, **kwargs):
        self.context = kwargs["context"]
        return GatewayResult(outcome=TestOutcome.SUCCESS)


async def test_profile_test_bench_uses_model_gateway_with_equivalent_metadata() -> None:
    gateway = RecordingGateway()
    test_bench_run_id = uuid4()
    result = await run_profile_test_bench(
        model_gateway=gateway,
        connection_id=uuid4(),
        model_id="gpt-test",
        test_bench_run_id=test_bench_run_id,
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
    assert gateway.context.test_bench_run_id == test_bench_run_id
    assert gateway.context.operation_identity.startswith("test-bench:")
    assert gateway.context.prompt_version_ids
