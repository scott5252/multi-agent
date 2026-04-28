from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.runtime.versioning import build_gateway_context_from_pins


def test_gateway_context_requires_prompt_and_profile_pins_before_model_work() -> None:
    with pytest.raises(PermissionError, match="prompt/profile pins"):
        build_gateway_context_from_pins(
            tenant_id=uuid4(),
            workflow_run_id=uuid4(),
            workflow_run_step_id=uuid4(),
            trace_id="trace",
            idempotency_key="idem",
            agent_key="planner",
            agent_kind="agent",
            agent_profile_version_id=None,
            prompt_version_ids=(),
            prompt_reference_version_ids=(),
            model_routing_provenance={},
        )


def test_gateway_context_contains_run_acceptance_pins_before_side_effects() -> None:
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

    assert context.operation_identity.startswith("runtime:")
    assert context.side_effect_boundary == "before_provider_invocation"
    assert context.prompt_version_ids
