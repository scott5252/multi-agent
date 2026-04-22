from __future__ import annotations

from multi_agent_platform.secrets.base import SecretProvider, SecretValue


class StaticSecretProvider(SecretProvider):
    provider_name = "static"

    def __init__(self, secrets: dict[str, str]) -> None:
        self._secrets = secrets

    async def resolve(self, reference: str) -> SecretValue:
        if reference not in self._secrets:
            raise KeyError(reference)
        return SecretValue(reference=reference, value=self._secrets[reference])
