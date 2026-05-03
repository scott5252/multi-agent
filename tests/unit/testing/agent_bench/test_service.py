from __future__ import annotations

import pytest

from multi_agent_platform.db.repositories.agent_tests import AgentTestRepository
from multi_agent_platform.testing.agent_bench.service import (
    AgentTestBenchError,
    AgentTestBenchService,
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
