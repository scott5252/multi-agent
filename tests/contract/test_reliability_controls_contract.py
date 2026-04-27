from __future__ import annotations

from fastapi.testclient import TestClient

from multi_agent_platform.api.main import create_app


def test_reliability_controls_routes_are_registered() -> None:
    app = create_app()
    paths = {route.path for route in app.routes}
    assert "/admin/reliability/dashboard" in paths
    assert "/admin/reliability/policies" in paths
    assert "/admin/reliability/dead-letters" in paths


def test_reliability_dashboard_openapi_contract_is_available() -> None:
    schema = TestClient(create_app()).get("/openapi.json").json()
    assert "/admin/reliability/dashboard" in schema["paths"]
    assert "/admin/reliability/breakers/{breaker_id}/reset" in schema["paths"]
