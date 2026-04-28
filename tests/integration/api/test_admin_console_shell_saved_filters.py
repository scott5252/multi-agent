from __future__ import annotations

from sqlite3 import connect
from uuid import uuid4

from fastapi.testclient import TestClient

from multi_agent_platform.api.main import create_app
from tests.integration.api.test_admin_console_shell_routes import _configure_env


def test_saved_filter_save_restore_delete_is_scope_bound(tmp_path, monkeypatch) -> None:
    tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id)
    app = create_app()

    with TestClient(app) as client:
        save = client.post(
            f"/admin/filters/workflows?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            data={
                "filter_key": "workflow-list",
                "display_name": "Drafts",
                "criteria": '{"status": "draft"}',
                "return_to": "/admin/workflows/ui",
            },
            follow_redirects=False,
        )
        listed = client.get(
            f"/admin/filters/workflows?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        invalid = client.post(
            f"/admin/filters/workflows?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            data={
                "filter_key": "workflow-list",
                "display_name": "Unsafe",
                "criteria": '{"status": "secret token"}',
            },
            follow_redirects=False,
        )
        unsupported = client.get(
            f"/admin/filters/unknown?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

        with connect(tmp_path / "admin-console-shell.db") as db:
            filter_id = db.execute(
                "SELECT admin_saved_filter_id FROM admin_saved_filters"
            ).fetchone()[0]

        restored = client.get(
            f"/admin/filters/workflows/{filter_id}/restore?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            follow_redirects=False,
        )
        deleted = client.post(
            f"/admin/filters/workflows/{filter_id}?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            data={"return_to": "/admin/filters/workflows"},
            follow_redirects=False,
        )
        after_delete = client.get(
            f"/admin/filters/workflows?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert save.status_code == 303
    assert listed.status_code == 200
    assert "Drafts" in listed.text
    assert "tenant_id=" in listed.text
    assert invalid.status_code == 400
    assert unsupported.status_code == 404
    assert restored.status_code == 303
    assert "status=draft" in restored.headers["location"]
    assert deleted.status_code == 303
    assert after_delete.status_code == 200
    assert "Drafts" not in after_delete.text
