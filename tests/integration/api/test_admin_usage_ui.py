from __future__ import annotations

from urllib.parse import parse_qs, urlparse

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
            follow_redirects=False,
        )
        export = client.post(
            "/admin/usage/exports",
            headers=ACME_HEADERS,
            data={"tenant_id": ACME_TENANT_ID, "model_id": "gpt-test"},
            follow_redirects=False,
        )
        export_id = urlparse(export.headers["location"]).path.rsplit("/", 1)[-1]
        detail = client.get(
            f"/admin/usage/exports/{export_id}?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
            follow_redirects=False,
        )

    assert dashboard.status_code == 303
    assert dashboard.headers["location"] == (
        f"/admin/app/usage?tenant_id={ACME_TENANT_ID}"
    )
    assert export.status_code == 303
    assert export.headers["location"].startswith("/admin/app/usage/exports/")
    assert parse_qs(urlparse(export.headers["location"]).query)["tenant_id"] == [
        ACME_TENANT_ID
    ]
    assert detail.status_code == 303
    assert detail.headers["location"].startswith("/admin/app/usage/exports/")
