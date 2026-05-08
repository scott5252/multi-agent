from __future__ import annotations

from datetime import UTC, datetime
from typing import cast
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession
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


def seed_live_agent_test_bench_session(
    session: Session,
    *,
    tenant_id: UUID,
    actor_principal_id: str = "tenant-admin",
) -> dict[str, UUID | str]:
    records = _live_agent_test_bench_records(
        tenant_id=tenant_id,
        actor_principal_id=actor_principal_id,
    )
    session.add_all(cast(list[object], records["objects"]))
    session.commit()
    return cast(dict[str, UUID | str], records["ids"])


async def seed_live_agent_test_bench_async_session(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    actor_principal_id: str = "tenant-admin",
) -> dict[str, UUID | str]:
    records = _live_agent_test_bench_records(
        tenant_id=tenant_id,
        actor_principal_id=actor_principal_id,
    )
    session.add_all(cast(list[object], records["objects"]))
    await session.flush()
    return cast(dict[str, UUID | str], records["ids"])


def _live_agent_test_bench_records(
    *,
    tenant_id: UUID,
    actor_principal_id: str,
) -> dict[str, object]:
    now = datetime(2026, 5, 7, 16, tzinfo=UTC)
    old = datetime(2026, 5, 7, 15, tzinfo=UTC)
    suite_id = uuid4()
    case_id = uuid4()
    assertion_id = uuid4()
    failed_run_id = uuid4()
    passed_run_id = uuid4()
    failed_step_id = uuid4()
    passed_step_id = uuid4()
    artifact_id = uuid4()
    requirement_id = uuid4()
    target_id = "workflow-draft-live-daily-briefing"
    current_revision = "workflow-draft-rev-live-current"
    stale_revision = "workflow-draft-rev-live-stale"
    suite = AgentTestSuite(
        agent_test_suite_id=suite_id,
        tenant_id=tenant_id,
        name="Live daily briefing release gate",
        description="Repository-backed release confidence suite.",
        target_type=AgentTestTargetType.WORKFLOW_DRAFT,
        target_id=target_id,
        target_version=current_revision,
        default_safe_mode=AgentTestSafeMode.MOCK_MODEL,
        model_mode="mock",
        tool_mode="mock",
        pass_threshold=0.9,
        is_required_for_publish=True,
        status=AgentTestStatus.ACTIVE,
        revision=2,
        created_by_principal_id=actor_principal_id,
        created_at=old,
        updated_at=now,
    )
    case = AgentTestCase(
        agent_test_case_id=case_id,
        agent_test_suite_id=suite_id,
        tenant_id=tenant_id,
        name="Briefing summary contract",
        description="Safe fixture summary only.",
        fixture_summary={
            "summary": "Fixture includes weather metadata summary.",
            "preview": {"request": "daily briefing"},
        },
        expected_contract_shape={"status": "passed", "contract": {"summary": True}},
        evaluator_prompt_ref="evaluator-live-safe-summary",
        pass_threshold=0.6,
        case_order=1,
        status=AgentTestStatus.ACTIVE,
        revision=3,
        created_at=old,
        updated_at=now,
    )
    assertion = AgentTestAssertion(
        agent_test_assertion_id=assertion_id,
        agent_test_case_id=case_id,
        tenant_id=tenant_id,
        kind=AgentTestAssertionKind.DETERMINISTIC,
        path="status",
        comparator="equals",
        expected_value="passed",
        severity="blocking",
        weight=0.5,
        description="Contract shape",
    )
    failed_run = AgentTestRun(
        agent_test_run_id=failed_run_id,
        tenant_id=tenant_id,
        agent_test_suite_id=suite_id,
        target_type=AgentTestTargetType.WORKFLOW_DRAFT,
        target_id=target_id,
        target_version=stale_revision,
        safe_mode=AgentTestSafeMode.REAL_MODEL_SIDE_EFFECTS_DISABLED,
        status=AgentTestRunStatus.FAILED,
        pass_status="failed",
        triggered_by_principal_id=actor_principal_id,
        idempotency_key="live-test-bench-failed",
        trace_id="trace-live-test-bench-failed",
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
    passed_run = AgentTestRun(
        agent_test_run_id=passed_run_id,
        tenant_id=tenant_id,
        agent_test_suite_id=suite_id,
        target_type=AgentTestTargetType.WORKFLOW_DRAFT,
        target_id=target_id,
        target_version=current_revision,
        safe_mode=AgentTestSafeMode.MOCK_MODEL,
        status=AgentTestRunStatus.PASSED,
        pass_status="passed",
        triggered_by_principal_id=actor_principal_id,
        idempotency_key="live-test-bench-passed",
        trace_id="trace-live-test-bench-passed",
        started_at=now,
        completed_at=now,
        usage_summary={"total_tokens": 30},
        latency_ms=30,
        redaction_summary={"transcripts_redacted": 1},
        artifact_summary={"artifact_count": 0},
        blocked_side_effect_count=0,
        created_at=now,
    )
    failed_step = AgentTestRunStep(
        agent_test_run_step_id=failed_step_id,
        agent_test_run_id=failed_run_id,
        tenant_id=tenant_id,
        agent_test_case_id=case_id,
        step_name="Connector side-effect decision",
        status=AgentTestRunStatus.FAILED,
        sequence=1,
        model_provider="mocked-gateway",
        model_id="gateway-mocked-test-model",
        prompt_version_id="prompt version live",
        profile_version_id="profile version live",
        skill_version_refs=["daily-briefing-connectors 1.4.0"],
        workflow_version_ref=stale_revision,
        latency_ms=240,
        token_usage={"total_tokens": 42},
        assertion_results=[
            {
                "passed": False,
                "safe_message": "Blocked side-effect assertion failed",
                "expected": "Gateway should report every blocked write attempt.",
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
        redacted_transcript={"summary": "Gateway summarized a blocked write decision."},
        artifact_refs=[str(artifact_id)],
        failure_reason="One or more assertions failed.",
        created_at=old,
    )
    passed_step = AgentTestRunStep(
        agent_test_run_step_id=passed_step_id,
        agent_test_run_id=passed_run_id,
        tenant_id=tenant_id,
        agent_test_case_id=case_id,
        step_name="Briefing summary contract",
        status=AgentTestRunStatus.PASSED,
        sequence=1,
        model_provider="mock",
        model_id="mock-model",
        prompt_version_id="evaluator-live-safe-summary",
        workflow_version_ref=current_revision,
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
    artifact = AgentTestArtifact(
        agent_test_artifact_id=artifact_id,
        tenant_id=tenant_id,
        agent_test_run_id=failed_run_id,
        agent_test_case_id=case_id,
        artifact_type="diagnostic_summary",
        storage_uri="artifact://live-test-bench/summary",
        checksum_sha256="sha256:liveartifactsummary",
        size_bytes=18_432,
        content_type="application/json",
        redaction_classification="safe-summary",
        retention_state="retained",
        safe_summary={
            "label": "Redacted run summary artifact",
            "summary": "Artifact metadata is available by governed reference only.",
        },
        created_at=old,
    )
    requirement = AgentTestPublicationRequirement(
        agent_test_publication_requirement_id=requirement_id,
        tenant_id=tenant_id,
        target_type=AgentTestTargetType.WORKFLOW_DRAFT,
        target_id=target_id,
        agent_test_suite_id=suite_id,
        required=True,
        minimum_pass_status="passed",
        created_by_principal_id=actor_principal_id,
        created_at=old,
        updated_at=now,
    )
    return {
        "objects": [
            suite,
            case,
            assertion,
            failed_run,
            passed_run,
            failed_step,
            passed_step,
            artifact,
            requirement,
        ],
        "ids": {
            "suite_id": suite_id,
            "case_id": case_id,
            "assertion_id": assertion_id,
            "failed_run_id": failed_run_id,
            "passed_run_id": passed_run_id,
            "artifact_id": artifact_id,
            "requirement_id": requirement_id,
            "target_id": target_id,
            "current_revision": current_revision,
            "stale_revision": stale_revision,
        },
    }
