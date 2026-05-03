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
from multi_agent_platform.db.models.usage import LlmUsageEvent
from multi_agent_platform.usage.models import UsageEventStatus

ACME_TENANT_ID = "11111111-1111-1111-1111-111111111111"
GLOBEX_TENANT_ID = "22222222-2222-2222-2222-222222222222"
PLATFORM_HEADERS = {"X-Local-Principal": "platform-admin"}
ACME_HEADERS = {"X-Local-Principal": "tenant-admin-acme"}
GLOBEX_HEADERS = {"X-Local-Principal": "tenant-admin-globex"}


def _configure_env(monkeypatch, tmp_path: Path) -> None:
    database_path = tmp_path / "usage.db"
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
                "VALUES ('0016_token_usage_cost_analytics')"
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
                LlmUsageEvent(
                    tenant_id=UUID(ACME_TENANT_ID),
                    principal_id="tenant-admin-acme",
                    provider_key="openai",
                    model_id="gpt-test",
                    agent_key="writer",
                    execution_mode="test",
                    total_tokens=10,
                    estimated_cost_micros=30,
                    latency_ms=5,
                    usage_status=UsageEventStatus.ESTIMATED,
                ),
                LlmUsageEvent(
                    tenant_id=UUID(GLOBEX_TENANT_ID),
                    principal_id="tenant-admin-globex",
                    provider_key="openai",
                    model_id="gpt-other",
                    execution_mode="test",
                    total_tokens=90,
                    estimated_cost_micros=270,
                    latency_ms=5,
                    usage_status=UsageEventStatus.ESTIMATED,
                ),
            ]
        )
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
                    "permission_codes": [
                        "platform:admin",
                        "usage:read",
                        "usage:export",
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
                        "usage:read",
                        "usage:export",
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
                        "usage:read",
                        "usage:export",
                    ],
                },
            }
        ),
    )


def test_usage_api_summary_events_export_and_tenant_denial(
    tmp_path,
    monkeypatch,
) -> None:
    _configure_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        platform_summary = client.get(
            "/admin/usage/api/summary",
            headers=PLATFORM_HEADERS,
        )
        tenant_summary = client.get(
            f"/admin/usage/api/summary?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
        )
        denied = client.get(
            f"/admin/usage/api/summary?tenant_id={ACME_TENANT_ID}",
            headers=GLOBEX_HEADERS,
        )
        export = client.post(
            "/admin/usage/api/exports",
            headers=ACME_HEADERS,
            json={"tenant_id": ACME_TENANT_ID, "filters": {"model_id": "gpt-test"}},
        )

    assert platform_summary.status_code == 200
    assert platform_summary.json()["total_tokens"] == 100
    assert tenant_summary.status_code == 200
    assert tenant_summary.json()["total_tokens"] == 10
    assert denied.status_code == 403
    assert export.status_code == 201, export.text
    assert export.json()["row_count"] == 1
    assert export.json()["artifact_uri"]
