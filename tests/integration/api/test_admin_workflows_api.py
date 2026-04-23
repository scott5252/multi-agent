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
    database_path = tmp_path / "workflow-api.db"
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
        "description": "API example workflow.",
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


def test_admin_workflows_api_create_list_fetch_and_conflict(
    tmp_path, monkeypatch
) -> None:
    tenant_id = uuid4()
    configure_env(monkeypatch, tmp_path, tenant_id)
    app = create_app()
    with TestClient(app) as client:
        created = client.post(
            "/admin/workflows",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "scope_type": "tenant",
                "workflow_kind": "main_workflow",
                "slug": "triage-flow",
                "display_name": "Triage Flow",
                "document": sample_document("triage-flow"),
            },
        )
        draft_id = created.json()["workflow_draft_id"]
        listed = client.get(
            "/admin/workflows",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        fetched = client.get(
            f"/admin/workflows/drafts/{draft_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        saved = client.put(
            f"/admin/workflows/drafts/{draft_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "base_revision_number": 1,
                "display_name": "Triage Flow Updated",
                "document": {
                    **sample_document("triage-flow"),
                    "display_name": "Triage Flow Updated",
                },
            },
        )
        stale = client.put(
            f"/admin/workflows/drafts/{draft_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "base_revision_number": 1,
                "display_name": "Outdated Save",
                "document": {
                    **sample_document("triage-flow"),
                    "display_name": "Outdated Save",
                },
            },
        )

    assert created.status_code == 201
    assert listed.status_code == 200
    assert listed.json()["items"][0]["display_name"] == "Triage Flow"
    assert fetched.status_code == 200
    assert saved.status_code == 200
    assert stale.status_code == 409


def test_platform_admin_can_create_platform_scoped_workflow(
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
                "slug": "platform-review",
                "display_name": "Platform Review",
                "document": sample_document("platform-review"),
            },
        )

    assert created.status_code == 201
    assert created.json()["scope_type"] == "platform"


def test_admin_workflows_api_validation_publish_and_version_detail(
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
                "slug": "platform-publish",
                "display_name": "Platform Publish",
                "document": sample_document("platform-publish"),
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
        shared = client.post(
            f"/admin/workflows/versions/{version_id}/sharing-grants",
            headers={"X-Local-Principal": "platform-admin"},
            json={"grantee_tenant_id": str(tenant_id)},
        )

    assert validated.status_code == 200
    assert validated.json()["status"] == "passed"
    assert published.status_code == 201
    assert published.json()["display_version"] == "v1"
    assert detail.status_code == 200
    assert detail.json()["compiled_bundle_digest"]
    assert shared.status_code == 201


def test_validation_and_publish_reject_stale_or_invalid_states(
    tmp_path, monkeypatch
) -> None:
    tenant_id = uuid4()
    configure_env(monkeypatch, tmp_path, tenant_id)
    app = create_app()
    with TestClient(app) as client:
        invalid = client.post(
            "/admin/workflows",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "scope_type": "tenant",
                "workflow_kind": "main_workflow",
                "slug": "invalid-flow",
                "display_name": "Invalid Flow",
                "document": {
                    **sample_document("invalid-flow"),
                    "roles": [
                        {
                            **sample_document("invalid-flow")["roles"][0],
                            "skill_bindings": [
                                {
                                    "binding_key": "triage-binding",
                                    "skill_slug": "triage-agent",
                                    "skill_version": "latest",
                                    "purpose": "Assess",
                                }
                            ],
                        }
                    ],
                },
            },
        )
        draft_id = invalid.json()["workflow_draft_id"]
        failed_validation = client.post(
            f"/admin/workflows/drafts/{draft_id}/validate",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        fixed = client.put(
            f"/admin/workflows/drafts/{draft_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "base_revision_number": 1,
                "display_name": "Invalid Flow Fixed",
                "document": {
                    **sample_document("invalid-flow"),
                    "display_name": "Invalid Flow Fixed",
                },
            },
        )
        stale_publish = client.post(
            f"/admin/workflows/drafts/{draft_id}/publish",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "validation_result_id": failed_validation.json()[
                    "validation_result_id"
                ],
            },
        )

    assert failed_validation.status_code == 200
    assert failed_validation.json()["status"] == "failed"
    assert failed_validation.json()["blocking_issue_count"] >= 1
    assert fixed.status_code == 200
    assert stale_publish.status_code == 409


