from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from multi_agent_platform.db.models.model_providers import ModelProviderConnection
from multi_agent_platform.db.repositories.model_providers import ModelProviderRepository
from multi_agent_platform.model_providers.models import (
    ErrorCategory,
    HealthState,
    SyncAction,
    TestOutcome,
    VisibilityMode,
)


@dataclass(frozen=True, slots=True)
class CatalogSyncSummary:
    created: int = 0
    updated: int = 0
    blocked: int = 0
    marked_unavailable: int = 0
    safe_summary: str = "Catalog synchronization completed"


class CatalogSynchronizer:
    def __init__(self, repository: ModelProviderRepository) -> None:
        self._repository = repository

    async def sync_connection(
        self,
        *,
        connection: ModelProviderConnection,
        principal_id: str,
    ) -> CatalogSyncSummary:
        models = await self._repository.list_models(connection.provider_connection_id)
        tenant_ids: tuple[UUID | None, ...]
        if connection.visibility_mode is VisibilityMode.PLATFORM_DEFAULT:
            tenant_ids = (None,)
        else:
            tenant_ids = await self._repository.visible_tenant_ids(
                connection.provider_connection_id
            )
        if not connection.active or connection.health_state is not HealthState.HEALTHY:
            count = 0
            for model in models:
                for tenant_id in tenant_ids:
                    await self._repository.record_catalog_sync(
                        connection_id=connection.provider_connection_id,
                        model_definition_id=model.provider_model_definition_id,
                        tenant_id=tenant_id,
                        sync_action=SyncAction.MARKED_UNAVAILABLE,
                        outcome=TestOutcome.SUCCESS,
                        reason=ErrorCategory.CATALOG_INACTIVE,
                        summary="Model catalog entry marked unavailable",
                        principal_id=principal_id,
                    )
                    count += 1
            return CatalogSyncSummary(marked_unavailable=count)
        count = 0
        for model in models:
            for tenant_id in tenant_ids:
                await self._repository.record_catalog_sync(
                    connection_id=connection.provider_connection_id,
                    model_definition_id=model.provider_model_definition_id,
                    tenant_id=tenant_id,
                    sync_action=SyncAction.UPDATED,
                    outcome=TestOutcome.SUCCESS,
                    reason=ErrorCategory.NONE,
                    summary="Model catalog entry is gateway-governed and selectable",
                    principal_id=principal_id,
                )
                count += 1
        return CatalogSyncSummary(updated=count)
