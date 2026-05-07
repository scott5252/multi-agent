from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from multi_agent_platform.api.main import create_app
from multi_agent_platform.db.base import Base
from multi_agent_platform.db.models import import_models
from multi_agent_platform.db.models.access_control import (
    AuthProviderType,
    PrincipalIdentity,
    RoleCode,
    RoleGrant,
    RoleScopeType,
)


def prepare_auth_database(database_path: Path, tenant_id: UUID) -> None:
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
        connection.execute(text("DELETE FROM alembic_version"))
        connection.execute(
            text(
                "INSERT INTO alembic_version(version_num) "
                "VALUES ('0002_auth_access_control')"
            )
        )
    with Session(engine) as session:
        identity = PrincipalIdentity(
            auth_provider=AuthProviderType.LOCAL_PRINCIPAL,
            external_subject="seed-user",
        )
        session.add(identity)
        session.flush()
        session.add(
            RoleGrant(
                principal_identity_id=identity.principal_identity_id,
                scope_type=RoleScopeType.TENANT,
                tenant_id=tenant_id,
                role_code=RoleCode.TENANT_ADMIN,
            )
        )
        session.commit()


def configure_local_auth(monkeypatch, tmp_path, tenant_id: UUID) -> None:
    database_path = tmp_path / "auth.db"
    prepare_auth_database(database_path, tenant_id)
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{database_path}")
    monkeypatch.setenv("FILESYSTEM_STORAGE_ROOT", str(tmp_path / "artifacts"))
    monkeypatch.setenv("AUTH_MODE", "local_principal")
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
                    "permission_codes": [
                        "tenant:read",
                        "tenant:admin",
                        "admin:role-grants:write",
                    ],
                }
            }
        ),
    )


def test_auth_routes_return_local_principal_context(tmp_path, monkeypatch) -> None:
    tenant_id = uuid4()
    configure_local_auth(monkeypatch, tmp_path, tenant_id)
    app = create_app()

    with TestClient(app) as client:
        me = client.get("/auth/me", headers={"X-Local-Principal": "tenant-admin-acme"})
        tenant = client.get(
            f"/auth/tenant-context/{tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert me.status_code == 200
    assert me.json()["auth_mode"] == "local_principal"
    assert tenant.status_code == 200
    assert tenant.json()["tenant_id"] == str(tenant_id)


def test_local_login_is_non_jinja_and_sanitizes_redirects(
    tmp_path,
    monkeypatch,
) -> None:
    tenant_id = uuid4()
    configure_local_auth(monkeypatch, tmp_path, tenant_id)
    app = create_app()

    with TestClient(app) as client:
        page = client.get("/auth/local-login?redirect_to=https://example.test/admin")
        envelope = client.get("/auth/local-login.json?redirect_to=/admin/app")
        run_envelope = client.get("/auth/local-login.json?redirect_to=/runs")
        invalid = client.post(
            "/auth/local-login",
            data={
                "principal": "tenant-admin-acme",
                "redirect_to": "/admin/app",
                "action_token": "bad-token",
            },
            follow_redirects=False,
        )
        submitted = client.post(
            "/auth/local-login",
            data={
                "principal": "tenant-admin-acme",
                "redirect_to": "https://example.test/admin",
                "action_token": "local-principal-login",
            },
            follow_redirects=False,
        )
        run_submitted = client.post(
            "/auth/local-login",
            data={
                "principal": "tenant-admin-acme",
                "redirect_to": "/runs",
                "action_token": "local-principal-login",
            },
            follow_redirects=False,
        )

    assert page.status_code == 200
    assert page.headers["X-Local-Login-Response"] == "non-jinja"
    assert "{%" not in page.text
    assert 'value="/admin/app"' in page.text
    assert envelope.status_code == 200
    assert {
        principal["catalog_key"] for principal in envelope.json()["principals"]
    } >= {"tenant-admin-acme"}
    assert run_envelope.status_code == 200
    assert run_envelope.json()["redirect_to"] == "/runs"
    assert invalid.status_code == 400
    assert submitted.status_code == 303
    assert submitted.headers["location"] == "/admin/app"
    assert run_submitted.status_code == 303
    assert run_submitted.headers["location"] == "/runs"


def test_tenant_admin_can_list_tenant_role_grants(tmp_path, monkeypatch) -> None:
    tenant_id = uuid4()
    configure_local_auth(monkeypatch, tmp_path, tenant_id)
    app = create_app()

    with TestClient(app) as client:
        response = client.get(
            f"/admin/tenants/{tenant_id}/role-grants",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert response.status_code == 200
    assert isinstance(response.json(), list)
