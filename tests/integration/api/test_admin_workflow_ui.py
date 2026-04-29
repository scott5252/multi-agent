from __future__ import annotations

import json
import re
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
                }
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


def test_registry_and_editor_pages_render_help_metadata(tmp_path, monkeypatch) -> None:
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
                "slug": "ui-flow",
                "display_name": "UI Flow",
                "document": sample_document(),
            },
        )
        draft_id = created.json()["workflow_draft_id"]
        registry = client.get(
            "/admin/workflows/ui",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        filtered_registry = client.get(
            "/admin/workflows/ui?scope_filter=tenant&status=draft&q=UI",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        empty_filtered_registry = client.get(
            "/admin/workflows/ui?scope_filter=tenant&status=draft&q=missing",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        editor = client.get(
            f"/admin/workflows/drafts/{draft_id}/editor",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        conflict = client.get(
            f"/admin/workflows/drafts/{draft_id}/editor?conflict=stale-save",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert registry.status_code == 200
    assert "Workflow Registry" in registry.text
    assert "Open Draft" in registry.text
    assert filtered_registry.status_code == 200
    assert 'value="tenant" selected' in filtered_registry.text
    assert 'value="draft" selected' in filtered_registry.text
    assert 'name="q" value="UI"' in filtered_registry.text
    assert "Open Draft" in filtered_registry.text
    assert empty_filtered_registry.status_code == 200
    assert "Open Draft" not in empty_filtered_registry.text
    assert editor.status_code == 200
    assert 'aria-haspopup="dialog"' in editor.text
    match = re.search(
        r'<script id="field-help-data" type="application/json">(.+?)</script>',
        editor.text,
        re.S,
    )
    assert match is not None
    metadata = json.loads(match.group(1))
    assert "&#34;" not in match.group(1)
    assert "roles[].input_contract_key" in metadata["field_help"]
    assert "validation-panel-placeholder" in editor.text
    assert conflict.status_code == 200
    assert "newer draft revision already exists" in conflict.text


def test_editor_and_version_pages_render_validation_and_publish_details(
    tmp_path, monkeypatch
) -> None:
    tenant_id = uuid4()
    configure_env(monkeypatch, tmp_path, tenant_id)
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
    app = create_app()
    with TestClient(app) as client:
        created = client.post(
            "/admin/workflows",
            headers={"X-Local-Principal": "platform-admin"},
            json={
                "scope_type": "platform",
                "workflow_kind": "main_workflow",
                "slug": "ui-publish",
                "display_name": "UI Publish",
                "document": {
                    **sample_document(),
                    "workflow_key": "ui-publish",
                    "display_name": "UI Publish",
                },
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
        editor = client.get(
            f"/admin/workflows/drafts/{draft_id}/editor",
            headers={"X-Local-Principal": "platform-admin"},
        )
        registry = client.get(
            "/admin/workflows/ui",
            headers={"X-Local-Principal": "platform-admin"},
        )
        version = client.get(
            f"/admin/workflows/versions/{version_id}/detail",
            headers={"X-Local-Principal": "platform-admin"},
        )

    assert editor.status_code == 200
    assert "Validation passed" in editor.text
    assert "Publish ready" in editor.text
    assert registry.status_code == 200
    assert "View Version" in registry.text
    assert version.status_code == 200
    assert "Compiled Bundle Digest" in version.text
    assert "v1" in version.text


def test_create_form_posts_platform_draft(tmp_path, monkeypatch) -> None:
    tenant_id = uuid4()
    configure_env(monkeypatch, tmp_path, tenant_id)
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
        editor = client.get(
            created.headers["location"],
            headers={"X-Local-Principal": "platform-admin"},
        )

    assert created.status_code == 303
    assert "/admin/workflows/drafts/" in created.headers["location"]
    assert editor.status_code == 200
    assert "UI Form Platform" in editor.text


def test_editor_and_version_pages_return_expected_404s(tmp_path, monkeypatch) -> None:
    tenant_id = uuid4()
    configure_env(monkeypatch, tmp_path, tenant_id)
    app = create_app()
    with TestClient(app) as client:
        missing_editor = client.get(
            f"/admin/workflows/drafts/{uuid4()}/editor",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        missing_version = client.get(
            f"/admin/workflows/versions/{uuid4()}/detail",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert missing_editor.status_code == 404
    assert missing_version.status_code == 404


def test_editor_and_version_pages_enforce_scope_visibility(
    tmp_path, monkeypatch
) -> None:
    tenant_id = uuid4()
    configure_env(monkeypatch, tmp_path, tenant_id)
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
    app = create_app()
    with TestClient(app) as client:
        created = client.post(
            "/admin/workflows",
            headers={"X-Local-Principal": "platform-admin"},
            json={
                "scope_type": "platform",
                "workflow_kind": "main_workflow",
                "slug": "ui-forbidden",
                "display_name": "UI Forbidden",
                "document": {
                    **sample_document(),
                    "workflow_key": "ui-forbidden",
                    "display_name": "UI Forbidden",
                },
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
        forbidden_editor = client.get(
            f"/admin/workflows/drafts/{draft_id}/editor",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        forbidden_version = client.get(
            f"/admin/workflows/versions/{version_id}/detail",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert forbidden_editor.status_code == 403
    assert forbidden_version.status_code == 403
