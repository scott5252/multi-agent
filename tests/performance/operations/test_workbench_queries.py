from __future__ import annotations

import time

import pytest

from multi_agent_platform.api.schemas.admin_react import ReactAdminScope
from multi_agent_platform.auth.principal import (
    AuthMode,
    AuthProvider,
    PrincipalContext,
)
from multi_agent_platform.bootstrap.container import build_container
from multi_agent_platform.operations.service import OperationsConsoleService
from multi_agent_platform.operations.workbench import (
    build_operations_workbench_envelope,
    build_run_debug_envelope,
)
from tests.fixtures.operations_workbench import seed_operations_workbench_live_data


def _principal() -> PrincipalContext:
    return PrincipalContext(
        principal_id="platform-admin",
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        auth_mode=AuthMode.LOCAL_PRINCIPAL,
        role_codes=("platform_admin",),
        permission_codes=("operations:read",),
        trace_id="trace-performance-workbench",
    )


@pytest.mark.asyncio
async def test_workbench_summary_build_is_bounded(session, settings) -> None:
    tenant_id = settings.local_principal_catalog_json["tenant-admin-acme"].tenant_id
    ids = await seed_operations_workbench_live_data(session, tenant_id=tenant_id)
    scope = ReactAdminScope(scope_type="platform", tenant_id=None, label="Platform")
    container = build_container(settings)
    try:
        service = OperationsConsoleService(session=session, container=container)
        started = time.perf_counter()
        for _ in range(25):
            envelope = await build_operations_workbench_envelope(
                scope=scope,
                principal=_principal(),
                service=service,
            )
        elapsed = time.perf_counter() - started
        filtered = await build_operations_workbench_envelope(
            scope=scope,
            principal=_principal(),
            service=service,
            severity="critical",
            subsystem="gateway",
        )
        run_debug = await build_run_debug_envelope(
            scope=scope,
            principal=_principal(),
            service=service,
            workflow_run_id=ids["run_id"],
        )
    finally:
        await container.dispose()

    assert envelope.logs
    assert len(filtered.logs) == 1
    assert filtered.logs[0].subsystem == "gateway"
    assert run_debug.timeline
    assert elapsed < 1.0
