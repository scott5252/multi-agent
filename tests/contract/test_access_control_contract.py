from __future__ import annotations

from multi_agent_platform.api.main import create_app


def test_access_control_routes_are_exposed_in_openapi() -> None:
    app = create_app()
    schema = app.openapi()

    assert "/auth/me" in schema["paths"]
    assert "/auth/tenant-context/{tenant_id}" in schema["paths"]
    assert "/admin/role-grants" in schema["paths"]
    assert "PrincipalContextResponse" in schema["components"]["schemas"]
