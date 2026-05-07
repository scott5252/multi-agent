from __future__ import annotations

from fastapi.testclient import TestClient

from multi_agent_platform.api.main import create_app
from tests.integration.api.test_admin_telegram_api import (
    ACME_HEADERS,
    ACME_TENANT_ID,
    _configure_env,
)


def test_telegram_ui_renders_console_and_mutates_config(
    tmp_path,
    monkeypatch,
) -> None:
    _configure_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        page = client.get(
            f"/admin/telegram?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
            follow_redirects=False,
        )
        config = client.get(
            f"/admin/telegram/api/config?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
        )
        revision = config.json()["revision_token"]
        updated = client.post(
            "/admin/telegram/config",
            headers=ACME_HEADERS,
            data={
                "tenant_id": ACME_TENANT_ID,
                "enabled": "true",
                "protected_commands": ["/run", "/status"],
                "status_note": "Ready for QA",
                "revision_token": revision,
            },
            follow_redirects=False,
        )
        stale = client.post(
            "/admin/telegram/config",
            headers=ACME_HEADERS,
            data={
                "tenant_id": ACME_TENANT_ID,
                "enabled": "false",
                "protected_commands": ["/run"],
                "revision_token": revision,
            },
        )

    assert page.status_code == 303
    assert page.headers["location"] == (
        f"/admin/app/channels?tenant_id={ACME_TENANT_ID}&panel=telegram"
    )
    assert updated.status_code == 303
    assert updated.headers["location"] == (
        f"/admin/app/channels?tenant_id={ACME_TENANT_ID}&panel=telegram"
    )
    assert stale.status_code == 409
    assert "stale revision" in stale.text


def test_telegram_ui_issues_link_token_once(tmp_path, monkeypatch) -> None:
    _configure_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        issued = client.post(
            "/admin/telegram/link-tokens",
            headers=ACME_HEADERS,
            data={"tenant_id": ACME_TENANT_ID},
        )
        listed = client.get(
            f"/admin/telegram/api/link-tokens?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
        )

    assert issued.status_code == 201
    assert issued.json()["link_token"]
    assert (
        issued.json()["token_audit"]["token_fingerprint"] != issued.json()["link_token"]
    )
    assert issued.json()["link_token"] not in listed.text


def test_telegram_ui_creates_alias(tmp_path, monkeypatch) -> None:
    _configure_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        created = client.post(
            "/admin/telegram/aliases",
            headers=ACME_HEADERS,
            data={
                "tenant_id": ACME_TENANT_ID,
                "alias_text": "Morning briefing",
                "published_workflow_version_id": "22222222-2222-2222-2222-222222222222",
                "description": "Daily Intelligence Briefing",
                "protected": "true",
                "enabled": "true",
            },
            follow_redirects=False,
        )
        page = client.get(
            f"/admin/telegram/api/aliases?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
        )

    assert created.status_code == 303
    assert created.headers["location"] == (
        f"/admin/app/channels?tenant_id={ACME_TENANT_ID}&panel=aliases"
    )
    assert "Morning briefing" in page.text
    assert "22222222-2222-2222-2222-222222222222" in page.text
