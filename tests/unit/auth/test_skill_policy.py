from __future__ import annotations

from multi_agent_platform.auth.local_principals import skill_registry_permission_codes
from multi_agent_platform.auth.policy import SURFACE_POLICIES


def test_skill_registry_surface_policies_are_registered() -> None:
    assert "POST:/admin/skill-registry/packages" in SURFACE_POLICIES
    assert "POST:/admin/skill-registry/installations" in SURFACE_POLICIES


def test_local_principal_skill_registry_grants_include_install_permission() -> None:
    assert "skill-registry:install" in skill_registry_permission_codes(platform=False)
