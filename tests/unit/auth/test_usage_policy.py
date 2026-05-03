from __future__ import annotations

from multi_agent_platform.auth.policy import SURFACE_POLICIES, resolve_surface


def test_usage_surfaces_are_registered_and_permissioned() -> None:
    expected = {
        "GET:/admin/usage": "render_usage_analytics_ui",
        "GET:/admin/usage/api/summary": "read_usage_summary",
        "GET:/admin/usage/api/events": "read_usage_events",
        "POST:/admin/usage/api/exports": "create_usage_export",
    }

    for surface, action in expected.items():
        assert SURFACE_POLICIES[surface].requested_action == action
        assert SURFACE_POLICIES[surface].required_permissions


def test_usage_surface_resolution_uses_route_templates() -> None:
    surface = resolve_surface("GET", "/admin/usage/exports/{usage_export_request_id}")

    assert surface.requested_action == "render_usage_export_ui"
    assert surface.required_permissions == ("usage:export",)
