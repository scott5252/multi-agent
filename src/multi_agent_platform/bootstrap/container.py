from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from starlette.templating import Jinja2Templates

from multi_agent_platform.agents.service import AgentProfileService
from multi_agent_platform.audit.service import AuditDebuggingService
from multi_agent_platform.auth.config import auth_configuration_error
from multi_agent_platform.auth.jwt_validator import Auth0JwtValidator
from multi_agent_platform.auth.local_principals import LocalPrincipalCatalog
from multi_agent_platform.config.service import ModelSkillConfigService
from multi_agent_platform.config.settings import (
    SecretProviderKind,
    Settings,
    StorageProviderKind,
)
from multi_agent_platform.db.repositories.agent_profiles import AgentProfileRepository
from multi_agent_platform.db.repositories.audit_debugging import (
    AuditDebuggingRepository,
)
from multi_agent_platform.db.repositories.model_providers import ModelProviderRepository
from multi_agent_platform.db.repositories.model_skill_config import (
    ModelSkillConfigRepository,
)
from multi_agent_platform.db.repositories.prompts import PromptRepository
from multi_agent_platform.db.repositories.usage import UsageRepository
from multi_agent_platform.db.session import create_engine
from multi_agent_platform.model_providers.adapters import ProviderAdapterRegistry
from multi_agent_platform.model_providers.allowlist import LocalEndpointAllowlist
from multi_agent_platform.model_providers.gateway import ModelGateway
from multi_agent_platform.model_providers.local_adapter import (
    LocalOpenAICompatibleAdapter,
)
from multi_agent_platform.model_providers.models import ProviderType
from multi_agent_platform.model_providers.openai_adapter import OpenAIAdapter
from multi_agent_platform.model_providers.probes import ProviderProbeRunner
from multi_agent_platform.model_providers.secrets import ProviderSecretResolver
from multi_agent_platform.model_providers.service import ModelProviderService
from multi_agent_platform.observability.logging import configure_logging
from multi_agent_platform.prompts.service import PromptService
from multi_agent_platform.reliability.breakers import gateway_breaker_summary
from multi_agent_platform.reliability.retries import gateway_retry_summary
from multi_agent_platform.secrets.base import SecretProvider
from multi_agent_platform.secrets.providers.env import EnvSecretProvider
from multi_agent_platform.secrets.providers.secret_manager import SecretManagerProvider
from multi_agent_platform.secrets.providers.static import StaticSecretProvider
from multi_agent_platform.storage.base import StorageProvider
from multi_agent_platform.storage.providers.filesystem import FilesystemStorageProvider
from multi_agent_platform.storage.providers.s3 import S3StorageProvider
from multi_agent_platform.usage.service import UsageAnalyticsService


def build_secret_provider(settings: Settings) -> SecretProvider:
    if settings.secret_provider is SecretProviderKind.ENV:
        return EnvSecretProvider(prefix=settings.env_secret_prefix)
    if settings.secret_provider is SecretProviderKind.SECRET_MANAGER:
        return SecretManagerProvider(prefix=settings.secret_manager_prefix)
    return StaticSecretProvider(settings.static_secrets_json)


def build_storage_provider(settings: Settings) -> StorageProvider:
    if settings.storage_provider is StorageProviderKind.S3:
        return S3StorageProvider(bucket=settings.s3_bucket, root=Path(".data/s3"))
    return FilesystemStorageProvider(root=settings.filesystem_storage_root)


def build_template_renderer(settings: Settings) -> Jinja2Templates:
    return Jinja2Templates(directory=str(settings.web_admin_templates_dir))


