from __future__ import annotations

from multi_agent_platform.model_providers.adapters import ProviderAdapterRegistry
from multi_agent_platform.model_providers.models import (
    AdapterRequest,
    ProviderTestSummary,
    ProviderType,
    TestOutcome,
    TimeoutPolicy,
)

SAFE_PROBE_MESSAGE = (
    {"role": "system", "content": "Return a short health check response."},
    {"role": "user", "content": "health"},
)


class ProviderProbeRunner:
    def __init__(self, registry: ProviderAdapterRegistry) -> None:
        self._registry = registry

    async def run_probe(
        self,
        *,
        provider_type: ProviderType,
        model_id: str,
        timeout_policy: TimeoutPolicy,
        base_url: str | None,
        credential: str | None,
    ) -> ProviderTestSummary:
        adapter = self._registry.get(provider_type)
        response = await adapter.chat_completion(
            AdapterRequest(
                model_id=model_id,
                messages=SAFE_PROBE_MESSAGE,
                timeout_policy=timeout_policy,
                base_url=base_url,
                credential=credential,
            )
        )
        return ProviderTestSummary(
            outcome=response.outcome,
            normalized_reason=response.normalized_error_category,
            latency_ms=response.latency_ms,
            tested_model_id=model_id,
            safe_diagnostic_summary=response.safe_diagnostic_summary,
            safe_provider_request_id=response.provider_request_id,
        )


def probe_succeeded(summary: ProviderTestSummary) -> bool:
    return summary.outcome is TestOutcome.SUCCESS
