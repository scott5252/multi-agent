from __future__ import annotations

from uuid import UUID

from multi_agent_platform.model_providers.gateway import ModelGateway
from multi_agent_platform.model_providers.models import GatewayResult
from multi_agent_platform.runtime.versioning import build_gateway_context_from_pins

SAFE_TEST_BENCH_MESSAGES = (
    {"role": "system", "content": "Return a safe profile test response."},
    {"role": "user", "content": "health"},
)


async def run_profile_test_bench(
    *,
    model_gateway: ModelGateway,
    connection_id: UUID,
    model_id: str,
    test_bench_run_id: UUID,
    tenant_id: UUID,
    trace_id: str,
    agent_key: str,
    agent_kind: str,
    agent_profile_version_id: UUID,
    prompt_version_ids: tuple[UUID, ...],
    prompt_reference_version_ids: tuple[UUID, ...],
    model_routing_provenance: dict[str, object],
) -> GatewayResult:
    context = build_gateway_context_from_pins(
        tenant_id=tenant_id,
        test_bench_run_id=test_bench_run_id,
        trace_id=trace_id,
        idempotency_key=f"test-bench:{test_bench_run_id}",
        agent_key=agent_key,
        agent_kind=agent_kind,
        agent_profile_version_id=agent_profile_version_id,
        prompt_version_ids=prompt_version_ids,
        prompt_reference_version_ids=prompt_reference_version_ids,
        model_routing_provenance=model_routing_provenance,
    )
    return await model_gateway.invoke(
        connection_id=connection_id,
        model_id=model_id,
        messages=SAFE_TEST_BENCH_MESSAGES,
        context=context,
    )
