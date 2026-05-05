from __future__ import annotations

from time import perf_counter

from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminScope,
    ReactAdminScopeType,
)
from multi_agent_platform.auth.principal import AuthMode, AuthProvider, PrincipalContext
from multi_agent_platform.testing.agent_bench.react_test_bench import (
    build_test_bench_dashboard,
    build_test_run_detail,
)


def test_react_test_bench_builders_are_bounded() -> None:
    scope = ReactAdminScope(
        scope_type=ReactAdminScopeType.TENANT,
        tenant_id="11111111-1111-1111-1111-111111111111",
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
    for _ in range(100):
        dashboard = build_test_bench_dashboard(scope=scope, principal=principal)
        detail = build_test_run_detail(run_id="run-qa033-failing", scope=scope)
    elapsed = perf_counter() - started

    assert dashboard.suites
    assert detail.trace_steps
    assert elapsed < 1.0
