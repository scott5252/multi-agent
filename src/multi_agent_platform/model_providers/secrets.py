from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from multi_agent_platform.model_providers.models import ProviderType
from multi_agent_platform.secrets.base import SecretProvider


class SecretReferenceError(PermissionError):
    def __init__(self, message: str, *, reference: str | None = None) -> None:
        super().__init__(message)
        self.reference = reference


@dataclass(frozen=True, slots=True)
class ResolvedProviderCredential:
    reference: str
    value: str


class ProviderSecretResolver:
    def __init__(self, provider: SecretProvider) -> None:
        self._provider = provider

    async def resolve(self, reference: str) -> ResolvedProviderCredential:
        safe_reference = reference.strip()
        if not safe_reference:
            raise SecretReferenceError("secret reference is required")
        try:
            secret = await self._provider.resolve(safe_reference)
        except Exception as exc:
            raise SecretReferenceError(
                "secret reference could not be resolved",
                reference=safe_reference,
            ) from exc
        if not secret.value:
            raise SecretReferenceError(
                "secret reference resolved to an empty value",
                reference=safe_reference,
            )
        return ResolvedProviderCredential(reference=safe_reference, value=secret.value)

    async def resolve_for_provider(
        self,
        *,
        provider_type: ProviderType,
        credential_secret_reference_ids: Sequence[str],
    ) -> ResolvedProviderCredential | None:
        reference = select_provider_credential_reference(
            credential_secret_reference_ids
        )
        if reference is None:
            if provider_requires_credential(provider_type):
                raise SecretReferenceError(
                    "provider credential reference is required",
                    reference=None,
                )
            return None
        return await self.resolve(reference)


def provider_requires_credential(provider_type: ProviderType) -> bool:
    return provider_type is ProviderType.OPENAI


def select_provider_credential_reference(
    credential_secret_reference_ids: Sequence[str],
) -> str | None:
    for reference in credential_secret_reference_ids:
        safe_reference = reference.strip()
        if safe_reference:
            return safe_reference
    return None
