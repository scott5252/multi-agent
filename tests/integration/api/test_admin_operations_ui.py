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
            "/admin/operations?trace_id=trace-ops", headers=PLATFORM_HEADERS
        )
        denied = client.get("/admin/operations", headers=TENANT_HEADERS)

    assert page.status_code == 200, page.text
    assert "Operations Console" in page.text
    assert "System Health" in page.text
    assert "Redacted Operational Logs" in page.text
    assert "Gateway completed safely" in page.text
    assert "must-redact" not in page.text
    assert denied.status_code == 403
