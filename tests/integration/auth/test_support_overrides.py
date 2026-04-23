from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

from multi_agent_platform.api.main import create_app
from multi_agent_platform.db.base import Base
from multi_agent_platform.db.models import import_models


def prepare_database(database_path: Path) -> None:
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


def test_platform_admin_support_override_requires_second_approver(
    tmp_path, monkeypatch
) -> None:
    database_path = tmp_path / "support-overrides.db"
    tenant_id = uuid4()
    prepare_database(database_path)
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{database_path}")
    monkeypatch.setenv("FILESYSTEM_STORAGE_ROOT", str(tmp_path / "artifacts"))
    monkeypatch.setenv(
        "LOCAL_PRINCIPAL_CATALOG_JSON",
        json.dumps(
            {
                "platform-admin-a": {
                    "catalog_key": "platform-admin-a",
                    "display_name": "Platform Admin A",
                    "role_codes": ["platform_admin"],
                    "permission_codes": [
                        "tenant:admin",
                        "admin:role-grants:write",
                        "admin:support-overrides:write",
                        "admin:support-overrides:approve",
                    ],
                },
                "platform-admin-b": {
                    "catalog_key": "platform-admin-b",
                    "display_name": "Platform Admin B",
                    "role_codes": ["platform_admin"],
                    "permission_codes": [
                        "tenant:admin",
                        "admin:role-grants:write",
                        "admin:support-overrides:write",
                        "admin:support-overrides:approve",
                    ],
                },
            }
        ),
    )
    app = create_app()

    with TestClient(app) as client:
        created = client.post(
            "/admin/support-overrides",
            headers={"X-Local-Principal": "platform-admin-a"},
            json={
                "tenant_id": str(tenant_id),
                "justification": "Investigate tenant issue",
                "idempotency_key": "override-1",
            },
        )
        support_override_request_id = created.json()["support_override_request_id"]
        same_user = client.post(
            f"/admin/support-overrides/{support_override_request_id}/approve",
            headers={"X-Local-Principal": "platform-admin-a"},
            json={"expires_in_hours": 1},
        )
        approved = client.post(
            f"/admin/support-overrides/{support_override_request_id}/approve",
            headers={"X-Local-Principal": "platform-admin-b"},
            json={"expires_in_hours": 1},
        )
        missing = client.post(
            f"/admin/support-overrides/{uuid4()}/approve",
            headers={"X-Local-Principal": "platform-admin-b"},
            json={"expires_in_hours": 1},
        )
        tenant_access = client.get(
            f"/admin/tenants/{tenant_id}/role-grants",
            headers={"X-Local-Principal": "platform-admin-a"},
        )

    assert created.status_code == 201
    assert same_user.status_code == 403
    assert approved.status_code == 200
    assert missing.status_code == 404
    assert tenant_access.status_code == 200


def test_platform_admin_can_upsert_role_grant(tmp_path, monkeypatch) -> None:
    database_path = tmp_path / "role-grants.db"
    prepare_database(database_path)
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{database_path}")
    monkeypatch.setenv("FILESYSTEM_STORAGE_ROOT", str(tmp_path / "artifacts"))
    monkeypatch.setenv(
        "LOCAL_PRINCIPAL_CATALOG_JSON",
        json.dumps(
            {
                "platform-admin-a": {
                    "catalog_key": "platform-admin-a",
                    "display_name": "Platform Admin A",
                    "role_codes": ["platform_admin"],
                    "permission_codes": ["admin:role-grants:write"],
                }
            }
        ),
    )
    app = create_app()

    with TestClient(app) as client:
        response = client.post(
            "/admin/role-grants",
            headers={"X-Local-Principal": "platform-admin-a"},
            json={
                "principal_identity_id": str(uuid4()),
                "scope_type": "platform",
                "role_code": "platform_admin",
            },
        )

    assert response.status_code == 201
