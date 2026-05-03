from __future__ import annotations

from multi_agent_platform.db.models.agent_tests import (
    AgentTestSafeMode,
    AgentTestSuite,
    AgentTestTargetType,
)


async def test_agent_test_suite_model_defaults(session, seeded_tenant) -> None:
    suite = AgentTestSuite(
        tenant_id=seeded_tenant.tenant_id,
        name="Draft guard",
        target_type=AgentTestTargetType.WORKFLOW_DRAFT,
        target_id="draft-1",
        created_by_principal_id="tenant-admin",
    )
    session.add(suite)
    await session.flush()

    assert suite.default_safe_mode is AgentTestSafeMode.MOCK_MODEL
    assert suite.pass_threshold == 1.0
    assert suite.revision == 1
