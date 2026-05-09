from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from multi_agent_platform.api.main import create_app
from multi_agent_platform.db.base import Base
from multi_agent_platform.db.models import import_models
from multi_agent_platform.db.models.design_review import (
    DesignDevelopmentHandoff,
    DesignDevelopmentHandoffStatus,
    DesignQuorumDecision,
    DesignQuorumDecisionStatus,
    DesignQuorumNextAction,
    DesignReviewerAssignment,
    DesignReviewerVerdict,
    DesignReviewerVerdictValue,
    DesignReviewRound,
    DesignReviewRoundStatus,
)
from multi_agent_platform.db.models.tenant import Tenant

ACME_TENANT_ID = "11111111-1111-1111-1111-111111111111"
GLOBEX_TENANT_ID = "22222222-2222-2222-2222-222222222222"
ACME_HEADERS = {"X-Local-Principal": "tenant-admin-acme"}
GLOBEX_HEADERS = {"X-Local-Principal": "tenant-admin-globex"}
PLATFORM_HEADERS = {"X-Local-Principal": "platform-admin"}


def _configure_env(monkeypatch, tmp_path: Path) -> None:
    database_path = tmp_path / "design-review.db"
    import_models()
    engine = create_engine(f"sqlite:///{database_path}")
    Base.metadata.create_all(engine)
    with engine.begin() as connection:
        connection.execute(
            text(
                "CREATE TABLE IF NOT EXISTS alembic_version "
                "(version_num VARCHAR(64) NOT NULL)"
            )
        )
        connection.execute(
            text(
                "INSERT INTO alembic_version(version_num) "
                "VALUES ('0021_design_review_domain')"
            )
        )
    with Session(engine) as session:
        session.add_all(
            [
                Tenant(
                    tenant_id=UUID(ACME_TENANT_ID),
                    slug="acme",
                    display_name="Acme",
                ),
                Tenant(
                    tenant_id=UUID(GLOBEX_TENANT_ID),
                    slug="globex",
                    display_name="Globex",
                ),
            ]
        )
        session.commit()
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("AUTH_MODE", "local_principal")
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{database_path}")
    monkeypatch.setenv("FILESYSTEM_STORAGE_ROOT", str(tmp_path / "artifacts"))
    monkeypatch.setenv(
        "LOCAL_PRINCIPAL_CATALOG_JSON",
        json.dumps(
            {
                "platform-admin": {
                    "catalog_key": "platform-admin",
                    "display_name": "Platform Admin",
                    "role_codes": ["platform_admin"],
                    "permission_codes": ["platform:admin"],
                },
                "tenant-admin-acme": {
                    "catalog_key": "tenant-admin-acme",
                    "display_name": "Acme Tenant Admin",
                    "tenant_id": ACME_TENANT_ID,
                    "role_codes": ["tenant_user", "tenant_admin"],
                    "permission_codes": ["tenant:read", "tenant:admin"],
                },
                "tenant-admin-globex": {
                    "catalog_key": "tenant-admin-globex",
                    "display_name": "Globex Tenant Admin",
                    "tenant_id": GLOBEX_TENANT_ID,
                    "role_codes": ["tenant_user", "tenant_admin"],
                    "permission_codes": ["tenant:read", "tenant:admin"],
                },
            }
        ),
    )


def _create_session(client: TestClient):
    return client.post(
        "/admin/design-reviews/sessions",
        headers=ACME_HEADERS,
        json={
            "tenant_id": ACME_TENANT_ID,
            "request_summary": "Review checkout redesign for clarity.",
            "quorum_policy_key": "four_of_five_no_blockers",
            "idempotency_key": "qa060-create-session",
        },
    )


