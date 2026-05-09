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


def test_design_review_template_install_replay_and_workspace_state(
    tmp_path,
    monkeypatch,
) -> None:
    _configure_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        first = client.post(
            "/admin/design-reviews/templates/council/install",
            headers=ACME_HEADERS,
            json={
                "tenant_id": ACME_TENANT_ID,
                "idempotency_key": "qa064-install",
                "safe_mode": "both",
            },
        )
        second = client.post(
            "/admin/design-reviews/templates/council/install",
            headers=ACME_HEADERS,
            json={
                "tenant_id": ACME_TENANT_ID,
                "idempotency_key": "qa064-install",
                "safe_mode": "both",
            },
        )
        workspace = client.get(
            f"/admin/app/design-reviews/bootstrap.json?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
        )

    assert first.status_code == 201
    first_payload = first.json()
    assert first_payload["template_key"] == "design-reviewer-council"
    assert first_payload["required_evidence_status"] == "passing"
    assert first_payload["publish_gate_status"] == "ready"
    assert first_payload["ready_to_publish"] is True
    assert set(first_payload["evidence_modes"]) == {
        "deterministic",
        "model backed safe",
    }
    assert first_payload["deterministic_run_id"]
    assert first_payload["model_safe_run_id"]
    assert "raw prompt" not in first.text.lower()
    assert "Authorization:" not in first.text

    assert second.status_code == 200
    assert second.json()["replayed"] is True
    assert second.json()["workflow_draft_id"] == first_payload["workflow_draft_id"]

    assert workspace.status_code == 200
    setup = workspace.json()["template_setup"]
    assert setup["status"] == "ready"
    assert setup["ready_to_publish"] is True
    assert setup["workflow_draft_id"] == first_payload["workflow_draft_id"]
    assert workspace.json()["sessions"] == []


def test_design_review_template_install_cross_tenant_denial(
    tmp_path,
    monkeypatch,
) -> None:
    _configure_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        response = client.post(
            "/admin/design-reviews/templates/council/install",
            headers=GLOBEX_HEADERS,
            json={
                "tenant_id": ACME_TENANT_ID,
                "idempotency_key": "qa064-denied",
            },
        )
        own_tenant = client.post(
            "/admin/design-reviews/templates/council/install",
            headers=GLOBEX_HEADERS,
            json={
                "tenant_id": GLOBEX_TENANT_ID,
                "idempotency_key": "qa064-globex",
            },
        )

    assert response.status_code == 403
    assert "access denied" in response.text
    assert own_tenant.status_code == 201
