from __future__ import annotations

import os
from pathlib import Path
from uuid import UUID

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from multi_agent_platform.db.models.design_review import (
    DesignDevelopmentHandoff,
    DesignDevelopmentHandoffStatus,
    DesignManualDecision,
    DesignManualDecisionType,
    DesignQuorumDecision,
    DesignQuorumDecisionStatus,
    DesignQuorumNextAction,
    DesignReviewerAssignment,
    DesignReviewerVerdict,
    DesignReviewerVerdictValue,
    DesignReviewRound,
    DesignReviewRoundStatus,
    DesignReviewSession,
    DesignReviewSessionStatus,
    DesignRevision,
)
from multi_agent_platform.db.models.tenant import Tenant, TenantStatus

ACME_TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")
GLOBEX_TENANT_ID = UUID("22222222-2222-2222-2222-222222222222")


def main() -> int:
    engine = create_engine(_database_url())
    with Session(engine) as session:
        _upsert_tenant(session, ACME_TENANT_ID, "acme", "Acme")
        _upsert_tenant(session, GLOBEX_TENANT_ID, "globex", "Globex")
        review_session = _upsert_review_session(session)
        revision = _upsert_revision(session, review_session)
        round_record = _upsert_round(session, review_session, revision)
        _upsert_assignment(
            session,
            round_record,
            reviewer_key="accessibility",
            role_key="accessibility_reviewer",
            provider_reference="qa060/provider/accessibility",
        )
        _upsert_assignment(
            session,
            round_record,
            reviewer_key="interaction",
            role_key="interaction_reviewer",
            provider_reference="qa060/provider/interaction",
        )
        _upsert_verdict(
            session,
            round_record,
            reviewer_key="accessibility",
            verdict=DesignReviewerVerdictValue.APPROVED,
            score=5,
            blocking_issue_count=0,
            safe_feedback_summary="Accessibility reviewer approved the safe summary.",
            output_digest="sha256-qa060-accessibility",
            idempotency_key="qa060-verdict-accessibility",
        )
        _upsert_verdict(
            session,
            round_record,
            reviewer_key="interaction",
            verdict=DesignReviewerVerdictValue.CHANGES_REQUESTED,
            score=3,
            blocking_issue_count=1,
            safe_feedback_summary="Interaction reviewer requested clearer state notes.",
            output_digest="sha256-qa060-interaction",
            idempotency_key="qa060-verdict-interaction",
        )
        _upsert_quorum_decision(session, round_record)
        _upsert_manual_decision(session, review_session, round_record)
        _upsert_handoff(session, review_session, revision)
        review_session_id = review_session.design_review_session_id
        review_round_id = round_record.design_review_round_id
        session.commit()

    print("Seeded QA060 design review live records")
    print(f"tenant_id={ACME_TENANT_ID}")
    print(f"design_review_session_id={review_session_id}")
    print(f"design_review_round_id={review_round_id}")
    return 0


def _upsert_tenant(
    session: Session, tenant_id: UUID, slug: str, display_name: str
) -> None:
    record = session.get(Tenant, tenant_id)
    if record is None:
        record = Tenant(tenant_id=tenant_id)
        session.add(record)
    record.slug = slug
    record.display_name = display_name
    record.status = TenantStatus.ACTIVE


def _upsert_review_session(session: Session) -> DesignReviewSession:
    record = session.scalar(
        select(DesignReviewSession).where(
            DesignReviewSession.tenant_id == ACME_TENANT_ID,
            DesignReviewSession.idempotency_key == "qa060-seeded-session",
        )
    )
    if record is None:
        record = DesignReviewSession(
            tenant_id=ACME_TENANT_ID,
            idempotency_key="qa060-seeded-session",
            owner_principal_id="tenant-admin-acme",
        )
        session.add(record)
    record.status = DesignReviewSessionStatus.APPROVED
    record.request_summary = "QA060 seeded design review for the domain foundation."
    record.active_revision_number = 1
    record.quorum_policy_key = "four_of_five_no_blockers"
    session.flush()
    return record


def _upsert_revision(
    session: Session, review_session: DesignReviewSession
) -> DesignRevision:
    record = session.scalar(
        select(DesignRevision).where(
            DesignRevision.design_review_session_id
            == review_session.design_review_session_id,
            DesignRevision.tenant_id == ACME_TENANT_ID,
            DesignRevision.revision_number == 1,
        )
    )
    if record is None:
        record = DesignRevision(
            design_review_session_id=review_session.design_review_session_id,
            tenant_id=ACME_TENANT_ID,
            revision_number=1,
        )
        session.add(record)
    record.author_role_key = "requester"
    record.safe_summary = "Seeded safe revision summary for QA060."
    record.payload_digest = "sha256-qa060-revision"
    session.flush()
    return record


def _upsert_round(
    session: Session,
    review_session: DesignReviewSession,
    revision: DesignRevision,
) -> DesignReviewRound:
    record = session.scalar(
        select(DesignReviewRound).where(
            DesignReviewRound.tenant_id == ACME_TENANT_ID,
            DesignReviewRound.idempotency_key == "qa060-round-1",
        )
    )
    if record is None:
        record = DesignReviewRound(
            design_review_session_id=review_session.design_review_session_id,
            design_revision_id=revision.design_revision_id,
            tenant_id=ACME_TENANT_ID,
            round_number=1,
            idempotency_key="qa060-round-1",
        )
        session.add(record)
    record.status = DesignReviewRoundStatus.COMPLETED
    record.reviewer_count = 2
    record.quorum_count = 2
    session.flush()
    return record


