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
        index = client.get("/runs", headers=acme_headers(), follow_redirects=False)
        new = client.get(
            "/runs/new?tenant_id=11111111-1111-1111-1111-111111111111&unsafe=raw",
            headers=acme_headers(),
            follow_redirects=False,
        )
        started = client.post(
            "/runs",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            data={"workflow_id": "web-ui-demo", "input": "hello"},
            follow_redirects=False,
        )
        detail = client.get(
            started.headers["location"],
            headers=acme_headers(),
            follow_redirects=False,
        )
        events = client.get(
            f"{started.headers['location']}/events",
            headers=acme_headers(),
        )

    assert index.status_code == 303
    assert index.headers["location"] == "/admin/app/channels/runs"
    assert new.status_code == 303
    assert (
        new.headers["location"]
        == "/admin/app/channels/runs?tenant_id=11111111-1111-1111-1111-111111111111"
    )
    assert started.status_code == 303
    assert started.headers["location"].startswith("/runs/")
    assert detail.status_code == 303
    assert detail.headers["location"].startswith("/admin/app/channels/runs/")
    assert "text/event-stream" in events.headers["content-type"]
