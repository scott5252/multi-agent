from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from multi_agent_platform.db.models.agent_tests import (
    AgentTestArtifact,
    AgentTestAssertion,
    AgentTestAssertionKind,
    AgentTestCase,
    AgentTestPublicationRequirement,
    AgentTestRun,
    AgentTestRunStatus,
    AgentTestRunStep,
    AgentTestSafeMode,
    AgentTestStatus,
    AgentTestSuite,
    AgentTestTargetType,
)

ACME_TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")
SUITE_ID = UUID("53000000-0000-0000-0000-000000000001")
CASE_ID = UUID("53000000-0000-0000-0000-000000000002")
ASSERTION_ID = UUID("53000000-0000-0000-0000-000000000003")
FAILED_RUN_ID = UUID("53000000-0000-0000-0000-000000000004")
PASSED_RUN_ID = UUID("53000000-0000-0000-0000-000000000005")
FAILED_STEP_ID = UUID("53000000-0000-0000-0000-000000000006")
PASSED_STEP_ID = UUID("53000000-0000-0000-0000-000000000007")
ARTIFACT_ID = UUID("53000000-0000-0000-0000-000000000008")
REQUIREMENT_ID = UUID("53000000-0000-0000-0000-000000000009")
TARGET_ID = "workflow-draft-qa053-live-daily-briefing"
CURRENT_REVISION = "workflow-draft-rev-qa053-current"
STALE_REVISION = "workflow-draft-rev-qa053-stale"


