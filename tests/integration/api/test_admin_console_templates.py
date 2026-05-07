from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from multi_agent_platform.api.main import create_app
from tests.integration.test_admin_react_routes import _configure_env


def test_admin_shell_is_react_host_with_accessible_fallback_landmarks(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, uuid4())
    app = create_app()

    with TestClient(app) as client:
        response = client.get(
            f"/admin/app?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert response.status_code == 200
    assert response.headers["X-React-Admin-Host"] == "non-jinja"
    assert not Path("src/multi_agent_platform/web_admin/templates").exists()
    assert "Skip to content" in response.text
    assert 'id="admin-main-content"' in response.text
    assert 'aria-label="Admin"' in response.text
    assert "{%" not in response.text
