from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.db.models.agent_tests import (
    AgentTestArtifact,
    AgentTestRun,
    AgentTestRunStatus,
    AgentTestSafeMode,
    AgentTestStatus,
    AgentTestTargetType,
)
from multi_agent_platform.db.repositories.agent_tests import AgentTestRepository
from multi_agent_platform.testing.agent_bench.models import RequiredSuiteEvidenceRequest
from multi_agent_platform.testing.agent_bench.service import (
    AgentTestBenchError,
    AgentTestBenchService,
    _status_value,
)


async def test_service_creates_suite_case_run_and_gate_evidence(
    session,
    seeded_tenant,
) -> None:
    service = AgentTestBenchService(AgentTestRepository(session))
    suite = await service.create_suite(
        tenant_id=seeded_tenant.tenant_id,
        name="Draft guard",
        target_type="workflow_draft",
        target_id="draft-1",
        target_version="rev-1",
        required_for_publish=True,
        actor_principal_id="tenant-admin",
    )
    await service.create_case(
        suite_id=suite.agent_test_suite_id,
        tenant_id=seeded_tenant.tenant_id,
        name="Passing case",
        fixture={"request": "summarize intake", "api_key": "secret"},
        expected_contract_shape={"status": {}, "contract": {}},
        assertions=[
            {
                "kind": "deterministic",
                "path": "status",
                "comparator": "equals",
                "expected_value": "passed",
            }
        ],
        actor_principal_id="tenant-admin",
    )
    run = await service.launch_run(
        suite_id=suite.agent_test_suite_id,
        tenant_id=seeded_tenant.tenant_id,
        actor_principal_id="tenant-admin",
        safe_mode="mock_model",
        target_version="rev-1",
        idempotency_key="idem-1",
        trace_id="trace-1",
    )
    repeated = await service.launch_run(
        suite_id=suite.agent_test_suite_id,
        tenant_id=seeded_tenant.tenant_id,
        actor_principal_id="tenant-admin",
        safe_mode="mock_model",
        target_version="rev-1",
        idempotency_key="idem-1",
        trace_id="trace-1",
    )
    evidence = await service.evidence_summary(
        tenant_id=seeded_tenant.tenant_id,
        target_type="workflow_draft",
        target_id="draft-1",
        target_version="rev-1",
    )

    assert run.status.value == "passed"
    assert repeated == run
    assert evidence.required_count == 1
    assert evidence.passing_count == 1


async def test_service_update_errors_blocked_runs_and_missing_evidence(
    session,
    seeded_tenant,
) -> None:
    service = AgentTestBenchService(AgentTestRepository(session))
    suite = await service.create_suite(
        tenant_id=seeded_tenant.tenant_id,
        name="Draft guard",
        target_type="workflow_draft",
        target_id="draft-2",
        target_version="rev-1",
        required_for_publish=True,
        actor_principal_id="tenant-admin",
    )
    updated = await service.update_suite(
        suite_id=suite.agent_test_suite_id,
        tenant_id=seeded_tenant.tenant_id,
        expected_revision=suite.revision,
        name="Updated guard",
        description="Updated description",
        target_version="rev-2",
        default_safe_mode="mock_tools",
        model_mode="mock",
        tool_mode="mock",
        pass_threshold=0.9,
        required_for_publish=False,
    )

    with pytest.raises(AgentTestBenchError, match="no active cases"):
        await service.launch_run(
            suite_id=suite.agent_test_suite_id,
            tenant_id=seeded_tenant.tenant_id,
            actor_principal_id="tenant-admin",
            safe_mode="mock_model",
            target_version="rev-2",
            idempotency_key=None,
            trace_id=None,
        )

    await service.create_case(
        suite_id=suite.agent_test_suite_id,
        tenant_id=seeded_tenant.tenant_id,
        name="Evaluator case",
        fixture={"request": "summarize intake"},
        expected_contract_shape={"status": {}},
        assertions=[
            {
                "kind": "evaluator",
                "threshold": "0.8",
                "weight": "2.0",
                "description": "safe evaluator",
            }
        ],
        actor_principal_id="tenant-admin",
    )
    blocked = await service.launch_run(
        suite_id=suite.agent_test_suite_id,
        tenant_id=seeded_tenant.tenant_id,
        actor_principal_id="tenant-admin",
        safe_mode="approved_real_probe",
        target_version="rev-2",
        idempotency_key="blocked-probe",
        trace_id=None,
    )
    stale = await service.evidence_summary(
        tenant_id=seeded_tenant.tenant_id,
        target_type="workflow_draft",
        target_id="draft-2",
        target_version="rev-2",
    )

    assert updated.name == "Updated guard"
    assert updated.default_safe_mode.value == "mock_tools"
    assert blocked.status.value == "blocked"
    assert stale.missing_count == 1