def test_workflow_version_and_sharing_routes_enforce_scope_and_not_found(
    tmp_path, monkeypatch
) -> None:
    tenant_id = uuid4()
    configure_env(monkeypatch, tmp_path, tenant_id)
    app = create_app()
    with TestClient(app) as client:
        missing_version = client.get(
            f"/admin/workflows/versions/{uuid4()}",
            headers={"X-Local-Principal": "platform-admin"},
        )
        missing_validation = client.post(
            f"/admin/workflows/drafts/{uuid4()}/validate",
            headers={"X-Local-Principal": "platform-admin"},
        )
        created = client.post(
            "/admin/workflows",
            headers={"X-Local-Principal": "platform-admin"},
            json={
                "scope_type": "platform",
                "workflow_kind": "main_workflow",
                "slug": "forbidden-share",
                "display_name": "Forbidden Share",
                "document": sample_document("forbidden-share"),
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
        forbidden_share = client.post(
            f"/admin/workflows/versions/{published.json()['workflow_version_bundle_id']}/sharing-grants",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={"grantee_tenant_id": str(tenant_id)},
        )

    assert missing_version.status_code == 404
    assert missing_validation.status_code == 404
    assert forbidden_share.status_code == 403


def test_workflow_route_error_branches_return_expected_status_codes(
    tmp_path, monkeypatch
) -> None:
    tenant_id = uuid4()
    configure_env(monkeypatch, tmp_path, tenant_id)
    app = create_app()
    with TestClient(app) as client:
        metadata = client.get(
            "/admin/workflows/editor-metadata",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        platform_created = client.post(
            "/admin/workflows",
            headers={"X-Local-Principal": "platform-admin"},
            json={
                "scope_type": "platform",
                "workflow_kind": "main_workflow",
                "slug": "access-denied",
                "display_name": "Access Denied",
                "document": sample_document("access-denied"),
            },
        )
        draft_id = platform_created.json()["workflow_draft_id"]
        duplicate = client.post(
            "/admin/workflows",
            headers={"X-Local-Principal": "platform-admin"},
            json={
                "scope_type": "platform",
                "workflow_kind": "main_workflow",
                "slug": "access-denied",
                "display_name": "Access Denied",
                "document": sample_document("access-denied"),
            },
        )
        forbidden_create = client.post(
            "/admin/workflows",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "scope_type": "platform",
                "workflow_kind": "main_workflow",
                "slug": "tenant-forbidden",
                "display_name": "Tenant Forbidden",
                "document": sample_document("tenant-forbidden"),
            },
        )
        forbidden_fetch = client.get(
            f"/admin/workflows/drafts/{draft_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        forbidden_validate = client.post(
            f"/admin/workflows/drafts/{draft_id}/validate",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        forbidden_publish = client.post(
            f"/admin/workflows/drafts/{draft_id}/publish",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={"validation_result_id": str(uuid4())},
        )
        version_created = client.post(
            "/admin/workflows",
            headers={"X-Local-Principal": "platform-admin"},
            json={
                "scope_type": "platform",
                "workflow_kind": "main_workflow",
                "slug": "version-denied",
                "display_name": "Version Denied",
                "document": sample_document("version-denied"),
            },
        )
        version_draft_id = version_created.json()["workflow_draft_id"]
        version_validation = client.post(
            f"/admin/workflows/drafts/{version_draft_id}/validate",
            headers={"X-Local-Principal": "platform-admin"},
        )
        version_publish = client.post(
            f"/admin/workflows/drafts/{version_draft_id}/publish",
            headers={"X-Local-Principal": "platform-admin"},
            json={
                "validation_result_id": version_validation.json()[
                    "validation_result_id"
                ],
            },
        )
        forbidden_version_detail = client.get(
            f"/admin/workflows/versions/{version_publish.json()['workflow_version_bundle_id']}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        missing_share = client.post(
            f"/admin/workflows/versions/{uuid4()}/sharing-grants",
            headers={"X-Local-Principal": "platform-admin"},
            json={"grantee_tenant_id": str(tenant_id)},
        )

    assert metadata.status_code == 200
    assert duplicate.status_code == 409
    assert forbidden_create.status_code == 403
    assert forbidden_fetch.status_code == 403
    assert forbidden_validate.status_code == 403
    assert forbidden_publish.status_code == 403
    assert forbidden_version_detail.status_code == 403
    assert missing_share.status_code == 404
