from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from multi_agent_platform.api.main import create_app
from multi_agent_platform.api.routers.admin_skill_registry import (
    reset_skill_registry_service,
)
from multi_agent_platform.db.base import Base
from multi_agent_platform.db.models import import_models
from multi_agent_platform.db.models.tenant import Tenant
from tests.fixtures.skill_registry import valid_skill_manifest

ACME_TENANT_ID = "11111111-1111-1111-1111-111111111111"
GLOBEX_TENANT_ID = "22222222-2222-2222-2222-222222222222"
PLATFORM_HEADERS = {"X-Local-Principal": "platform-admin"}
ACME_HEADERS = {"X-Local-Principal": "tenant-admin-acme"}
GLOBEX_HEADERS = {"X-Local-Principal": "tenant-admin-globex"}


def _configure_env(monkeypatch, tmp_path: Path) -> None:
    database_path = tmp_path / "skill-registry-ui.db"
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
                "VALUES ('0014_skill_registry_lifecycle')"
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
                        "skill-registry:publish",
                        "skill-registry:audit",
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
                        "skill-registry:install",
                        "skill-registry:bind",
                        "skill-registry:audit",
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
                        "skill-registry:install",
                        "skill-registry:bind",
                        "skill-registry:audit",
                    ],
                },
            }
        ),
    )


def test_browser_skill_registry_lifecycle(tmp_path, monkeypatch) -> None:
    reset_skill_registry_service()
    _configure_env(monkeypatch, tmp_path)
    app = create_app()
    manifest = valid_skill_manifest()

    with TestClient(app) as client:
        empty = client.get(
            "/admin/skill-registry/ui/packages",
            headers=PLATFORM_HEADERS,
        )
        created = client.post(
            "/admin/skill-registry/ui/packages",
            headers=PLATFORM_HEADERS,
            data={
                "slug": "calendar-assistant",
                "display_name": "Calendar Assistant",
                "description": "Safe calendar skill.",
                "owner_principal_id": "platform-admin",
            },
            follow_redirects=False,
        )
        candidate = client.post(
            "/admin/skill-registry/ui/packages/calendar-assistant/candidate",
            headers=PLATFORM_HEADERS,
            data={
                "manifest": json.dumps(manifest),
                "artifact_digest": "sha256:artifact",
                "approved_integration_refs": "tool:calendar:v1",
            },
            follow_redirects=True,
        )
        assert candidate.status_code == 200, candidate.text
        token = _extract_value(candidate.text, "revision_token")
        validated = client.post(
            "/admin/skill-registry/ui/packages/calendar-assistant/candidate/validate",
            headers=PLATFORM_HEADERS,
            data={"revision_token": token},
            follow_redirects=True,
        )
        assert validated.status_code == 200, validated.text
        publish_token = _extract_value(validated.text, "revision_token")
        published = client.post(
            "/admin/skill-registry/ui/packages/calendar-assistant/candidate/publish",
            headers=PLATFORM_HEADERS,
            data={"revision_token": publish_token},
            follow_redirects=False,
        )
        granted = client.post(
            "/admin/skill-registry/ui/packages/calendar-assistant/versions/1.2.3/grants",
            headers=PLATFORM_HEADERS,
            data={"tenant_ids": ACME_TENANT_ID, "grant_reason": "QA"},
            follow_redirects=True,
        )
        acme_available = client.get(
            f"/admin/skill-registry/ui/available-versions?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
        )
        globex_available = client.get(
            f"/admin/skill-registry/ui/available-versions?tenant_id={GLOBEX_TENANT_ID}",
            headers=GLOBEX_HEADERS,
        )
        installed = client.post(
            "/admin/skill-registry/ui/installations",
            headers=ACME_HEADERS,
            data={
                "tenant_id": ACME_TENANT_ID,
                "slug": "calendar-assistant",
                "semantic_version": "1.2.3",
            },
            follow_redirects=False,
        )
        installation_path = installed.headers["location"]
        blocked_detail = client.get(installation_path, headers=ACME_HEADERS)
        revision_token = _extract_value(blocked_detail.text, "revision_token")
        configured = client.post(
            f"{installation_path}/credentials",
            headers=ACME_HEADERS,
            data={
                "revision_token": revision_token,
                "requirement_key": "calendar-oauth",
                "credential_kind": "delegated_credential",
                "reference_id": "delegated-calendar-acme",
                "delegated_scope": "calendar.readonly",
            },
            follow_redirects=True,
        )
        stale = client.post(
            f"{installation_path}/credentials",
            headers=ACME_HEADERS,
            data={
                "revision_token": revision_token,
                "requirement_key": "calendar-oauth",
                "credential_kind": "delegated_credential",
                "reference_id": "",
            },
            follow_redirects=True,
        )
        denied = client.get(installation_path, headers=GLOBEX_HEADERS)

    assert empty.status_code == 200
    assert "No skill packages are visible" in empty.text
    assert created.status_code == 303
    assert created.headers["location"].endswith(
        "/admin/skill-registry/ui/packages/calendar-assistant"
    )
    assert "Status: passed" in validated.text or "passed" in validated.text
    assert published.status_code == 303
    assert published.headers["location"].endswith("/versions/1.2.3")
    assert granted.status_code == 200
    assert ACME_TENANT_ID in granted.text
    assert acme_available.status_code == 200
    assert "calendar-assistant" in acme_available.text
    assert globex_available.status_code == 200
    assert "No skill versions are available" in globex_available.text
    assert installed.status_code == 303
    assert "blocked" in blocked_detail.text
    assert configured.status_code == 200
    assert "ready" in configured.text
    assert "Stale Revision Conflict" in stale.text
    assert denied.status_code == 403


