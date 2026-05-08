from __future__ import annotations

import os
from pathlib import Path
from uuid import UUID

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from multi_agent_platform.db.models.agent_tests import (
    AgentTestArtifact,
    AgentTestCase,
    AgentTestPublicationRequirement,
    AgentTestRun,
    AgentTestRunStatus,
    AgentTestSuite,
)

ACME_TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")
GLOBEX_TENANT_ID = UUID("22222222-2222-2222-2222-222222222222")
SUITE_ID = UUID("53000000-0000-0000-0000-000000000001")
CASE_ID = UUID("53000000-0000-0000-0000-000000000002")
ARTIFACT_ID = UUID("53000000-0000-0000-0000-000000000008")
TARGET_ID = "workflow-draft-qa053-live-daily-briefing"


def main() -> int:
    engine = create_engine(_database_url())
    with Session(engine) as session:
        suite = session.get(AgentTestSuite, SUITE_ID)
        case = session.get(AgentTestCase, CASE_ID)
        artifact = session.get(AgentTestArtifact, ARTIFACT_ID)
        passed_runs = session.scalar(
            select(func.count())
            .select_from(AgentTestRun)
            .where(
                AgentTestRun.tenant_id == ACME_TENANT_ID,
                AgentTestRun.agent_test_suite_id == SUITE_ID,
                AgentTestRun.status == AgentTestRunStatus.PASSED,
            )
        )
        globex_suites = session.scalar(
            select(func.count())
            .select_from(AgentTestSuite)
            .where(AgentTestSuite.tenant_id == GLOBEX_TENANT_ID)
        )
        requirement = session.scalar(
            select(AgentTestPublicationRequirement).where(
                AgentTestPublicationRequirement.tenant_id == ACME_TENANT_ID,
                AgentTestPublicationRequirement.target_id == TARGET_ID,
                AgentTestPublicationRequirement.agent_test_suite_id == SUITE_ID,
            )
        )
        if suite is None:
            raise RuntimeError("QA053 suite is missing")
        if case is None:
            raise RuntimeError("QA053 case is missing")
        if artifact is None:
            raise RuntimeError("QA053 artifact metadata is missing")
        if requirement is None:
            raise RuntimeError("QA053 publication requirement is missing")
        if suite.revision < 3:
            raise RuntimeError(
                "Expected suite revision >= 3 after Playwright Save suite, "
                f"got {suite.revision}"
            )
        if suite.tenant_id != ACME_TENANT_ID:
            raise RuntimeError("QA053 suite tenant mismatch")
        if passed_runs < 1:
            raise RuntimeError("Expected at least one persisted passing QA053 run")
        if globex_suites:
            raise RuntimeError("Globex should not have QA053 seeded suite rows")
    print("Verified QA053 test bench suite persistence")
    print(f"suite_id={SUITE_ID}")
    print(f"suite_revision={suite.revision}")
    print(f"case_revision={case.revision}")
    print(f"passed_runs={passed_runs}")
    print(f"artifact_id={ARTIFACT_ID}")
    return 0


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
