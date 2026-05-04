from __future__ import annotations

import httpx
import pytest

from multi_agent_platform.model_providers.adapters import (
    ProviderAdapterRegistry,
    post_openai_chat_completion,
)
from multi_agent_platform.model_providers.allowlist import LocalEndpointAllowlist
from multi_agent_platform.model_providers.local_adapter import (
    LocalOpenAICompatibleAdapter,
)
from multi_agent_platform.model_providers.models import (
    AdapterRequest,
    ErrorCategory,
    ProviderType,
    TestOutcome,
    TimeoutPolicy,
    UsageAvailability,
)
from multi_agent_platform.model_providers.openai_adapter import OpenAIAdapter


def _request() -> AdapterRequest:
    return AdapterRequest(
        model_id="gpt-test",
        messages=({"role": "user", "content": "health"},),
        timeout_policy=TimeoutPolicy(),
    )


@pytest.mark.asyncio
async def test_post_openai_chat_completion_normalizes_success() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer [redacted]"
        return httpx.Response(
            200,
            json={
                "choices": [{"message": {"content": "ok"}}],
                "usage": {"prompt_tokens": 1, "completion_tokens": 1},
            },
            headers={"x-request-id": "req-safe"},
        )

    response = await post_openai_chat_completion(
        client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
        request=_request(),
        url="https://provider.test/v1/chat/completions",
        headers={"Authorization": "Bearer [redacted]"},
    )

    assert response.outcome is TestOutcome.SUCCESS
    assert response.content == "ok"
    assert response.usage.availability is UsageAvailability.AVAILABLE


@pytest.mark.asyncio
async def test_post_openai_chat_completion_normalizes_provider_errors() -> None:
    async def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={"error": "rate limited"})

    response = await post_openai_chat_completion(
        client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
        request=_request(),
        url="https://provider.test/v1/chat/completions",
        headers={},
    )

    assert response.outcome is TestOutcome.FAILURE
    assert response.normalized_error_category is ErrorCategory.RATE_LIMIT


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("status_code", "category"),
    [
        (401, ErrorCategory.AUTHORIZATION_FAILURE),
        (403, ErrorCategory.AUTHORIZATION_FAILURE),
        (404, ErrorCategory.INVALID_MODEL),
        (500, ErrorCategory.PROVIDER_UNAVAILABLE),
    ],
)
async def test_post_openai_chat_completion_normalizes_common_http_failures(
    status_code: int,
    category: ErrorCategory,
) -> None:
    async def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json={"error": "failure"})

    response = await post_openai_chat_completion(
        client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
        request=_request(),
        url="https://provider.test/v1/chat/completions",
        headers={},
    )

    assert response.outcome is TestOutcome.FAILURE
    assert response.normalized_error_category is category


@pytest.mark.asyncio
async def test_post_openai_chat_completion_normalizes_transport_failures() -> None:
    async def timeout_handler(_request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("slow")

    async def connect_handler(_request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("down")

    timeout_response = await post_openai_chat_completion(
        client=httpx.AsyncClient(transport=httpx.MockTransport(timeout_handler)),
        request=_request(),
        url="https://provider.test/v1/chat/completions",
        headers={},
    )
    connect_response = await post_openai_chat_completion(
        client=httpx.AsyncClient(transport=httpx.MockTransport(connect_handler)),
        request=_request(),
        url="https://provider.test/v1/chat/completions",
        headers={},
    )

    assert timeout_response.normalized_error_category is ErrorCategory.TIMEOUT
    assert (
        connect_response.normalized_error_category is ErrorCategory.PROVIDER_UNAVAILABLE
    )


@pytest.mark.asyncio
async def test_post_openai_chat_completion_rejects_malformed_success_payload() -> None:
    async def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"choices": []})

    response = await post_openai_chat_completion(
        client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
        request=_request(),
        url="https://provider.test/v1/chat/completions",
        headers={},
    )

    assert response.outcome is TestOutcome.FAILURE
    assert (
        response.normalized_error_category is ErrorCategory.MALFORMED_PROVIDER_RESPONSE
    )


def test_provider_adapter_registry_rejects_unknown_provider() -> None:
    registry = ProviderAdapterRegistry({})

    with pytest.raises(ValueError, match="unsupported provider type"):
        registry.get(ProviderType.OPENAI)


@pytest.mark.asyncio
async def test_openai_and_local_adapters_delegate_to_chat_completions() -> None:
    seen_authorization_headers: list[str | None] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url).endswith("/v1/chat/completions")
        seen_authorization_headers.append(request.headers.get("authorization"))
        return httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}]})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    openai_response = await OpenAIAdapter(client).chat_completion(
        AdapterRequest(
            model_id="gpt-test",
            messages=({"role": "user", "content": "health"},),
            timeout_policy=TimeoutPolicy(),
            credential="resolved",
        )
    )
    local_response = await LocalOpenAICompatibleAdapter(
        allowlist=LocalEndpointAllowlist(("http",), ("localhost",), (11434,)),
        client=client,
    ).chat_completion(
        AdapterRequest(
            model_id="local-test",
            messages=({"role": "user", "content": "health"},),
            timeout_policy=TimeoutPolicy(),
            base_url="http://localhost:11434",
        )
    )
    local_credential_response = await LocalOpenAICompatibleAdapter(
        allowlist=LocalEndpointAllowlist(("http",), ("localhost",), (11434,)),
        client=client,
    ).chat_completion(
        AdapterRequest(
            model_id="local-test",
            messages=({"role": "user", "content": "health"},),
            timeout_policy=TimeoutPolicy(),
            base_url="http://localhost:11434",
            credential="local-resolved",
        )
    )

    assert openai_response.outcome is TestOutcome.SUCCESS
    assert local_response.outcome is TestOutcome.SUCCESS
    assert local_credential_response.outcome is TestOutcome.SUCCESS
    assert seen_authorization_headers == [
        "Bearer resolved",
        None,
        "Bearer local-resolved",
    ]
    assert (
        ProviderAdapterRegistry({ProviderType.OPENAI: OpenAIAdapter(client)})
        .get(ProviderType.OPENAI)
        .provider_type
        is ProviderType.OPENAI
    )
