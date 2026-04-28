from __future__ import annotations

import pytest

from multi_agent_platform.model_providers.adapters import ProviderAdapterRegistry
from multi_agent_platform.model_providers.models import (
    AdapterRequest,
    AdapterResponse,
    ErrorCategory,
    ProviderType,
    TestOutcome,
    TimeoutPolicy,
)
from multi_agent_platform.model_providers.probes import (
    ProviderProbeRunner,
    probe_succeeded,
)


class ProbeAdapter:
    provider_type = ProviderType.OPENAI

    async def chat_completion(self, request: AdapterRequest) -> AdapterResponse:
        assert request.messages[0]["content"] == "Return a short health check response."
        return AdapterResponse(
            outcome=TestOutcome.SUCCESS,
            normalized_error_category=ErrorCategory.NONE,
            latency_ms=10,
        )


@pytest.mark.asyncio
async def test_probe_runner_uses_safe_probe_message() -> None:
    result = await ProviderProbeRunner(
        ProviderAdapterRegistry({ProviderType.OPENAI: ProbeAdapter()})
    ).run_probe(
        provider_type=ProviderType.OPENAI,
        model_id="gpt-test",
        timeout_policy=TimeoutPolicy(),
        base_url=None,
        credential=None,
    )

    assert probe_succeeded(result)
    assert result.safe_diagnostic_summary == "Provider call completed"
