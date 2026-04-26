from __future__ import annotations

from multi_agent_platform.api.main import create_app


def test_admin_run_inspection_api_routes_are_registered() -> None:
    paths = {route.path for route in create_app().routes}
    assert "/admin/runs/debug-search" in paths
    assert "/admin/runs/{workflow_run_id}/timeline" in paths
    assert "/admin/runs/{workflow_run_id}/replay" in paths
    assert "/admin/runs/{workflow_run_id}/lineage" in paths
    assert "/admin/runs/{workflow_run_id}/exports" in paths
