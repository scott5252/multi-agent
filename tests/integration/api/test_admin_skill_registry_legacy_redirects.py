from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from multi_agent_platform.api.main import create_app
from multi_agent_platform.api.routers.admin_skill_registry import (
    reset_skill_registry_service,
)
from tests.integration.api.skill_registry_test_support import (
    ACME_HEADERS,
    ACME_TENANT_ID,
    GLOBEX_TENANT_ID,
    PLATFORM_HEADERS,
    configure_skill_registry_env,
)


def test_platform_package_legacy_routes_redirect_to_react(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    reset_skill_registry_service()
    configure_skill_registry_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        routes = {
            "/admin/skill-registry/ui/packages?state=published": (
                "/admin/app/skills/packages?state=published"
            ),
            "/admin/skill-registry/ui/packages/new": ("/admin/app/skills/packages/new"),
            "/admin/skill-registry/ui/packages/calendar-assistant": (
                "/admin/app/skills/packages/calendar-assistant"
            ),
            "/admin/skill-registry/ui/packages/calendar-assistant/candidate": (
                "/admin/app/skills/packages/calendar-assistant/candidate"
            ),
            (
                "/admin/skill-registry/ui/packages/calendar-assistant/versions/1.2.3"
            ): "/admin/app/skills/packages/calendar-assistant/versions/1.2.3",
            (
                "/admin/skill-registry/ui/packages/calendar-assistant/"
                "versions/1.2.3/grants?tenant_id=acme"
            ): (
                "/admin/app/skills/packages/calendar-assistant/"
                "versions/1.2.3/grants?tenant_id=acme"
            ),
        }
        responses = {
            source: client.get(
                source,
                headers=PLATFORM_HEADERS,
                follow_redirects=False,
            )
            for source in routes
        }

    for source, response in responses.items():
        assert response.status_code == 303, source
        assert response.headers["location"] == routes[source]
        assert "skill_registry/" not in response.text


def test_tenant_installation_legacy_routes_redirect_or_deny_without_jinja(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    reset_skill_registry_service()
    configure_skill_registry_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        available = client.get(
            (
                "/admin/skill-registry/ui/available-versions"
                f"?tenant_id={ACME_TENANT_ID}&status=ready"
            ),
            headers=ACME_HEADERS,
            follow_redirects=False,
        )
        installation_list = client.get(
            f"/admin/skill-registry/ui/installations?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
            follow_redirects=False,
        )
        installation_detail = client.get(
            "/admin/skill-registry/ui/installations/install-qa042",
            headers=ACME_HEADERS,
            follow_redirects=False,
        )
        credentials = client.get(
            (
                "/admin/skill-registry/ui/installations/install-qa042/"
                "credentials?conflict=stale"
            ),
            headers=ACME_HEADERS,
            follow_redirects=False,
        )
        cross_tenant = client.get(
            (
                "/admin/skill-registry/ui/available-versions"
                f"?tenant_id={GLOBEX_TENANT_ID}"
            ),
            headers=ACME_HEADERS,
            follow_redirects=False,
        )

    assert available.status_code == 303
    assert available.headers["location"] == (
        f"/admin/app/skills/available-versions?tenant_id={ACME_TENANT_ID}&status=ready"
    )
    assert installation_list.status_code == 303
    assert installation_list.headers["location"] == (
        f"/admin/app/skills/installations?tenant_id={ACME_TENANT_ID}"
    )
    assert installation_detail.status_code == 303
    assert installation_detail.headers["location"] == (
        "/admin/app/skills/installations/install-qa042"
    )
    assert credentials.status_code == 303
    assert credentials.headers["location"] == (
        "/admin/app/skills/installations/install-qa042/credentials?conflict=stale"
    )
    assert cross_tenant.status_code == 403
    assert "Globex" not in cross_tenant.text
    assert "skill_registry/" not in cross_tenant.text
