from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.db.models.agent_tests import (
    AgentTestAssertion,
    AgentTestAssertionKind,
    AgentTestCase,
)
from multi_agent_platform.testing.agent_bench.models import (
    AgentBenchRunStatus,
    AgentBenchSafeMode,
)
from multi_agent_platform.testing.agent_bench.sandbox import (
    AgentBenchSandbox,
    AgentBenchSandboxError,
)


def _case() -> AgentTestCase:
    return AgentTestCase(
        agent_test_suite_id=uuid4(),
        tenant_id=uuid4(),
        name="Passing case",
        fixture_summary={
            "preview": {"request": "summarize intake"},
            "redacted": False,
        },
        expected_contract_shape={"status": {}, "contract": {}},
    )


def test_sandbox_executes_mock_model_and_records_safe_metadata() -> None:
    case = _case()
    assertion = AgentTestAssertion(
        agent_test_case_id=case.agent_test_case_id,
        tenant_id=case.tenant_id,
        kind=AgentTestAssertionKind.DETERMINISTIC,
        path="contract.summary",
        comparator="contains",
        expected_value="intake",
    )

    result = AgentBenchSandbox().execute(
        safe_mode=AgentBenchSafeMode.MOCK_MODEL,
        cases=[(case, [assertion])],
        target_version="draft-rev-1",
    )

    assert result.status is AgentBenchRunStatus.PASSED
    assert result.usage_summary["test_mode"] == 1
    assert result.steps[0].model_provider == "mock"
    assert result.steps[0].assertion_results[0].passed is True
    assert result.redaction_summary["raw_secret_values"] == 0


def test_sandbox_blocks_side_effects_and_unapproved_real_probe() -> None:
    case = _case()

    side_effects_disabled = AgentBenchSandbox().execute(
        safe_mode=AgentBenchSafeMode.REAL_MODEL_SIDE_EFFECTS_DISABLED,
        cases=[(case, [])],
        target_version="draft-rev-1",
    )

    assert side_effects_disabled.blocked_side_effect_count == 1
    assert side_effects_disabled.steps[0].model_provider == "mocked-gateway"
    with pytest.raises(AgentBenchSandboxError):
        AgentBenchSandbox().execute(
            safe_mode=AgentBenchSafeMode.APPROVED_REAL_PROBE,
            cases=[(case, [])],
            target_version="draft-rev-1",
        )
