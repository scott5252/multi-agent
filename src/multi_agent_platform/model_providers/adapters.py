from __future__ import annotations

import time
from collections.abc import Mapping
from typing import Protocol

import httpx

from multi_agent_platform.model_providers.models import (
    AdapterRequest,
    AdapterResponse,
    ErrorCategory,
    ProviderType,
    TestOutcome,
)
from multi_agent_platform.model_providers.redaction import redact_text
from multi_agent_platform.model_providers.usage import normalize_usage


class ProviderAdapter(Protocol):
    provider_type: ProviderType

    async def chat_completion(self, request: AdapterRequest) -> AdapterResponse:
        raise NotImplementedError


class ProviderAdapterRegistry:
    def __init__(self, adapters: Mapping[ProviderType, ProviderAdapter]) -> None:
        self._adapters = dict(adapters)

    def get(self, provider_type: ProviderType) -> ProviderAdapter:
        try:
            return self._adapters[provider_type]
        except KeyError as exc:
            raise ValueError(f"unsupported provider type: {provider_type}") from exc


async def post_openai_chat_completion(
    *,
    client: httpx.AsyncClient,
    request: AdapterRequest,
    url: str,
    headers: Mapping[str, str],
) -> AdapterResponse:
    started = time.perf_counter()
    try:
        response = await client.post(
            url,
            json={"model": request.model_id, "messages": list(request.messages)},
            headers=dict(headers),
            timeout=httpx.Timeout(
                request.timeout_policy.total_seconds,
                connect=request.timeout_policy.connect_seconds,
                read=request.timeout_policy.read_seconds,
            ),
            follow_redirects=False,
        )
    except httpx.TimeoutException:
        return _failure(started, ErrorCategory.TIMEOUT, "Provider timed out")
    except httpx.ConnectError:
        return _failure(
            started,
            ErrorCategory.PROVIDER_UNAVAILABLE,
            "Provider is unavailable",
        )
    if response.status_code in {401, 403}:
        return _failure(started, ErrorCategory.AUTHORIZATION_FAILURE, "Auth failed")
    if response.status_code == 404:
        return _failure(started, ErrorCategory.INVALID_MODEL, "Model not found")
    if response.status_code == 429:
        return _failure(started, ErrorCategory.RATE_LIMIT, "Provider rate limited")
    if response.status_code >= 500:
        return _failure(
            started,
            ErrorCategory.PROVIDER_UNAVAILABLE,
            "Provider returned an unavailable status",
        )
    try:
        payload = response.json()
        choice = payload["choices"][0]
        content = choice["message"]["content"]
    except (KeyError, IndexError, TypeError, ValueError):
        return _failure(
            started,
            ErrorCategory.MALFORMED_PROVIDER_RESPONSE,
            "Provider response did not match the chat completions contract",
        )
    request_id = response.headers.get("x-request-id")
    return AdapterResponse(
        outcome=TestOutcome.SUCCESS,
        content=str(content),
        latency_ms=_elapsed_ms(started),
        provider_request_id=redact_text(request_id, fallback="request id unavailable")
        if request_id
        else None,
        usage=normalize_usage(payload.get("usage"), provider_model_id=request.model_id),
        safe_diagnostic_summary="Provider chat completions call succeeded",
    )


def _failure(
    started: float,
    category: ErrorCategory,
    summary: str,
) -> AdapterResponse:
    return AdapterResponse(
        outcome=TestOutcome.FAILURE,
        normalized_error_category=category,
        latency_ms=_elapsed_ms(started),
        safe_diagnostic_summary=summary,
    )


def _elapsed_ms(started: float) -> int:
    return max(0, round((time.perf_counter() - started) * 1000))