@dataclass(slots=True)
class Container:
    settings: Settings
    engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]
    secret_provider: SecretProvider
    storage_provider: StorageProvider
    workflow_ui_templates: Jinja2Templates
    jwt_validator: Auth0JwtValidator | None
    local_principal_catalog: LocalPrincipalCatalog
    logger: logging.Logger
    model_skill_service_factory: Callable[[AsyncSession], ModelSkillConfigService]
    model_provider_repository_factory: Callable[[AsyncSession], ModelProviderRepository]
    model_provider_service_factory: (
        Callable[[AsyncSession], ModelProviderService] | None
    )
    provider_adapter_registry_factory: Callable[[], ProviderAdapterRegistry] | None
    model_gateway_factory: Callable[[AsyncSession], ModelGateway] | None
    provider_secret_resolver_factory: (
        Callable[[AsyncSession], ProviderSecretResolver] | None
    )
    gateway_metrics_hooks: object | None
    gateway_tracing_hooks: object | None
    gateway_audit_hooks: object | None
    retry_decision_helper: object | None
    breaker_decision_helper: object | None
    prompt_service_factory: Callable[[AsyncSession], PromptService]
    agent_profile_service_factory: Callable[[AsyncSession], AgentProfileService]
    audit_debugging_service_factory: Callable[[AsyncSession], AuditDebuggingService]
    auth_failure_detail: str | None = None
    worker_dependencies_ready: bool = True
    state: dict[str, object] = field(default_factory=dict)

    async def dispose(self) -> None:
        registry = self.state.get("provider_adapter_registry")
        if isinstance(registry, ProviderAdapterRegistry):
            await registry.aclose()
        await self.engine.dispose()


def build_model_provider_allowlist(settings: Settings) -> LocalEndpointAllowlist:
    return LocalEndpointAllowlist(
        schemes=settings.model_provider_local_allowed_schemes,
        hosts=settings.model_provider_local_allowed_hosts,
        ports=settings.model_provider_local_allowed_ports,
        cidrs=settings.model_provider_local_allowed_cidrs,
    )


def _provider_adapter_registry(container: Container) -> ProviderAdapterRegistry:
    registry = container.state.get("provider_adapter_registry")
    if isinstance(registry, ProviderAdapterRegistry):
        return registry
    allowlist = build_model_provider_allowlist(container.settings)
    registry = ProviderAdapterRegistry(
        {
            ProviderType.OPENAI: OpenAIAdapter(),
            ProviderType.LOCAL_OPENAI_COMPATIBLE: LocalOpenAICompatibleAdapter(
                allowlist=allowlist
            ),
        }
    )
    container.state["provider_adapter_registry"] = registry
    return registry


def build_container(settings: Settings | None = None) -> Container:
    resolved_settings = settings or Settings()
    resolved_settings.ensure_directories()
    engine = create_engine(resolved_settings)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    holder: dict[str, Container] = {}
    container = Container(
        settings=resolved_settings,
        engine=engine,
        session_factory=session_factory,
        secret_provider=build_secret_provider(resolved_settings),
        storage_provider=build_storage_provider(resolved_settings),
        workflow_ui_templates=build_template_renderer(resolved_settings),
        jwt_validator=Auth0JwtValidator(resolved_settings)
        if resolved_settings.auth_mode.value == "auth0"
        else None,
        local_principal_catalog=LocalPrincipalCatalog(
            resolved_settings.local_principal_catalog_json
        ),
        logger=configure_logging(resolved_settings.log_level),
        model_skill_service_factory=lambda session: ModelSkillConfigService(
            repository=ModelSkillConfigRepository(session),
        ),
        model_provider_repository_factory=lambda session: ModelProviderRepository(
            session
        ),
        model_provider_service_factory=lambda session: ModelProviderService(
            repository=ModelProviderRepository(session),
            allowlist=build_model_provider_allowlist(resolved_settings),
            probe_runner=ProviderProbeRunner(
                _provider_adapter_registry(holder["container"])
            ),
        ),
        provider_adapter_registry_factory=lambda: _provider_adapter_registry(
            holder["container"]
        ),
        model_gateway_factory=lambda session: ModelGateway(
            repository=ModelProviderRepository(session),
            registry=_provider_adapter_registry(holder["container"]),
            usage_recorder=UsageAnalyticsService(UsageRepository(session)),
        ),
        provider_secret_resolver_factory=lambda _session: ProviderSecretResolver(
            build_secret_provider(resolved_settings)
        ),
        gateway_metrics_hooks=object(),
        gateway_tracing_hooks=object(),
        gateway_audit_hooks=object(),
        retry_decision_helper=gateway_retry_summary,
        breaker_decision_helper=gateway_breaker_summary,
        prompt_service_factory=lambda session: PromptService(
            repository=PromptRepository(session),
        ),
        agent_profile_service_factory=lambda session: AgentProfileService(
            repository=AgentProfileRepository(session),
        ),
        audit_debugging_service_factory=lambda session: AuditDebuggingService(
            repository=AuditDebuggingRepository(session),
        ),
        auth_failure_detail=auth_configuration_error(resolved_settings),
    )
    holder["container"] = container
    return container
