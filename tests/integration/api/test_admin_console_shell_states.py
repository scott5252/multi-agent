from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from multi_agent_platform.api.main import create_app
from tests.integration.api.test_admin_console_shell_routes import _configure_env


def test_empty_and_unavailable_states_render_without_sensitive_details(
    tmp_path, monkeypatch
) -> None:
    tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id)
    app = create_app()

    with TestClient(app) as client:
        response = client.get(
            f"/admin/runs?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            follow_redirects=False,
        )

    assert response.status_code == 303
    assert response.headers["location"] == (
        f"/admin/app/operations?tenant_id={tenant_id}&panel=runs"
    )
    assert "traceback" not in response.text.lower()