async def test_service_fail_closed_and_required_suite_evidence_edges(
    session,
    seeded_tenant,
) -> None:
    repository = AgentTestRepository(session)
    service = AgentTestBenchService(repository)

    with pytest.raises(AgentTestBenchError, match="suite not found"):
        await service.create_case(
            suite_id=uuid4(),
            tenant_id=seeded_tenant.tenant_id,
            name="Missing suite case",
            actor_principal_id="tenant-admin",
        )
    with pytest.raises(AgentTestBenchError, match="suite not found"):
        await service.launch_run(
            suite_id=uuid4(),
            tenant_id=seeded_tenant.tenant_id,
            actor_principal_id="tenant-admin",
            safe_mode="mock_model",
            target_version="rev-current",
            idempotency_key="missing-run",
            trace_id=None,
        )
    with pytest.raises(LookupError, match="suite not found"):
        await repository.require_suite_revision(
            suite_id=uuid4(),
            tenant_id=seeded_tenant.tenant_id,
            expected_revision=1,
        )

    archived_suite = await service.create_suite(
        tenant_id=seeded_tenant.tenant_id,
        name="Archived guard",
        target_type="workflow_draft",
        target_id="draft-3",
        target_version="rev-current",
        actor_principal_id="tenant-admin",
    )
    archived_suite.status = AgentTestStatus.ARCHIVED
    with pytest.raises(AgentTestBenchError, match="archived"):
        await service.launch_run(
            suite_id=archived_suite.agent_test_suite_id,
            tenant_id=seeded_tenant.tenant_id,
            actor_principal_id="tenant-admin",
            safe_mode="mock_model",
            target_version="rev-current",
            idempotency_key="archived-run",
            trace_id=None,
        )

    wrong_target_suite = await service.create_suite(
        tenant_id=seeded_tenant.tenant_id,
        name="Wrong target guard",
        target_type="workflow_draft",
        target_id="draft-other",
        target_version="rev-current",
        actor_principal_id="tenant-admin",
    )
    failed_current_suite = await service.create_suite(
        tenant_id=seeded_tenant.tenant_id,
        name="Failed current guard",
        target_type="workflow_draft",
        target_id="draft-3",
        target_version="rev-current",
        actor_principal_id="tenant-admin",
    )
    stale_suite = await service.create_suite(
        tenant_id=seeded_tenant.tenant_id,
        name="Stale guard",
        target_type="workflow_draft",
        target_id="draft-3",
        target_version="rev-current",
        actor_principal_id="tenant-admin",
    )
    no_run_suite = await service.create_suite(
        tenant_id=seeded_tenant.tenant_id,
        name="No run guard",
        target_type="workflow_draft",
        target_id="draft-3",
        target_version="rev-current",
        actor_principal_id="tenant-admin",
    )
    no_version_suite = await service.create_suite(
        tenant_id=seeded_tenant.tenant_id,
        name="No version guard",
        target_type="workflow_draft",
        target_id="draft-3",
        target_version=None,
        actor_principal_id="tenant-admin",
    )
    failed_run = await repository.add_run(
        AgentTestRun(
            tenant_id=seeded_tenant.tenant_id,
            agent_test_suite_id=failed_current_suite.agent_test_suite_id,
            target_type=AgentTestTargetType.WORKFLOW_DRAFT,
            target_id="draft-3",
            target_version="rev-current",
            safe_mode=AgentTestSafeMode.MOCK_MODEL,
            status=AgentTestRunStatus.FAILED,
            pass_status="failed",
            triggered_by_principal_id="tenant-admin",
            idempotency_key="failed-current-evidence",
        )
    )
    stale_run = await repository.add_run(
        AgentTestRun(
            tenant_id=seeded_tenant.tenant_id,
            agent_test_suite_id=stale_suite.agent_test_suite_id,
            target_type=AgentTestTargetType.WORKFLOW_DRAFT,
            target_id="draft-3",
            target_version="rev-old",
            safe_mode=AgentTestSafeMode.MOCK_MODEL,
            status=AgentTestRunStatus.PASSED,
            pass_status="passed",
            triggered_by_principal_id="tenant-admin",
            idempotency_key="stale-evidence",
        )
    )
    no_version_run = await repository.add_run(
        AgentTestRun(
            tenant_id=seeded_tenant.tenant_id,
            agent_test_suite_id=no_version_suite.agent_test_suite_id,
            target_type=AgentTestTargetType.WORKFLOW_DRAFT,
            target_id="draft-3",
            target_version=None,
            safe_mode=AgentTestSafeMode.MOCK_MODEL,
            status=AgentTestRunStatus.PASSED,
            pass_status="passed",
            triggered_by_principal_id="tenant-admin",
            idempotency_key="no-version-evidence",
        )
    )
    artifact = await repository.add_artifact(
        AgentTestArtifact(
            tenant_id=seeded_tenant.tenant_id,
            agent_test_run_id=no_version_run.agent_test_run_id,
            artifact_type="diagnostic_summary",
            checksum_sha256="sha256:serviceartifact",
            retention_state="retained",
            redaction_classification="safe-summary",
            safe_summary={"summary": "Service artifact metadata."},
        )
    )
    latest_no_version = await repository.latest_run_for_suite(
        suite_id=no_version_suite.agent_test_suite_id,
        tenant_id=seeded_tenant.tenant_id,
        target_version=None,
        match_target_version=True,
    )

    summary = await service.evidence_summary_for_required_suites(
        tenant_id=seeded_tenant.tenant_id,
        target_type="workflow_draft",
        target_id="draft-3",
        target_version="rev-current",
        requirements=[
            RequiredSuiteEvidenceRequest(
                requirement_key="invalid",
                suite_id="not-a-uuid",
            ),
            RequiredSuiteEvidenceRequest(
                requirement_key="missing",
                suite_id=str(uuid4()),
            ),
            RequiredSuiteEvidenceRequest(
                requirement_key="archived",
                suite_id=str(archived_suite.agent_test_suite_id),
            ),
            RequiredSuiteEvidenceRequest(
                requirement_key="wrong-target",
                suite_id=str(wrong_target_suite.agent_test_suite_id),
            ),
            RequiredSuiteEvidenceRequest(
                requirement_key="failed-current",
                suite_id=str(failed_current_suite.agent_test_suite_id),
            ),
            RequiredSuiteEvidenceRequest(
                requirement_key="stale",
                suite_id=str(stale_suite.agent_test_suite_id),
            ),
            RequiredSuiteEvidenceRequest(
                requirement_key="no-run",
                suite_id=str(no_run_suite.agent_test_suite_id),
            ),
        ],
    )
    by_key = {item.requirement_key: item for item in summary.evidence}

    assert by_key["invalid"].status == "missing"
    assert by_key["missing"].status == "missing"
    assert by_key["archived"].status == "missing"
    assert by_key["wrong-target"].status == "stale"
    assert by_key["failed-current"].status == "failed"
    assert by_key["failed-current"].evidence_run_id == str(failed_run.agent_test_run_id)
    assert by_key["stale"].status == "stale"
    assert by_key["stale"].evidence_run_id == str(stale_run.agent_test_run_id)
    assert by_key["no-run"].status == "missing"
    assert summary.failing_count == 1
    assert summary.stale_count == 2
    assert summary.missing_count == 4
    assert latest_no_version == no_version_run
    assert artifact.agent_test_artifact_id is not None
    assert _status_value(AgentTestStatus.ACTIVE) == "active"
    assert _status_value("AgentTestStatus.ACTIVE") == "active"
