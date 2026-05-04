from __future__ import annotations

from multi_agent_platform.auth.local_principals import (
    briefing_preferences_permission_codes,
)
from multi_agent_platform.auth.policy import SURFACE_POLICIES


def test_briefing_preferences_surfaces_require_dedicated_permissions() -> None:
    assert SURFACE_POLICIES["GET:/admin/briefing-preferences"].required_permissions == (
        "briefing-preferences:read",
    )
    assert SURFACE_POLICIES[
        "POST:/admin/briefing-preferences/api/resolve"
    ].required_permissions == ("briefing-preferences:resolve",)


def test_local_principal_permissions_cover_platform_and_tenant() -> None:
    assert "briefing-preferences:read" in briefing_preferences_permission_codes(
        platform=True
    )
    assert "briefing-preferences:write" in briefing_preferences_permission_codes(
        platform=False
    )
