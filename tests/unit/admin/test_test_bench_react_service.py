from __future__ import annotations

import json
from datetime import datetime
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.api.routers import admin_react as admin_react_routes
from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminScope,
    ReactAdminScopeType,
)
from multi_agent_platform.api.schemas.admin_test_bench import (
    AssertionDefinition,
    GateEvidenceRefreshRequest,
)
from multi_agent_platform.api.schemas.admin_test_bench import (
    TestBenchStatus as BenchStatus,
)
from multi_agent_platform.api.schemas.admin_test_bench import (
    TestCaseSaveRequest as CaseSaveRequest,
)
from multi_agent_platform.api.schemas.admin_test_bench import (
    TestRunLaunchRequest as RunLaunchRequest,
)
from multi_agent_platform.api.schemas.admin_test_bench import (
    TestSuiteSaveRequest as SuiteSaveRequest,
)
from multi_agent_platform.api.ui.admin_console import AdminConsoleAccessError
from multi_agent_platform.auth.principal import AuthMode, AuthProvider, PrincipalContext
from multi_agent_platform.db.models.agent_tests import (
    AgentTestArtifact,
    AgentTestAssertion,
    AgentTestAssertionKind,
    AgentTestPublicationRequirement,
    AgentTestRun,
    AgentTestRunStatus,
    AgentTestSafeMode,
    AgentTestTargetType,
)
from multi_agent_platform.db.models.tenant import Tenant
from multi_agent_platform.db.repositories.agent_tests import AgentTestRepository
from multi_agent_platform.testing.agent_bench.react_test_bench import (
    _artifact_summary,
    _blocked_effects,
    _case_result_summary,
    _diagnostics,
    _expected_summary,
    _gate_evidence,
    _gate_evidence_for_requirements,
    _gate_for_run,
    _mapping_summary,
    _redaction_summary,
    _revision_int,
    _run_failure_category,
    _safe_mode,
    _safe_text,
    _timestamp_label,
    _token_usage_label,
    build_artifact_reference,
    build_case_save_result,
    build_gate_refresh_result,
    build_publish_gate_evidence,
    build_run_launch_result,
    build_suite_save_result,
    build_test_bench_audit,
    build_test_bench_dashboard,
    build_test_run_detail,
    build_test_run_list,
    build_test_suite_detail,
    build_test_suite_list,
    is_platform_admin,
)
from multi_agent_platform.testing.agent_bench.service import AgentTestBenchService
from tests.fixtures.agent_tests import seed_live_agent_test_bench_async_session


def _tenant_scope(tenant_id: UUID) -> ReactAdminScope:
    return ReactAdminScope(
        scope_type=ReactAdminScopeType.TENANT,
        tenant_id=str(tenant_id),
        label="Acme",
    )


def _platform_scope() -> ReactAdminScope:
    return ReactAdminScope(
        scope_type=ReactAdminScopeType.PLATFORM,
        label="Platform",
    )


def _principal(*, platform: bool = False) -> PrincipalContext:
    return PrincipalContext(
        principal_id="platform" if platform else "tenant-admin",
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        auth_mode=AuthMode.LOCAL_PRINCIPAL,
        role_codes=("platform_admin",) if platform else ("tenant_user", "tenant_admin"),
        permission_codes=("tenant:read", "tenant:admin"),
        trace_id="trace-test-bench",
    )


@pytest.mark.asyncio
async def test_test_bench_dashboard_empty_and_seeded_live_states(
    session: AsyncSession,
    seeded_tenant: Tenant,
) -> None:
    repository = AgentTestRepository(session)
    scope = _tenant_scope(seeded_tenant.tenant_id)
    empty = await build_test_bench_dashboard(
        repository=repository,
        scope=scope,
        principal=_principal(),
    )
    ids = await seed_live_agent_test_bench_async_session(
        session,
        tenant_id=seeded_tenant.tenant_id,
    )
    seeded = await build_test_bench_dashboard(
        repository=repository,
        scope=scope,
        principal=_principal(),
    )
    suite_detail = await build_test_suite_detail(
        repository=repository,
        suite_id=str(ids["suite_id"]),
        scope=scope,
    )

    assert empty.empty_state is not None
    assert empty.selected_suite is None
    assert seeded.title == "Test Bench"
    assert seeded.selected_suite is not None
    assert seeded.selected_suite.summary.suite_id == str(ids["suite_id"])
    assert suite_detail.summary.suite_id == str(ids["suite_id"])
    assert seeded.selected_suite.run_launcher.default_safe_mode == "mock_model"
    assert seeded.gate_alerts[0].evidence_status == "passed"
    assert seeded.provenance is not None
    serialized = json.dumps(seeded.model_dump(mode="json")).lower()
    assert "qa033-secret-value" not in serialized
    assert "raw prompt" not in serialized
    assert "raw completion" not in serialized
    assert "connector request" not in serialized
    assert "globex" not in serialized


