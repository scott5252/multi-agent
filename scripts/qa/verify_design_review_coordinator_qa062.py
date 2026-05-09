from __future__ import annotations

import json
import os
from pathlib import Path
from uuid import UUID

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from multi_agent_platform.db.models.design_review import (
    DesignDevelopmentHandoff,
    DesignQuorumDecision,
    DesignReviewerVerdict,
    DesignReviewRound,
    DesignReviewSession,
    DesignRevision,
)
from multi_agent_platform.db.models.runtime_orchestration import WorkflowRunRecord

ACME_TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")
GLOBEX_TENANT_ID = UUID("22222222-2222-2222-2222-222222222222")
EVIDENCE_PATH = Path(
    ".data/qa062-artifacts/evidence/qa062-design-review-coordinator-seed.json"
)
UNSAFE_MARKERS = (
    "raw prompt",
    "raw completion",
    "provider payload",
    "authorization:",
    "bearer ",
    "sk-",
    "/users/",
)


def main() -> int:
    if not EVIDENCE_PATH.exists():
        raise RuntimeError(f"missing QA062 evidence: {EVIDENCE_PATH}")
    encoded = EVIDENCE_PATH.read_text(encoding="utf-8").lower()
    for marker in UNSAFE_MARKERS:
        if marker in encoded:
            raise RuntimeError(f"unsafe marker leaked into QA062 evidence: {marker}")
    evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
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
        handoffs = _count(
            session,
            select(func.count())
            .select_from(DesignDevelopmentHandoff)
            .where(DesignDevelopmentHandoff.tenant_id == ACME_TENANT_ID),
        )
        runtime_runs = _count(
            session,
            select(func.count())
            .select_from(WorkflowRunRecord)
            .where(WorkflowRunRecord.tenant_id == ACME_TENANT_ID),
        )
        if acme_sessions < 1:
            raise RuntimeError("Expected at least one Acme coordinator session")
        if globex_sessions:
            raise RuntimeError("Globex should not have QA062 coordinator sessions")
        if revisions < 1:
            raise RuntimeError("Expected coordinator revision evidence")
        if rounds < 1:
            raise RuntimeError("Expected coordinator round evidence")
        if verdicts < 5:
            raise RuntimeError("Expected five coordinator verdicts")
        if quorum_decisions < 1:
            raise RuntimeError("Expected coordinator quorum decision")
        if handoffs < 1:
            raise RuntimeError("Expected coordinator handoff")
        if runtime_runs < 1:
            raise RuntimeError("Expected coordinator runtime run")
        if evidence.get("quorum_status") != "passed":
            raise RuntimeError("Expected seeded coordinator quorum to pass")
        if evidence.get("handoff_state") != "ready":
            raise RuntimeError("Expected seeded coordinator handoff to be ready")

    print("Verified QA062 design review coordinator loop")
    print(f"tenant_id={ACME_TENANT_ID}")
    print(f"sessions={acme_sessions}")
    print(f"rounds={rounds}")
    print(f"verdicts={verdicts}")
    print(f"runtime_runs={runtime_runs}")
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
