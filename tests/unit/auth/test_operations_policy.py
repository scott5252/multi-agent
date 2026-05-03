from __future__ import annotations

from multi_agent_platform.auth.local_principals import operations_permission_codes
from multi_agent_platform.auth.policy import SURFACE_POLICIES, resolve_surface


def test_operations_surfaces_are_registered_and_permissioned() -> None:
    expected = {
        "GET:/admin/operations": "render_operations_console_ui",
        "GET:/admin/operations/api/dashboard": "read_operations_dashboard",
        "GET:/admin/operations/api/logs": "query_operations_logs",
        "POST:/admin/operations/api/logs/export": "export_operations_logs",
    }

    for surface_key, action in expected.items():
        assert SURFACE_POLICIES[surface_key].requested_action == action

    assert SURFACE_POLICIES["GET:/admin/operations"].required_permissions == (
        "operations:read",
    )
    assert SURFACE_POLICIES[
        "POST:/admin/operations/api/logs/export"
    ].required_permissions == ("operations:export",)
    assert "operations:read" in operations_permission_codes()
    assert "operations:export" in operations_permission_codes(auditor=True)


def test_operations_surface_resolution_uses_route_templates() -> None:
    surface = resolve_surface("GET", "/admin/operations/api/dashboard")

    assert surface.requested_action == "read_operations_dashboard"
