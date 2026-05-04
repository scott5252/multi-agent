from __future__ import annotations

from fastapi.testclient import TestClient

from multi_agent_platform.api.main import create_app
from multi_agent_platform.channels.telegram_delivery import MockTelegramBotApiClient
from tests.integration.api.test_channel_run_api import (
    ACME_TENANT_ID,
    acme_headers,
    configure_channel_env,
)


def test_telegram_webhook_link_run_status_and_duplicate(tmp_path, monkeypatch) -> None:
    configure_channel_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        token = client.post(
            "/channels/telegram/link-token",
            headers=acme_headers(),
        ).json()["link_token"]
        linked = client.post(
            "/channels/telegram/webhook/local-dev-secret",
            json={
                "update_id": 1001,
                "message": {
                    "chat": {"id": 12345},
                    "from": {"id": 67890},
                    "text": f"/link {token}",
                },
            },
        )
        started = client.post(
            "/channels/telegram/webhook/local-dev-secret",
            json={
                "update_id": 1002,
                "message": {
                    "chat": {"id": 12345},
                    "from": {"id": 67890},
                    "text": "/run demo hello",
                },
            },
        )
        duplicate = client.post(
            "/channels/telegram/webhook/local-dev-secret",
            json={
                "update_id": 1002,
                "message": {
                    "chat": {"id": 12345},
                    "from": {"id": 67890},
                    "text": "/run demo hello",
                },
            },
        )
        run_id = started.json()["run_id"]
        status = client.post(
            "/channels/telegram/webhook/local-dev-secret",
            json={
                "update_id": 1003,
                "message": {
                    "chat": {"id": 12345},
                    "from": {"id": 67890},
                    "text": f"/status {run_id}",
                },
            },
        )
        unlinked = client.post(
            "/channels/telegram/webhook/local-dev-secret",
            json={
                "update_id": 1004,
                "message": {
                    "chat": {"id": 999},
                    "from": {"id": 888},
                    "text": f"/status {run_id}",
                },
            },
        )

    assert linked.json()["ok"] is True
    assert duplicate.json() == started.json()
    assert status.json()["state"] == "queued"
    assert unlinked.json()["error_category"] == "unauthorized"


def test_telegram_webhook_routes_alias_and_persists_delivery(
    tmp_path,
    monkeypatch,
) -> None:
    configure_channel_env(monkeypatch, tmp_path)
    app = create_app()
    mock_client = MockTelegramBotApiClient()

    with TestClient(app) as client:
        client.app.state.container.state["telegram_bot_client"] = mock_client
        config = client.get(
            f"/admin/telegram/api/config?tenant_id={ACME_TENANT_ID}",
            headers=acme_headers(),
        )
        client.post(
            "/admin/telegram/api/config",
            headers=acme_headers(),
            json={
                "tenant_id": str(ACME_TENANT_ID),
                "enabled": True,
                "protected_commands": ["/run", "/status"],
                "revision_token": config.json()["revision_token"],
            },
        )
        client.post(
            "/admin/telegram/api/aliases",
            headers=acme_headers(),
            json={
                "tenant_id": str(ACME_TENANT_ID),
                "alias_text": "Morning briefing",
                "published_workflow_version_id": "22222222-2222-2222-2222-222222222222",
                "description": "Daily Intelligence Briefing",
                "protected": True,
                "enabled": True,
            },
        )
        issued = client.post(
            f"/admin/telegram/api/link-tokens?tenant_id={ACME_TENANT_ID}",
            headers=acme_headers(),
        )
        raw_token = issued.json()["link_token"]
        linked = client.post(
            "/channels/telegram/webhook/local-dev-secret",
            json={
                "update_id": 22001,
                "message": {
                    "chat": {"id": 123456789},
                    "from": {"id": 987654321},
                    "text": f"/link {raw_token}",
                },
            },
        )
        triggered = client.post(
            "/channels/telegram/webhook/local-dev-secret",
            json={
                "update_id": 22002,
                "message": {
                    "chat": {"id": 123456789},
                    "from": {"id": 987654321},
                    "text": "Morning briefing",
                },
            },
        )
        duplicate = client.post(
            "/channels/telegram/webhook/local-dev-secret",
            json={
                "update_id": 22002,
                "message": {
                    "chat": {"id": 123456789},
                    "from": {"id": 987654321},
                    "text": "Morning briefing",
                },
            },
        )

    assert linked.json()["ok"] is True
    assert triggered.status_code == 200
    assert triggered.json()["alias"] == "Morning briefing"
    assert triggered.json()["delivered"] is True
    assert duplicate.json() == triggered.json()
    assert len(mock_client.sent_messages) == 1
    assert mock_client.sent_messages[0].chat_id == 123456789
    assert "Daily Intelligence Briefing" in mock_client.sent_messages[0].text


def test_telegram_webhook_rejects_disabled_config_for_alias(
    tmp_path,
    monkeypatch,
) -> None:
    configure_channel_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        client.app.state.container.state["telegram_bot_client"] = (
            MockTelegramBotApiClient()
        )
        client.post(
            "/admin/telegram/api/aliases",
            headers=acme_headers(),
            json={
                "tenant_id": str(ACME_TENANT_ID),
                "alias_text": "Morning briefing",
                "published_workflow_version_id": "22222222-2222-2222-2222-222222222222",
                "enabled": True,
            },
        )
        issued = client.post(
            f"/admin/telegram/api/link-tokens?tenant_id={ACME_TENANT_ID}",
            headers=acme_headers(),
        )
        client.post(
            "/channels/telegram/webhook/local-dev-secret",
            json={
                "update_id": 22003,
                "message": {
                    "chat": {"id": 123456789},
                    "from": {"id": 987654321},
                    "text": f"/link {issued.json()['link_token']}",
                },
            },
        )
        denied = client.post(
            "/channels/telegram/webhook/local-dev-secret",
            json={
                "update_id": 22004,
                "message": {
                    "chat": {"id": 123456789},
                    "from": {"id": 987654321},
                    "text": "Morning briefing",
                },
            },
        )

    assert denied.json()["error_category"] == "unavailable_channel_delivery"
