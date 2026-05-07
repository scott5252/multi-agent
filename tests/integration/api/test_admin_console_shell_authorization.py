from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from multi_agent_platform.api.main import create_app
from tests.integration.api.test_admin_console_shell_routes import _configure_env


def test_denied_shell_access_fails_closed(tmp_path, monkeypatch) -> None:
    tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id)
    app = create_app()

    with TestClient(app) as client:
        missing = client.get("/admin")
        forged = client.get(
            f"/admin?tenant_id={uuid4()}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert missing.status_code == 401
    assert forged.status_code == 403
    assert "secret" not in forged.text.lower()


def test_direct_destination_uses_shell_frame_when_authorized(
    tmp_path, monkeypatch
) -> None:
    tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id)
    app = create_app()

    with TestClient(app) as client:
        response = client.get(
            f"/admin/reliability/ui/breakers?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            follow_redirects=False,
        )

    assert response.status_code == 303
    assert response.headers["location"] == (
        f"/admin/app/operations?tenant_id={tenant_id}&panel=breakers"
    )


def test_reliability_dashboard_and_dead_letter_views_share_shell(
    tmp_path, monkeypatch
) -> None:
    tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id)
    app = create_app()

    with TestClient(app) as client:
        dashboard = client.get(
            f"/admin/reliability/ui/?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            follow_redirects=False,
        )
        dead_letters = client.get(
            f"/admin/reliability/ui/dead-letters?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            follow_redirects=False,
        )

    assert dashboard.status_code == 303
    assert dashboard.headers["location"] == (
        f"/admin/app/operations?tenant_id={tenant_id}&panel=reliability"
    )
    assert dead_letters.status_code == 303
    assert dead_letters.headers["location"] == (
        f"/admin/app/operations?tenant_id={tenant_id}&panel=dead-letters"
    )
