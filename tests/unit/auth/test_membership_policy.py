from __future__ import annotations

from multi_agent_platform.auth.local_principals import (
    membership_admin_permission_codes,
)
from multi_agent_platform.auth.policy import resolve_surface


def test_membership_policy_registers_ui_and_api_surfaces() -> None:
    ui = resolve_surface("GET", "/admin/memberships")
    api = resolve_surface("POST", "/admin/memberships/api/invitations")

    assert ui.requested_action == "render_membership_administration_ui"
    assert ui.required_permissions == ("membership-admin:read",)
    assert api.requested_action == "create_membership_invitation"
    assert api.required_permissions == ("membership-admin:invite",)


def test_local_principal_membership_permissions_cover_platform_and_tenant() -> None:
    assert "membership-admin:grants" in membership_admin_permission_codes(platform=True)
    assert "tenant:admin" in membership_admin_permission_codes(platform=False)
