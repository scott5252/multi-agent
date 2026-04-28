from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.model_providers.models import GatewayInvocationContext


def test_gateway_context_safe_summary_excludes_prompts_completions_and_secrets() -> (
    None
):
    context = GatewayInvocationContext(
        tenant_id=uuid4(),
        workflow_run_id=uuid4(),
        trace_id="trace",
        idempotency_key="idem",
        operation_identity="runtime:safe",
        agent_profile_version_id=uuid4(),
        prompt_version_ids=(uuid4(),),
        prompt_reference_version_ids=(uuid4(),),
        model_routing_provenance={"resolver": "model_skill_config"},
    )

    rendered = str(context.safe_summary()).lower()

    assert "raw prompt" not in rendered
    assert "completion" not in rendered
    assert "api_key" not in rendered
    assert "secret" not in rendered
