from __future__ import annotations

from multi_agent_platform.secrets.base import SecretProvider, SecretValue


class SecretManagerProvider(SecretProvider):
    provider_name = "secret_manager"

    def __init__(
        self, prefix: str, backing_store: dict[str, str] | None = None
    ) -> None:
        self._prefix = prefix
        self._backing_store = backing_store or {}

    async def resolve(self, reference: str) -> SecretValue:
        full_reference = (
            reference
            if reference.startswith(self._prefix)
            else f"{self._prefix}{reference}"
        )
        if full_reference not in self._backing_store:
            raise KeyError(reference)
        return SecretValue(
            reference=full_reference, value=self._backing_store[full_reference]
        )
