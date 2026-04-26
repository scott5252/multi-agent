from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.audit.service import AuditDebuggingService
from multi_agent_platform.bootstrap.container import Container
from multi_agent_platform.config.settings import Settings
from multi_agent_platform.db.repositories.audit_debugging import (
    AuditDebuggingRepository,
)
from multi_agent_platform.db.session import session_scope
from multi_agent_platform.secrets.base import SecretProvider
from multi_agent_platform.storage.base import StorageProvider
from multi_agent_platform.tenancy.context import ScopeContext, get_scope_context


def get_container(request: Request) -> Container:
    return request.app.state.container  # type: ignore[no-any-return]


ContainerDep = Annotated[Container, Depends(get_container)]


def get_settings(container: ContainerDep) -> Settings:
    return container.settings


async def get_session(
    container: ContainerDep,
) -> AsyncIterator[AsyncSession]:
    async with session_scope(container.session_factory) as session:
        yield session


def get_scope(request: Request) -> ScopeContext:
    scope = getattr(request.state, "scope_context", None) or get_scope_context()
    if scope is None:
        raise RuntimeError("scope context missing")
    return scope


def get_secret_provider(
    container: ContainerDep,
) -> SecretProvider:
    return container.secret_provider


def get_storage_provider(
    container: ContainerDep,
) -> StorageProvider:
    return container.storage_provider


async def get_audit_debugging_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AuditDebuggingService:
    return AuditDebuggingService(AuditDebuggingRepository(session))