@pytest.mark.asyncio
async def test_test_bench_lists_return_scoped_empty_live_states(
    session: AsyncSession,
    seeded_tenant: Tenant,
) -> None:
    repository = AgentTestRepository(session)
    tenant_scope = _tenant_scope(seeded_tenant.tenant_id)
    platform_scope = _platform_scope()

    dashboard = await build_test_bench_dashboard(
        repository=repository,
        scope=platform_scope,
        principal=_principal(platform=True),
    )
    suite_list = await build_test_suite_list(
        repository=repository,
        scope=platform_scope,
    )
    run_list = await build_test_run_list(
        repository=repository,
        scope=platform_scope,
    )
    gate_list = await build_publish_gate_evidence(
        repository=repository,
        scope=platform_scope,
    )
    audit = await build_test_bench_audit(
        repository=repository,
        scope=platform_scope,
    )
    tenant_gate_refresh = await build_gate_refresh_result(
        repository=repository,
        gate_id="gate-empty",
        scope=tenant_scope,
        request=GateEvidenceRefreshRequest(
            target_revision="workflow-draft-rev-empty",
            idempotency_key="empty-gate-refresh",
        ),
    )
    tenant_run_list = await build_test_run_list(
        repository=repository,
        scope=tenant_scope,
    )
    tenant_gate_list = await build_publish_gate_evidence(
        repository=repository,
        scope=tenant_scope,
    )
    tenant_audit = await build_test_bench_audit(
        repository=repository,
        scope=tenant_scope,
    )

    assert is_platform_admin(_principal(platform=True))
    assert not is_platform_admin(_principal())
    assert dashboard.empty_state is not None
    assert suite_list.empty_state is not None
    assert run_list.empty_state is not None
    assert gate_list.empty_state is not None
    assert audit.empty_state is not None
    assert tenant_run_list.empty_state is not None
    assert tenant_gate_list.empty_state is not None
    assert tenant_audit.empty_state is not None
    assert tenant_gate_refresh.status == "validation_error"


@pytest.mark.asyncio
async def test_suite_save_and_stale_conflict_results_are_safe(
    session: AsyncSession,
    seeded_tenant: Tenant,
) -> None:
    ids = await seed_live_agent_test_bench_async_session(
        session,
        tenant_id=seeded_tenant.tenant_id,
    )
    repository = AgentTestRepository(session)
    service = AgentTestBenchService(repository)
    scope = _tenant_scope(seeded_tenant.tenant_id)

    accepted = await build_suite_save_result(
        repository=repository,
        service=service,
        scope=scope,
        principal=_principal(),
        request=SuiteSaveRequest(
            name="Live daily briefing release gate",
            target_type="workflow_draft",
            target_id=str(ids["target_id"]),
            target_revision=str(ids["current_revision"]),
            default_safe_mode="mock_model",
            pass_threshold=0.95,
            revision="2",
            idempotency_key="suite-save",
        ),
    )
    stale = await build_suite_save_result(
        repository=repository,
        service=service,
        scope=scope,
        principal=_principal(),
        request=SuiteSaveRequest(
            name="Live daily briefing release gate",
            target_type="workflow_draft",
            target_id=str(ids["target_id"]),
            target_revision=str(ids["current_revision"]),
            default_safe_mode="mock_model",
            pass_threshold=0.95,
            revision="1",
            idempotency_key="suite-save-stale",
        ),
    )

    assert accepted.status == "accepted"
    assert accepted.suite is not None
    assert accepted.suite.summary.suite_revision == "3"
    assert stale.status == "stale_conflict"
    assert stale.stale_conflict is not None