def test_design_review_session_create_replay_and_detail(tmp_path, monkeypatch) -> None:
    _configure_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        created = _create_session(client)
        replay = _create_session(client)
        session_id = created.json()["design_review_session_id"]
        listed = client.get(
            f"/admin/design-reviews/sessions?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
        )
        detail = client.get(
            f"/admin/design-reviews/sessions/{session_id}?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
        )
        revisions = client.get(
            f"/admin/design-reviews/sessions/{session_id}/revisions"
            f"?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
        )
        rounds = client.get(
            f"/admin/design-reviews/sessions/{session_id}/rounds"
            f"?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
        )
        handoff = client.get(
            f"/admin/design-reviews/sessions/{session_id}/handoff"
            f"?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
        )

    assert created.status_code == 201
    assert replay.status_code == 200
    assert replay.json()["replayed"] is True
    assert replay.json()["design_review_session_id"] == session_id
    assert listed.json()["items"][0]["design_review_session_id"] == session_id
    assert detail.json()["revisions"][0]["revision_number"] == 1
    assert revisions.json()["items"][0]["payload_digest"]
    assert rounds.json()["items"] == []
    assert handoff.json()["state"]["kind"] == "pending"
    assert "Authorization:" not in detail.text


def test_design_review_cross_tenant_and_empty_states(tmp_path, monkeypatch) -> None:
    _configure_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        created = _create_session(client)
        session_id = created.json()["design_review_session_id"]
        denied = client.get(
            f"/admin/design-reviews/sessions/{session_id}?tenant_id={ACME_TENANT_ID}",
            headers=GLOBEX_HEADERS,
        )
        hidden = client.get(
            f"/admin/design-reviews/sessions/{session_id}?tenant_id={GLOBEX_TENANT_ID}",
            headers=GLOBEX_HEADERS,
        )
        globex_empty = client.get(
            f"/admin/design-reviews/sessions?tenant_id={GLOBEX_TENANT_ID}",
            headers=GLOBEX_HEADERS,
        )
        platform_read = client.get(
            f"/admin/design-reviews/sessions/{session_id}?tenant_id={ACME_TENANT_ID}",
            headers=PLATFORM_HEADERS,
        )

    assert denied.status_code == 403
    assert hidden.status_code == 404
    assert globex_empty.status_code == 200
    assert globex_empty.json()["state"]["kind"] == "empty"
    assert platform_read.status_code == 200


def test_design_review_manual_decision_routes(tmp_path, monkeypatch) -> None:
    _configure_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        created = _create_session(client)
        session_id = created.json()["design_review_session_id"]
        manual = client.post(
            f"/admin/design-reviews/sessions/{session_id}/manual-decisions",
            headers=ACME_HEADERS,
            json={
                "tenant_id": ACME_TENANT_ID,
                "decision_type": "revise",
                "safe_rationale": "Ask for clearer accessibility notes.",
                "idempotency_key": "manual-decision-1",
            },
        )
        replay = client.post(
            f"/admin/design-reviews/sessions/{session_id}/manual-decisions",
            headers=ACME_HEADERS,
            json={
                "tenant_id": ACME_TENANT_ID,
                "decision_type": "revise",
                "safe_rationale": "Ask for clearer accessibility notes.",
                "idempotency_key": "manual-decision-1",
            },
        )
        listed = client.get(
            f"/admin/design-reviews/sessions/{session_id}/manual-decisions"
            f"?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
        )

    assert manual.status_code == 201
    assert replay.status_code == 200
    assert replay.json()["replayed"] is True
    assert listed.json()["items"][0]["decision_type"] == "revise"
    assert listed.json()["state"]["kind"] == "ready"


