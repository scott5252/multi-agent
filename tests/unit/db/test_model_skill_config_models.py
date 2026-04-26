from __future__ import annotations

from uuid import uuid4

from sqlalchemy import select

from multi_agent_platform.db.models.model_skill_config import (
    ActiveConfigurationPointer,
    ModelProviderCatalogEntry,
    ModelRoutingVersion,
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
