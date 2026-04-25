from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from multi_agent_platform.api.main import create_app
from tests.integration.api.test_channel_run_api import (
    acme_headers,
    configure_channel_env,
)


def test_channel_openapi_contract_contains_required_paths() -> None:
    contract_text = Path(
        "specs/006-user-interaction-channels/contracts/channel-layer.openapi.yaml"
    ).read_text()

    assert "  /runs:" in contract_text
    assert "  /runs/{run_id}/status:" in contract_text
    assert "  /runs/{run_id}/events:" in contract_text
    assert "  /runs/{run_id}/artifacts/{artifact_id}/download-url:" in contract_text


def test_run_start_contract_responses(tmp_path, monkeypatch) -> None:
    configure_channel_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        missing_input = client.post(
            "/runs",
            headers=acme_headers("idem-contract-missing"),
            json={
                "workflow_id": "demo",
                "inputs": {},
                "channel": "web_api",
            },
        )
        accepted = client.post(
            "/runs",
            headers=acme_headers("idem-contract-accepted"),
            json={
                "workflow_id": "demo",
                "inputs": {"topic": "contract"},
                "channel": "web_api",
            },
        )
        run_id = accepted.json()["run_id"]
        status = client.get(f"/runs/{run_id}/status", headers=acme_headers())
        timeline = client.get(f"/runs/{run_id}/timeline", headers=acme_headers())
        events = client.get(f"/runs/{run_id}/events", headers=acme_headers())
        result = client.get(f"/runs/{run_id}/result", headers=acme_headers())

    assert missing_input.status_code == 400
    assert missing_input.json()["error"]["category"] == "missing_input"
    assert accepted.status_code == 202
    assert {"run_id", "state", "status_url", "trace_id"} <= set(accepted.json())
    assert {"run_id", "state", "permitted_actions"} <= set(status.json())
    assert "items" in timeline.json()
    assert "text/event-stream" in events.headers["content-type"]
    assert result.json()["availability"] == "unavailable"
