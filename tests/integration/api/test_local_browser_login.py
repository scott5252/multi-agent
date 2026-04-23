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


def prepare_database(database_path: Path, tenant_id) -> None:
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
                "VALUES ('0003_workflow_registry')"
            )
        )
    with Session(engine) as session:
        session.add(Tenant(tenant_id=tenant_id, slug="acme", display_name="Acme"))
        session.commit()


def configure_env(monkeypatch, tmp_path, tenant_id) -> None:
    database_path = tmp_path / "browser-login.db"
    prepare_database(database_path, tenant_id)
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


def sample_document() -> dict[str, object]:
    return {
        "workflow_key": "browser-ui-flow",
        "display_name": "Browser UI Flow",
        "description": "Browser login workflow example.",
        "workflow_kind": "main_workflow",
        "entry_node_key": "triage-node",
        "roles": [
            {
                "role_key": "triage-role",
                "display_name": "Triage Role",
                "purpose": "Assess",
                "input_contract_key": "inbound",
                "output_contract_key": "result",
                "skill_bindings": [
                    {
                        "binding_key": "triage-binding",
                        "skill_slug": "triage-agent",
                        "skill_version": "2026.04.1",
                        "purpose": "Assess",
                    }
                ],
            }
        ],
        "contracts": [
            {"contract_key": "inbound", "json_schema": {"type": "object"}},
            {"contract_key": "result", "json_schema": {"type": "object"}},
        ],
        "nodes": [
            {
                "node_key": "triage-node",
                "node_type": "role",
                "display_name": "Triage",
                "role_key": "triage-role",
            }
        ],
        "edges": [],
        "join_policies": [],
        "approval_gates": [],
        "subworkflow_refs": [],
    }


def test_local_browser_login_sets_cookie_and_unlocks_ui(
    tmp_path, monkeypatch
) -> None:
    tenant_id = uuid4()
    configure_env(monkeypatch, tmp_path, tenant_id)
    app = create_app()
    with TestClient(app) as client:
        login_page = client.get("/auth/local-login?redirect_to=/admin/workflows/ui")
        login_submit = client.post(
            "/auth/local-login",
            data={
                "principal": "tenant-admin-acme",
                "redirect_to": "/auth/me",
            },
            follow_redirects=False,
        )
        auth_me = client.get("/auth/me")
        created = client.post(
            "/admin/workflows",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "scope_type": "tenant",
                "workflow_kind": "main_workflow",
                "slug": "browser-ui-flow",
                "display_name": "Browser UI Flow",
                "document": sample_document(),
            },
        )
        ui = client.get("/admin/workflows/ui")

    assert login_page.status_code == 200
    assert "Choose a local principal" in login_page.text
    assert login_submit.status_code == 303
    assert "map_local_principal" in login_submit.headers["set-cookie"]
    assert auth_me.status_code == 200
    assert auth_me.json()["principal_id"] == "tenant-admin-acme"
    assert created.status_code == 201
    assert ui.status_code == 200
    assert "Workflow Registry" in ui.text
