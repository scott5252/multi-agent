from __future__ import annotations

from collections.abc import AsyncIterator

import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from multi_agent_platform.db.base import Base
from multi_agent_platform.db.models import import_models
from multi_agent_platform.db.models.tenant import Tenant
from multi_agent_platform.db.session import create_engine, session_scope
from tests.fixtures.config import make_settings


@pytest_asyncio.fixture
async def engine(tmp_path) -> AsyncIterator[AsyncEngine]:
    settings = make_settings(tmp_path)
    engine = create_engine(settings)
    import_models()
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
        await connection.execute(
            text("CREATE TABLE alembic_version (version_num VARCHAR(64) NOT NULL)")
        )
        await connection.execute(
            text(
                "INSERT INTO alembic_version(version_num) "
                "VALUES ('0004_durable_runtime')"
            )
        )
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


@pytest_asyncio.fixture
async def session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncSession]:
    async with session_scope(session_factory) as session:
        yield session


@pytest_asyncio.fixture
async def seeded_tenant(session: AsyncSession, settings) -> Tenant:
    tenant = Tenant(
        tenant_id=settings.local_principal_catalog_json["tenant-admin-acme"].tenant_id,
        slug="acme",
        display_name="Acme",
    )
    session.add(tenant)
    await session.flush()
    return tenant
