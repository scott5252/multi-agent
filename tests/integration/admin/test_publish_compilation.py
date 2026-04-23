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
    database_path = tmp_path / "workflow-publish.db"
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


def sample_document(name: str) -> dict[str, object]:
    return {
        "workflow_key": name,
        "display_name": name.replace("-", " ").title(),
        "description": "Publish compilation example workflow.",
        "workflow_kind": "subworkflow",
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


def test_publish_creates_artifact_version_detail_and_successor_flow(
    tmp_path, monkeypatch
) -> None:
    tenant_id = uuid4()
    configure_env(monkeypatch, tmp_path, tenant_id)
    app = create_app()
    artifact_dir = tmp_path / "artifacts"
    with TestClient(app) as client:
        created = client.post(
            "/admin/workflows",
            headers={"X-Local-Principal": "platform-admin"},
            json={
                "scope_type": "platform",
                "workflow_kind": "subworkflow",
                "slug": "document-extraction",
                "display_name": "Document Extraction",
                "document": sample_document("document-extraction"),
            },
        )
        draft_id = created.json()["workflow_draft_id"]
        validated = client.post(
            f"/admin/workflows/drafts/{draft_id}/validate",
            headers={"X-Local-Principal": "platform-admin"},
        )
        published = client.post(
            f"/admin/workflows/drafts/{draft_id}/publish",
            headers={"X-Local-Principal": "platform-admin"},
            json={
                "validation_result_id": validated.json()["validation_result_id"],
            },
        )
        version_id = published.json()["workflow_version_bundle_id"]
        detail = client.get(
            f"/admin/workflows/versions/{version_id}",
            headers={"X-Local-Principal": "platform-admin"},
        )
        grant = client.post(
            f"/admin/workflows/versions/{version_id}/sharing-grants",
            headers={"X-Local-Principal": "platform-admin"},
            json={"grantee_tenant_id": str(tenant_id)},
        )
        successor = client.post(
            "/admin/workflows",
            headers={"X-Local-Principal": "platform-admin"},
            json={
                "scope_type": "platform",
                "workflow_kind": "subworkflow",
                "slug": "document-extraction",
                "display_name": "Document Extraction",
                "created_from_version_id": version_id,
                "document": sample_document("document-extraction"),
            },
        )
        tenant_listed = client.get(
            "/admin/workflows?status=published",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert validated.status_code == 200
    assert published.status_code == 201
    assert published.json()["display_version"] == "v1"
    assert detail.status_code == 200
    assert detail.json()["compiled_bundle_digest"]
    assert grant.status_code == 201
    assert successor.status_code == 201
    assert successor.json()["created_from_version_id"] == version_id
    assert any(
        item["workflow_version_bundle_id"] == version_id
        for item in tenant_listed.json()["items"]
    )
    assert any(path.suffix == ".json" for path in artifact_dir.rglob("*.json"))


def test_publish_returns_error_when_artifact_write_fails(tmp_path, monkeypatch) -> None:
    tenant_id = uuid4()
    configure_env(monkeypatch, tmp_path, tenant_id)
    app = create_app()

    async def broken_put(
        key: str, payload: bytes
    ):  # pragma: no cover - exercised via route
        raise RuntimeError("artifact write failed")

    with TestClient(app) as client:
        client.app.state.container.storage_provider.put = broken_put  # type: ignore[method-assign]
        created = client.post(
            "/admin/workflows",
            headers={"X-Local-Principal": "platform-admin"},
            json={
                "scope_type": "platform",
                "workflow_kind": "subworkflow",
                "slug": "broken-publish",
                "display_name": "Broken Publish",
                "document": sample_document("broken-publish"),
            },
        )
        draft_id = created.json()["workflow_draft_id"]
        validated = client.post(
            f"/admin/workflows/drafts/{draft_id}/validate",
            headers={"X-Local-Principal": "platform-admin"},
        )
        published = client.post(
            f"/admin/workflows/drafts/{draft_id}/publish",
            headers={"X-Local-Principal": "platform-admin"},
            json={
                "validation_result_id": validated.json()["validation_result_id"],
            },
        )

    assert published.status_code == 503
    assert published.json()["detail"] == "compiled bundle artifact persistence failed"
