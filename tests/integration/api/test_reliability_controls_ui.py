from __future__ import annotations

from fastapi.testclient import TestClient

from multi_agent_platform.api.main import create_app
from multi_agent_platform.api.ui.reliability_controls import (
    reliability_breakers_filter_profile,
    reliability_dead_letters_filter_profile,
)
from tests.integration.api.test_admin_operations_api import (
    PLATFORM_HEADERS,
    _configure_env,
)


def test_reliability_ui_routes_redirect_to_react(tmp_path, monkeypatch) -> None:
    _configure_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        dashboard = client.get(
            "/admin/reliability/ui/?tenant_id=11111111-1111-1111-1111-111111111111",
            headers=PLATFORM_HEADERS,
            follow_redirects=False,
        )
        breakers = client.get(
            "/admin/reliability/ui/breakers?state=open",
            headers=PLATFORM_HEADERS,
            follow_redirects=False,
        )
        dead_letters = client.get(
            "/admin/reliability/ui/dead-letters?status=ready",
            headers=PLATFORM_HEADERS,
            follow_redirects=False,
        )

    assert dashboard.status_code == 303
    assert dashboard.headers["location"] == (
        "/admin/app/operations?"
        "tenant_id=11111111-1111-1111-1111-111111111111&panel=reliability"
    )
    assert breakers.status_code == 303
    assert breakers.headers["location"] == (
        "/admin/app/operations?state=open&panel=breakers"
    )
    assert dead_letters.status_code == 303
    assert dead_letters.headers["location"] == (
        "/admin/app/operations?status=ready&panel=dead-letters"
    )


def test_reliability_filter_profiles_point_to_shell_destinations() -> None:
    assert (
        reliability_breakers_filter_profile().destination_href
        == "/admin/app/operations?panel=breakers"
    )
    assert (
        reliability_dead_letters_filter_profile().destination_href
        == "/admin/app/operations?panel=dead-letters"
    )
