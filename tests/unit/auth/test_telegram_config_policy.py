from __future__ import annotations

from multi_agent_platform.auth.local_principals import (
    telegram_config_permission_codes,
)
from multi_agent_platform.auth.policy import SURFACE_POLICIES


def test_telegram_config_surfaces_require_dedicated_permissions() -> None:
    assert SURFACE_POLICIES["GET:/admin/telegram"].required_permissions == (
        "telegram-config:read",
    )
    assert SURFACE_POLICIES[
        "POST:/admin/telegram/api/link-tokens"
    ].required_permissions == ("telegram-config:tokens",)


def test_telegram_config_local_permissions_cover_platform_and_tenant() -> None:
    assert "telegram-config:read" in telegram_config_permission_codes(platform=True)
    assert "telegram-config:write" in telegram_config_permission_codes(platform=False)
