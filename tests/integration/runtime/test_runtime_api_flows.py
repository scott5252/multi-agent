from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

from multi_agent_platform.api.main import create_app
from multi_agent_platform.db.base import Base
from multi_agent_platform.db.models import import_models

ACME_TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")
GLOBEX_TENANT_ID = UUID("22222222-2222-2222-2222-222222222222")


def configure_runtime_auth(monkeypatch, tmp_path: Path) -> None:
    database_path = tmp_path / "runtime-api.db"
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
                "VALUES ('0004_durable_runtime')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO tenants (tenant_id, slug, display_name, status, "
                "created_at, updated_at) VALUES "
                "(:acme_id, 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, "
                "CURRENT_TIMESTAMP), "
                "(:globex_id, 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, "
                "CURRENT_TIMESTAMP)"
            ),
            {"acme_id": str(ACME_TENANT_ID), "globex_id": str(GLOBEX_TENANT_ID)},
        )
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
                    "tenant_id": str(ACME_TENANT_ID),
                    "org_id": "org-acme",
                    "role_codes": ["tenant_user", "tenant_admin"],
                    "permission_codes": ["tenant:read", "tenant:admin"],
                },
                "tenant-admin-globex": {
                    "catalog_key": "tenant-admin-globex",
                    "display_name": "Globex Tenant Admin",
                    "tenant_id": str(GLOBEX_TENANT_ID),
                    "org_id": "org-globex",
                    "role_codes": ["tenant_user", "tenant_admin"],
                    "permission_codes": ["tenant:read", "tenant:admin"],
                },
            }
        ),
    )


def test_runtime_run_start_inspect_cancel_flow(tmp_path, monkeypatch) -> None:
    configure_runtime_auth(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        start = client.post(
            "/runtime/runs",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "published_workflow_version_id": str(uuid4()),
                "idempotency_key": "demo-run-001",
                "input": {"prompt": "hello"},
            },
        )
        assert start.status_code == 202
        workflow_run_id = start.json()["workflow_run_id"]

        inspect = client.get(
            f"/runtime/runs/{workflow_run_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        assert inspect.status_code == 200
        assert inspect.json()["status"] == "runnable"

        cross_tenant = client.get(
            f"/runtime/runs/{workflow_run_id}",
            headers={"X-Local-Principal": "tenant-admin-globex"},
        )
        assert cross_tenant.status_code == 404

        cancel = client.post(
            f"/runtime/runs/{workflow_run_id}/cancel",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={"reason": "operator requested"},
        )
        assert cancel.status_code == 202
        assert cancel.json()["status"] == "cancelled"
