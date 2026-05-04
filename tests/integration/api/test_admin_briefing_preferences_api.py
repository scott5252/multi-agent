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
    database_path = tmp_path / "briefing-preferences.db"
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
            text("INSERT INTO alembic_version(version_num) VALUES ('0020')")
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
    permissions = [
        "tenant:read",
        "tenant:admin",
        "briefing-preferences:read",
        "briefing-preferences:write",
        "briefing-preferences:export",
        "briefing-preferences:resolve",
        "telegram-config:read",
        "telegram-config:write",
        "telegram-config:tokens",
        "telegram-config:diagnostics",
    ]
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("AUTH_MODE", "local_principal")
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{database_path}")
    monkeypatch.setenv("FILESYSTEM_STORAGE_ROOT", str(tmp_path / "artifacts"))
    monkeypatch.setenv("TELEGRAM_PROVIDER_TOKEN_REF", "env:QA023_TELEGRAM_TOKEN")
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
                        "briefing-preferences:read",
                        "briefing-preferences:write",
                        "briefing-preferences:export",
                        "briefing-preferences:resolve",
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
                    "permission_codes": permissions,
                },
                "tenant-admin-globex": {
                    "catalog_key": "tenant-admin-globex",
                    "display_name": "Globex Tenant Admin",
                    "tenant_id": GLOBEX_TENANT_ID,
                    "role_codes": ["tenant_user", "tenant_admin"],
                    "permission_codes": permissions,
                },
            }
        ),
    )


def _profile_payload() -> dict[str, object]:
    return {
        "tenant_id": ACME_TENANT_ID,
        "location_label": "Providence, RI",
        "timezone": "America/New_York",
        "news_topics": ["AI", "markets"],
        "vip_senders": ["sarah@example.com"],
        "workday_start": "09:00",
        "workday_end": "17:30",
        "commute_mode": "driving",
        "calendar_account_ref": "delegated:calendar:primary",
        "email_account_ref": "delegated:gmail:primary",
        "output_style": "standard",
        "scheduled_enabled": True,
        "scheduled_time": "08:00",
    }


def test_briefing_preferences_api_profile_summary_and_resolve(
    tmp_path,
    monkeypatch,
) -> None:
    _configure_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        missing = client.get(
            f"/admin/briefing-preferences/api/profile?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
        )
        saved = client.post(
            "/admin/briefing-preferences/api/profile",
            headers=ACME_HEADERS,
            json=_profile_payload(),
        )
        summaries = client.get(
            f"/admin/briefing-preferences/api/summaries?tenant_id={ACME_TENANT_ID}",
            headers=PLATFORM_HEADERS,
        )
        resolved = client.post(
            "/admin/briefing-preferences/api/resolve",
            headers=ACME_HEADERS,
            json={
                "tenant_id": ACME_TENANT_ID,
                "principal_id": "tenant-admin-acme",
                "source_channel": "telegram",
                "trace_id": "trace-qa023",
            },
        )
        denied = client.get(
            f"/admin/briefing-preferences/api/profile?tenant_id={ACME_TENANT_ID}",
            headers=GLOBEX_HEADERS,
        )

    assert missing.status_code == 200
    assert missing.json()["profile"] is None
    assert saved.status_code == 200
    assert saved.json()["revision_number"] == 1
    assert summaries.status_code == 200
    assert "sarah@example.com" not in summaries.text
    assert "s***@example.com" in summaries.text
    assert "delegated:calendar:primary" not in summaries.text
    assert resolved.status_code == 200
    assert resolved.json()["available"] is True
    assert resolved.json()["preferences"]["timezone"] == "America/New_York"
    assert denied.status_code == 403


def test_briefing_preferences_export_and_import_ownership(
    tmp_path,
    monkeypatch,
) -> None:
    _configure_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        saved = client.post(
            "/admin/briefing-preferences/api/profile",
            headers=ACME_HEADERS,
            json=_profile_payload(),
        )
        exported = client.get(
            f"/admin/briefing-preferences/api/export?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
        )
        document = exported.json()["document"]
        document["principal_id"] = "tenant-admin-globex"
        rejected = client.post(
            "/admin/briefing-preferences/api/import",
            headers=ACME_HEADERS,
            json={
                "tenant_id": ACME_TENANT_ID,
                "document": document,
                "revision_token": saved.json()["revision_token"],
            },
        )

    assert exported.status_code == 200
    assert rejected.status_code == 403


def test_briefing_preferences_api_error_paths_and_import_success(
    tmp_path,
    monkeypatch,
) -> None:
    _configure_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        missing_export = client.get(
            f"/admin/briefing-preferences/api/export?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
        )
        saved = client.post(
            "/admin/briefing-preferences/api/profile",
            headers=ACME_HEADERS,
            json=_profile_payload(),
        )
        raw_denied = client.get(
            (
                "/admin/briefing-preferences/api/profile"
                f"?tenant_id={ACME_TENANT_ID}&principal_id=other-user"
            ),
            headers=ACME_HEADERS,
        )
        stale_payload = _profile_payload()
        stale_payload["revision_token"] = "stale"
        stale = client.post(
            "/admin/briefing-preferences/api/profile",
            headers=ACME_HEADERS,
            json=stale_payload,
        )
        exported = client.get(
            f"/admin/briefing-preferences/api/export?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
        )
        document = exported.json()["document"]
        document["preferences"]["output_style"] = "executive"
        imported = client.post(
            "/admin/briefing-preferences/api/import",
            headers=ACME_HEADERS,
            json={
                "tenant_id": ACME_TENANT_ID,
                "document": document,
                "revision_token": saved.json()["revision_token"],
            },
        )
        bad_import = client.post(
            "/admin/briefing-preferences/api/import",
            headers=ACME_HEADERS,
            json={
                "tenant_id": ACME_TENANT_ID,
                "document": {
                    "schema_version": "1.0",
                    "tenant_id": ACME_TENANT_ID,
                    "principal_id": "tenant-admin-acme",
                    "preferences": "not an object",
                },
            },
        )
        resolve_denied = client.post(
            "/admin/briefing-preferences/api/resolve",
            headers=ACME_HEADERS,
            json={
                "tenant_id": ACME_TENANT_ID,
                "principal_id": "other-user",
                "source_channel": "telegram",
            },
        )

    assert missing_export.status_code == 404
    assert raw_denied.status_code == 403
    assert stale.status_code == 409
    assert imported.status_code == 200
    assert imported.json()["output_style"] == "executive"
    assert bad_import.status_code == 422
    assert resolve_denied.status_code == 403
