from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.db.repositories.model_providers import ModelProviderRepository
from multi_agent_platform.model_providers.models import OperationStatus


async def test_denied_and_throttled_probe_attempts_persist_safe_evidence(
    session,
) -> None:
    repo = ModelProviderRepository(session)
    operation, _created = await repo.get_or_create_provider_probe_operation(
        operation_identity="probe:denied",
        provider_connection_id=uuid4(),
        provider_model_definition_id=None,
        tenant_id=uuid4(),
        actor_principal_id="tenant-admin",
        rate_limit_scope={"actor": "tenant-admin"},
        bounded_operation_decision={"allowed": False},
        safe_summary={"decision_category": "denied"},
    )
    operation.status = OperationStatus.DENIED
    await session.flush()

    assert operation.safe_summary_json == {"decision_category": "denied"}
    assert "secret" not in str(operation.safe_summary_json).lower()
    assert operation.status is OperationStatus.DENIED
