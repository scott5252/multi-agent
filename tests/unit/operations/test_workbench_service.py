from __future__ import annotations

from multi_agent_platform.api.schemas.admin_react import ReactAdminScope
from multi_agent_platform.auth.principal import (
    AuthMode,
    AuthProvider,
    PrincipalContext,
)
from multi_agent_platform.operations.workbench import (
    build_operations_workbench_envelope,
    build_run_debug_envelope,
    build_workbench_export_snapshot,
)


def _principal() -> PrincipalContext:
    return PrincipalContext(
        principal_id="platform-admin",
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        auth_mode=AuthMode.LOCAL_PRINCIPAL,
        role_codes=("platform_admin",),
        permission_codes=("operations:read",),
        trace_id="trace-workbench-test",
    )


def test_platform_workbench_contains_likely_causes_and_refresh_hint() -> None:
    scope = ReactAdminScope(scope_type="platform", tenant_id=None, label="Platform")
    envelope = build_operations_workbench_envelope(
        scope=scope,
        principal=_principal(),
    )

    assert envelope.time_range.preset == "60m"
    assert envelope.refresh is not None
    assert envelope.refresh.interval_seconds == 30
    assert envelope.summary_cards[0].label == "Health"
    assert envelope.likely_causes[0].likely_cause_category == "retryable_timeout"
    assert "Provider health" in {card.label for card in envelope.summary_cards}


def test_tenant_workbench_hides_platform_provider_card() -> None:
    scope = ReactAdminScope(scope_type="tenant", tenant_id=None, label="Acme")
    envelope = build_operations_workbench_envelope(
        scope=scope,
        principal=_principal(),
    )

    labels = {card.label for card in envelope.summary_cards}
    assert "Tenant run health" in labels
    assert "Provider health" not in labels
    assert envelope.health_panels[0].partial_reason is not None


def test_run_debug_and_export_are_safe() -> None:
    scope = ReactAdminScope(scope_type="platform", tenant_id=None, label="Platform")
    envelope = build_operations_workbench_envelope(
        scope=scope,
        principal=_principal(),
    )
    run_debug = build_run_debug_envelope(
        scope=scope,
        workflow_run_id="00000000-0000-0000-0000-000000000029",
    )
    export = build_workbench_export_snapshot(scope=scope)

    assert run_debug.branches[0].label == "Calendar branch"
    assert run_debug.gateway_attempts[0].credential_diagnostic_category
    assert run_debug.tool_calls[0].policy_outcome == "allowed_read_only"
    assert run_debug.deliveries[0].failure_category == "mock_delivery_retry"
    assert envelope.reliability.breakers[0].label == "Model gateway breaker"
    assert envelope.reliability.confirmations[0].confirmation
    assert export.artifact_reference_id == "artifact-ref-qa029-platform"
    assert not export.artifact_reference_id.startswith("/")
