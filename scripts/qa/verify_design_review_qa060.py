from __future__ import annotations

import os
from pathlib import Path
from uuid import UUID

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from multi_agent_platform.db.models.design_review import (
    DesignDevelopmentHandoff,
    DesignManualDecision,
    DesignQuorumDecision,
    DesignReviewerAssignment,
    DesignReviewerVerdict,
    DesignReviewRound,
    DesignReviewSession,
    DesignRevision,
)

ACME_TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")
GLOBEX_TENANT_ID = UUID("22222222-2222-2222-2222-222222222222")


def main() -> int:
    engine = create_engine(_database_url())
    with Session(engine) as session:
        acme_sessions = _count(
            session,
            select(func.count())
            .select_from(DesignReviewSession)
            .where(DesignReviewSession.tenant_id == ACME_TENANT_ID),
        )
        globex_sessions = _count(
            session,
            select(func.count())
            .select_from(DesignReviewSession)
            .where(DesignReviewSession.tenant_id == GLOBEX_TENANT_ID),
        )
        revisions = _count(
            session,
            select(func.count())
            .select_from(DesignRevision)
            .where(DesignRevision.tenant_id == ACME_TENANT_ID),
        )
        rounds = _count(
            session,
            select(func.count())
            .select_from(DesignReviewRound)
            .where(DesignReviewRound.tenant_id == ACME_TENANT_ID),
        )
        assignments = _count(
            session,
            select(func.count())
            .select_from(DesignReviewerAssignment)
            .where(DesignReviewerAssignment.tenant_id == ACME_TENANT_ID),
        )
        verdicts = _count(
            session,
            select(func.count())
            .select_from(DesignReviewerVerdict)
            .where(DesignReviewerVerdict.tenant_id == ACME_TENANT_ID),
        )
        quorum_decisions = _count(
            session,
            select(func.count())
            .select_from(DesignQuorumDecision)
            .where(DesignQuorumDecision.tenant_id == ACME_TENANT_ID),
        )
        manual_decisions = _count(
            session,
            select(func.count())
            .select_from(DesignManualDecision)
            .where(DesignManualDecision.tenant_id == ACME_TENANT_ID),
        )
        handoffs = _count(
            session,
            select(func.count())
            .select_from(DesignDevelopmentHandoff)
            .where(DesignDevelopmentHandoff.tenant_id == ACME_TENANT_ID),
        )
        if acme_sessions < 1:
            raise RuntimeError("Expected at least one Acme design review session")
        if globex_sessions:
            raise RuntimeError("Globex should not have QA060 design review sessions")
        if revisions < acme_sessions:
            raise RuntimeError("Expected every QA060 session to have a revision")
        if rounds < 1:
            raise RuntimeError("Expected at least one seeded design review round")
        if assignments < 2:
            raise RuntimeError("Expected seeded reviewer assignments")
        if verdicts < 2:
            raise RuntimeError("Expected seeded reviewer verdicts")
        if quorum_decisions < 1:
            raise RuntimeError("Expected seeded quorum decision evidence")
        if manual_decisions < 1:
            raise RuntimeError("Expected manual decision evidence")
        if handoffs < 1:
            raise RuntimeError("Expected handoff evidence")

    print("Verified QA060 design review live-data persistence")
    print(f"tenant_id={ACME_TENANT_ID}")
    print(f"sessions={acme_sessions}")
    print(f"revisions={revisions}")
    print(f"rounds={rounds}")
    print(f"assignments={assignments}")
    print(f"verdicts={verdicts}")
    print(f"quorum_decisions={quorum_decisions}")
    print(f"manual_decisions={manual_decisions}")
    print(f"handoffs={handoffs}")
    return 0


def _count(session: Session, stmt) -> int:
    return int(session.scalar(stmt) or 0)


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
