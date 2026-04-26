from __future__ import annotations

from pathlib import Path

from multi_agent_platform.api.main import create_app

CONTRACT = Path(
    "specs/008-production-audit-debugging/contracts/"
    "production-audit-debugging.openapi.yaml"
)


def test_openapi_contract_declares_required_admin_routes() -> None:
    text = CONTRACT.read_text()
    for route in (
        "/admin/runs/debug-search",
        "/admin/runs/{workflow_run_id}/timeline",
        "/admin/runs/{workflow_run_id}/replay",
        "/admin/runs/{workflow_run_id}/lineage",
        "/admin/runs/{workflow_run_id}/bundle",
        "/admin/runs/{workflow_run_id}/exports",
    ):
        assert route in text


def test_implemented_routes_align_with_contract() -> None:
    app_paths = {route.path for route in create_app().routes}
    assert "/admin/runs/debug-search" in app_paths
    assert "/admin/runs/{workflow_run_id}/timeline" in app_paths
    assert "/admin/runs/{workflow_run_id}/replay" in app_paths
    assert "/admin/runs/{workflow_run_id}/lineage" in app_paths
    assert "/admin/runs/{workflow_run_id}/bundle" in app_paths
    assert "/admin/runs/{workflow_run_id}/exports" in app_paths
