from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.agents.test_bench import (
    run_workflow_test_bench_gateway_probe,
)
from multi_agent_platform.model_providers.models import GatewayResult, TestOutcome


class RecordingGateway:
    def __init__(self) -> None:
        self.context = None

    async def invoke(self, **kwargs):
        self.context = kwargs["context"]
        return GatewayResult(outcome=TestOutcome.SUCCESS)


async def test_workflow_test_bench_gateway_probe_persists_pins() -> None:
    gateway = RecordingGateway()
    test_bench_run_id = uuid4()
    profile_version_id = uuid4()
    prompt_version_id = uuid4()

    result = await run_workflow_test_bench_gateway_probe(
        model_gateway=gateway,
        connection_id=uuid4(),
        model_id="gpt-test",
        test_bench_run_id=test_bench_run_id,
        tenant_id=uuid4(),
        trace_id="trace",
        workflow_key="draft-triage",
        workflow_version_ref="draft-rev-1",
        agent_profile_version_id=profile_version_id,
        prompt_version_ids=(prompt_version_id,),
        prompt_reference_version_ids=(),
        model_routing_provenance={"resolver": "model_skill_config"},
    )

    assert result.outcome is TestOutcome.SUCCESS
    assert gateway.context.test_bench_run_id == test_bench_run_id
    assert gateway.context.agent_kind == "workflow"
    assert gateway.context.agent_profile_version_id == profile_version_id
    assert gateway.context.prompt_version_ids == (prompt_version_id,)
    assert gateway.context.model_routing_provenance["workflow_version_ref"] == (
        "draft-rev-1"
    )
