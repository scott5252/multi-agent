from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from multi_agent_platform.bootstrap.container import Container
from multi_agent_platform.runtime.health.models import (
    DependencyHealthCheck,
    DependencyStatus,
)


async def check_configuration(container: Container) -> DependencyHealthCheck:
    settings = container.settings
    detail = None
    status = DependencyStatus.READY
    if not settings.app_name or not settings.database_url:
        status = DependencyStatus.UNAVAILABLE
        detail = "required settings are missing"
    return DependencyHealthCheck(
        name="config", required=True, status=status, detail=detail
    )


async def check_auth_configuration(container: Container) -> DependencyHealthCheck:
    if container.auth_failure_detail is not None:
        return DependencyHealthCheck(
            name="auth",
            required=True,
            status=DependencyStatus.UNAVAILABLE,
            detail=container.auth_failure_detail,
        )
    return DependencyHealthCheck(
        name="auth",
        required=True,
        status=DependencyStatus.READY,
    )


async def check_database(container: Container) -> DependencyHealthCheck:
    try:
        async with container.engine.begin() as connection:
            await connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        return DependencyHealthCheck(
            name="postgres",
            required=True,
            status=DependencyStatus.UNAVAILABLE,
            detail=str(exc),
        )
    return DependencyHealthCheck(
        name="postgres", required=True, status=DependencyStatus.READY
    )


async def check_migrations(container: Container) -> DependencyHealthCheck:
    try:
        async with container.engine.begin() as connection:
            result = await connection.execute(
                text("SELECT version_num FROM alembic_version")
            )
            version = result.scalar_one_or_none()
    except SQLAlchemyError:
        return DependencyHealthCheck(
            name="migrations",
            required=True,
            status=DependencyStatus.UNAVAILABLE,
            detail="alembic_version table is missing",
        )
    if version is None:
        return DependencyHealthCheck(
            name="migrations",
            required=True,
            status=DependencyStatus.UNAVAILABLE,
            detail="database is not migrated",
        )
    return DependencyHealthCheck(
        name="migrations",
        required=True,
        status=DependencyStatus.READY,
        detail=version,
    )


async def check_worker_dependencies(container: Container) -> DependencyHealthCheck:
    return DependencyHealthCheck(
        name="worker",
        required=True,
        status=DependencyStatus.READY
        if container.worker_dependencies_ready
        else DependencyStatus.UNAVAILABLE,
        detail=None
        if container.worker_dependencies_ready
        else "worker bootstrap check failed",
    )
