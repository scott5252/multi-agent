from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

from multi_agent_platform.api.main import create_app
from multi_agent_platform.db.base import Base
from multi_agent_platform.db.models import import_models


def prepare_ready_database(database_path: Path) -> None:
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


def test_operational_endpoints_return_expected_payloads(tmp_path, monkeypatch) -> None:
    database_path = tmp_path / "api.db"
    tenant_id = uuid4()
    prepare_ready_database(database_path)
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
                }
            }
        ),
    )
    app = create_app()
    with TestClient(app) as client:
        live = client.get("/health/live")
        ready = client.get("/health/ready")
        version = client.get("/version")
        dependencies = client.get("/dependencies")
    assert live.status_code == 200
    assert ready.status_code == 200
    assert version.json()["commit_sha"] == "dev"
    assert dependencies.json()["status"] == "ready"
