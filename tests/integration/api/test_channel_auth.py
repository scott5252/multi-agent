from __future__ import annotations

from fastapi.testclient import TestClient

from multi_agent_platform.api.main import create_app
from tests.integration.api.test_channel_run_api import (
    acme_headers,
    configure_channel_env,
)


def test_channel_api_requires_authenticated_local_principal(
    tmp_path, monkeypatch
) -> None:
    configure_channel_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        response = client.post(
            "/runs",
            headers={"X-Idempotency-Key": "idem-auth-missing"},
            json={
                "workflow_id": "demo",
                "inputs": {"topic": "auth"},
                "channel": "web_api",
            },
        )

    assert response.status_code == 401


def test_channel_api_hides_cross_tenant_runs(tmp_path, monkeypatch) -> None:
    configure_channel_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        started = client.post(
            "/runs",
            headers=acme_headers("idem-auth-cross"),
            json={
                "workflow_id": "demo",
                "inputs": {"topic": "auth"},
                "channel": "web_api",
            },
        )
        run_id = started.json()["run_id"]
        response = client.get(
            f"/runs/{run_id}/status",
            headers={"X-Local-Principal": "tenant-admin-globex"},
        )

    assert response.status_code == 404
    assert response.json()["error"]["category"] == "invalid_run_id"
