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
    database_path = tmp_path / "workflow-ui.db"
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
                },
                "platform-admin": {
                    "catalog_key": "platform-admin",
                    "display_name": "Platform Admin",
                    "role_codes": ["platform_admin"],
                    "permission_codes": ["tenant:admin"],
                },
            }
        ),
    )


def sample_document() -> dict[str, object]:
    return {
        "workflow_key": "ui-flow",
        "display_name": "UI Flow",
        "description": "UI example workflow.",
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


def test_legacy_workflow_get_routes_redirect_to_react(tmp_path, monkeypatch) -> None:
    tenant_id = uuid4()
    configure_env(monkeypatch, tmp_path, tenant_id)
    draft_id = uuid4()
    version_id = uuid4()
    app = create_app()

    with TestClient(app) as client:
        requests = {
            "/admin/workflows/ui?scope_filter=tenant&status=draft&q=UI": (
                "/admin/app/workflows?scope_filter=tenant&status=draft&q=UI"
            ),
            "/admin/workflows/new": "/admin/app/workflows/new",
            f"/admin/workflows/drafts/{draft_id}/editor?conflict=stale-save": (
                f"/admin/app/workflows/drafts/{draft_id}?conflict=stale-save"
            ),
            f"/admin/workflows/drafts/{draft_id}/revisions/ui": (
                f"/admin/app/workflows/drafts/{draft_id}/revisions"
            ),
            f"/admin/workflows/drafts/{draft_id}/publish-gate/ui": (
                f"/admin/app/workflows/drafts/{draft_id}/publish-gate"
            ),
            f"/admin/workflows/versions/{version_id}/detail": (
                f"/admin/app/workflows/versions/{version_id}"
            ),
        }
        responses = {
            path: client.get(
                path,
                headers={"X-Local-Principal": "tenant-admin-acme"},
                follow_redirects=False,
            )
            for path in requests
        }

    for path, response in responses.items():
        assert response.status_code == 303
        assert response.headers["location"] == requests[path]
        assert "workflows/" not in response.text


def test_create_form_posts_redirect_to_react_draft(tmp_path, monkeypatch) -> None:
    tenant_id = uuid4()
    configure_env(monkeypatch, tmp_path, tenant_id)
    app = create_app()

    with TestClient(app) as client:
        created = client.post(
            "/admin/workflows/new",
            headers={"X-Local-Principal": "platform-admin"},
            data={
                "starter_template": "minimal_ready",
                "scope_type": "platform",
                "workflow_kind": "main_workflow",
                "slug": "ui-form-platform",
                "display_name": "UI Form Platform",
                "description": "Created from the browser form.",
            },
            follow_redirects=False,
        )
        react_host = client.get(
            created.headers["location"],
            headers={"X-Local-Principal": "platform-admin"},
        )

    assert created.status_code == 303
    assert created.headers["location"].startswith("/admin/app/workflows/drafts/")
    assert react_host.status_code == 200
    assert react_host.headers["X-React-Admin-Host"] == "non-jinja"


def test_legacy_workflow_post_routes_redirect_without_jinja(
    tmp_path, monkeypatch
) -> None:
    tenant_id = uuid4()
    configure_env(monkeypatch, tmp_path, tenant_id)
    app = create_app()

    with TestClient(app) as client:
        created = client.post(
            "/admin/workflows",
            headers={"X-Local-Principal": "platform-admin"},
            json={
                "scope_type": "platform",
                "workflow_kind": "main_workflow",
                "slug": "ui-posts",
                "display_name": "UI Posts",
                "document": {
                    **sample_document(),
                    "workflow_key": "ui-posts",
                    "display_name": "UI Posts",
                },
            },
        )
        draft_id = created.json()["workflow_draft_id"]
        save = client.post(
            f"/admin/workflows/drafts/{draft_id}/save-ui",
            headers={"X-Local-Principal": "platform-admin"},
            data={
                "base_revision_number": 1,
                "description": "Updated from compatibility form.",
                "change_summary": "Compatibility save",
            },
            follow_redirects=False,
        )
        validate = client.post(
            f"/admin/workflows/drafts/{draft_id}/validate/ui",
            headers={"X-Local-Principal": "platform-admin"},
            follow_redirects=False,
        )

    assert save.status_code == 303
    assert save.headers["location"] == f"/admin/app/workflows/drafts/{draft_id}"
    assert validate.status_code == 303
    assert validate.headers["location"] == f"/admin/app/workflows/drafts/{draft_id}"