@pytest.mark.asyncio
async def test_suite_case_and_run_mutations_cover_create_and_error_paths(
    session: AsyncSession,
    seeded_tenant: Tenant,
) -> None:
    repository = AgentTestRepository(session)
    service = AgentTestBenchService(repository)
    scope = _tenant_scope(seeded_tenant.tenant_id)
    target_id = f"workflow-draft-{uuid4()}"
    suite = await build_suite_save_result(
        repository=repository,
        service=service,
        scope=scope,
        principal=_principal(),
        request=SuiteSaveRequest(
            name="New live confidence suite",
            target_type="workflow_draft",
            target_id=target_id,
            target_revision="workflow-draft-rev-new",
            default_safe_mode="mock_model_tools",
            pass_threshold=0.8,
            idempotency_key="create-live-suite",
        ),
    )
    assert suite.status == "accepted"
    assert suite.suite is not None
    assert suite.suite.summary.default_safe_mode == "mock_model"

    no_case_run = await build_run_launch_result(
        repository=repository,
        service=service,
        suite_id=suite.suite.summary.suite_id,
        scope=scope,
        principal=_principal(),
        request=RunLaunchRequest(
            target_revision="workflow-draft-rev-new",
            safe_mode="mock_model",
            idempotency_key="run-without-cases",
        ),
    )
    assert no_case_run.status == "validation_error"
    assert "no active cases" in no_case_run.summary

    assertion = AssertionDefinition(
        assertion_id="assert-new-status",
        label="Status contract",
        kind="deterministic",
        path_summary="status",
        comparator="equals",
        expected_summary="passed",
        severity="blocking",
        threshold_weight=0.7,
        validation_status=BenchStatus.READY,
    )
    created_case = await build_case_save_result(
        repository=repository,
        service=service,
        suite_id=suite.suite.summary.suite_id,
        scope=scope,
        principal=_principal(),
        request=CaseSaveRequest(
            name="New live case",
            fixture_summary="Safe fixture summary",
            expected_contract_summary="Safe expected contract",
            assertions=(assertion,),
            evaluator_reference_id="evaluator-new-live-case",
            idempotency_key="create-live-case",
        ),
    )
    assert created_case.status == "accepted"
    assert created_case.case is not None
    assert created_case.case.assertions[0].expected_summary == "passed"

    updated_case = await build_case_save_result(
        repository=repository,
        service=service,
        suite_id=suite.suite.summary.suite_id,
        scope=scope,
        principal=_principal(),
        request=CaseSaveRequest(
            name="New live case",
            fixture_summary="Updated fixture summary",
            expected_contract_summary="Updated expected contract",
            assertions=(assertion,),
            evaluator_reference_id="evaluator-new-live-case",
            revision=created_case.case.case_revision,
            idempotency_key="update-live-case",
        ),
    )
    stale_case = await build_case_save_result(
        repository=repository,
        service=service,
        suite_id=suite.suite.summary.suite_id,
        scope=scope,
        principal=_principal(),
        request=CaseSaveRequest(
            name="New live case",
            fixture_summary="Stale fixture summary",
            expected_contract_summary="Stale expected contract",
            assertions=(assertion,),
            revision=created_case.case.case_revision,
            idempotency_key="stale-live-case",
        ),
    )

    assert updated_case.status == "accepted"
    assert updated_case.case is not None
    assert updated_case.case.case_revision == "2"
    assert stale_case.status == "stale_conflict"


