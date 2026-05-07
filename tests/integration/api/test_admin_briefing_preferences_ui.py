from __future__ import annotations

import json

from fastapi.testclient import TestClient

from multi_agent_platform.api.main import create_app
from tests.integration.api.test_admin_briefing_preferences_api import (
    ACME_HEADERS,
    ACME_TENANT_ID,
    PLATFORM_HEADERS,
    _configure_env,
)


def test_briefing_preferences_ui_saves_profile_and_masks_admin_summary(
    tmp_path,
    monkeypatch,
) -> None:
    _configure_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        page = client.get(
            f"/admin/briefing-preferences?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
            follow_redirects=False,
        )
        saved = client.post(
            "/admin/briefing-preferences",
            headers=ACME_HEADERS,
            data={
                "tenant_id": ACME_TENANT_ID,
                "location_label": "Providence, RI",
                "timezone": "America/New_York",
                "news_topics": "AI, markets",
                "vip_senders": "sarah@example.com",
                "workday_start": "09:00",
                "workday_end": "17:30",
                "commute_mode": "driving",
                "calendar_account_ref": "delegated:calendar:primary",
                "email_account_ref": "delegated:gmail:primary",
                "output_style": "standard",
                "scheduled_enabled": "true",
                "scheduled_time": "08:00",
            },
            follow_redirects=False,
        )
        admin_summary = client.get(
            f"/admin/briefing-preferences/api/summaries?tenant_id={ACME_TENANT_ID}",
            headers=PLATFORM_HEADERS,
        )

    assert page.status_code == 303
    assert page.headers["location"] == (
        f"/admin/app/channels?tenant_id={ACME_TENANT_ID}&panel=briefing"
    )
    assert saved.status_code == 303
    assert saved.headers["location"] == (
        f"/admin/app/channels?tenant_id={ACME_TENANT_ID}&panel=briefing"
    )
    assert "sarah@example.com" not in admin_summary.text
    assert "s***@example.com" in admin_summary.text
    assert "delegated:calendar:primary" not in admin_summary.text


def test_briefing_preferences_ui_export_import_and_error_states(
    tmp_path,
    monkeypatch,
) -> None:
    _configure_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        platform_page = client.get(
            "/admin/briefing-preferences",
            headers=PLATFORM_HEADERS,
            follow_redirects=False,
        )
        saved = client.post(
            "/admin/briefing-preferences",
            headers=ACME_HEADERS,
            data={
                "tenant_id": ACME_TENANT_ID,
                "location_label": "Providence, RI",
                "timezone": "America/New_York",
                "news_topics": "AI, markets",
                "vip_senders": "sarah@example.com",
                "workday_start": "09:00",
                "workday_end": "17:30",
                "commute_mode": "driving",
                "calendar_account_ref": "delegated:calendar:primary",
                "email_account_ref": "delegated:gmail:primary",
                "output_style": "standard",
                "scheduled_enabled": "true",
                "scheduled_time": "08:00",
            },
            follow_redirects=False,
        )
        exported = client.get(
            f"/admin/briefing-preferences/api/export?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
        )
        old_export = client.get(
            f"/admin/briefing-preferences/export?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
            follow_redirects=False,
        )
        document = exported.json()["document"]
        document["preferences"]["output_style"] = "executive"
        imported = client.post(
            "/admin/briefing-preferences/import",
            headers=ACME_HEADERS,
            data={
                "tenant_id": ACME_TENANT_ID,
                "import_document": json.dumps(document),
            },
            follow_redirects=False,
        )
        invalid_form = client.post(
            "/admin/briefing-preferences",
            headers=ACME_HEADERS,
            data={
                "tenant_id": ACME_TENANT_ID,
                "location_label": "Providence, RI",
                "timezone": "Mars/Base",
                "calendar_account_ref": "delegated:calendar:primary",
                "email_account_ref": "delegated:gmail:primary",
            },
        )
        invalid_import = client.post(
            "/admin/briefing-preferences/import",
            headers=ACME_HEADERS,
            data={
                "tenant_id": ACME_TENANT_ID,
                "import_document": "[]",
            },
        )

    assert platform_page.status_code == 303
    assert platform_page.headers["location"] == "/admin/app/channels?panel=briefing"
    assert saved.status_code == 303
    assert exported.status_code == 200
    assert old_export.status_code == 303
    assert old_export.headers["location"] == (
        f"/admin/app/channels?tenant_id={ACME_TENANT_ID}&panel=briefing-export"
    )
    assert imported.status_code == 303
    assert imported.headers["location"] == (
        f"/admin/app/channels?tenant_id={ACME_TENANT_ID}&panel=briefing-import"
    )
    assert invalid_form.status_code == 422
    assert "timezone must be a valid IANA timezone" in invalid_form.text
    assert invalid_import.status_code == 422
    assert "import document must be a JSON object" in invalid_import.text
