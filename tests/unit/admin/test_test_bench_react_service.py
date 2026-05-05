from __future__ import annotations

import json

from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminScope,
    ReactAdminScopeType,
)
from multi_agent_platform.api.schemas.admin_test_bench import (
    GateEvidenceRefreshRequest,
    TestRunLaunchRequest,
    TestSuiteSaveRequest,
)
from multi_agent_platform.auth.principal import AuthMode, AuthProvider, PrincipalContext
from multi_agent_platform.testing.agent_bench.react_test_bench import (
    CURRENT_TARGET_REVISION,
    build_gate_refresh_result,
    build_run_launch_result,
    build_suite_save_result,
    build_test_bench_dashboard,
    build_test_run_detail,
)


def _tenant_scope() -> ReactAdminScope:
    return ReactAdminScope(
        scope_type=ReactAdminScopeType.TENANT,
        tenant_id="11111111-1111-1111-1111-111111111111",
        label="Acme",
    )


def _principal(*, platform: bool = False) -> PrincipalContext:
    return PrincipalContext(
        principal_id="platform" if platform else "tenant",
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        auth_mode=AuthMode.LOCAL_PRINCIPAL,
        role_codes=("platform_admin",) if platform else ("tenant_user", "tenant_admin"),
        permission_codes=("tenant:read", "tenant:admin"),
        trace_id="trace-test-bench",
    )


def test_test_bench_dashboard_contains_safe_authoring_and_gate_evidence() -> None:
    dashboard = build_test_bench_dashboard(
        scope=_tenant_scope(),
        principal=_principal(),
    )

    assert dashboard.title == "Test Bench"
    assert dashboard.selected_suite is not None
    assert dashboard.selected_suite.summary.suite_name == "Daily briefing release gate"
    assert dashboard.selected_suite.run_launcher.default_safe_mode == "mock_model_tools"
    assert dashboard.gate_alerts[0].evidence_status == "stale"
    serialized = json.dumps(dashboard.model_dump(mode="json")).lower()
    assert "qa033-secret-value" not in serialized
    assert "raw prompt" not in serialized
    assert "raw completion" not in serialized
    assert "connector request" not in serialized
    assert "globex" not in serialized


def test_suite_save_and_stale_conflict_results_are_safe() -> None:
    accepted = build_suite_save_result(
        scope=_tenant_scope(),
        request=TestSuiteSaveRequest(
            name="Daily briefing release gate",
            target_type="workflow_draft",
            target_id="workflow-draft-qa033-daily-briefing",
            target_revision=CURRENT_TARGET_REVISION,
            default_safe_mode="mock_model_tools",
            pass_threshold=0.9,
            revision="suite-rev-qa033-current",
            idempotency_key="suite-save",
        ),
    )
    stale = build_suite_save_result(
        scope=_tenant_scope(),
        request=TestSuiteSaveRequest(
            name="Daily briefing release gate",
            target_type="workflow_draft",
            target_id="workflow-draft-qa033-daily-briefing",
            target_revision=CURRENT_TARGET_REVISION,
            default_safe_mode="mock_model_tools",
            pass_threshold=0.9,
            revision="stale-suite-revision",
            idempotency_key="suite-save",
        ),
    )

    assert accepted.status == "accepted"
    assert accepted.suite is not None
    assert stale.status == "stale_conflict"
    assert stale.stale_conflict is not None


def test_run_launch_denies_real_probe_and_records_progress() -> None:
    running = build_run_launch_result(
        suite_id="suite-qa033-daily-briefing",
        scope=_tenant_scope(),
        request=TestRunLaunchRequest(
            target_revision=CURRENT_TARGET_REVISION,
            safe_mode="side_effect_disabled_gateway",
            idempotency_key="run-launch",
        ),
    )
    denied = build_run_launch_result(
        suite_id="suite-qa033-daily-briefing",
        scope=_tenant_scope(),
        request=TestRunLaunchRequest(
            target_revision=CURRENT_TARGET_REVISION,
            safe_mode="real_dependency_probe",
            idempotency_key="run-launch-probe",
        ),
    )

    assert running.status == "accepted"
    assert running.run is not None
    assert running.run.progress.status == "running"
    assert running.run.blocked_side_effects
    assert denied.status == "validation_error"
    assert "No provider" in denied.diagnostics[0]


def test_run_detail_distinguishes_passing_failing_and_artifact_metadata() -> None:
    passing = build_test_run_detail(run_id="run-qa033-passing", scope=_tenant_scope())
    failing = build_test_run_detail(run_id="run-qa033-failing", scope=_tenant_scope())

    assert passing.summary.status == "passed"
    assert passing.assertion_diagnostics[0].category == "passed"
    assert failing.summary.status == "failed"
    assert failing.assertion_diagnostics[0].category == "failed_assertion"
    assert failing.artifacts[0].authorized_href is not None
    assert "raw" not in failing.redaction_summary.lower()


def test_publish_gate_refresh_rejects_stale_evidence() -> None:
    current = build_gate_refresh_result(
        request=GateEvidenceRefreshRequest(
            target_revision=CURRENT_TARGET_REVISION,
            idempotency_key="gate-current",
        )
    )
    stale = build_gate_refresh_result(
        request=GateEvidenceRefreshRequest(
            target_revision="workflow-draft-rev-qa033-stale",
            idempotency_key="gate-stale",
        )
    )

    assert current.status == "accepted"
    assert current.gate is not None
    assert current.gate.evidence_status == "passed"
    assert stale.status == "stale_conflict"
