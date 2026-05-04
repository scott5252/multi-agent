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
from multi_agent_platform.model_providers.secrets import ProviderSecretResolver
from multi_agent_platform.secrets.base import SecretValue


class ProbeAdapter:
    provider_type = ProviderType.OPENAI

    async def chat_completion(self, request: AdapterRequest) -> AdapterResponse:
        assert request.messages[0]["content"] == "Return a short health check response."
        return AdapterResponse(
            outcome=TestOutcome.SUCCESS,
            normalized_error_category=ErrorCategory.NONE,
            latency_ms=10,
        )


class CapturingProbeAdapter:
    provider_type = ProviderType.OPENAI

    def __init__(self) -> None:
        self.credentials: list[str | None] = []

    async def chat_completion(self, request: AdapterRequest) -> AdapterResponse:
        self.credentials.append(request.credential)
        return AdapterResponse(
            outcome=TestOutcome.SUCCESS,
            normalized_error_category=ErrorCategory.NONE,
            latency_ms=3,
        )


class MissingProbeAdapter:
    provider_type = ProviderType.OPENAI

    def __init__(self) -> None:
        self.calls = 0

    async def chat_completion(self, request: AdapterRequest) -> AdapterResponse:
        self.calls += 1
        return AdapterResponse(outcome=TestOutcome.SUCCESS)


class FakeSecretProvider:
    provider_name = "fake"

    async def resolve(self, reference: str) -> SecretValue:
        if reference == "missing":
            raise LookupError(reference)
        return SecretValue(reference=reference, value="resolved-probe-secret")


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


@pytest.mark.asyncio
async def test_probe_runner_resolves_configured_credential_reference() -> None:
    adapter = CapturingProbeAdapter()

    result = await ProviderProbeRunner(
        ProviderAdapterRegistry({ProviderType.OPENAI: adapter}),
        secret_resolver=ProviderSecretResolver(FakeSecretProvider()),
    ).run_probe(
        provider_type=ProviderType.OPENAI,
        model_id="gpt-test",
        timeout_policy=TimeoutPolicy(),
        base_url=None,
        credential_secret_reference_ids=("qa025/openai-placeholder",),
    )

    assert probe_succeeded(result)
    assert adapter.credentials == ["resolved-probe-secret"]


@pytest.mark.asyncio
async def test_probe_runner_fails_closed_without_adapter_call_on_secret_error() -> None:
    adapter = MissingProbeAdapter()

    result = await ProviderProbeRunner(
        ProviderAdapterRegistry({ProviderType.OPENAI: adapter}),
        secret_resolver=ProviderSecretResolver(FakeSecretProvider()),
    ).run_probe(
        provider_type=ProviderType.OPENAI,
        model_id="gpt-test",
        timeout_policy=TimeoutPolicy(),
        base_url=None,
        credential_secret_reference_ids=("missing",),
    )

    assert result.outcome is TestOutcome.FAILURE
    assert result.normalized_reason is ErrorCategory.SECRET_REFERENCE_INVALID
    assert result.tested_model_id == "gpt-test"
    assert adapter.calls == 0
