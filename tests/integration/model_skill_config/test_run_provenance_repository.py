from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.config.model_skill import DecisionCategory, PolicyOutcome
from multi_agent_platform.config.provenance import SafeRuntimeDecision
from multi_agent_platform.db.models.model_skill_config import (
    RuntimeDecisionOutcome,
    RuntimePolicyDecision,
)
from multi_agent_platform.db.repositories.model_skill_config import (
    ModelSkillConfigRepository,
)


async def test_runtime_policy_decision_idempotency_and_secret_redaction(
    session,
) -> None:
    tenant_id = uuid4()
    run_id = uuid4()
    repo = ModelSkillConfigRepository(session)
    payload = SafeRuntimeDecision(
        tenant_id=tenant_id,
        workflow_run_id=run_id,
        decision_category=DecisionCategory.TOOL,
        outcome=PolicyOutcome.DENY,
        requested_resource="http.fetch",
        idempotency_key="tool-once",
        safe_reason="denied before side effects",
        redacted_metadata={"secret_reference_id": "ref"},
    ).to_record_payload()
    await repo.add_runtime_decision(
        RuntimePolicyDecision(
            tenant_id=tenant_id,
            workflow_run_id=run_id,
            decision_category=DecisionCategory.TOOL.value,
            requested_resource=str(payload["requested_resource"]),
            outcome=RuntimeDecisionOutcome.DENY,
            safe_reason=str(payload["safe_reason"]),
            evaluated_version_ids=[],
            winning_version_ids=[],
            source_scopes=[],
            idempotency_key="tool-once",
            redacted_metadata={"secret_reference_id": "ref"},
        )
    )

    reused = await repo.get_runtime_decision_by_idempotency(
        tenant_id=tenant_id,
        workflow_run_id=run_id,
        decision_category=DecisionCategory.TOOL.value,
        idempotency_key="tool-once",
    )

    assert reused is not None
    assert "fixture-secret" not in str(reused.redacted_metadata)
