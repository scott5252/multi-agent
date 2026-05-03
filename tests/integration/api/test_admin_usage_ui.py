from __future__ import annotations

from fastapi.testclient import TestClient

from multi_agent_platform.api.main import create_app
from tests.integration.api.test_admin_usage_api import (
    ACME_HEADERS,
    ACME_TENANT_ID,
    _configure_env,
)


def test_usage_ui_renders_dashboard_and_export(tmp_path, monkeypatch) -> None:
    _configure_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        dashboard = client.get(
            f"/admin/usage?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
        )
        export = client.post(
            "/admin/usage/exports",
            headers=ACME_HEADERS,
            data={"tenant_id": ACME_TENANT_ID, "model_id": "gpt-test"},
            follow_redirects=False,
        )
        detail = client.get(export.headers["location"], headers=ACME_HEADERS)

    assert dashboard.status_code == 200
    assert "Usage Analytics" in dashboard.text
    assert "gpt-test" in dashboard.text
    assert "Raw prompts" in dashboard.text
    assert export.status_code == 303
    assert detail.status_code == 200
    assert "Usage Export" in detail.text
