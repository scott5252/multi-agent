from __future__ import annotations

from fastapi.testclient import TestClient
from tests.integration.api.test_channel_run_api import (
    acme_headers,
    configure_channel_env,
)

from multi_agent_platform.api.main import create_app


def test_run_started_in_api_can_be_recovered_in_web_ui(tmp_path, monkeypatch) -> None:
    configure_channel_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        start = client.post(
            "/runs",
            headers=acme_headers("idem-cross-001"),
            json={
                "workflow_id": "cross-channel",
                "inputs": {"topic": "recover"},
                "channel": "web_api",
            },
        )
        run_id = start.json()["run_id"]
        web_detail = client.get(
            f"/runs/{run_id}",
            headers=acme_headers(),
            follow_redirects=False,
        )
        api_status = client.get(f"/runs/{run_id}/status", headers=acme_headers())

    assert web_detail.status_code == 303
    assert web_detail.headers["location"] == f"/admin/app/channels/runs/{run_id}"
    assert api_status.json()["state"] == "queued"