def test_browser_skill_registry_error_and_secondary_routes(
    tmp_path,
    monkeypatch,
) -> None:
    reset_skill_registry_service()
    _configure_env(monkeypatch, tmp_path)
    app = create_app()
    manifest = valid_skill_manifest()

    with TestClient(app) as client:
        create_form = client.get(
            "/admin/skill-registry/ui/packages/new",
            headers=PLATFORM_HEADERS,
        )
        invalid_create = client.post(
            "/admin/skill-registry/ui/packages",
            headers=PLATFORM_HEADERS,
            data={"slug": "", "display_name": ""},
        )
        created = client.post(
            "/admin/skill-registry/ui/packages",
            headers=PLATFORM_HEADERS,
            data={
                "slug": "calendar-assistant",
                "display_name": "Calendar Assistant",
                "description": "Safe calendar skill.",
                "owner_principal_id": "platform-admin",
            },
            follow_redirects=False,
        )
        duplicate = client.post(
            "/admin/skill-registry/ui/packages",
            headers=PLATFORM_HEADERS,
            data={
                "slug": "calendar-assistant",
                "display_name": "Calendar Assistant",
                "owner_principal_id": "platform-admin",
            },
        )
        missing_package = client.get(
            "/admin/skill-registry/ui/packages/missing",
            headers=PLATFORM_HEADERS,
        )
        missing_candidate = client.get(
            "/admin/skill-registry/ui/packages/missing/candidate",
            headers=PLATFORM_HEADERS,
        )
        invalid_candidate = client.post(
            "/admin/skill-registry/ui/packages/calendar-assistant/candidate",
            headers=PLATFORM_HEADERS,
            data={"manifest": "", "artifact_digest": ""},
        )
        candidate = client.post(
            "/admin/skill-registry/ui/packages/calendar-assistant/candidate",
            headers=PLATFORM_HEADERS,
            data={
                "manifest": json.dumps(manifest),
                "artifact_digest": "sha256:artifact",
                "approved_integration_refs": "tool:calendar:v1",
            },
            follow_redirects=True,
        )
        stale_validate = client.post(
            "/admin/skill-registry/ui/packages/calendar-assistant/candidate/validate",
            headers=PLATFORM_HEADERS,
            data={"revision_token": "stale"},
            follow_redirects=False,
        )
        token = _extract_value(candidate.text, "revision_token")
        validated = client.post(
            "/admin/skill-registry/ui/packages/calendar-assistant/candidate/validate",
            headers=PLATFORM_HEADERS,
            data={"revision_token": token},
            follow_redirects=True,
        )
        stale_publish = client.post(
            "/admin/skill-registry/ui/packages/calendar-assistant/candidate/publish",
            headers=PLATFORM_HEADERS,
            data={"revision_token": "stale"},
            follow_redirects=False,
        )
        publish_token = _extract_value(validated.text, "revision_token")
        published = client.post(
            "/admin/skill-registry/ui/packages/calendar-assistant/candidate/publish",
            headers=PLATFORM_HEADERS,
            data={"revision_token": publish_token},
            follow_redirects=False,
        )
        missing_version = client.get(
            "/admin/skill-registry/ui/packages/calendar-assistant/versions/9.9.9",
            headers=PLATFORM_HEADERS,
        )
        grant_form = client.get(
            "/admin/skill-registry/ui/packages/calendar-assistant/versions/1.2.3/grants",
            headers=PLATFORM_HEADERS,
        )
        empty_grant = client.post(
            "/admin/skill-registry/ui/packages/calendar-assistant/versions/1.2.3/grants",
            headers=PLATFORM_HEADERS,
            data={"tenant_ids": ""},
        )
        granted = client.post(
            "/admin/skill-registry/ui/packages/calendar-assistant/versions/1.2.3/grants",
            headers=PLATFORM_HEADERS,
            data={"tenant_ids": ACME_TENANT_ID, "grant_reason": "QA"},
            follow_redirects=True,
        )
        installation_list_empty = client.get(
            f"/admin/skill-registry/ui/installations?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
        )
        invalid_install = client.post(
            "/admin/skill-registry/ui/installations",
            headers=ACME_HEADERS,
            data={"tenant_id": ACME_TENANT_ID},
        )
        installed = client.post(
            "/admin/skill-registry/ui/installations",
            headers=ACME_HEADERS,
            data={
                "tenant_id": ACME_TENANT_ID,
                "slug": "calendar-assistant",
                "semantic_version": "1.2.3",
            },
            follow_redirects=False,
        )
        installation_path = installed.headers["location"]
        credentials_page = client.get(
            f"{installation_path}/credentials",
            headers=ACME_HEADERS,
        )
        detail = client.get(installation_path, headers=ACME_HEADERS)
        revision_token = _extract_value(detail.text, "revision_token")
        invalid_credentials = client.post(
            f"{installation_path}/credentials",
            headers=ACME_HEADERS,
            data={"revision_token": ""},
        )
        stale_smoke = client.post(
            f"{installation_path}/smoke-tests",
            headers=ACME_HEADERS,
            data={"revision_token": "stale"},
            follow_redirects=False,
        )
        smoke = client.post(
            f"{installation_path}/smoke-tests",
            headers=ACME_HEADERS,
            data={"revision_token": revision_token},
            follow_redirects=False,
        )
        detail_after_smoke = client.get(installation_path, headers=ACME_HEADERS)
        eligibility = client.post(
            f"{installation_path}/eligibility-preview",
            headers=ACME_HEADERS,
            data={
                "revision_token": _extract_value(
                    detail_after_smoke.text,
                    "revision_token",
                ),
                "context_type": "profile",
                "context_id": "qa-profile",
            },
            follow_redirects=False,
        )
        missing_installation = client.get(
            "/admin/skill-registry/ui/installations/missing",
            headers=ACME_HEADERS,
        )

    assert create_form.status_code == 200
    assert "Package Identity" in create_form.text
    assert invalid_create.status_code == 422
    assert "Slug is required" in invalid_create.text
    assert created.status_code == 303
    assert duplicate.status_code == 422
    assert "already exists" in duplicate.text
    assert missing_package.status_code == 404
    assert missing_candidate.status_code == 404
    assert invalid_candidate.status_code == 422
    assert stale_validate.status_code == 303
    assert stale_validate.headers["location"].endswith("conflict=stale")
    assert stale_publish.status_code == 303
    assert stale_publish.headers["location"].endswith("conflict=stale")
    assert published.status_code == 303
    assert missing_version.status_code == 404
    assert grant_form.status_code == 200
    assert "Current Grants" in grant_form.text
    assert empty_grant.status_code == 422
    assert granted.status_code == 200
    assert installation_list_empty.status_code == 200
    assert "No installed skills" in installation_list_empty.text
    assert invalid_install.status_code == 422
    assert credentials_page.status_code == 200
    assert "Credential References" in credentials_page.text
    assert invalid_credentials.status_code == 422
    assert stale_smoke.status_code == 303
    assert stale_smoke.headers["location"].endswith("conflict=stale")
    assert smoke.status_code == 303
    assert eligibility.status_code == 303
    assert missing_installation.status_code == 404


def _extract_value(html: str, name: str) -> str:
    needle = f'name="{name}" value="'
    start = html.index(needle) + len(needle)
    end = html.index('"', start)
    return html[start:end]
