from __future__ import annotations

from multi_agent_platform.secrets.providers.secret_manager import SecretManagerProvider


async def test_secret_manager_provider_applies_prefix() -> None:
    provider = SecretManagerProvider(
        "secret-manager/", {"secret-manager/example": "value"}
    )
    resolved = await provider.resolve("example")
    assert resolved.reference == "secret-manager/example"
    assert resolved.value == "value"
