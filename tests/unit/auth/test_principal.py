from __future__ import annotations

from multi_agent_platform.auth.principal import Principal


def test_principal_admin_detection() -> None:
    assert Principal(roles=("admin",)).is_admin is True
    assert Principal(roles=("user",)).is_admin is False
