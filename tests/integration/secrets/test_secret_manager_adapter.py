from __future__ import annotations

from multi_agent_platform.secrets.providers.secret_manager import SecretManagerProvider


async def test_secret_manager_adapter_resolves_backing_store() -> None:
    provider = SecretManagerProvider(
        "secret-manager/", {"secret-manager/demo": "value"}
    )
    secret = await provider.resolve("demo")
    assert secret.value == "value"