def main() -> int:
    engine = create_engine(_database_url())
    now = datetime(2026, 5, 7, 17, tzinfo=UTC)
    old = datetime(2026, 5, 7, 16, tzinfo=UTC)
    with Session(engine) as session:
        session.merge(
            AgentTestSuite(
                agent_test_suite_id=SUITE_ID,
                tenant_id=ACME_TENANT_ID,
                name="QA053 live daily briefing release gate",
                description="Repository-backed release confidence suite.",
                target_type=AgentTestTargetType.WORKFLOW_DRAFT,
                target_id=TARGET_ID,
                target_version=CURRENT_REVISION,
                default_safe_mode=AgentTestSafeMode.MOCK_MODEL,
                model_mode="mock",
                tool_mode="mock",
                pass_threshold=0.9,
                is_required_for_publish=True,
                status=AgentTestStatus.ACTIVE,
                revision=2,
                created_by_principal_id="tenant-admin-acme",
                created_at=old,
                updated_at=now,
            )
        )
        session.merge(
            AgentTestCase(
                agent_test_case_id=CASE_ID,
                agent_test_suite_id=SUITE_ID,
                tenant_id=ACME_TENANT_ID,
                name="Briefing summary contract",
                description="Safe fixture summary only.",
                fixture_summary={
                    "summary": "Fixture includes weather metadata summary.",
                    "preview": {"request": "qa053 daily briefing"},
                },
                expected_contract_shape={
                    "status": "passed",
                    "contract": {"summary": True},
                },
                evaluator_prompt_ref="evaluator-qa053-safe-summary",
                pass_threshold=0.6,
                case_order=1,
                status=AgentTestStatus.ACTIVE,
                revision=3,
                created_at=old,
                updated_at=now,
            )
        )
        session.merge(
            AgentTestAssertion(
                agent_test_assertion_id=ASSERTION_ID,
                agent_test_case_id=CASE_ID,
                tenant_id=ACME_TENANT_ID,
                kind=AgentTestAssertionKind.DETERMINISTIC,
                path="status",
                comparator="equals",
                expected_value="passed",
                severity="blocking",
                weight=0.5,
                description="Contract shape",
            )
        )
        session.merge(
            AgentTestRun(
                agent_test_run_id=FAILED_RUN_ID,
                tenant_id=ACME_TENANT_ID,
                agent_test_suite_id=SUITE_ID,
                target_type=AgentTestTargetType.WORKFLOW_DRAFT,
                target_id=TARGET_ID,
                target_version=STALE_REVISION,
                safe_mode=AgentTestSafeMode.REAL_MODEL_SIDE_EFFECTS_DISABLED,
                status=AgentTestRunStatus.FAILED,
                pass_status="failed",
                triggered_by_principal_id="tenant-admin-acme",
                idempotency_key="qa053-failed-run",
                trace_id="trace-qa053-failed-run",
                started_at=old,
                completed_at=old,
                usage_summary={"total_tokens": 166},
                latency_ms=1800,
                redaction_summary={"transcripts_redacted": 1},
                artifact_summary={"artifact_count": 1},
                blocked_side_effect_count=1,
                failure_summary="One blocked notification summary was missing.",
                created_at=old,
            )
        )
        session.merge(
            AgentTestRun(
                agent_test_run_id=PASSED_RUN_ID,
                tenant_id=ACME_TENANT_ID,
                agent_test_suite_id=SUITE_ID,
                target_type=AgentTestTargetType.WORKFLOW_DRAFT,
                target_id=TARGET_ID,
                target_version=CURRENT_REVISION,
                safe_mode=AgentTestSafeMode.MOCK_MODEL,
                status=AgentTestRunStatus.PASSED,
                pass_status="passed",
                triggered_by_principal_id="tenant-admin-acme",
                idempotency_key="qa053-passed-run",
                trace_id="trace-qa053-passed-run",
                started_at=now,
                completed_at=now,
                usage_summary={"total_tokens": 30},
                latency_ms=30,
                redaction_summary={"transcripts_redacted": 1},
                artifact_summary={"artifact_count": 0},
                blocked_side_effect_count=0,
                created_at=now,
            )
        )
        session.merge(
            AgentTestRunStep(
                agent_test_run_step_id=FAILED_STEP_ID,
                agent_test_run_id=FAILED_RUN_ID,
                tenant_id=ACME_TENANT_ID,
                agent_test_case_id=CASE_ID,
                step_name="Connector side-effect decision",
                status=AgentTestRunStatus.FAILED,
                sequence=1,
                model_provider="mocked-gateway",
                model_id="gateway-mocked-test-model",
                prompt_version_id="prompt version qa053",
                profile_version_id="profile version qa053",
                skill_version_refs=["daily-briefing-connectors 1.4.0"],
                workflow_version_ref=STALE_REVISION,
                latency_ms=240,
                token_usage={"total_tokens": 42},
                assertion_results=[
                    {
                        "passed": False,
                        "safe_message": "Blocked side-effect assertion failed",
                        "expected": "Gateway should report every blocked attempt.",
                        "actual": "One blocked notification summary was missing.",
                        "comparator": "contains",
                        "path": "trace_steps[side-effect].blocked_side_effects",
                        "severity": "blocking",
                    }
                ],
                blocked_side_effects=[
                    {
                        "tool_name": "email.send",
                        "reason": "safe mode disables external side effects",
                    }
                ],
                redacted_transcript={
                    "summary": "Gateway summarized a blocked write decision."
                },
                artifact_refs=[str(ARTIFACT_ID)],
                failure_reason="One or more assertions failed.",
                created_at=old,
            )
        )
        session.merge(
            AgentTestRunStep(
                agent_test_run_step_id=PASSED_STEP_ID,
                agent_test_run_id=PASSED_RUN_ID,
                tenant_id=ACME_TENANT_ID,
                agent_test_case_id=CASE_ID,
                step_name="Briefing summary contract",
                status=AgentTestRunStatus.PASSED,
                sequence=1,
                model_provider="mock",
                model_id="mock-model",
                prompt_version_id="evaluator-qa053-safe-summary",
                workflow_version_ref=CURRENT_REVISION,
                latency_ms=30,
                token_usage={"total_tokens": 30},
                assertion_results=[
                    {
                        "passed": True,
                        "safe_message": "Contract shape passed",
                        "expected": "status passed",
                        "actual": "status passed",
                        "comparator": "equals",
                        "path": "status",
                        "severity": "blocking",
                    }
                ],
                redacted_transcript={"summary": "Safe contract run summary."},
                artifact_refs=[],
                created_at=now,
            )
        )
        session.merge(
            AgentTestArtifact(
                agent_test_artifact_id=ARTIFACT_ID,
                tenant_id=ACME_TENANT_ID,
                agent_test_run_id=FAILED_RUN_ID,
                agent_test_case_id=CASE_ID,
                artifact_type="diagnostic_summary",
                storage_uri="artifact://qa053/test-bench-summary",
                checksum_sha256="sha256:qa053liveartifactsummary",
                size_bytes=18432,
                content_type="application/json",
                redaction_classification="safe-summary",
                retention_state="retained",
                safe_summary={
                    "label": "Redacted run summary artifact",
                    "summary": (
                        "Artifact metadata is available by governed reference only."
                    ),
                },
                created_at=old,
            )
        )
        session.merge(
            AgentTestPublicationRequirement(
                agent_test_publication_requirement_id=REQUIREMENT_ID,
                tenant_id=ACME_TENANT_ID,
                target_type=AgentTestTargetType.WORKFLOW_DRAFT,
                target_id=TARGET_ID,
                agent_test_suite_id=SUITE_ID,
                required=True,
                minimum_pass_status="passed",
                created_by_principal_id="tenant-admin-acme",
                created_at=old,
                updated_at=now,
            )
        )
        session.commit()
    print("Seeded QA053 test bench live records")
    print(f"suite_id={SUITE_ID}")
    print(f"passed_run_id={PASSED_RUN_ID}")
    print(f"failed_run_id={FAILED_RUN_ID}")
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
