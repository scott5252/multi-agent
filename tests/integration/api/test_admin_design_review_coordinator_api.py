from __future__ import annotations

from pathlib import Path
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from multi_agent_platform.api.main import create_app
from multi_agent_platform.db.models.workflow_registry import WorkflowVersionBundle
from tests.integration.api.test_admin_design_review_api import (
    ACME_HEADERS,
    ACME_TENANT_ID,
    GLOBEX_HEADERS,
    _configure_env,
)
from tests.unit.runtime.orchestration.test_graph_execution import simple_graph_document


def _seed_workflow_bundle(tmp_path: Path) -> str:
    workflow_version_bundle_id = uuid4()
    engine = create_engine(f"sqlite:///{tmp_path / 'design-review.db'}")
    with Session(engine) as session:
        session.add(
            WorkflowVersionBundle(
                workflow_version_bundle_id=workflow_version_bundle_id,
                workflow_lineage_id=uuid4(),
                scope_type="tenant",
                tenant_id=UUID(ACME_TENANT_ID),
                version_sequence=1,
                display_version="v1",
                published_from_draft_id=uuid4(),
                published_from_revision_id=uuid4(),
                published_by_principal_id=uuid4(),
                summary_json={"document": simple_graph_document()},
            )
        )
        session.commit()
    return str(workflow_version_bundle_id)


def _create_session(client: TestClient, workflow_version_bundle_id: str):
    return client.post(
        "/admin/design-reviews/sessions",
        headers=ACME_HEADERS,
        json={
            "tenant_id": ACME_TENANT_ID,
            "request_summary": "Review checkout redesign for coordinator QA.",
            "quorum_policy_key": "four_of_five_no_blockers",
            "workflow_version_bundle_id": workflow_version_bundle_id,
            "idempotency_key": "qa062-create-session",
        },
    )


def _reviewers() -> list[dict[str, object]]:
    return [
        {
            "reviewer_key": f"reviewer-{index}",
            "role_key": f"reviewer-role-{index}",
            "enabled": True,
        }
        for index in range(5)
    ]


def _verdicts(approved_count: int) -> list[dict[str, object]]:
    return [
        {
            "reviewer_key": f"reviewer-{index}",
            "verdict": "approved" if index < approved_count else "changes_requested",
            "score": 5 if index < approved_count else 3,
            "blocking_issue_count": 0,
            "safe_feedback_summary": f"Safe reviewer {index} feedback.",
            "output_digest": f"digest-{index}",
        }
        for index in range(5)
    ]


def test_coordinator_launch_state_and_completion_api(tmp_path, monkeypatch) -> None:
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
                "idempotency_key": "qa062-launch",
            },
        )
        replay = client.post(
            f"/admin/design-reviews/sessions/{session_id}/coordinator/launch-round",
            headers=ACME_HEADERS,
            json={
                "tenant_id": ACME_TENANT_ID,
                "workflow_version_bundle_id": workflow_version_bundle_id,
                "reviewers": _reviewers(),
                "idempotency_key": "qa062-launch",
            },
        )
        round_id = launch.json()["round"]["design_review_round_id"]
        state = client.get(
            f"/admin/design-reviews/sessions/{session_id}/coordinator"
            f"?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
        )
        complete = client.post(
            f"/admin/design-reviews/rounds/{round_id}/coordinator/complete",
            headers=ACME_HEADERS,
            json={
                "tenant_id": ACME_TENANT_ID,
                "verdicts": _verdicts(approved_count=4),
                "safe_synthesis_summary": "Council approves handoff.",
                "idempotency_key": "qa062-complete",
            },
        )

    assert created.status_code == 201
    assert launch.status_code == 201
    assert replay.status_code == 200
    assert replay.json()["replayed"] is True
    assert launch.json()["workflow_run_id"]
    assert state.json()["latest_round"]["design_review_round_id"] == round_id
    assert complete.status_code == 200
    assert complete.json()["quorum_decision"]["status"] == "passed"
    assert complete.json()["handoff"]["state"]["kind"] == "ready"
    assert complete.json()["session"]["status"] == "approved"
    assert "Authorization:" not in complete.text


def test_coordinator_cross_tenant_denial(tmp_path, monkeypatch) -> None:
    _configure_env(monkeypatch, tmp_path)
    workflow_version_bundle_id = _seed_workflow_bundle(tmp_path)
    app = create_app()

    with TestClient(app) as client:
        created = _create_session(client, workflow_version_bundle_id)
        session_id = created.json()["design_review_session_id"]
        denied = client.post(
            f"/admin/design-reviews/sessions/{session_id}/coordinator/launch-round",
            headers=GLOBEX_HEADERS,
            json={
                "tenant_id": ACME_TENANT_ID,
                "workflow_version_bundle_id": workflow_version_bundle_id,
                "reviewers": _reviewers(),
                "idempotency_key": "qa062-denied",
            },
        )

    assert denied.status_code == 403
