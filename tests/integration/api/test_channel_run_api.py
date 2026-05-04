from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

from multi_agent_platform.api.main import create_app
from multi_agent_platform.db.base import Base
from multi_agent_platform.db.models import import_models

ACME_TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")
GLOBEX_TENANT_ID = UUID("22222222-2222-2222-2222-222222222222")


def configure_channel_env(monkeypatch, tmp_path: Path) -> None:
    database_path = tmp_path / "channels-api.db"
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
                "VALUES ('0006_user_interaction_channels')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO tenants (tenant_id, slug, display_name, status, "
                "created_at, updated_at) VALUES "
                "(:acme_id, 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, "
                "CURRENT_TIMESTAMP), "
                "(:globex_id, 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, "
                "CURRENT_TIMESTAMP)"
            ),
            {"acme_id": str(ACME_TENANT_ID), "globex_id": str(GLOBEX_TENANT_ID)},
        )
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{database_path}")
    monkeypatch.setenv("FILESYSTEM_STORAGE_ROOT", str(tmp_path / "artifacts"))
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", "local-dev-secret")
    monkeypatch.setenv("TELEGRAM_PROVIDER_TOKEN_REF", "env:QA022_TELEGRAM_TOKEN")
    monkeypatch.setenv(
        "LOCAL_PRINCIPAL_CATALOG_JSON",
        json.dumps(
            {
                "tenant-admin-acme": {
                    "catalog_key": "tenant-admin-acme",
                    "display_name": "Tenant Admin",
                    "tenant_id": str(ACME_TENANT_ID),
                    "org_id": "org-acme",
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
                    "tenant_id": str(GLOBEX_TENANT_ID),
                    "org_id": "org-globex",
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


def acme_headers(idempotency_key: str | None = None) -> dict[str, str]:
    headers = {"X-Local-Principal": "tenant-admin-acme"}
    if idempotency_key:
        headers["X-Idempotency-Key"] = idempotency_key
    return headers


def test_channel_run_rest_lifecycle_and_cross_tenant_denial(
    tmp_path, monkeypatch
) -> None:
    configure_channel_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        start = client.post(
            "/runs",
            headers=acme_headers("idem-rest-001"),
            json={
                "workflow_id": "published-demo",
                "inputs": {"topic": "rest"},
                "channel": "web_api",
            },
        )
        assert start.status_code == 202
        run_id = start.json()["run_id"]

        replay = client.post(
            "/runs",
            headers=acme_headers("idem-rest-001"),
            json={
                "workflow_id": "published-demo",
                "inputs": {"topic": "rest"},
                "channel": "web_api",
            },
        )
        conflict = client.post(
            "/runs",
            headers=acme_headers("idem-rest-001"),
            json={
                "workflow_id": "published-demo",
                "inputs": {"topic": "different"},
                "channel": "web_api",
            },
        )
        status = client.get(f"/runs/{run_id}/status", headers=acme_headers())
        timeline = client.get(f"/runs/{run_id}/timeline", headers=acme_headers())
        subscribe = client.post(
            f"/runs/{run_id}/subscriptions",
            headers=acme_headers("idem-sub-001"),
            json={"channel": "web_api", "event_types": ["terminal"]},
        )
        callback = client.post(
            f"/runs/{run_id}/callbacks",
            headers=acme_headers("idem-callback-001"),
            json={
                "callback_url": "https://example.test/callback",
                "event_types": ["terminal"],
            },
        )
        cancel = client.post(
            f"/runs/{run_id}/cancel",
            headers=acme_headers("idem-cancel-001"),
            json={"reason": "test cancellation"},
        )
        cross_tenant = client.get(
            f"/runs/{run_id}/status",
            headers={"X-Local-Principal": "tenant-admin-globex"},
        )

    assert replay.json()["run_id"] == run_id
    assert conflict.status_code == 409
    assert status.json()["state"] == "queued"
    assert timeline.json()["items"][0]["event_type"] == "run_queued"
    assert subscribe.status_code == 201
    assert callback.status_code == 201
    assert cancel.json()["state"] == "canceled"
    assert cross_tenant.status_code == 404


def test_channel_result_artifacts_and_approval_flow(tmp_path, monkeypatch) -> None:
    configure_channel_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        completed = client.post(
            "/runs",
            headers=acme_headers("idem-complete-001"),
            json={
                "workflow_id": "completed-demo",
                "inputs": {"topic": "done", "_channel_state": "completed"},
                "channel": "web_api",
            },
        )
        completed_run_id = completed.json()["run_id"]
        result = client.get(
            f"/runs/{completed_run_id}/result",
            headers=acme_headers(),
        )
        artifacts = client.get(
            f"/runs/{completed_run_id}/artifacts",
            headers=acme_headers(),
        )
        artifact_id = artifacts.json()["items"][0]["artifact_id"]
        download = client.post(
            f"/runs/{completed_run_id}/artifacts/{artifact_id}/download-url",
            headers=acme_headers("idem-download-001"),
        )

        waiting = client.post(
            "/runs",
            headers=acme_headers("idem-waiting-001"),
            json={
                "workflow_id": "waiting-demo",
                "inputs": {"topic": "approval", "_channel_state": "waiting"},
                "channel": "web_api",
            },
        )
        waiting_run_id = waiting.json()["run_id"]
        waiting_status = client.get(
            f"/runs/{waiting_run_id}/status",
            headers=acme_headers(),
        )
        prompt = waiting_status.json()["waiting_prompt"]
        decision = client.post(
            f"/runs/{waiting_run_id}/approvals/{prompt['prompt_id']}/decision",
            headers=acme_headers("idem-decision-001"),
            json={"action": "approve", "prompt_version": 1},
        )
        stale = client.post(
            f"/runs/{waiting_run_id}/approvals/{prompt['prompt_id']}/decision",
            headers=acme_headers("idem-decision-002"),
            json={"action": "approve", "prompt_version": 1},
        )

    assert result.json()["availability"] == "available"
    assert artifacts.json()["items"][0]["download_url_available"] is True
    assert download.status_code == 201
    assert prompt["allowed_actions"] == ["approve", "reject", "resume", "cancel"]
    assert decision.json()["accepted"] is True
    assert stale.status_code == 409
    assert stale.json()["accepted"] is False
