from __future__ import annotations

import pytest

from multi_agent_platform.secrets.providers.env import EnvSecretProvider
from multi_agent_platform.secrets.providers.static import StaticSecretProvider


async def test_static_secret_provider_resolves_value() -> None:
    provider = StaticSecretProvider({"example/api-key": "value"})
    resolved = await provider.resolve("example/api-key")
    assert resolved.value == "value"


async def test_env_secret_provider_uses_prefix(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MAP_SECRET_EXAMPLE_API_KEY", "from-env")
    provider = EnvSecretProvider("MAP_SECRET_")
    resolved = await provider.resolve("example/api-key")
    assert resolved.value == "from-env"
