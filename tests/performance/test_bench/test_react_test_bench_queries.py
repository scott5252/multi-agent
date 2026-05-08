from __future__ import annotations

from time import perf_counter

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from tests.fixtures.agent_tests import seed_live_agent_test_bench_async_session

from multi_agent_platform.api.schemas.admin_react import ReactAdminScope
from multi_agent_platform.auth.principal import AuthMode, AuthProvider, PrincipalContext
from multi_agent_platform.db.models.tenant import Tenant
from multi_agent_platform.db.repositories.agent_tests import AgentTestRepository
from multi_agent_platform.testing.agent_bench.react_test_bench import (
    build_test_bench_dashboard,
    build_test_run_detail,
)


@pytest.mark.asyncio
async def test_react_test_bench_builders_are_bounded(
    session: AsyncSession,
    seeded_tenant: Tenant,
) -> None:
    ids = await seed_live_agent_test_bench_async_session(
        session,
        tenant_id=seeded_tenant.tenant_id,
    )
    repository = AgentTestRepository(session)
    scope = ReactAdminScope(
        scope_type="tenant",
        tenant_id=str(seeded_tenant.tenant_id),
        label="Acme",
    )
    principal = PrincipalContext(
        principal_id="tenant",
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        auth_mode=AuthMode.LOCAL_PRINCIPAL,
        role_codes=("tenant_user", "tenant_admin"),
        permission_codes=("tenant:read", "tenant:admin"),
        trace_id="trace-test-bench-performance",
    )

    started = perf_counter()
    for _ in range(20):
        dashboard = await build_test_bench_dashboard(
            repository=repository,
            scope=scope,
            principal=principal,
        )
        detail = await build_test_run_detail(
            repository=repository,
            run_id=str(ids["failed_run_id"]),
            scope=scope,
        )
    elapsed = perf_counter() - started

    assert dashboard.suites
    assert detail.trace_steps
    assert elapsed < 1.0
