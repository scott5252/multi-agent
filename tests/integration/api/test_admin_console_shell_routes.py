from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from multi_agent_platform.api.main import create_app
from multi_agent_platform.db.base import Base
from multi_agent_platform.db.models import import_models
from multi_agent_platform.db.models.tenant import Tenant
from tests.fixtures.admin_console import (
    assert_nav_item,
    assert_scope_label,
    assert_shell_landmarks,
)


def _configure_env(monkeypatch, tmp_path: Path, tenant_id) -> None:
    database_path = tmp_path / "admin-console-shell.db"
    import_models()
    engine = create_engine(f"sqlite:///{database_path}")
    Base.metadata.create_all(engine)
    with engine.begin() as connection:
        connection.execute(
            text(
                "CREATE TABLE IF NOT EXISTS alembic_version "
                "(version_num VARCHAR(64) NOT NULL)"
            )
        )
        connection.execute(
            text(
                "INSERT INTO alembic_version(version_num) "
                "VALUES ('0010_admin_console_shell')"
            )
        )
    with Session(engine) as session:
        session.add(Tenant(tenant_id=tenant_id, slug="acme", display_name="Acme"))
        session.commit()
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{database_path}")
    monkeypatch.setenv("FILESYSTEM_STORAGE_ROOT", str(tmp_path / "artifacts"))
    monkeypatch.setenv(
        "LOCAL_PRINCIPAL_CATALOG_JSON",
        json.dumps(
            {
                "tenant-admin-acme": {
                    "catalog_key": "tenant-admin-acme",
                    "display_name": "Tenant Admin",
                    "tenant_id": str(tenant_id),
                    "org_id": "org-acme",
                    "role_codes": ["tenant_user", "tenant_admin"],
                    "permission_codes": ["tenant:read", "tenant:admin"],
                },
                "platform-admin": {
                    "catalog_key": "platform-admin",
                    "display_name": "Platform Admin",
                    "role_codes": ["platform_admin"],
                    "permission_codes": ["tenant:admin", "tenant:read"],
                },
            }
        ),
    )


def test_create_app_mounts_admin_console_and_static_assets(
    tmp_path,
    monkeypatch,
) -> None:
    tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id)
    app = create_app()
    routes = {getattr(route, "path", "") for route in app.routes}

    assert "/admin" in routes
    assert "/admin/static" in routes


def test_admin_landing_renders_scope_navigation_and_tenant_links(
    tmp_path, monkeypatch
) -> None:
    tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id)
    app = create_app()

    with TestClient(app) as client:
        response = client.get(
            f"/admin?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert response.status_code == 200
    assert_shell_landmarks(response.text)
    assert_scope_label(response.text, "Tenant")
    assert_nav_item(response.text, "Workflow Registry")
    assert "tenant_id=" in response.text


def test_platform_admin_landing_offers_active_tenant_scope_dropdown(
    tmp_path, monkeypatch
) -> None:
    tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id)
    app = create_app()

    with TestClient(app) as client:
        response = client.get(
            "/admin",
            headers={"X-Local-Principal": "platform-admin"},
        )

    assert response.status_code == 200
    assert_scope_label(response.text, "Platform")
    assert 'id="admin-scope-select"' in response.text
    assert "Switch scope" in response.text
    assert "Tenant scope Acme" in response.text
    assert f'value="{tenant_id}"' in response.text


def test_scope_selector_audits_and_sanitizes_redirects(tmp_path, monkeypatch) -> None:
    tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id)
    app = create_app()

    with TestClient(app) as client:
        response = client.get(
            (f"/admin/scope?tenant_id={tenant_id}&next=https://example.test/admin"),
            headers={"X-Local-Principal": "platform-admin"},
            follow_redirects=False,
        )
        forbidden = client.get(
            f"/admin/scope?tenant_id={uuid4()}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert response.status_code == 303
    assert response.headers["location"] == f"/admin?tenant_id={tenant_id}"
    assert forbidden.status_code == 403
