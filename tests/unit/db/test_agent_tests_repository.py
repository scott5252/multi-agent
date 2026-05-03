from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.db.models.agent_tests import (
    AgentTestPublicationRequirement,
    AgentTestRun,
    AgentTestRunStatus,
    AgentTestSafeMode,
    AgentTestSuite,
    AgentTestTargetType,
)
from multi_agent_platform.db.repositories.agent_tests import (
    AgentTestRepository,
    StaleAgentTestWriteError,
)


async def test_agent_test_repository_filters_by_tenant_and_revision(
    session,
    seeded_tenant,
) -> None:
    repository = AgentTestRepository(session)
    suite = await repository.add_suite(
        AgentTestSuite(
            tenant_id=seeded_tenant.tenant_id,
            name="Draft guard",
            target_type=AgentTestTargetType.WORKFLOW_DRAFT,
            target_id="draft-1",
            created_by_principal_id="tenant-admin",
        )
    )

    assert await repository.list_suites_for_tenant(
        tenant_id=seeded_tenant.tenant_id
    ) == [suite]
    assert await repository.list_suites_for_tenant(tenant_id=uuid4()) == []
    assert await repository.require_suite_revision(
        suite_id=suite.agent_test_suite_id,
        tenant_id=seeded_tenant.tenant_id,
        expected_revision=1,
    )
    with pytest.raises(StaleAgentTestWriteError):
        await repository.require_suite_revision(
            suite_id=suite.agent_test_suite_id,
            tenant_id=seeded_tenant.tenant_id,
            expected_revision=2,
        )


async def test_agent_test_repository_finds_current_passing_gate_evidence(
    session,
    seeded_tenant,
) -> None:
    repository = AgentTestRepository(session)
    suite = await repository.add_suite(
        AgentTestSuite(
            tenant_id=seeded_tenant.tenant_id,
            name="Draft guard",
            target_type=AgentTestTargetType.WORKFLOW_DRAFT,
            target_id="draft-1",
            target_version="rev-1",
            is_required_for_publish=True,
            created_by_principal_id="tenant-admin",
        )
    )
    await repository.add_publication_requirement(
        AgentTestPublicationRequirement(
            tenant_id=seeded_tenant.tenant_id,
            target_type=AgentTestTargetType.WORKFLOW_DRAFT,
            target_id="draft-1",
            agent_test_suite_id=suite.agent_test_suite_id,
            created_by_principal_id="tenant-admin",
        )
    )
    run = await repository.add_run(
        AgentTestRun(
            tenant_id=seeded_tenant.tenant_id,
            agent_test_suite_id=suite.agent_test_suite_id,
            target_type=AgentTestTargetType.WORKFLOW_DRAFT,
            target_id="draft-1",
            target_version="rev-1",
            safe_mode=AgentTestSafeMode.MOCK_MODEL,
            status=AgentTestRunStatus.PASSED,
            pass_status="passed",
            triggered_by_principal_id="tenant-admin",
            idempotency_key="idem-1",
        )
    )

    requirements = await repository.list_publication_requirements(
        tenant_id=seeded_tenant.tenant_id,
        target_type="workflow_draft",
        target_id="draft-1",
    )
    latest = await repository.latest_passing_run_for_suite(
        suite_id=suite.agent_test_suite_id,
        tenant_id=seeded_tenant.tenant_id,
        target_version="rev-1",
    )

    assert requirements[0].agent_test_suite_id == suite.agent_test_suite_id
    assert latest == run
