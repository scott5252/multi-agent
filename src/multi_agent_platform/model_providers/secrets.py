from __future__ import annotations

from dataclasses import dataclass

from multi_agent_platform.secrets.base import SecretProvider


class SecretReferenceError(PermissionError):
    pass


@dataclass(frozen=True, slots=True)
class ResolvedProviderCredential:
    reference: str
    value: str


class ProviderSecretResolver:
    def __init__(self, provider: SecretProvider) -> None:
        self._provider = provider

    async def resolve(self, reference: str) -> ResolvedProviderCredential:
        if not reference.strip():
            raise SecretReferenceError("secret reference is required")
        try:
            secret = await self._provider.resolve(reference)
        except Exception as exc:
            raise SecretReferenceError(
                "secret reference could not be resolved"
            ) from exc
        if not secret.value:
            raise SecretReferenceError("secret reference resolved to an empty value")
        return ResolvedProviderCredential(reference=reference, value=secret.value)
