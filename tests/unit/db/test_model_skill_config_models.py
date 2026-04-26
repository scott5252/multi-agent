from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from multi_agent_platform.db.models.model_skill_config import (
    ActiveConfigurationPointer,
    ConfigurationAuditRecord,
    ModelProviderCatalogEntry,
    ModelRoutingVersion,
    ModelSkillConfigKind,
    RuntimeDecisionOutcome,
    RuntimePolicyDecision,
)


async def test_model_skill_config_models_persist_version_and_pointer(session) -> None:
    tenant_id = uuid4()
    principal_id = uuid4()
    provider = ModelProviderCatalogEntry(
        tenant_id=tenant_id,
        provider_key="openai",
        model_id="gpt-5.4",
        display_name="GPT 5.4",
    )
    session.add(provider)
    await session.flush()
    version = ModelRoutingVersion(
        tenant_id=tenant_id,
        scope_type="tenant_default",
        scope_hash="abc",
        model_provider_entry_id=provider.model_provider_entry_id,
        created_by_principal_id=principal_id,
        activation_reason="test",
    )
    session.add(version)
    await session.flush()
    pointer = ActiveConfigurationPointer(
        tenant_id=tenant_id,
        config_kind="model_routing",
        scope_hash="abc",
        scope_selectors={"tenant_id": str(tenant_id)},
        active_version_id=version.model_routing_version_id,
        activated_by_principal_id=principal_id,
        activation_reason="test",
    )
    session.add(pointer)
    await session.flush()

    stored = (
        await session.execute(
            select(ActiveConfigurationPointer).where(
                ActiveConfigurationPointer.scope_hash == "abc"
            )
        )
    ).scalar_one()
    assert stored.active_version_id == version.model_routing_version_id


async def test_active_configuration_pointer_is_unique_per_kind_and_scope(
    session,
) -> None:
    tenant_id = uuid4()
    principal_id = uuid4()
    pointer = ActiveConfigurationPointer(
        tenant_id=tenant_id,
        config_kind=ModelSkillConfigKind.MODEL_ROUTING,
        scope_hash="abc",
        scope_selectors={"tenant_id": str(tenant_id)},
        active_version_id=uuid4(),
        activated_by_principal_id=principal_id,
        activation_reason="first",
    )
    duplicate = ActiveConfigurationPointer(
        tenant_id=tenant_id,
        config_kind=ModelSkillConfigKind.MODEL_ROUTING,
        scope_hash="abc",
        scope_selectors={"tenant_id": str(tenant_id)},
        active_version_id=uuid4(),
        activated_by_principal_id=principal_id,
        activation_reason="second",
    )
    session.add_all([pointer, duplicate])

    with pytest.raises(IntegrityError):
        await session.flush()
    await session.rollback()


async def test_runtime_decision_and_configuration_audit_rows_persist(
    session,
) -> None:
    tenant_id = uuid4()
    workflow_run_id = uuid4()
    decision = RuntimePolicyDecision(
        tenant_id=tenant_id,
        workflow_run_id=workflow_run_id,
        decision_category="tool",
        requested_resource="http.fetch",
        requested_action="read",
        outcome=RuntimeDecisionOutcome.DENY,
        denial_category="tool_denied",
        safe_reason="no active tool allow policy matched",
        evaluated_version_ids=["version-a"],
        winning_version_ids=[],
        source_scopes=["agent"],
        idempotency_key="run-step-tool-1",
        redacted_metadata={"tool_id": "http.fetch"},
    )
    audit = ConfigurationAuditRecord(
        tenant_id=tenant_id,
        actor_principal_id=uuid4(),
        actor_role="tenant_admin",
        action="activate",
        config_kind=ModelSkillConfigKind.MODEL_ROUTING,
        affected_scope={"tenant_id": str(tenant_id)},
        new_version_id=uuid4(),
        reason="test activation",
        redacted_diff_summary={"scope_hash": "abc"},
    )
    session.add_all([decision, audit])
    await session.flush()

    stored_decision = (
        await session.execute(
            select(RuntimePolicyDecision).where(
                RuntimePolicyDecision.workflow_run_id == workflow_run_id
            )
        )
    ).scalar_one()
    stored_audit = (
        await session.execute(
            select(ConfigurationAuditRecord).where(
                ConfigurationAuditRecord.new_version_id == audit.new_version_id
            )
        )
    ).scalar_one()

    assert stored_decision.outcome is RuntimeDecisionOutcome.DENY
    assert stored_decision.redacted_metadata == {"tool_id": "http.fetch"}
    assert stored_audit.reason == "test activation"
