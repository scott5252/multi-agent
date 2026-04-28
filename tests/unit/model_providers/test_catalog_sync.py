from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4

import pytest

from multi_agent_platform.db.models.model_providers import (
    ModelProviderConnection,
    ProviderModelDefinition,
)
from multi_agent_platform.model_providers.catalog_sync import CatalogSynchronizer
from multi_agent_platform.model_providers.models import (
    HealthState,
    ProviderType,
    SyncAction,
    TestOutcome,
    VisibilityMode,
)


@dataclass
class FakeCatalogRepository:
    models: list[ProviderModelDefinition]
    tenant_ids: tuple[UUID, ...] = ()
    records: list[tuple[SyncAction, TestOutcome, UUID | None]] | None = None

    async def list_models(self, _connection_id: UUID) -> list[ProviderModelDefinition]:
        return self.models

    async def visible_tenant_ids(self, _connection_id: UUID) -> tuple[UUID, ...]:
        return self.tenant_ids

    async def record_catalog_sync(self, **kwargs: object) -> None:
        if self.records is None:
            self.records = []
        self.records.append(
            (
                kwargs["sync_action"],
                kwargs["outcome"],
                kwargs["tenant_id"],
            )
        )


def _connection(
    *,
    healthy: bool,
    visibility: VisibilityMode,
) -> ModelProviderConnection:
    return ModelProviderConnection(
        provider_connection_id=uuid4(),
        provider_type=ProviderType.OPENAI,
        display_name="Provider",
        timeout_policy={},
        visibility_mode=visibility,
        active=healthy,
        health_state=HealthState.HEALTHY if healthy else HealthState.DISABLED,
        credential_secret_reference_ids=[],
        safe_metadata={},
        created_by_principal_id="admin",
        updated_by_principal_id="admin",
    )


def _model(connection_id: UUID) -> ProviderModelDefinition:
    return ProviderModelDefinition(
        provider_connection_id=connection_id,
        model_id="gpt-test",
        display_name="GPT Test",
        capability_metadata={},
        cost_metadata={},
        default_parameters={},
        available=True,
    )


@pytest.mark.asyncio
async def test_catalog_sync_marks_unhealthy_entries_unavailable() -> None:
    connection = _connection(healthy=False, visibility=VisibilityMode.PLATFORM_DEFAULT)
    repo = FakeCatalogRepository(models=[_model(connection.provider_connection_id)])

    summary = await CatalogSynchronizer(repo).sync_connection(
        connection=connection,
        principal_id="admin",
    )

    assert summary.marked_unavailable == 1
    assert repo.records == [(SyncAction.MARKED_UNAVAILABLE, TestOutcome.SUCCESS, None)]


@pytest.mark.asyncio
async def test_catalog_sync_updates_healthy_tenant_entries() -> None:
    tenant_id = uuid4()
    connection = _connection(healthy=True, visibility=VisibilityMode.TENANT_ALLOWLIST)
    repo = FakeCatalogRepository(
        models=[_model(connection.provider_connection_id)],
        tenant_ids=(tenant_id,),
    )

    summary = await CatalogSynchronizer(repo).sync_connection(
        connection=connection,
        principal_id="admin",
    )

    assert summary.updated == 1
    assert repo.records == [(SyncAction.UPDATED, TestOutcome.SUCCESS, tenant_id)]
