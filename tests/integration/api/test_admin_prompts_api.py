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


def prepare_prompt_database(database_path: Path, tenant_id) -> None:
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
                "VALUES ('0012_prompt_runtime_profiles')"
            )
        )
    with Session(engine) as session:
        session.add(Tenant(tenant_id=tenant_id, slug="acme", display_name="Acme"))
        session.commit()


def configure_prompt_env(monkeypatch, tmp_path, tenant_id) -> None:
    database_path = tmp_path / "prompt-runtime-api.db"
    prepare_prompt_database(database_path, tenant_id)
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
                    "permission_codes": ["tenant:read", "tenant:admin"],
                }
            }
        ),
    )


def test_admin_prompts_api_draft_validate_preview_publish(
    tmp_path,
    monkeypatch,
) -> None:
    tenant_id = uuid4()
    configure_prompt_env(monkeypatch, tmp_path, tenant_id)
    app = create_app()
    headers = {"X-Local-Principal": "tenant-admin-acme"}
    with TestClient(app) as client:
        created = client.post(
            "/admin/prompt-runtime/api/prompts",
            headers=headers,
            json={
                "scope_type": "tenant",
                "tenant_id": str(tenant_id),
                "slug": "triage-summary",
                "display_name": "Triage Summary",
                "purpose": "Summarize intake",
            },
        )
        lineage_id = created.json()["prompt_lineage_id"]
        saved = client.put(
            f"/admin/prompt-runtime/api/prompts/{lineage_id}/draft",
            headers=headers,
            json={
                "expected_revision_number": 0,
                "prompt_title": "Triage Summary",
                "purpose": "Summarize intake",
                "usage_notes": "",
                "template_content": "Hello {{name}}",
                "variables": [{"name": "name", "purpose": "Recipient"}],
                "fixture_sets": [
                    {
                        "fixture_set_id": "default",
                        "label": "Default",
                        "values_by_variable": {"name": "Ada"},
                    }
                ],
            },
        )
        validated = client.post(
            f"/admin/prompt-runtime/api/prompts/{lineage_id}/validate",
            headers=headers,
        )
        preview = client.post(
            f"/admin/prompt-runtime/api/prompts/{lineage_id}/preview",
            headers=headers,
            json={"fixture_set_id": "default"},
        )
        published = client.post(
            f"/admin/prompt-runtime/api/prompts/{lineage_id}/publish",
            headers=headers,
            json={"reason": "Initial publication"},
        )

    assert created.status_code == 201
    assert saved.status_code == 200
    assert validated.status_code == 200
    assert validated.json()["status"] == "passed"
    assert preview.status_code == 200
    assert preview.json()["rendered_preview"] == "Hello Ada"
    assert published.status_code == 201
    assert published.json()["display_version"] == "v1"


def test_admin_prompt_draft_rejects_byte_oversized_template_with_safe_error(
    tmp_path,
    monkeypatch,
) -> None:
    tenant_id = uuid4()
    configure_prompt_env(monkeypatch, tmp_path, tenant_id)
    app = create_app()
    headers = {"X-Local-Principal": "tenant-admin-acme"}
    template_content = "\u0100" * 32769
    assert len(template_content) <= 65536
    assert len(template_content.encode("utf-8")) > 64 * 1024

    with TestClient(app) as client:
        created = client.post(
            "/admin/prompt-runtime/api/prompts",
            headers=headers,
            json={
                "scope_type": "tenant",
                "tenant_id": str(tenant_id),
                "slug": "large-prompt",
                "display_name": "Large Prompt",
                "purpose": "Exercise safe prompt size rejection",
            },
        )
        lineage_id = created.json()["prompt_lineage_id"]
        oversized = client.put(
            f"/admin/prompt-runtime/api/prompts/{lineage_id}/draft",
            headers=headers,
            json={
                "expected_revision_number": 0,
                "prompt_title": "Too Large",
                "purpose": "QA negative path",
                "template_content": template_content,
                "variables": [],
                "fixture_sets": [],
            },
        )

    assert created.status_code == 201
    assert oversized.status_code == 413
    assert oversized.json() == {"detail": {"code": "prompt_too_large"}}