@pytest.mark.asyncio
async def test_test_bench_router_functions_wire_live_builders(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    calls: list[tuple[str, dict[str, object]]] = []

    async def fake_shell(**_: object) -> SimpleNamespace:
        return SimpleNamespace(
            active_scope=SimpleNamespace(
                scope_type="tenant",
                tenant_id=tenant_id,
                label="Acme",
            ),
        )

    def async_return(name: str):
        async def inner(**kwargs: object) -> str:
            calls.append((name, kwargs))
            return name

        return inner

    monkeypatch.setattr(admin_react_routes, "build_react_shell", fake_shell)
    monkeypatch.setattr(
        admin_react_routes,
        "build_test_bench_dashboard",
        async_return("dashboard"),
    )
    monkeypatch.setattr(
        admin_react_routes,
        "build_test_suite_list",
        async_return("suite-list"),
    )
    monkeypatch.setattr(
        admin_react_routes,
        "build_suite_save_result",
        async_return("suite-save"),
    )
    monkeypatch.setattr(
        admin_react_routes,
        "build_test_suite_detail",
        async_return("suite-detail"),
    )
    monkeypatch.setattr(
        admin_react_routes,
        "build_case_save_result",
        async_return("case-save"),
    )
    monkeypatch.setattr(
        admin_react_routes,
        "build_run_launch_result",
        async_return("run-launch"),
    )
    monkeypatch.setattr(
        admin_react_routes,
        "build_test_run_list",
        async_return("run-list"),
    )
    monkeypatch.setattr(
        admin_react_routes,
        "build_test_run_detail",
        async_return("run-detail"),
    )
    monkeypatch.setattr(
        admin_react_routes,
        "build_publish_gate_evidence",
        async_return("gates"),
    )
    monkeypatch.setattr(
        admin_react_routes,
        "build_gate_refresh_result",
        async_return("gate-refresh"),
    )
    monkeypatch.setattr(
        admin_react_routes,
        "build_artifact_reference",
        async_return("artifact"),
    )
    monkeypatch.setattr(
        admin_react_routes,
        "build_test_bench_audit",
        async_return("audit"),
    )

    suite_payload = SuiteSaveRequest(
        name="Router suite",
        target_type="workflow_draft",
        target_id="workflow-draft-router",
        target_revision="workflow-draft-rev-router",
        default_safe_mode="mock_model",
        pass_threshold=0.9,
        idempotency_key="router-suite",
    )
    case_payload = CaseSaveRequest(
        name="Router case",
        fixture_summary="Safe fixture summary.",
        expected_contract_summary="Safe expected contract.",
        idempotency_key="router-case",
    )
    run_payload = RunLaunchRequest(
        target_revision="workflow-draft-rev-router",
        safe_mode="mock_model",
        idempotency_key="router-run",
    )
    gate_payload = GateEvidenceRefreshRequest(
        target_revision="workflow-draft-rev-router",
        idempotency_key="router-gate",
    )

    assert (
        await admin_react_routes.react_admin_test_bench_bootstrap(
            None,
            _principal(),
            object(),
            str(tenant_id),
        )
        == "dashboard"
    )
    assert (
        await admin_react_routes.react_admin_test_bench_suites(
            None,
            _principal(),
            object(),
            str(tenant_id),
        )
        == "suite-list"
    )
    assert (
        await admin_react_routes.react_admin_test_bench_suite_save(
            suite_payload,
            None,
            _principal(),
            object(),
            str(tenant_id),
        )
        == "suite-save"
    )
    assert (
        await admin_react_routes.react_admin_test_bench_suite_detail(
            "suite-id",
            None,
            _principal(),
            object(),
            str(tenant_id),
        )
        == "suite-detail"
    )
    assert (
        await admin_react_routes.react_admin_test_bench_case_save(
            "suite-id",
            case_payload,
            None,
            _principal(),
            object(),
            str(tenant_id),
        )
        == "case-save"
    )
    assert (
        await admin_react_routes.react_admin_test_bench_run_launch(
            "suite-id",
            run_payload,
            None,
            _principal(),
            object(),
            str(tenant_id),
        )
        == "run-launch"
    )
    assert (
        await admin_react_routes.react_admin_test_bench_runs(
            None,
            _principal(),
            object(),
            str(tenant_id),
        )
        == "run-list"
    )
    assert (
        await admin_react_routes.react_admin_test_bench_run_detail(
            "run-id",
            None,
            _principal(),
            object(),
            str(tenant_id),
        )
        == "run-detail"
    )
    assert (
        await admin_react_routes.react_admin_test_bench_gates(
            None,
            _principal(),
            object(),
            str(tenant_id),
        )
        == "gates"
    )
    assert (
        await admin_react_routes.react_admin_test_bench_gate_refresh(
            "gate-id",
            gate_payload,
            None,
            _principal(),
            object(),
            str(tenant_id),
        )
        == "gate-refresh"
    )
    assert (
        await admin_react_routes.react_admin_test_bench_artifact(
            "artifact-id",
            None,
            _principal(),
            object(),
            str(tenant_id),
        )
        == "artifact"
    )
    assert (
        await admin_react_routes.react_admin_test_bench_audit(
            None,
            _principal(),
            object(),
            str(tenant_id),
        )
        == "audit"
    )

    async def missing_detail(**_: object) -> str:
        raise LookupError("missing")

    monkeypatch.setattr(
        admin_react_routes,
        "build_test_suite_detail",
        missing_detail,
    )
    with pytest.raises(HTTPException) as suite_exc:
        await admin_react_routes.react_admin_test_bench_suite_detail(
            "missing-suite",
            None,
            _principal(),
            object(),
            str(tenant_id),
        )
    monkeypatch.setattr(
        admin_react_routes,
        "build_test_run_detail",
        missing_detail,
    )
    with pytest.raises(HTTPException) as run_exc:
        await admin_react_routes.react_admin_test_bench_run_detail(
            "missing-run",
            None,
            _principal(),
            object(),
            str(tenant_id),
        )
    monkeypatch.setattr(
        admin_react_routes,
        "build_artifact_reference",
        missing_detail,
    )
    with pytest.raises(HTTPException) as artifact_exc:
        await admin_react_routes.react_admin_test_bench_artifact(
            "missing-artifact",
            None,
            _principal(),
            object(),
            str(tenant_id),
        )
    monkeypatch.setattr(
        admin_react_routes,
        "build_case_save_result",
        missing_detail,
    )
    with pytest.raises(HTTPException) as case_exc:
        await admin_react_routes.react_admin_test_bench_case_save(
            "missing-suite",
            case_payload,
            None,
            _principal(),
            object(),
            str(tenant_id),
        )
    monkeypatch.setattr(
        admin_react_routes,
        "build_run_launch_result",
        missing_detail,
    )
    with pytest.raises(HTTPException) as launch_exc:
        await admin_react_routes.react_admin_test_bench_run_launch(
            "missing-suite",
            run_payload,
            None,
            _principal(),
            object(),
            str(tenant_id),
        )

    async def denied_shell(**_: object) -> SimpleNamespace:
        raise AdminConsoleAccessError("denied")

    monkeypatch.setattr(admin_react_routes, "build_react_shell", denied_shell)
    denied_calls = (
        lambda: admin_react_routes.react_admin_test_bench_suites(
            None,
            _principal(),
            object(),
            str(tenant_id),
        ),
        lambda: admin_react_routes.react_admin_test_bench_suite_save(
            suite_payload,
            None,
            _principal(),
            object(),
            str(tenant_id),
        ),
        lambda: admin_react_routes.react_admin_test_bench_case_save(
            "suite-id",
            case_payload,
            None,
            _principal(),
            object(),
            str(tenant_id),
        ),
        lambda: admin_react_routes.react_admin_test_bench_run_launch(
            "suite-id",
            run_payload,
            None,
            _principal(),
            object(),
            str(tenant_id),
        ),
        lambda: admin_react_routes.react_admin_test_bench_runs(
            None,
            _principal(),
            object(),
            str(tenant_id),
        ),
        lambda: admin_react_routes.react_admin_test_bench_gates(
            None,
            _principal(),
            object(),
            str(tenant_id),
        ),
        lambda: admin_react_routes.react_admin_test_bench_gate_refresh(
            "gate-id",
            gate_payload,
            None,
            _principal(),
            object(),
            str(tenant_id),
        ),
        lambda: admin_react_routes.react_admin_test_bench_audit(
            None,
            _principal(),
            object(),
            str(tenant_id),
        ),
    )
    for denied_call in denied_calls:
        with pytest.raises(HTTPException) as denied_exc:
            await denied_call()
        assert denied_exc.value.status_code == 403

    assert {name for name, _ in calls} == {
        "dashboard",
        "suite-list",
        "suite-save",
        "suite-detail",
        "case-save",
        "run-launch",
        "run-list",
        "run-detail",
        "gates",
        "gate-refresh",
        "artifact",
        "audit",
    }
    assert suite_exc.value.status_code == 404
    assert run_exc.value.status_code == 404
    assert artifact_exc.value.status_code == 404
    assert case_exc.value.status_code == 404
    assert launch_exc.value.status_code == 404


@pytest.mark.asyncio
async def test_run_launch_denies_real_probe_and_records_progress(
    session: AsyncSession,
    seeded_tenant: Tenant,
) -> None:
    ids = await seed_live_agent_test_bench_async_session(
        session,
        tenant_id=seeded_tenant.tenant_id,
    )
    repository = AgentTestRepository(session)
    service = AgentTestBenchService(repository)
    scope = _tenant_scope(seeded_tenant.tenant_id)

    launched = await build_run_launch_result(
        repository=repository,
        service=service,
        suite_id=str(ids["suite_id"]),
        scope=scope,
        principal=_principal(),
        request=RunLaunchRequest(
            target_revision=str(ids["current_revision"]),
            safe_mode="real_model_side_effects_disabled",
            idempotency_key="run-launch",
        ),
    )
    denied = await build_run_launch_result(
        repository=repository,
        service=service,
        suite_id=str(ids["suite_id"]),
        scope=scope,
        principal=_principal(),
        request=RunLaunchRequest(
            target_revision=str(ids["current_revision"]),
            safe_mode="approved_real_probe",
            idempotency_key="run-launch-probe",
        ),
    )

    assert launched.status == "accepted"
    assert launched.run is not None
    assert launched.run.progress.status == "passed"
    assert launched.run.blocked_side_effects
    assert denied.status == "validation_error"
    assert "No provider" in denied.diagnostics[0]


@pytest.mark.asyncio
async def test_run_detail_distinguishes_passing_failing_and_artifact_metadata(
    session: AsyncSession,
    seeded_tenant: Tenant,
) -> None:
    ids = await seed_live_agent_test_bench_async_session(
        session,
        tenant_id=seeded_tenant.tenant_id,
    )
    repository = AgentTestRepository(session)
    scope = _tenant_scope(seeded_tenant.tenant_id)
    passing = await build_test_run_detail(
        repository=repository,
        run_id=str(ids["passed_run_id"]),
        scope=scope,
    )
    failing = await build_test_run_detail(
        repository=repository,
        run_id=str(ids["failed_run_id"]),
        scope=scope,
    )

    assert passing.summary.status == "passed"
    assert passing.assertion_diagnostics[0].category == "passed"
    assert failing.summary.status == "failed"
    assert failing.assertion_diagnostics[0].category == "failed_assertion"
    assert failing.artifacts[0].authorized_href is not None
    assert "raw" not in failing.redaction_summary.lower()


@pytest.mark.asyncio
async def test_artifact_and_gate_evidence_are_metadata_only(
    session: AsyncSession,
    seeded_tenant: Tenant,
) -> None:
    ids = await seed_live_agent_test_bench_async_session(
        session,
        tenant_id=seeded_tenant.tenant_id,
    )
    repository = AgentTestRepository(session)
    scope = _tenant_scope(seeded_tenant.tenant_id)
    artifact = await build_artifact_reference(
        repository=repository,
        artifact_reference_id=str(ids["artifact_id"]),
        scope=scope,
    )
    gates = await build_publish_gate_evidence(repository=repository, scope=scope)

    assert artifact.access_status == "ready"
    assert artifact.authorized_href is not None
    assert artifact.checksum == "sha256:liveartifactsummary"
    assert gates.gates[0].evidence_status == "passed"
    serialized = json.dumps(gates.model_dump(mode="json")).lower()
    assert "storage path" not in serialized
    assert "raw transcript" not in serialized


@pytest.mark.asyncio
async def test_missing_live_records_raise_safe_lookup_errors(
    session: AsyncSession,
    seeded_tenant: Tenant,
) -> None:
    repository = AgentTestRepository(session)
    scope = _tenant_scope(seeded_tenant.tenant_id)

    with pytest.raises(LookupError, match="suite not found"):
        await build_test_suite_detail(
            repository=repository,
            suite_id=str(uuid4()),
            scope=scope,
        )
    with pytest.raises(LookupError, match="record id must be a UUID"):
        await build_test_suite_detail(
            repository=repository,
            suite_id="not-a-uuid",
            scope=scope,
        )
    with pytest.raises(LookupError, match="tenant scope"):
        await build_test_run_detail(
            repository=repository,
            run_id=str(uuid4()),
            scope=_platform_scope(),
        )
    with pytest.raises(LookupError):
        await build_test_run_detail(
            repository=repository,
            run_id=str(uuid4()),
            scope=scope,
        )
    with pytest.raises(LookupError):
        await build_artifact_reference(
            repository=repository,
            artifact_reference_id=str(uuid4()),
            scope=scope,
        )


@pytest.mark.asyncio
async def test_publish_gate_reports_missing_required_suite(
    session: AsyncSession,
    seeded_tenant: Tenant,
) -> None:
    repository = AgentTestRepository(session)
    missing_suite_id = uuid4()
    requirement = AgentTestPublicationRequirement(
        agent_test_publication_requirement_id=uuid4(),
        tenant_id=seeded_tenant.tenant_id,
        target_type=AgentTestTargetType.WORKFLOW_DRAFT,
        target_id="workflow-draft-missing-suite",
        agent_test_suite_id=missing_suite_id,
        created_by_principal_id="tenant-admin",
    )
    gates = await _gate_evidence_for_requirements(
        repository=repository,
        requirements=(requirement,),
        suites_by_id={},
        target_revision="workflow-draft-rev-missing",
    )
    missing_gate = await _gate_for_run(
        repository=repository,
        run=AgentTestRun(
            agent_test_run_id=uuid4(),
            tenant_id=seeded_tenant.tenant_id,
            agent_test_suite_id=missing_suite_id,
            target_type=AgentTestTargetType.WORKFLOW_DRAFT,
            target_id="workflow-draft-missing-suite",
            target_version="workflow-draft-rev-missing",
            safe_mode=AgentTestSafeMode.MOCK_MODEL,
            status=AgentTestRunStatus.PASSED,
            pass_status="passed",
            triggered_by_principal_id="tenant-admin",
            idempotency_key="missing-suite-run",
        ),
        suite=None,
    )

    assert gates[0].required_suite_id == "missing"
    assert gates[0].evidence_status == "missing"
    assert gates[0].target_revision == "workflow-draft-rev-missing"
    assert missing_gate.required_suite_id == "missing"


@pytest.mark.asyncio
async def test_case_result_without_matching_step_keeps_case_status(
    session: AsyncSession,
    seeded_tenant: Tenant,
) -> None:
    ids = await seed_live_agent_test_bench_async_session(
        session,
        tenant_id=seeded_tenant.tenant_id,
    )
    repository = AgentTestRepository(session)
    case = await repository.get_case_for_tenant(
        case_id=ids["case_id"],
        tenant_id=seeded_tenant.tenant_id,
    )
    assert case is not None

    summary = await _case_result_summary(
        repository=repository,
        case=case,
        steps=(),
    )

    assert summary.case_status == "ready"


def test_projection_helpers_keep_unusual_live_metadata_safe() -> None:
    tenant_id = uuid4()
    suite_id = uuid4()
    run_id = uuid4()
    now = datetime(2026, 5, 7, 16, 30)
    run = AgentTestRun(
        agent_test_run_id=run_id,
        tenant_id=tenant_id,
        agent_test_suite_id=suite_id,
        target_type=AgentTestTargetType.WORKFLOW_DRAFT,
        target_id="workflow-draft-helper",
        target_version="rev-helper",
        safe_mode=AgentTestSafeMode.MOCK_MODEL,
        status=AgentTestRunStatus.PASSED,
        pass_status="passed",
        triggered_by_principal_id="tenant-admin",
        idempotency_key="helper-run",
        created_at=now,
    )
    artifact = AgentTestArtifact(
        agent_test_artifact_id=uuid4(),
        tenant_id=tenant_id,
        agent_test_run_id=run_id,
        artifact_type="diagnostic_summary",
        checksum_sha256=None,
        size_bytes=None,
        redaction_classification="safe-summary",
        retention_state="expired",
        safe_summary={},
    )
    assertion = AgentTestAssertion(
        agent_test_assertion_id=uuid4(),
        agent_test_case_id=uuid4(),
        tenant_id=tenant_id,
        kind=AgentTestAssertionKind.DETERMINISTIC,
        path="status",
        comparator="equals",
        expected_schema={"summary": "Expected schema summary"},
        severity="blocking",
        weight=0.5,
        description="Schema expectation",
    )
    step = SimpleNamespace(
        agent_test_run_step_id=uuid4(),
        assertion_results=("not-a-mapping",),
        blocked_side_effects=("email blocked",),
    )

    assert _revision_int(None) is None
    assert _revision_int("not-int") == -1
    assert _safe_mode("side_effect_disabled_gateway") == (
        "real_model_side_effects_disabled"
    )
    assert _safe_mode("real_dependency_probe") == "approved_real_probe"
    assert _safe_text("raw prompt was removed") == "Safe summary unavailable."
    assert _mapping_summary({}, "Fallback summary") == "Fallback summary"
    assert (
        _mapping_summary(
            {"preview": {"b": 1, "a": 2}},
            "Fallback summary",
        )
        == "Safe fixture fields: a, b"
    )
    assert _mapping_summary({"preview": ["one"]}, "Fallback summary") == (
        "Safe fixture fields: ['one']"
    )
    assert _mapping_summary({"ids": ["one"]}, "Fallback summary") == (
        "Safe fields: ids"
    )
    assert _token_usage_label({"total_tokens": "not-int"}) == "0 total tokens"
    assert _token_usage_label({"total_tokens": object()}) == "0 total tokens"
    assert _redaction_summary({}) == "Sensitive transcript content is summarized."
    assert _blocked_effects((step,)) == ["email blocked"]
    assert _timestamp_label(None) == "Not recorded"
    assert _timestamp_label(now) == "2026-05-07 16:30 UTC"
    assert _expected_summary(assertion) == "Expected schema summary"
    assertion.expected_schema = {}
    assert _expected_summary(assertion) == "No explicit expected value."

    artifact_summary = _artifact_summary(artifact)
    assert artifact_summary.label == "Diagnostic Summary"
    assert artifact_summary.access_status == "artifact_unavailable"
    assert artifact_summary.checksum.startswith("sha256:")

    assert _run_failure_category(run) is None
    stale_gate = _gate_evidence(
        suite=SimpleNamespace(
            agent_test_suite_id=suite_id,
            target_type=AgentTestTargetType.WORKFLOW_DRAFT,
            target_id="workflow-draft-helper",
            target_version="rev-current",
            name="Helper suite",
        ),
        run=run,
        target_revision="rev-newer",
    )
    assert stale_gate.evidence_status == "stale"

    run.status = AgentTestRunStatus.BLOCKED
    assert _run_failure_category(run) == BenchStatus.SAFE_MODE_BLOCK
    run.status = AgentTestRunStatus.ERROR
    assert _run_failure_category(run) == BenchStatus.RUNTIME_ERROR
    run.status = AgentTestRunStatus.FAILED
    assert _run_failure_category(run) == BenchStatus.FAILED_ASSERTION
    run.status = AgentTestRunStatus.RUNNING
    assert _run_failure_category(run) is None

    diagnostics = _diagnostics((step,), run)
    assert diagnostics[0].category == "running"

    gate = _gate_evidence(
        suite=SimpleNamespace(
            agent_test_suite_id=suite_id,
            target_type=AgentTestTargetType.WORKFLOW_DRAFT,
            target_id="workflow-draft-helper",
            target_version="rev-current",
            name="Helper suite",
        ),
        run=run,
        target_revision="rev-current",
    )
    assert gate.evidence_status == "running"


@pytest.mark.asyncio
async def test_publish_gate_refresh_reads_current_and_stale_live_evidence(
    session: AsyncSession,
    seeded_tenant: Tenant,
) -> None:
    ids = await seed_live_agent_test_bench_async_session(
        session,
        tenant_id=seeded_tenant.tenant_id,
    )
    repository = AgentTestRepository(session)
    scope = _tenant_scope(seeded_tenant.tenant_id)
    current = await build_gate_refresh_result(
        repository=repository,
        gate_id=f"gate-{ids['suite_id']}",
        scope=scope,
        request=GateEvidenceRefreshRequest(
            target_revision=str(ids["current_revision"]),
            idempotency_key="gate-current",
        ),
    )
    stale = await build_gate_refresh_result(
        repository=repository,
        gate_id=f"gate-{ids['suite_id']}",
        scope=scope,
        request=GateEvidenceRefreshRequest(
            target_revision=str(ids["stale_revision"]),
            idempotency_key="gate-stale",
        ),
    )

    assert current.status == "accepted"
    assert current.gate is not None
    assert current.gate.evidence_status == "passed"
    assert stale.status == "accepted"
    assert stale.gate is not None
    assert stale.gate.evidence_status == "failed"
