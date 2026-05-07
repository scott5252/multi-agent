from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from multi_agent_platform.api.main import create_app
from tests.integration.test_admin_react_routes import _configure_env


def test_react_admin_host_routes_are_non_jinja(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, uuid4())
    app = create_app()

    with TestClient(app) as client:
        root = client.get(
            f"/admin/app?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        migration = client.get(
            f"/admin/app/migration?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        saved_filters = client.get(
            f"/admin/app/saved-filters/workflows?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        old_admin = client.get(
            f"/admin?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            follow_redirects=False,
        )

    assert root.status_code == 200
    assert root.headers["X-React-Admin-Host"] == "non-jinja"
    assert "React Admin" in root.text
    assert "{%" not in root.text
    assert migration.status_code == 200
    assert migration.headers["X-React-Admin-Host"] == "non-jinja"
    assert saved_filters.status_code == 200
    assert saved_filters.headers["X-React-Admin-Host"] == "non-jinja"
    assert old_admin.status_code == 303
    assert old_admin.headers["location"] == f"/admin/app?tenant_id={tenant_id}"
