from __future__ import annotations

import time

from multi_agent_platform.api.schemas.admin_react import ReactAdminScope
from multi_agent_platform.auth.principal import (
    AuthMode,
    AuthProvider,
    PrincipalContext,
)
from multi_agent_platform.operations.workbench import (
    build_operations_workbench_envelope,
)


def test_workbench_summary_build_is_bounded() -> None:
    principal = PrincipalContext(
        principal_id="platform-admin",
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        auth_mode=AuthMode.LOCAL_PRINCIPAL,
        role_codes=("platform_admin",),
        permission_codes=("operations:read",),
        trace_id="trace-performance-workbench",
    )
    scope = ReactAdminScope(scope_type="platform", tenant_id=None, label="Platform")

    started = time.perf_counter()
    for _ in range(500):
        envelope = build_operations_workbench_envelope(
            scope=scope,
            principal=principal,
        )
    elapsed = time.perf_counter() - started

    assert envelope.logs
    filtered = build_operations_workbench_envelope(
        scope=scope,
        principal=principal,
        severity="warning",
        subsystem="gateway",
    )
    assert len(filtered.logs) == 1
    assert filtered.logs[0].subsystem == "gateway"
    assert elapsed < 1.0
