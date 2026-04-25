from __future__ import annotations

from fastapi.testclient import TestClient

from multi_agent_platform.api.main import create_app
from tests.integration.api.test_channel_run_api import (
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
