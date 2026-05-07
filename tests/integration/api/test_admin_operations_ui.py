from __future__ import annotations

from fastapi.testclient import TestClient

from multi_agent_platform.api.main import create_app
from tests.integration.api.test_admin_operations_api import (
    PLATFORM_HEADERS,
    TENANT_HEADERS,
    _configure_env,
)


def test_operations_ui_renders_dashboard_and_redacted_logs(
    tmp_path, monkeypatch
) -> None:
    _configure_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        page = client.get(
            "/admin/operations?trace_id=trace-ops",
            headers=PLATFORM_HEADERS,
            follow_redirects=False,
        )
        dashboard = client.get(
            "/admin/operations/api/dashboard?trace_id=trace-ops",
            headers=PLATFORM_HEADERS,
        )
        tenant_redirect = client.get(
            "/admin/operations",
            headers=TENANT_HEADERS,
            follow_redirects=False,
        )

    assert page.status_code == 303, page.text
    assert page.headers["location"] == "/admin/app/operations?trace_id=trace-ops"
    assert dashboard.status_code == 200
    assert "Gateway completed safely" in dashboard.text
    assert "must-redact" not in dashboard.text
    assert tenant_redirect.status_code == 303
    assert tenant_redirect.headers["location"] == "/admin/app/operations"
