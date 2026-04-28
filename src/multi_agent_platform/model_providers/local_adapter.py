from __future__ import annotations

import httpx

from multi_agent_platform.model_providers.adapters import post_openai_chat_completion
from multi_agent_platform.model_providers.allowlist import (
    LocalEndpointAllowlist,
    validate_local_endpoint,
)
from multi_agent_platform.model_providers.models import (
    AdapterRequest,
    AdapterResponse,
    ErrorCategory,
    ProviderType,
    TestOutcome,
)


class LocalOpenAICompatibleAdapter:
    provider_type = ProviderType.LOCAL_OPENAI_COMPATIBLE

    def __init__(
        self,
        *,
        allowlist: LocalEndpointAllowlist,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._allowlist = allowlist
        self._client = client or httpx.AsyncClient()

    async def chat_completion(self, request: AdapterRequest) -> AdapterResponse:
        if request.base_url is None:
            return AdapterResponse(
                outcome=TestOutcome.FAILURE,
                normalized_error_category=ErrorCategory.POLICY_OR_VISIBILITY_DENIAL,
                safe_diagnostic_summary="Local provider base URL is required",
            )
        try:
            base_url = validate_local_endpoint(request.base_url, self._allowlist)
        except ValueError:
            return AdapterResponse(
                outcome=TestOutcome.FAILURE,
                normalized_error_category=ErrorCategory.POLICY_OR_VISIBILITY_DENIAL,
                safe_diagnostic_summary="Local provider endpoint is not allowlisted",
            )
        headers = {}
        if request.credential:
            headers["Authorization"] = "Bearer [resolved]"
        return await post_openai_chat_completion(
            client=self._client,
            request=request,
            url=f"{base_url}/v1/chat/completions",
            headers=headers,
        )
