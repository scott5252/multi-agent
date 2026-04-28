from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from multi_agent_platform.runtime.versioning import build_gateway_context_from_pins


def test_runtime_gateway_contract_names_required_ordering_and_safe_context() -> None:
    contract = Path(
        "specs/012-prompt-runtime-profiles/contracts/runtime-gateway-execution.md"
    ).read_text()

    assert "Persist or recover `GatewayOperation`" in contract
    assert "before_provider_invocation" in contract
    assert "raw prompts" in contract

    context = build_gateway_context_from_pins(
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

    assert set(context.safe_summary()) >= {
        "tenant_id",
        "workflow_run_id",
        "workflow_run_step_id",
        "trace_id",
        "idempotency_key",
        "operation_identity",
        "agent_profile_version_id",
        "prompt_version_ids",
        "prompt_reference_version_ids",
        "model_routing_provenance",
    }
