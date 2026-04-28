from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.config.provenance import (
    combine_gateway_prompt_profile_provenance,
)
from multi_agent_platform.runtime.versioning import build_runtime_gateway_provenance


def test_runtime_provenance_links_prompt_profile_pins_with_gateway_metadata() -> None:
    prompt_id = uuid4()
    profile_id = uuid4()
    operation_id = uuid4()

    projection = build_runtime_gateway_provenance(
        tenant_id=uuid4(),
        workflow_run_id=uuid4(),
        workflow_run_step_id=uuid4(),
        trace_id="trace",
        agent_key="planner",
        agent_kind="agent",
        agent_profile_version_id=profile_id,
        prompt_version_ids=(prompt_id,),
        prompt_reference_version_ids=(uuid4(),),
        gateway_operation_id=operation_id,
        provider_connection_id=uuid4(),
        provider_model_definition_id=uuid4(),
        model_id="gpt-test",
        retry_category="skipped",
        breaker_scope="provider_connection:pc:model:gpt-test",
        latency_ms=3,
        usage_available=True,
        normalized_outcome="success",
        safe_summary={"outcome": "success"},
    )
    combined = combine_gateway_prompt_profile_provenance(projection)

    assert combined["agent_profile_version_id"] == str(profile_id)
    assert combined["prompt_version_ids"] == [str(prompt_id)]
    assert combined["gateway_operation_id"] == str(operation_id)
    assert combined["metadata_available"] is True


def test_historical_runtime_provenance_without_gateway_metadata_is_unavailable() -> (
    None
):
    projection = build_runtime_gateway_provenance(
        tenant_id=uuid4(),
        workflow_run_id=uuid4(),
        workflow_run_step_id=None,
        trace_id="trace",
        agent_key="planner",
        agent_kind="agent",
        agent_profile_version_id=uuid4(),
        prompt_version_ids=(uuid4(),),
        prompt_reference_version_ids=(),
        gateway_operation_id=None,
        provider_connection_id=None,
        provider_model_definition_id=None,
        model_id=None,
        retry_category=None,
        breaker_scope=None,
        latency_ms=None,
        usage_available=None,
        normalized_outcome=None,
        safe_summary={},
    )

    assert projection["metadata_available"] is False
    assert projection["metadata_status"] == "pre_v2_metadata_unavailable"