def test_design_review_round_quorum_and_handoff_routes(tmp_path, monkeypatch) -> None:
    _configure_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        created = _create_session(client)
        session_id = created.json()["design_review_session_id"]
        revision_id = created.json()["current_revision"]["design_revision_id"]
        round_id = _seed_round_evidence(
            tmp_path=tmp_path,
            session_id=session_id,
            revision_id=revision_id,
        )
        rounds = client.get(
            f"/admin/design-reviews/sessions/{session_id}/rounds"
            f"?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
        )
        round_detail = client.get(
            f"/admin/design-reviews/rounds/{round_id}?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
        )
        quorum = client.get(
            f"/admin/design-reviews/rounds/{round_id}/quorum-decision"
            f"?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
        )
        handoff = client.get(
            f"/admin/design-reviews/sessions/{session_id}/handoff"
            f"?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
        )
        manual = client.post(
            f"/admin/design-reviews/sessions/{session_id}/manual-decisions",
            headers=ACME_HEADERS,
            json={
                "tenant_id": ACME_TENANT_ID,
                "round_id": round_id,
                "decision_type": "approve_exception",
                "safe_rationale": "Accept limited risk with clear follow-up.",
                "accepted_risk": True,
                "idempotency_key": "manual-round-decision",
            },
        )

    assert rounds.status_code == 200
    assert rounds.json()["items"][0]["design_review_round_id"] == round_id
    assert round_detail.status_code == 200
    assert round_detail.json()["assignments"][0]["reviewer_key"] == "accessibility"
    assert round_detail.json()["verdicts"][0]["verdict"] == "approved"
    assert round_detail.json()["quorum_decision"]["next_action"] == "handoff"
    assert quorum.status_code == 200
    assert quorum.json()["state"]["kind"] == "ready"
    assert handoff.status_code == 200
    assert handoff.json()["status"] == "ready"
    assert manual.status_code == 201
    assert manual.json()["accepted_risk"] is True


def _seed_round_evidence(
    *,
    tmp_path: Path,
    session_id: str,
    revision_id: str,
) -> str:
    engine = create_engine(f"sqlite:///{tmp_path / 'design-review.db'}")
    with Session(engine) as session:
        round_record = DesignReviewRound(
            design_review_session_id=UUID(session_id),
            design_revision_id=UUID(revision_id),
            tenant_id=UUID(ACME_TENANT_ID),
            round_number=1,
            status=DesignReviewRoundStatus.COMPLETED,
            reviewer_count=1,
            quorum_count=1,
            idempotency_key="round-api-evidence",
        )
        session.add(round_record)
        session.flush()
        session.add(
            DesignReviewerAssignment(
                design_review_round_id=round_record.design_review_round_id,
                tenant_id=UUID(ACME_TENANT_ID),
                reviewer_key="accessibility",
                role_key="accessibility_reviewer",
                provider_reference="qa060/provider/accessibility",
                enabled=True,
            )
        )
        session.add(
            DesignReviewerVerdict(
                design_review_round_id=round_record.design_review_round_id,
                tenant_id=UUID(ACME_TENANT_ID),
                reviewer_key="accessibility",
                verdict=DesignReviewerVerdictValue.APPROVED,
                score=5,
                blocking_issue_count=0,
                safe_feedback_summary="Accessibility concerns are addressed.",
                output_digest="digest-verdict",
                usage_summary={"tokens": 10},
                idempotency_key="verdict-api-evidence",
            )
        )
        session.add(
            DesignQuorumDecision(
                design_review_round_id=round_record.design_review_round_id,
                tenant_id=UUID(ACME_TENANT_ID),
                status=DesignQuorumDecisionStatus.PASSED,
                approval_count=1,
                blocking_issue_count=0,
                next_action=DesignQuorumNextAction.HANDOFF,
                policy_version="qa060-v1",
                safe_rationale="Quorum passed.",
            )
        )
        session.add(
            DesignDevelopmentHandoff(
                design_review_session_id=UUID(session_id),
                tenant_id=UUID(ACME_TENANT_ID),
                approved_revision_id=UUID(revision_id),
                safe_summary="Ready for development handoff.",
                output_digest="digest-handoff",
                status=DesignDevelopmentHandoffStatus.READY,
                idempotency_key="handoff-api-evidence",
            )
        )
        session.commit()
        return str(round_record.design_review_round_id)
