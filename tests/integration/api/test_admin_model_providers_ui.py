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


def _configure_env(monkeypatch, tmp_path: Path, tenant_id) -> None:
    database_path = tmp_path / "model-providers.db"
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
        connection.execute(
            text(
                "INSERT INTO alembic_version(version_num) "
                "VALUES ('0011_model_provider_gateway')"
            )
        )
    with Session(engine) as session:
        session.add(Tenant(tenant_id=tenant_id, slug="acme", display_name="Acme"))
        session.commit()
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{database_path}")
    monkeypatch.setenv("FILESYSTEM_STORAGE_ROOT", str(tmp_path / "artifacts"))
    monkeypatch.setenv(
        "LOCAL_PRINCIPAL_CATALOG_JSON",
        json.dumps(
            {
                "platform-admin": {
                    "catalog_key": "platform-admin",
                    "display_name": "Platform Admin",
                    "role_codes": ["platform_admin"],
                    "permission_codes": ["tenant:read", "tenant:admin"],
                },
                "tenant-admin-acme": {
                    "catalog_key": "tenant-admin-acme",
                    "display_name": "Tenant Admin",
                    "tenant_id": str(tenant_id),
                    "role_codes": ["tenant_user", "tenant_admin"],
                    "permission_codes": ["tenant:read", "tenant:admin"],
                },
            }
        ),
    )


def test_admin_model_provider_pages_and_json_api(tmp_path, monkeypatch) -> None:
    tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id)
    app = create_app()

    with TestClient(app) as client:
        list_page = client.get(
            "/admin/model-providers",
            headers={"X-Local-Principal": "platform-admin"},
        )
        new_page = client.get(
            "/admin/model-providers/new",
            headers={"X-Local-Principal": "platform-admin"},
        )
        created = client.post(
            "/admin/model-providers/api/connections",
            headers={"X-Local-Principal": "platform-admin"},
            json={
                "provider_type": "openai",
                "display_name": "Provider",
                "models": [{"model_id": "gpt-test"}],
                "credential_secret_reference_ids": ["qa011/openai-placeholder"],
                "active": True,
            },
        )
        assert created.status_code == 200, created.text
        connection_id = created.json()["provider_connection_id"]
        detail_page = client.get(
            f"/admin/model-providers/{connection_id}",
            headers={"X-Local-Principal": "platform-admin"},
        )
        edit_page = client.get(
            f"/admin/model-providers/{connection_id}/edit",
            headers={"X-Local-Principal": "platform-admin"},
        )
        listed = client.get(
            "/admin/model-providers/api/connections",
            headers={"X-Local-Principal": "platform-admin"},
        )
        updated = client.put(
            f"/admin/model-providers/api/connections/{connection_id}",
            headers={"X-Local-Principal": "platform-admin"},
            json={
                "provider_type": "openai",
                "display_name": "Provider Updated",
                "models": [{"model_id": "gpt-test-updated"}],
                "credential_secret_reference_ids": ["qa011/openai-placeholder"],
                "active": True,
            },
        )
        deactivated = client.post(
            f"/admin/model-providers/{connection_id}/deactivate",
            headers={"X-Local-Principal": "platform-admin"},
            follow_redirects=False,
        )
        activated = client.post(
            f"/admin/model-providers/{connection_id}/activate",
            headers={"X-Local-Principal": "platform-admin"},
            follow_redirects=False,
        )
        synced = client.post(
            f"/admin/model-providers/{connection_id}/sync-catalog",
            headers={"X-Local-Principal": "platform-admin"},
        )
        form_saved = client.post(
            "/admin/model-providers",
            headers={"X-Local-Principal": "platform-admin"},
            data={
                "provider_type": "openai",
                "display_name": "Form Provider",
                "model_ids": "gpt-form",
                "credential_secret_reference_ids": "qa011/openai-placeholder",
                "visibility_mode": "platform_default",
                "connect_seconds": "5",
                "read_seconds": "30",
                "total_seconds": "45",
                "active": "true",
            },
            follow_redirects=False,
        )
        catalog_page = client.get(
            "/admin/model-providers/catalog",
            headers={"X-Local-Principal": "platform-admin"},
        )
        denied = client.post(
            "/admin/model-providers/api/connections",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "provider_type": "openai",
                "display_name": "Denied",
                "models": [{"model_id": "denied"}],
            },
        )
        unsafe_local = client.post(
            "/admin/model-providers/api/connections",
            headers={"X-Local-Principal": "platform-admin"},
            json={
                "provider_type": "local_openai_compatible",
                "display_name": "Unsafe",
                "base_url": ("http://user:pass@192.0.2.10:9999/v1?token=value"),
                "models": [{"model_id": "unsafe"}],
                "credential_secret_reference_ids": ["qa011/local-placeholder"],
            },
        )

    assert list_page.status_code == 200
    assert "Model Providers" in list_page.text
    assert new_page.status_code == 200
    assert "Provider type" in new_page.text
    assert detail_page.status_code == 200
    assert "Provider" in detail_page.text
    assert edit_page.status_code == 200
    assert listed.status_code == 200
    assert listed.json()["items"][0]["display_name"] == "Provider"
    assert updated.status_code == 200
    assert updated.json()["display_name"] == "Provider Updated"
    assert deactivated.status_code == 303
    assert activated.status_code == 303
    assert synced.status_code == 200
    assert form_saved.status_code == 303
    assert catalog_page.status_code == 200
    assert denied.status_code in {403, 422}
    assert unsafe_local.status_code == 422
    assert unsafe_local.json() == {
        "detail": "local provider URL cannot include userinfo"
    }
    assert "user:pass" not in unsafe_local.text
    assert "token=value" not in unsafe_local.text
