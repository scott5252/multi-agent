from __future__ import annotations

import httpx

from multi_agent_platform.model_providers.adapters import post_openai_chat_completion
from multi_agent_platform.model_providers.models import (
    AdapterRequest,
    AdapterResponse,
    ProviderType,
)


class OpenAIAdapter:
    provider_type = ProviderType.OPENAI

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client or httpx.AsyncClient()
        self._owns_client = client is None

    async def chat_completion(self, request: AdapterRequest) -> AdapterResponse:
        base_url = (request.base_url or "https://api.openai.com").rstrip("/")
        headers = {"Authorization": f"Bearer {request.credential or ''}"}
        return await post_openai_chat_completion(
            client=self._client,
            request=request,
            url=f"{base_url}/v1/chat/completions",
            headers=headers,
        )

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()
