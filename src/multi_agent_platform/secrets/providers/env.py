from __future__ import annotations

import os

from multi_agent_platform.secrets.base import SecretProvider, SecretValue


class EnvSecretProvider(SecretProvider):
    provider_name = "env"

    def __init__(self, prefix: str) -> None:
        self._prefix = prefix

    def _env_name(self, reference: str) -> str:
        token = reference.upper().replace("/", "_").replace("-", "_")
        return f"{self._prefix}{token}"

    async def resolve(self, reference: str) -> SecretValue:
        env_name = self._env_name(reference)
        if env_name not in os.environ:
            raise KeyError(reference)
        return SecretValue(reference=reference, value=os.environ[env_name])
