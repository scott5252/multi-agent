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


def _prepare_database(database_path: Path, tenant_id) -> None:
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
                "VALUES ('0005_immutable_memory')"
            )
        )
    with Session(engine) as session:
        session.add(Tenant(tenant_id=tenant_id, slug="acme", display_name="Acme"))
        session.commit()


def test_memory_api_creates_versions_replays_diffs_and_lists_audit(
    tmp_path, monkeypatch
) -> None:
    tenant_id = uuid4()
    database_path = tmp_path / "memory-api.db"
    _prepare_database(database_path, tenant_id)
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
                "tenant-admin-globex": {
                    "catalog_key": "tenant-admin-globex",
                    "display_name": "Globex Admin",
                    "tenant_id": str(uuid4()),
                    "org_id": "org-globex",
                    "role_codes": ["tenant_user", "tenant_admin"],
                    "permission_codes": ["tenant:read", "tenant:admin"],
                },
            }
        ),
    )

    headers = {"X-Local-Principal": "tenant-admin-acme"}
    with TestClient(create_app()) as client:
        first = client.post(
            "/memory/versions",
            headers=headers,
            json={
                "scope": {
                    "workflow_lineage_id": "workflow.demo",
                    "agent_key": "triage",
                    "memory_key": "prefs",
                },
                "assert_no_current_head": True,
                "content": {"preferred_contact": "sms"},
                "change_summary_redacted": "Captured preference",
            },
        )
        first_version_id = first.json()["version"]["memory_version_id"]
        scope_id = first.json()["scope"]["memory_scope_id"]
        head = client.get(
            "/memory/head"
            "?workflow_lineage_id=workflow.demo&agent_key=triage&memory_key=prefs",
            headers=headers,
        )
        second = client.post(
            "/memory/versions",
            headers=headers,
            json={
                "scope": {
                    "workflow_lineage_id": "workflow.demo",
                    "agent_key": "triage",
                    "memory_key": "prefs",
                },
                "expected_current_version_id": first_version_id,
                "content": {"preferred_contact": "email"},
            },
        )
        second_version_id = second.json()["version"]["memory_version_id"]
        stale = client.post(
            "/memory/versions",
            headers=headers,
            json={
                "scope": {
                    "workflow_lineage_id": "workflow.demo",
                    "agent_key": "triage",
                    "memory_key": "prefs",
                },
                "expected_current_version_id": first_version_id,
                "content": {"preferred_contact": "phone"},
            },
        )
        history = client.get(f"/memory/scopes/{scope_id}/versions", headers=headers)
        replay = client.get(
            f"/memory/versions/{first_version_id}/replay", headers=headers
        )
        diff = client.post(
            "/memory/diffs",
            headers=headers,
            json={
                "base_memory_version_id": first_version_id,
                "compare_memory_version_id": second_version_id,
            },
        )
        audit = client.get(f"/memory/audit?memory_scope_id={scope_id}", headers=headers)
        globex_denied = client.get(
            f"/memory/versions/{first_version_id}",
            headers={"X-Local-Principal": "tenant-admin-globex"},
        )

    assert first.status_code == 201
    assert head.json()["has_memory"] is True
    assert second.json()["version"]["previous_memory_version_id"] == first_version_id
    assert stale.status_code == 409
    assert history.json()["versions"][0]["memory_version_id"] == second_version_id
    assert replay.json()["content"] == {"preferred_contact": "sms"}
    assert diff.json()["changes"][0]["path"] == "/preferred_contact"
    assert "preferred_contact" not in json.dumps(audit.json())
    assert globex_denied.status_code == 404
