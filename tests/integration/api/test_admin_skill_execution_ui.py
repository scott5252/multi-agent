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
PLATFORM_HEADERS = {"X-Local-Principal": "platform-admin"}


def _configure_env(monkeypatch, tmp_path: Path) -> None:
    database_path = tmp_path / "skill-execution-ui.db"
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
            text("INSERT INTO alembic_version(version_num) VALUES ('qa021')")
        )
    with Session(engine) as session:
        session.add(
            Tenant(
                tenant_id=UUID(ACME_TENANT_ID),
                slug="acme",
                display_name="Acme",
            )
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
                        "tenant:read",
                        "tenant:admin",
                        "skill-execution:read",
                    ],
                }
            }
        ),
    )


def test_skill_execution_diagnostics_page_and_api(tmp_path, monkeypatch) -> None:
    _configure_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        page = client.get(
            "/admin/skill-execution/ui/diagnostics",
            headers=PLATFORM_HEADERS,
            follow_redirects=False,
        )
        payload = client.get(
            "/admin/skill-execution/api/diagnostics",
            headers=PLATFORM_HEADERS,
        )
        refresh = client.post(
            "/admin/skill-execution/api/diagnostics/run",
            headers=PLATFORM_HEADERS,
            json={"tool_names": ["weather.forecast.read"]},
        )
        unknown_tool = client.post(
            "/admin/skill-execution/api/diagnostics/run",
            headers=PLATFORM_HEADERS,
            json={"tool_names": ["provider.raw.payload"]},
        )

    assert page.status_code == 303, page.text
    assert page.headers["location"] == "/admin/app/skills/diagnostics"
    assert payload.status_code == 200
    assert len(payload.json()["items"]) == 5
    assert "connector request" not in payload.text.lower()
    assert refresh.status_code == 200
    assert len(refresh.json()["items"]) == 1
    assert refresh.json()["items"][0]["tool_name"] == "weather.forecast.read"
    assert "connector request" not in refresh.text.lower()
    assert unknown_tool.status_code == 422
    assert "provider.raw.payload" in unknown_tool.text
