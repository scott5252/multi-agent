from __future__ import annotations

from uuid import UUID

from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.db.base import utcnow
from multi_agent_platform.db.models.model_providers import ModelProviderConnection
from multi_agent_platform.db.repositories.model_providers import ModelProviderRepository
from multi_agent_platform.model_providers.allowlist import LocalEndpointAllowlist
from multi_agent_platform.model_providers.catalog_sync import (
    CatalogSynchronizer,
    CatalogSyncSummary,
)
from multi_agent_platform.model_providers.health import derive_health_state
from multi_agent_platform.model_providers.models import (
    ProviderConnectionSummary,
    ProviderModel,
    ProviderTestSummary,
    ProviderType,
    TenantVisibility,
    TimeoutPolicy,
)
from multi_agent_platform.model_providers.probes import ProviderProbeRunner
from multi_agent_platform.model_providers.redaction import safe_url
from multi_agent_platform.model_providers.validation import (
    ProviderConnectionDraft,
    validate_connection_draft,
)


class ModelProviderPermissionError(PermissionError):
    pass


class ModelProviderService:
    def __init__(
        self,
        *,
        repository: ModelProviderRepository,
        allowlist: LocalEndpointAllowlist,
        probe_runner: ProviderProbeRunner | None = None,
    ) -> None:
        self._repository = repository
        self._allowlist = allowlist
        self._probe_runner = probe_runner

    async def list_connections(
        self,
        *,
        principal: PrincipalContext,
    ) -> list[ProviderConnectionSummary]:
        platform_scope = "platform_admin" in principal.role_codes
        return await self._repository.list_connections(
            tenant_id=principal.tenant_id,
            platform_scope=platform_scope,
        )

    async def get_connection(
        self,
        *,
        connection_id: UUID,
        principal: PrincipalContext,
    ) -> ModelProviderConnection:
        connection = await self._repository.get_connection(connection_id)
        if "platform_admin" in principal.role_codes:
            return connection
        if connection.provider_connection_id not in {
            summary.provider_connection_id
            for summary in await self.list_connections(principal=principal)
        }:
            raise ModelProviderPermissionError("connection is not visible")
        return connection

    async def save_connection(
        self,
        *,
        principal: PrincipalContext,
        connection_id: UUID | None,
        provider_type: ProviderType,
        display_name: str,
        base_url: str | None,
        timeout_policy: TimeoutPolicy,
        visibility: TenantVisibility,
        models: tuple[ProviderModel, ...],
        credential_secret_reference_ids: tuple[str, ...],
        active: bool,
    ) -> ModelProviderConnection:
        draft = validate_connection_draft(
            ProviderConnectionDraft(
                provider_type=provider_type,
                display_name=display_name,
                base_url=base_url,
                timeout_policy=timeout_policy,
                visibility=visibility,
                models=models,
                credential_secret_reference_ids=credential_secret_reference_ids,
                active=active,
            ),
            principal=principal,
            allowlist=self._allowlist,
        )
        connection = await self._repository.save_connection(
            connection_id=connection_id,
            provider_type=draft.provider_type,
            display_name=draft.display_name.strip(),
            base_url_safe=safe_url(draft.base_url),
            timeout_policy=draft.timeout_policy,
            visibility=draft.visibility,
            credential_secret_reference_ids=draft.credential_secret_reference_ids,
            models=draft.models,
            active=draft.active,
            principal_id=principal.principal_id,
        )
        await self._repository.update_health(
            connection=connection,
            test_result_id=None,
            health_state=connection.health_state,
            selectable=False,
            reason="connection metadata saved",
        )
        return connection

    async def set_active(
        self,
        *,
        principal: PrincipalContext,
        connection_id: UUID,
        active: bool,
    ) -> ModelProviderConnection:
        if "platform_admin" not in principal.role_codes:
            raise ModelProviderPermissionError("platform administrator required")
        connection = await self._repository.get_connection(connection_id)
        connection.active = active
        connection.deactivated_at = None if active else utcnow()
        health_state, selectable, reason = derive_health_state(
            active=active,
            latest_test=None,
        )
        await self._repository.update_health(
            connection=connection,
            test_result_id=None,
            health_state=health_state,
            selectable=selectable,
            reason=reason,
        )
        return connection

    async def test_connection(
        self,
        *,
        principal: PrincipalContext,
        connection_id: UUID,
    ) -> ProviderTestSummary:
        if "platform_admin" not in principal.role_codes:
            raise ModelProviderPermissionError("platform administrator required")
        if self._probe_runner is None:
            raise RuntimeError("provider probe runner is not configured")
        connection = await self._repository.get_connection(connection_id)
        models = await self._repository.list_models(connection_id)
        if not models:
            raise LookupError("connection has no models")
        started_at = utcnow()
        result = await self._probe_runner.run_probe(
            provider_type=connection.provider_type,
            model_id=models[0].model_id,
            timeout_policy=TimeoutPolicy.model_validate(connection.timeout_policy),
            base_url=connection.base_url_safe,
            credential=None,
        )
        record = await self._repository.append_test_result(
            connection=connection,
            model_definition_id=models[0].provider_model_definition_id,
            actor_principal_id=principal.principal_id,
            started_at=started_at,
            result=result,
        )
        health_state, selectable, reason = derive_health_state(
            active=connection.active,
            latest_test=result,
        )
        await self._repository.update_health(
            connection=connection,
            test_result_id=record.connection_test_result_id,
            health_state=health_state,
            selectable=selectable,
            reason=reason,
        )
        return result

    async def sync_catalog(
        self,
        *,
        principal: PrincipalContext,
        connection_id: UUID,
    ) -> CatalogSyncSummary:
        if "platform_admin" not in principal.role_codes:
            raise ModelProviderPermissionError("platform administrator required")
        connection = await self._repository.get_connection(connection_id)
        return await CatalogSynchronizer(self._repository).sync_connection(
            connection=connection,
            principal_id=principal.principal_id,
        )