def _upsert_assignment(
    session: Session,
    round_record: DesignReviewRound,
    *,
    reviewer_key: str,
    role_key: str,
    provider_reference: str,
) -> DesignReviewerAssignment:
    record = session.scalar(
        select(DesignReviewerAssignment).where(
            DesignReviewerAssignment.design_review_round_id
            == round_record.design_review_round_id,
            DesignReviewerAssignment.reviewer_key == reviewer_key,
        )
    )
    if record is None:
        record = DesignReviewerAssignment(
            design_review_round_id=round_record.design_review_round_id,
            tenant_id=ACME_TENANT_ID,
            reviewer_key=reviewer_key,
        )
        session.add(record)
    record.role_key = role_key
    record.provider_reference = provider_reference
    record.enabled = True
    session.flush()
    return record


def _upsert_verdict(
    session: Session,
    round_record: DesignReviewRound,
    *,
    reviewer_key: str,
    verdict: DesignReviewerVerdictValue,
    score: int,
    blocking_issue_count: int,
    safe_feedback_summary: str,
    output_digest: str,
    idempotency_key: str,
) -> DesignReviewerVerdict:
    record = session.scalar(
        select(DesignReviewerVerdict).where(
            DesignReviewerVerdict.tenant_id == ACME_TENANT_ID,
            DesignReviewerVerdict.idempotency_key == idempotency_key,
        )
    )
    if record is None:
        record = DesignReviewerVerdict(
            design_review_round_id=round_record.design_review_round_id,
            tenant_id=ACME_TENANT_ID,
            reviewer_key=reviewer_key,
            idempotency_key=idempotency_key,
        )
        session.add(record)
    record.verdict = verdict
    record.score = score
    record.blocking_issue_count = blocking_issue_count
    record.safe_feedback_summary = safe_feedback_summary
    record.output_digest = output_digest
    record.usage_summary = {"usage_reference": f"qa060/{reviewer_key}"}
    session.flush()
    return record


def _upsert_quorum_decision(
    session: Session,
    round_record: DesignReviewRound,
) -> DesignQuorumDecision:
    record = session.scalar(
        select(DesignQuorumDecision).where(
            DesignQuorumDecision.design_review_round_id
            == round_record.design_review_round_id,
            DesignQuorumDecision.tenant_id == ACME_TENANT_ID,
        )
    )
    if record is None:
        record = DesignQuorumDecision(
            design_review_round_id=round_record.design_review_round_id,
            tenant_id=ACME_TENANT_ID,
        )
        session.add(record)
    record.status = DesignQuorumDecisionStatus.REVISION_REQUIRED
    record.approval_count = 1
    record.blocking_issue_count = 1
    record.next_action = DesignQuorumNextAction.REVISE
    record.policy_version = "qa060-quorum-v1"
    record.safe_rationale = "One reviewer requested a revision before handoff."
    session.flush()
    return record


def _upsert_manual_decision(
    session: Session,
    review_session: DesignReviewSession,
    round_record: DesignReviewRound,
) -> DesignManualDecision:
    record = session.scalar(
        select(DesignManualDecision).where(
            DesignManualDecision.tenant_id == ACME_TENANT_ID,
            DesignManualDecision.idempotency_key == "qa060-manual-seeded",
        )
    )
    if record is None:
        record = DesignManualDecision(
            design_review_session_id=review_session.design_review_session_id,
            tenant_id=ACME_TENANT_ID,
            idempotency_key="qa060-manual-seeded",
        )
        session.add(record)
    record.design_review_round_id = round_record.design_review_round_id
    record.decision_type = DesignManualDecisionType.REVISE
    record.actor_principal_id = "tenant-admin-acme"
    record.safe_rationale = "Seeded manual decision asks for revision evidence."
    record.accepted_risk = False
    session.flush()
    return record


def _upsert_handoff(
    session: Session,
    review_session: DesignReviewSession,
    revision: DesignRevision,
) -> DesignDevelopmentHandoff:
    record = session.scalar(
        select(DesignDevelopmentHandoff).where(
            DesignDevelopmentHandoff.design_review_session_id
            == review_session.design_review_session_id,
            DesignDevelopmentHandoff.tenant_id == ACME_TENANT_ID,
        )
    )
    if record is None:
        record = DesignDevelopmentHandoff(
            design_review_session_id=review_session.design_review_session_id,
            tenant_id=ACME_TENANT_ID,
            idempotency_key="qa060-handoff",
        )
        session.add(record)
    record.approved_revision_id = revision.design_revision_id
    record.safe_summary = "Seeded handoff metadata remains safe and referential."
    record.output_digest = "sha256-qa060-handoff"
    record.status = DesignDevelopmentHandoffStatus.READY
    session.flush()
    return record


def _database_url() -> str:
    value = os.environ.get("DATABASE_URL") or _env_file_value("DATABASE_URL")
    if not value:
        raise RuntimeError("DATABASE_URL is required")
    return value


def _env_file_value(key: str) -> str | None:
    env_file = Path(".env")
    if not env_file.exists():
        return None
    for line in env_file.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        if name == key:
            return value
    return None


if __name__ == "__main__":
    raise SystemExit(main())
