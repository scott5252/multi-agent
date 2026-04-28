from __future__ import annotations

from sqlalchemy import select
from tests.integration.runtime.test_gateway_operation_recovery import (
    test_gateway_operation_duplicate_reuses_authoritative_outcome,
)

from multi_agent_platform.db.models.model_providers import GatewayPhysicalAttempt


async def test_gateway_attempts_include_safe_retry_breaker_and_usage_evidence(
    session,
) -> None:
    await test_gateway_operation_duplicate_reuses_authoritative_outcome(session)

    attempt = (
        await session.execute(select(GatewayPhysicalAttempt).limit(1))
    ).scalar_one()

    assert attempt.retry_category in {"skipped", "recovered"}
    assert attempt.breaker_scope.startswith("provider_connection:")
    assert "normalized_error_category" in attempt.safe_audit_summary_json
    assert isinstance(attempt.usage_available, bool)
