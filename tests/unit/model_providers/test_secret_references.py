from __future__ import annotations

import pytest

from multi_agent_platform.model_providers.secrets import (
    ProviderSecretResolver,
    SecretReferenceError,
)
from multi_agent_platform.secrets.base import SecretValue


class FakeSecretProvider:
    provider_name = "fake"

    async def resolve(self, reference: str) -> SecretValue:
        if reference == "missing":
            raise LookupError("missing")
        return SecretValue(reference=reference, value="resolved")


@pytest.mark.asyncio
async def test_secret_resolver_returns_reference_and_value() -> None:
    credential = await ProviderSecretResolver(FakeSecretProvider()).resolve(
        "qa011/openai-placeholder"
    )

    assert credential.reference == "qa011/openai-placeholder"
    assert credential.value == "resolved"


@pytest.mark.asyncio
async def test_secret_resolver_fails_closed_for_missing_ref() -> None:
    with pytest.raises(SecretReferenceError):
        await ProviderSecretResolver(FakeSecretProvider()).resolve("missing")
