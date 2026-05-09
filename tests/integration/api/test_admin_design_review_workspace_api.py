from __future__ import annotations

from fastapi.testclient import TestClient

from multi_agent_platform.api.main import create_app
from tests.integration.api.test_admin_design_review_api import (
    ACME_HEADERS,
    ACME_TENANT_ID,
    GLOBEX_HEADERS,
    GLOBEX_TENANT_ID,
    _configure_env,
)
from tests.integration.api.test_admin_design_review_coordinator_api import (
    _create_session,
    _reviewers,
    _seed_workflow_bundle,
    _verdicts,
)


def test_design_review_workspace_empty_state(tmp_path, monkeypatch) -> None:
    _configure_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        response = client.get(
            f"/admin/app/design-reviews/bootstrap.json?tenant_id={GLOBEX_TENANT_ID}",
            headers=GLOBEX_HEADERS,
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["sessions"] == []
    assert payload["selected_session"] is None
    assert payload["state"]["state"] == "empty"
    assert payload["actions"]["create_session"]["href"] == (
        "/admin/design-reviews/sessions"
    )
    assert "fixture" not in response.text.lower()
    assert "mock" not in response.text.lower()


def test_design_review_workspace_live_session_detail(tmp_path, monkeypatch) -> None:
    _configure_env(monkeypatch, tmp_path)
    workflow_version_bundle_id = _seed_workflow_bundle(tmp_path)
    app = create_app()

    with TestClient(app) as client:
        created = _create_session(client, workflow_version_bundle_id)
        session_id = created.json()["design_review_session_id"]
        launch = client.post(
            f"/admin/design-reviews/sessions/{session_id}/coordinator/launch-round",
            headers=ACME_HEADERS,
            json={
                "tenant_id": ACME_TENANT_ID,
                "workflow_version_bundle_id": workflow_version_bundle_id,
                "reviewers": _reviewers(),
                "idempotency_key": "qa063-launch",
            },
        )
        round_id = launch.json()["round"]["design_review_round_id"]
        complete = client.post(
            f"/admin/design-reviews/rounds/{round_id}/coordinator/complete",
            headers=ACME_HEADERS,
            json={
                "tenant_id": ACME_TENANT_ID,
                "verdicts": _verdicts(approved_count=4),
                "safe_synthesis_summary": "Council approves workspace handoff.",
                "idempotency_key": "qa063-complete",
            },
        )
        response = client.get(
            f"/admin/app/design-reviews/bootstrap.json?tenant_id={ACME_TENANT_ID}"
            f"&session_id={session_id}",
            headers=ACME_HEADERS,
        )

    assert complete.status_code == 200
    assert response.status_code == 200
    payload = response.json()
    assert payload["sessions"][0]["design_review_session_id"] == session_id
    assert payload["selected_session"]["session"]["status"] == "approved"
    assert payload["selected_session"]["handoff"]["state"]["kind"] == "ready"
    assert payload["selected_session"]["rounds"][0]["quorum_decision"]["status"] == (
        "passed"
    )
    assert len(payload["selected_session"]["rounds"][0]["verdicts"]) == 5
    assert payload["workflow_options"][0]["workflow_version_bundle_id"] == (
        workflow_version_bundle_id
    )
    assert "Authorization:" not in response.text
    assert "raw prompt" not in response.text.lower()


def test_design_review_workspace_cross_tenant_denial(tmp_path, monkeypatch) -> None:
    _configure_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        response = client.get(
            f"/admin/app/design-reviews/bootstrap.json?tenant_id={ACME_TENANT_ID}",
            headers=GLOBEX_HEADERS,
        )

    assert response.status_code == 403
