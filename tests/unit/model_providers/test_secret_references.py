from __future__ import annotations

import pytest

from multi_agent_platform.model_providers.models import ProviderType
from multi_agent_platform.model_providers.secrets import (
    ProviderSecretResolver,
    SecretReferenceError,
    provider_requires_credential,
    select_provider_credential_reference,
)
from multi_agent_platform.secrets.base import SecretValue


class FakeSecretProvider:
    provider_name = "fake"

    async def resolve(self, reference: str) -> SecretValue:
        if reference == "missing":
            raise LookupError("missing")
        if reference == "empty":
            return SecretValue(reference=reference, value="")
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


def test_provider_credential_reference_selection_uses_first_non_empty() -> None:
    assert (
        select_provider_credential_reference(
            ("  ", "qa025/openai-primary", "qa025/openai-secondary")
        )
        == "qa025/openai-primary"
    )


def test_openai_requires_credentials_but_local_provider_can_be_no_auth() -> None:
    assert provider_requires_credential(ProviderType.OPENAI) is True
    assert provider_requires_credential(ProviderType.LOCAL_OPENAI_COMPATIBLE) is False


@pytest.mark.asyncio
async def test_secret_resolver_resolves_selected_provider_reference() -> None:
    credential = await ProviderSecretResolver(
        FakeSecretProvider()
    ).resolve_for_provider(
        provider_type=ProviderType.OPENAI,
        credential_secret_reference_ids=("qa025/openai-primary",),
    )

    assert credential is not None
    assert credential.reference == "qa025/openai-primary"
    assert credential.value == "resolved"


@pytest.mark.asyncio
async def test_secret_resolver_allows_local_no_auth_without_reference() -> None:
    credential = await ProviderSecretResolver(
        FakeSecretProvider()
    ).resolve_for_provider(
        provider_type=ProviderType.LOCAL_OPENAI_COMPATIBLE,
        credential_secret_reference_ids=(),
    )

    assert credential is None


@pytest.mark.asyncio
async def test_secret_resolver_requires_openai_reference() -> None:
    with pytest.raises(SecretReferenceError) as exc_info:
        await ProviderSecretResolver(FakeSecretProvider()).resolve_for_provider(
            provider_type=ProviderType.OPENAI,
            credential_secret_reference_ids=(),
        )

    assert exc_info.value.reference is None


@pytest.mark.asyncio
async def test_secret_resolver_rejects_empty_secret_values() -> None:
    with pytest.raises(SecretReferenceError) as exc_info:
        await ProviderSecretResolver(FakeSecretProvider()).resolve_for_provider(
            provider_type=ProviderType.OPENAI,
            credential_secret_reference_ids=("empty",),
        )

    assert exc_info.value.reference == "empty"
