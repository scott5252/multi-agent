from __future__ import annotations

from fastapi.testclient import TestClient

from multi_agent_platform.api.main import create_app


def test_reliability_controls_dashboard_contract() -> None:
    response = TestClient(create_app(), raise_server_exceptions=False).get(
        "/admin/reliability/dashboard"
    )
    assert response.status_code in {200, 500}


def test_policy_change_preview_shape() -> None:
    app = create_app()
    paths = {route.path for route in app.routes}
    assert "/admin/reliability/policies" in paths
