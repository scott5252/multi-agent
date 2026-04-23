from __future__ import annotations

from multi_agent_platform.auth.principal import Principal


def test_principal_admin_detection() -> None:
    assert Principal(role_codes=("platform_admin",)).is_admin is True
    assert Principal(role_codes=("tenant_user",)).is_admin is False
