from __future__ import annotations

from multi_agent_platform.auth.policy import SURFACE_POLICIES, resolve_surface


def test_agent_test_surfaces_are_registered_and_permissioned() -> None:
    expected = {
        "GET:/admin/agent-tests/ui": "render_agent_test_bench_ui",
        "POST:/admin/agent-tests/suites": "create_agent_test_suite",
        "POST:/admin/agent-tests/suites/{suite_id}/runs": "launch_agent_test_run",
        "GET:/admin/agent-tests/runs/{run_id}": "read_agent_test_run",
        "POST:/admin/agent-tests/publish-gates/evaluate": (
            "evaluate_agent_test_publish_gate"
        ),
    }

    for surface, action in expected.items():
        assert SURFACE_POLICIES[surface].requested_action == action
        assert SURFACE_POLICIES[surface].required_permissions


def test_agent_test_surface_resolution_uses_route_templates() -> None:
    surface = resolve_surface("GET", "/admin/agent-tests/ui/runs/{run_id}")

    assert surface.requested_action == "render_agent_test_run_detail_ui"
    assert surface.required_permissions == ("agent-tests:read",)
