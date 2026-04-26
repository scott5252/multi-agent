from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from starlette.templating import Jinja2Templates

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
from multi_agent_platform.db.repositories.audit_debugging import (
    AuditDebuggingRepository,
)
from multi_agent_platform.db.repositories.model_skill_config import (
    ModelSkillConfigRepository,
)
from multi_agent_platform.db.session import create_engine
from multi_agent_platform.observability.logging import configure_logging
from multi_agent_platform.secrets.base import SecretProvider
from multi_agent_platform.secrets.providers.env import EnvSecretProvider
from multi_agent_platform.secrets.providers.secret_manager import SecretManagerProvider
from multi_agent_platform.secrets.providers.static import StaticSecretProvider
from multi_agent_platform.storage.base import StorageProvider
from multi_agent_platform.storage.providers.filesystem import FilesystemStorageProvider
from multi_agent_platform.storage.providers.s3 import S3StorageProvider


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
    audit_debugging_service_factory: Callable[[AsyncSession], AuditDebuggingService]
    auth_failure_detail: str | None = None
    worker_dependencies_ready: bool = True
    state: dict[str, object] = field(default_factory=dict)

    async def dispose(self) -> None:
        await self.engine.dispose()


def build_container(settings: Settings | None = None) -> Container:
    resolved_settings = settings or Settings()
    resolved_settings.ensure_directories()
    engine = create_engine(resolved_settings)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    return Container(
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
        audit_debugging_service_factory=lambda session: AuditDebuggingService(
            repository=AuditDebuggingRepository(session),
        ),
        auth_failure_detail=auth_configuration_error(resolved_settings),
    )
