from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from multi_agent_platform.api.main import create_app
from multi_agent_platform.db.base import Base
from multi_agent_platform.db.models import import_models
from multi_agent_platform.db.models.tenant import Tenant

ACME_TENANT_ID = "11111111-1111-1111-1111-111111111111"
GLOBEX_TENANT_ID = "22222222-2222-2222-2222-222222222222"
PLATFORM_HEADERS = {"X-Local-Principal": "platform-admin"}
ACME_HEADERS = {"X-Local-Principal": "tenant-admin-acme"}
GLOBEX_HEADERS = {"X-Local-Principal": "tenant-admin-globex"}


def _configure_env(monkeypatch, tmp_path: Path) -> None:
    database_path = tmp_path / "telegram.db"
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
                "VALUES ('0017_telegram_config_console')"
            )
        )
    with Session(engine) as session:
        session.add_all(
            [
                Tenant(
                    tenant_id=UUID(ACME_TENANT_ID),
                    slug="acme",
                    display_name="Acme",
                ),
                Tenant(
                    tenant_id=UUID(GLOBEX_TENANT_ID),
                    slug="globex",
                    display_name="Globex",
                ),
            ]
        )
        session.commit()
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("AUTH_MODE", "local_principal")
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{database_path}")
    monkeypatch.setenv("FILESYSTEM_STORAGE_ROOT", str(tmp_path / "artifacts"))
    monkeypatch.setenv("TELEGRAM_PROVIDER_TOKEN_REF", "env:QA017_TELEGRAM_TOKEN")
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", "local-dev-secret")
    monkeypatch.setenv(
        "LOCAL_PRINCIPAL_CATALOG_JSON",
        json.dumps(
            {
                "platform-admin": {
                    "catalog_key": "platform-admin",
                    "display_name": "Platform Admin",
                    "role_codes": ["platform_admin"],
                    "permission_codes": [
                        "platform:admin",
                        "telegram-config:read",
                        "telegram-config:write",
                        "telegram-config:tokens",
                        "telegram-config:diagnostics",
                    ],
                },
                "tenant-admin-acme": {
                    "catalog_key": "tenant-admin-acme",
                    "display_name": "Acme Tenant Admin",
                    "tenant_id": ACME_TENANT_ID,
                    "role_codes": ["tenant_user", "tenant_admin"],
                    "permission_codes": [
                        "tenant:read",
                        "tenant:admin",
                        "telegram-config:read",
                        "telegram-config:write",
                        "telegram-config:tokens",
                        "telegram-config:diagnostics",
                    ],
                },
                "tenant-admin-globex": {
                    "catalog_key": "tenant-admin-globex",
                    "display_name": "Globex Tenant Admin",
                    "tenant_id": GLOBEX_TENANT_ID,
                    "role_codes": ["tenant_user", "tenant_admin"],
                    "permission_codes": [
                        "tenant:read",
                        "tenant:admin",
                        "telegram-config:read",
                        "telegram-config:write",
                        "telegram-config:tokens",
                        "telegram-config:diagnostics",
                    ],
                },
            }
        ),
    )


def test_telegram_api_readiness_config_conflict_and_tenant_denial(
    tmp_path,
    monkeypatch,
) -> None:
    _configure_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        readiness = client.get(
            "/admin/telegram/api/readiness",
            headers=PLATFORM_HEADERS,
        )
        config = client.get(
            f"/admin/telegram/api/config?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
        )
        revision = config.json()["revision_token"]
        updated = client.post(
            "/admin/telegram/api/config",
            headers=ACME_HEADERS,
            json={
                "tenant_id": ACME_TENANT_ID,
                "enabled": True,
                "protected_commands": ["/run", "/status"],
                "status_note": "Ready for QA",
                "revision_token": revision,
            },
        )
        stale = client.post(
            "/admin/telegram/api/config",
            headers=ACME_HEADERS,
            json={
                "tenant_id": ACME_TENANT_ID,
                "enabled": False,
                "protected_commands": ["/run"],
                "revision_token": revision,
            },
        )
        denied = client.get(
            f"/admin/telegram/api/config?tenant_id={ACME_TENANT_ID}",
            headers=GLOBEX_HEADERS,
        )

    assert readiness.status_code == 200
    assert readiness.json()["ready"] is True
    assert "local-dev-secret" not in readiness.text
    assert updated.status_code == 200
    assert updated.json()["enabled"] is True
    assert stale.status_code == 409
    assert denied.status_code == 403


def test_telegram_api_issues_token_syncs_masked_identity_and_diagnostics(
    tmp_path,
    monkeypatch,
) -> None:
    _configure_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        issued = client.post(
            f"/admin/telegram/api/link-tokens?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
        )
        raw_token = issued.json()["link_token"]
        linked = client.post(
            "/channels/telegram/webhook/local-dev-secret",
            json={
                "update_id": 501,
                "message": {
                    "chat": {"id": 123456789},
                    "from": {"id": 987654321},
                    "text": f"/link {raw_token}",
                },
            },
        )
        identities = client.get(
            f"/admin/telegram/api/identities?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
        )
        diagnostic = client.post(
            f"/admin/telegram/api/webhook/validate?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
        )
        diagnostics = client.get(
            f"/admin/telegram/api/diagnostics?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
        )

    assert issued.status_code == 201
    assert issued.json()["token_audit"]["token_fingerprint"] != raw_token
    assert linked.json()["ok"] is True
    assert identities.status_code == 200
    assert "123456789" not in identities.text
    assert "987654321" not in identities.text
    assert "123***789" in identities.text
    assert diagnostic.json()["redacted_metadata"]["external_call_performed"] is False
    assert diagnostics.json()["items"]
