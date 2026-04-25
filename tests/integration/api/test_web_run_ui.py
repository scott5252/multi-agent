from __future__ import annotations

from fastapi.testclient import TestClient

from multi_agent_platform.api.main import create_app
from tests.integration.api.test_channel_run_api import (
    acme_headers,
    configure_channel_env,
)


def test_web_run_ui_lists_starts_and_renders_detail(tmp_path, monkeypatch) -> None:
    configure_channel_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        index = client.get("/runs", headers=acme_headers())
        started = client.post(
            "/runs",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            data={"workflow_id": "web-ui-demo", "input": "hello"},
            follow_redirects=False,
        )
        detail = client.get(started.headers["location"], headers=acme_headers())
        events = client.get(
            f"{started.headers['location']}/events",
            headers=acme_headers(),
        )

    assert index.status_code == 200
    assert "Workflow Runs" in index.text
    assert started.status_code == 303
    assert "Run Details" in detail.text
    assert "text/event-stream" in events.headers["content-type"]
