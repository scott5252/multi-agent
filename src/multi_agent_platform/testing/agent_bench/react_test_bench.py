from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from uuid import UUID

from multi_agent_platform.api.schemas.admin_patterns import (
    AdminAction,
    AdminActionMethod,
    AdminMutationStatus,
    RefreshHint,
    RevisionConflict,
    ToastHint,
    ValidationFieldError,
)
from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminNotificationTone,
    ReactAdminPageActionVariant,
    ReactAdminPageProvenance,
    ReactAdminScope,
)
from multi_agent_platform.api.schemas.admin_test_bench import (
    ArtifactReferenceSummary,
    AssertionDefinition,
    DiagnosticFinding,
    GateEvidenceRefreshRequest,
    PublishGateEvidence,
    PublishGateEvidenceList,
    SafeExecutionModeOption,
    TargetOption,
    TargetRevisionBinding,
    TestBenchAuditList,
    TestBenchAuditRecord,
    TestBenchDashboard,
    TestBenchFormMetadata,
    TestBenchMutationResult,
    TestBenchSection,
    TestBenchStatus,
    TestBenchSummaryMetric,
    TestCaseSaveRequest,
    TestCaseSummary,
    TestRunDetail,
    TestRunLaunchRequest,
    TestRunList,
    TestRunProgressSnapshot,
    TestRunSummary,
    TestSuiteDetail,
    TestSuiteList,
    TestSuiteSaveRequest,
    TestSuiteSummary,
    TraceStepSummary,
    empty_test_bench_state,
    live_test_bench_provenance,
    safe_test_bench_text,
)
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.db.models.agent_tests import (
    AgentTestArtifact,
    AgentTestAssertion,
    AgentTestCase,
    AgentTestPublicationRequirement,
    AgentTestRun,
    AgentTestRunStatus,
    AgentTestRunStep,
    AgentTestSafeMode,
    AgentTestStatus,
    AgentTestSuite,
)
from multi_agent_platform.db.repositories.agent_tests import (
    AgentTestRepository,
    StaleAgentTestWriteError,
)
from multi_agent_platform.testing.agent_bench.service import (
    AgentTestBenchError,
    AgentTestBenchService,
)

DEFAULT_TARGET_REVISION = "current"


def is_platform_admin(principal: PrincipalContext) -> bool:
    return "platform_admin" in principal.role_codes


async def build_test_bench_dashboard(
    *,
    repository: AgentTestRepository,
    scope: ReactAdminScope,
    principal: PrincipalContext,
) -> TestBenchDashboard:
    tenant_id = _tenant_uuid(scope)
    if tenant_id is None:
        return _empty_dashboard(
            scope=scope,
            title="Select a tenant to review test bench evidence",
            summary="The test bench workspace is tenant-scoped.",
        )

    suites = await repository.list_suites_for_tenant(tenant_id=tenant_id, limit=20)
    runs = await repository.list_runs_for_tenant(tenant_id=tenant_id, limit=20)
    requirements = await repository.list_publication_requirements_for_tenant(
        tenant_id=tenant_id,
        limit=20,
    )
    suite_by_id = {suite.agent_test_suite_id: suite for suite in suites}
    selected_suite = suites[0] if suites else None
    selected_detail = (
        await _suite_detail(repository=repository, suite=selected_suite, scope=scope)
        if selected_suite is not None
        else None
    )
    gate_alerts = await _gate_evidence_for_requirements(
        repository=repository,
        requirements=requirements,
        suites_by_id=suite_by_id,
    )
    recent_runs = [
        await _run_summary(
            repository=repository,
            run=run,
            suite=suite_by_id.get(run.agent_test_suite_id),
            scope=scope,
        )
        for run in runs[:10]
    ]
    audit_timeline = _audit_records(
        scope=scope,
        suites=suites,
        runs=runs,
        requirements=requirements,
    )
    empty_state = (
        empty_test_bench_state(
            title="No test bench records found",
            summary=(
                "Create or seed agent test suites before release confidence "
                "evidence can appear."
            ),
            setup_hint=(
                "Run the documented seed helper or create a suite through the "
                "test bench."
            ),
        )
        if not suites and not runs and not requirements
        else None
    )
    return TestBenchDashboard(
        page_id="react-test-bench",
        title="Test Bench",
        description=(
            "Guided suite authoring, safe run launch, diagnostics, artifacts, "
            "publish gates, and governance evidence."
        ),
        scope=scope,
        sections=_sections(
            suite_count=len(suites),
            run_count=len(runs),
            gate_count=len(requirements),
            audit_count=len(audit_timeline),
        ),
        summary_cards=_summary_cards(
            suites=suites,
            runs=runs,
            requirements=requirements,
        ),
        gate_alerts=tuple(gate_alerts),
        suites=tuple(
            [
                await _suite_summary(
                    repository=repository,
                    suite=suite,
                    scope=scope,
                )
                for suite in suites
            ]
        ),
        selected_suite=selected_detail,
        recent_runs=tuple(recent_runs),
        audit_timeline=audit_timeline,
        refresh=RefreshHint(mode="poll", interval_seconds=15),
        actions=(
            AdminAction(
                action_id="create-suite",
                label="Save suite",
                method=AdminActionMethod.POST,
                href="/admin/app/test-bench/suites",
                variant=ReactAdminPageActionVariant.PRIMARY,
                requires_idempotency_key=True,
            ),
        ),
        provenance=_provenance(
            suites=len(suites),
            runs=len(runs),
            gates=len(requirements),
        ),
        empty_state=empty_state,
    )


async def build_test_suite_list(
    *,
    repository: AgentTestRepository,
    scope: ReactAdminScope,
) -> TestSuiteList:
    tenant_id = _tenant_uuid(scope)
    if tenant_id is None:
        return TestSuiteList(
            scope=scope,
            suites=(),
            form_metadata=_form_metadata(),
            provenance=_provenance(),
            empty_state=empty_test_bench_state(
                title="Select a tenant",
                summary="Suites are tenant-scoped live records.",
            ),
        )
    suites = await repository.list_suites_for_tenant(tenant_id=tenant_id, limit=50)
    return TestSuiteList(
        scope=scope,
        suites=tuple(
            [
                await _suite_summary(
                    repository=repository,
                    suite=suite,
                    scope=scope,
                )
                for suite in suites
            ]
        ),
        form_metadata=_form_metadata(),
        provenance=_provenance(suites=len(suites)),
        empty_state=empty_test_bench_state(
            title="No test suites found",
            summary="No authorized live agent test suites exist for this scope.",
            setup_hint="Create a suite or run the documented seed helper.",
        )
        if not suites
        else None,
    )


async def build_test_suite_detail(
    *,
    repository: AgentTestRepository,
    suite_id: str,
    scope: ReactAdminScope,
) -> TestSuiteDetail:
    suite = await _suite_for_scope(
        repository=repository, suite_id=suite_id, scope=scope
    )
    return await _suite_detail(repository=repository, suite=suite, scope=scope)


async def build_suite_save_result(
    *,
    repository: AgentTestRepository,
    service: AgentTestBenchService,
    request: TestSuiteSaveRequest,
    scope: ReactAdminScope,
    principal: PrincipalContext,
) -> TestBenchMutationResult:
    tenant_id = _require_tenant(scope)
    suite = await repository.find_suite_for_tenant(
        tenant_id=tenant_id,
        target_type=request.target_type,
        target_id=request.target_id,
        name=request.name,
    )
    requested_revision = _revision_int(request.revision)
    try:
        if suite is None:
            suite = await service.create_suite(
                tenant_id=tenant_id,
                name=request.name,
                description=request.description,
                target_type=request.target_type,
                target_id=request.target_id,
                target_version=request.target_revision,
                default_safe_mode=_safe_mode(request.default_safe_mode),
                model_mode="mock",
                tool_mode="mock",
                pass_threshold=request.pass_threshold,
                required_for_publish=request.required_for_publish,
                actor_principal_id=principal.principal_id,
            )
        else:
            expected_revision = (
                requested_revision if requested_revision else suite.revision
            )
            suite = await service.update_suite(
                suite_id=suite.agent_test_suite_id,
                tenant_id=tenant_id,
                expected_revision=expected_revision,
                name=request.name,
                description=request.description,
                target_version=request.target_revision,
                default_safe_mode=_safe_mode(request.default_safe_mode),
                model_mode=suite.model_mode,
                tool_mode=suite.tool_mode,
                pass_threshold=request.pass_threshold,
                required_for_publish=request.required_for_publish,
            )
    except StaleAgentTestWriteError:
        current_revision = str(suite.revision if suite is not None else 0)
        return TestBenchMutationResult(
            status=AdminMutationStatus.STALE_CONFLICT,
            summary="Reload the suite before saving changes.",
            stale_conflict=RevisionConflict(
                submitted_revision=request.revision or "missing",
                current_revision=current_revision,
                message="The suite has a newer safe revision.",
                reload_href="/admin/app/test-bench",
            ),
            audit_reference_id=f"audit-test-suite-stale-{current_revision}",
        )
    detail = await _suite_detail(repository=repository, suite=suite, scope=scope)
    return TestBenchMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Test suite saved with repository-backed target revision binding.",
        revision=str(suite.revision),
        suite=detail,
        diagnostics=("Suite state was persisted through AgentTestBenchService.",),
        audit_reference_id=f"audit-test-suite-save-{suite.agent_test_suite_id}",
        toast=ToastHint(
            tone=ReactAdminNotificationTone.SUCCESS,
            title="Suite saved",
            summary="Safe suite metadata is ready for test runs.",
        ),
    )


async def build_case_save_result(
    *,
    repository: AgentTestRepository,
    service: AgentTestBenchService,
    suite_id: str,
    request: TestCaseSaveRequest,
    scope: ReactAdminScope,
    principal: PrincipalContext,
) -> TestBenchMutationResult:
    tenant_id = _require_tenant(scope)
    suite = await _suite_for_scope(
        repository=repository, suite_id=suite_id, scope=scope
    )
    cases = await repository.list_cases_for_suite(suite.agent_test_suite_id)
    existing = next((case for case in cases if case.name == request.name), None)
    requested_revision = _revision_int(request.revision)
    if (
        existing is not None
        and requested_revision
        and requested_revision != existing.revision
    ):
        return TestBenchMutationResult(
            status=AdminMutationStatus.STALE_CONFLICT,
            summary="Reload the case before saving assertions.",
            stale_conflict=RevisionConflict(
                submitted_revision=request.revision or "missing",
                current_revision=str(existing.revision),
                message="The case has a newer safe revision.",
                reload_href="/admin/app/test-bench",
            ),
            audit_reference_id=f"audit-test-case-stale-{existing.agent_test_case_id}",
        )
    if existing is None:
        case = await service.create_case(
            suite_id=suite.agent_test_suite_id,
            tenant_id=tenant_id,
            name=request.name,
            actor_principal_id=principal.principal_id,
            fixture={"summary": request.fixture_summary},
            expected_contract_shape={"summary": request.expected_contract_summary},
            assertions=[_assertion_payload(item) for item in request.assertions],
            evaluator_prompt_ref=request.evaluator_reference_id,
        )
    else:
        existing.description = request.fixture_summary
        existing.expected_contract_shape = {
            "summary": request.expected_contract_summary
        }
        existing.revision += 1
        case = existing
    case_summary = await _case_summary(repository=repository, case=case)
    return TestBenchMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Test case saved with structured assertion descriptors.",
        revision=str(case.revision),
        case=case_summary,
        diagnostics=("Raw fixture bodies and evaluator prompts were not returned.",),
        audit_reference_id=f"audit-test-case-save-{case.agent_test_case_id}",
    )


async def build_run_launch_result(
    *,
    repository: AgentTestRepository,
    service: AgentTestBenchService,
    suite_id: str,
    request: TestRunLaunchRequest,
    scope: ReactAdminScope,
    principal: PrincipalContext,
) -> TestBenchMutationResult:
    tenant_id = _require_tenant(scope)
    suite = await _suite_for_scope(
        repository=repository, suite_id=suite_id, scope=scope
    )
    safe_mode = _safe_mode(request.safe_mode)
    if safe_mode == AgentTestSafeMode.APPROVED_REAL_PROBE.value:
        return TestBenchMutationResult(
            status=AdminMutationStatus.VALIDATION_ERROR,
            summary="Real dependency probes require policy approval before execution.",
            field_errors=(
                ValidationFieldError(
                    field="safe_mode",
                    label="Safe mode",
                    message="Use mock mode or side-effect-disabled mode in QA.",
                    code="probe_requires_approval",
                ),
            ),
            diagnostics=(
                "No provider, connector, credential, or external call was made.",
            ),
            audit_reference_id=f"audit-test-run-probe-denied-{suite.agent_test_suite_id}",
        )
    try:
        run = await service.launch_run(
            suite_id=suite.agent_test_suite_id,
            tenant_id=tenant_id,
            actor_principal_id=principal.principal_id,
            safe_mode=safe_mode,
            target_version=request.target_revision,
            idempotency_key=request.idempotency_key,
            trace_id=principal.trace_id,
        )
    except AgentTestBenchError as exc:
        return TestBenchMutationResult(
            status=AdminMutationStatus.VALIDATION_ERROR,
            summary=_safe_text(str(exc)),
            field_errors=(
                ValidationFieldError(
                    field="suite_id",
                    label="Suite",
                    message=_safe_text(str(exc)),
                    code="test_bench_unavailable",
                ),
            ),
            audit_reference_id=f"audit-test-run-unavailable-{suite.agent_test_suite_id}",
        )
    detail = await _run_detail(repository=repository, run=run, suite=suite, scope=scope)
    return TestBenchMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Test run persisted with backend-owned progress evidence.",
        revision=str(run.agent_test_run_id),
        run=detail,
        diagnostics=(
            "Run is idempotent for the submitted key.",
            "Blocked side effects are summarized without raw payloads.",
        ),
        audit_reference_id=f"audit-test-run-launch-{run.agent_test_run_id}",
        toast=ToastHint(
            tone=ReactAdminNotificationTone.SUCCESS,
            title="Run persisted",
            summary="Progress refreshed from live backend run state.",
        ),
    )


async def build_test_run_list(
    *,
    repository: AgentTestRepository,
    scope: ReactAdminScope,
) -> TestRunList:
    tenant_id = _tenant_uuid(scope)
    if tenant_id is None:
        return TestRunList(
            scope=scope,
            runs=(),
            provenance=_provenance(),
            empty_state=empty_test_bench_state(
                title="Select a tenant",
                summary="Runs are tenant-scoped live records.",
            ),
        )
    runs = await repository.list_runs_for_tenant(tenant_id=tenant_id, limit=50)
    suites = {
        suite.agent_test_suite_id: suite
        for suite in await repository.list_suites_for_tenant(
            tenant_id=tenant_id, limit=50
        )
    }
    summaries = [
        await _run_summary(
            repository=repository,
            run=run,
            suite=suites.get(run.agent_test_suite_id),
            scope=scope,
        )
        for run in runs
    ]
    return TestRunList(
        scope=scope,
        runs=tuple(summaries),
        provenance=_provenance(runs=len(runs)),
        empty_state=empty_test_bench_state(
            title="No test runs found",
            summary="No authorized live test runs exist for this scope.",
        )
        if not runs
        else None,
    )


async def build_test_run_detail(
    *,
    repository: AgentTestRepository,
    run_id: str,
    scope: ReactAdminScope,
) -> TestRunDetail:
    tenant_id = _require_tenant(scope)
    run = await repository.get_run_for_tenant(
        run_id=_uuid(run_id),
        tenant_id=tenant_id,
    )
    if run is None:
        raise LookupError("agent test run not found")
    suite = await repository.get_suite_for_tenant(
        suite_id=run.agent_test_suite_id,
        tenant_id=tenant_id,
    )
    return await _run_detail(repository=repository, run=run, suite=suite, scope=scope)


async def build_artifact_reference(
    *,
    repository: AgentTestRepository,
    artifact_reference_id: str,
    scope: ReactAdminScope,
) -> ArtifactReferenceSummary:
    tenant_id = _require_tenant(scope)
    artifact = await repository.get_artifact_for_tenant(
        artifact_id=_uuid(artifact_reference_id),
        tenant_id=tenant_id,
    )
    if artifact is None:
        raise LookupError("agent test artifact not found")
    return _artifact_summary(artifact)


async def build_publish_gate_evidence(
    *,
    repository: AgentTestRepository,
    scope: ReactAdminScope,
) -> PublishGateEvidenceList:
    tenant_id = _tenant_uuid(scope)
    if tenant_id is None:
        return PublishGateEvidenceList(
            scope=scope,
            gates=(),
            provenance=_provenance(),
            empty_state=empty_test_bench_state(
                title="Select a tenant",
                summary="Publish-gate evidence is tenant-scoped.",
            ),
        )
    requirements = await repository.list_publication_requirements_for_tenant(
        tenant_id=tenant_id,
        limit=50,
    )
    suites = {
        suite.agent_test_suite_id: suite
        for suite in await repository.list_suites_for_tenant(
            tenant_id=tenant_id, limit=50
        )
    }
    gates = await _gate_evidence_for_requirements(
        repository=repository,
        requirements=requirements,
        suites_by_id=suites,
    )
    return PublishGateEvidenceList(
        scope=scope,
        gates=tuple(gates),
        provenance=_provenance(gates=len(gates)),
        empty_state=empty_test_bench_state(
            title="No publish-gate evidence found",
            summary="No current live test bench publication requirements exist.",
        )
        if not gates
        else None,
    )


async def build_gate_refresh_result(
    *,
    repository: AgentTestRepository,
    gate_id: str,
    request: GateEvidenceRefreshRequest,
    scope: ReactAdminScope,
) -> TestBenchMutationResult:
    _ = gate_id
    tenant_id = _require_tenant(scope)
    requirements = await repository.list_publication_requirements_for_tenant(
        tenant_id=tenant_id,
        limit=50,
    )
    suites = {
        suite.agent_test_suite_id: suite
        for suite in await repository.list_suites_for_tenant(
            tenant_id=tenant_id, limit=50
        )
    }
    gates = await _gate_evidence_for_requirements(
        repository=repository,
        requirements=requirements,
        suites_by_id=suites,
        target_revision=request.target_revision,
    )
    gate = gates[0] if gates else None
    if gate is None:
        return TestBenchMutationResult(
            status=AdminMutationStatus.VALIDATION_ERROR,
            summary=(
                "No repository-backed publish-gate requirement exists for this scope."
            ),
            audit_reference_id="audit-test-gate-unavailable",
        )
    return TestBenchMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Publish-gate evidence refreshed from live test bench records.",
        revision=gate.target_revision,
        gate=gate,
        diagnostics=("Evidence is derived from persisted publication requirements.",),
        audit_reference_id=gate.audit_reference_id,
    )


async def build_test_bench_audit(
    *,
    repository: AgentTestRepository,
    scope: ReactAdminScope,
) -> TestBenchAuditList:
    tenant_id = _tenant_uuid(scope)
    if tenant_id is None:
        return TestBenchAuditList(
            scope=scope,
            audit_timeline=(),
            provenance=_provenance(),
            empty_state=empty_test_bench_state(
                title="Select a tenant",
                summary="Audit evidence is tenant-scoped.",
            ),
        )
    suites = await repository.list_suites_for_tenant(tenant_id=tenant_id, limit=20)
    runs = await repository.list_runs_for_tenant(tenant_id=tenant_id, limit=20)
    requirements = await repository.list_publication_requirements_for_tenant(
        tenant_id=tenant_id,
        limit=20,
    )
    audit = _audit_records(
        scope=scope,
        suites=suites,
        runs=runs,
        requirements=requirements,
    )
    return TestBenchAuditList(
        scope=scope,
        audit_timeline=audit,
        provenance=_provenance(
            suites=len(suites),
            runs=len(runs),
            gates=len(requirements),
        ),
        empty_state=empty_test_bench_state(
            title="No test bench audit records found",
            summary="No live suite, run, or gate events exist for this scope.",
        )
        if not audit
        else None,
    )


def _empty_dashboard(
    *,
    scope: ReactAdminScope,
    title: str,
    summary: str,
) -> TestBenchDashboard:
    empty = empty_test_bench_state(title=title, summary=summary)
    return TestBenchDashboard(
        page_id="react-test-bench",
        title="Test Bench",
        description=(
            "Guided suite authoring, safe run launch, diagnostics, artifacts, "
            "publish gates, and governance evidence."
        ),
        scope=scope,
        sections=_sections(suite_count=0, run_count=0, gate_count=0, audit_count=0),
        summary_cards=_summary_cards(suites=(), runs=(), requirements=()),
        gate_alerts=(),
        suites=(),
        selected_suite=None,
        recent_runs=(),
        audit_timeline=(),
        refresh=RefreshHint(mode="manual"),
        actions=(),
        provenance=_provenance(),
        empty_state=empty,
    )


def _sections(
    *,
    suite_count: int,
    run_count: int,
    gate_count: int,
    audit_count: int,
) -> tuple[TestBenchSection, ...]:
    return (
        TestBenchSection(
            section_id="suites",
            label="Suites",
            status=TestBenchStatus.READY
            if suite_count
            else TestBenchStatus.UNAVAILABLE,
            summary=f"{suite_count} live suite records.",
        ),
        TestBenchSection(
            section_id="runs",
            label="Runs",
            status=TestBenchStatus.RUNNING
            if run_count and gate_count
            else TestBenchStatus.UNAVAILABLE,
            summary=f"{run_count} live run records.",
        ),
        TestBenchSection(
            section_id="diagnostics",
            label="Diagnostics",
            status=TestBenchStatus.READY if run_count else TestBenchStatus.UNAVAILABLE,
            summary="Diagnostics are projected from persisted run steps.",
        ),
        TestBenchSection(
            section_id="gates",
            label="Publish gates",
            status=TestBenchStatus.READY if gate_count else TestBenchStatus.MISSING,
            summary=f"{gate_count} live publication requirements.",
        ),
        TestBenchSection(
            section_id="audit",
            label="Audit",
            status=TestBenchStatus.READY
            if audit_count
            else TestBenchStatus.AUDIT_UNAVAILABLE,
            summary=f"{audit_count} safe audit-style timeline entries.",
        ),
    )


def _summary_cards(
    *,
    suites: Sequence[AgentTestSuite],
    runs: Sequence[AgentTestRun],
    requirements: Sequence[AgentTestPublicationRequirement],
) -> tuple[TestBenchSummaryMetric, ...]:
    failing = sum(
        1
        for run in runs
        if run.status in {AgentTestRunStatus.FAILED, AgentTestRunStatus.ERROR}
    )
    running = sum(1 for run in runs if run.status is AgentTestRunStatus.RUNNING)
    return (
        TestBenchSummaryMetric(
            metric_id="suite-count",
            label="Suites",
            value=str(len(suites)),
            status=TestBenchStatus.READY if suites else TestBenchStatus.UNAVAILABLE,
            summary="Reusable suites are read from persisted tenant records.",
        ),
        TestBenchSummaryMetric(
            metric_id="running-runs",
            label="Running",
            value=str(running),
            status=TestBenchStatus.RUNNING if running else TestBenchStatus.READY,
            summary="Progress is read from backend run snapshots.",
        ),
        TestBenchSummaryMetric(
            metric_id="failing-runs",
            label="Needs review",
            value=str(failing),
            status=TestBenchStatus.FAILED if failing else TestBenchStatus.READY,
            summary="Failure diagnostics are summarized safely.",
        ),
        TestBenchSummaryMetric(
            metric_id="publish-requirements",
            label="Required gates",
            value=str(len(requirements)),
            status=TestBenchStatus.READY if requirements else TestBenchStatus.MISSING,
            summary="Publish requirements are repository-backed.",
        ),
    )


async def _suite_summary(
    *,
    repository: AgentTestRepository,
    suite: AgentTestSuite,
    scope: ReactAdminScope,
) -> TestSuiteSummary:
    cases = await repository.list_cases_for_suite(suite.agent_test_suite_id)
    latest_run = await repository.latest_run_for_suite(
        suite_id=suite.agent_test_suite_id,
        tenant_id=suite.tenant_id,
    )
    gate_status = (
        TestBenchStatus.PASSED
        if latest_run and latest_run.status is AgentTestRunStatus.PASSED
        else TestBenchStatus.MISSING
    )
    return TestSuiteSummary(
        suite_id=str(suite.agent_test_suite_id),
        suite_slug=_slug(suite.name),
        suite_name=_safe_text(suite.name),
        tenant_id=str(suite.tenant_id),
        tenant_label=_safe_text(scope.label),
        target_type=suite.target_type.value,
        target_label=_target_label(suite),
        target_revision=suite.target_version or DEFAULT_TARGET_REVISION,
        target_status=TestBenchStatus.READY,
        default_safe_mode=suite.default_safe_mode.value,
        pass_threshold=suite.pass_threshold,
        required_for_publish=suite.is_required_for_publish,
        case_count=len(cases),
        latest_run_status=_run_status(latest_run.status)
        if latest_run
        else TestBenchStatus.MISSING,
        latest_run_id=str(latest_run.agent_test_run_id) if latest_run else None,
        publish_gate_status=gate_status,
        suite_revision=str(suite.revision),
        archive_status=_suite_status(suite.status),
        audit_reference_id=f"audit-suite-{suite.agent_test_suite_id}",
        authorized_actions=(
            AdminAction(
                action_id="open-suite",
                label="Open suite",
                method=AdminActionMethod.GET,
                href=f"/admin/app/test-bench/suites/{suite.agent_test_suite_id}",
            ),
            AdminAction(
                action_id="launch-run",
                label="Launch run",
                method=AdminActionMethod.POST,
                href=f"/admin/app/test-bench/suites/{suite.agent_test_suite_id}/runs",
                variant=ReactAdminPageActionVariant.PRIMARY,
                requires_idempotency_key=True,
            ),
        ),
    )


async def _suite_detail(
    *,
    repository: AgentTestRepository,
    suite: AgentTestSuite,
    scope: ReactAdminScope,
) -> TestSuiteDetail:
    cases = await repository.list_cases_for_suite(suite.agent_test_suite_id)
    runs = await repository.list_runs_for_suite(
        suite_id=suite.agent_test_suite_id,
        tenant_id=suite.tenant_id,
        limit=10,
    )
    case_summaries = tuple(
        [await _case_summary(repository=repository, case=case) for case in cases]
    )
    run_summaries = tuple(
        [
            await _run_summary(
                repository=repository,
                run=run,
                suite=suite,
                scope=scope,
            )
            for run in runs
        ]
    )
    target = _target_binding(suite)
    publish_gate = await _gate_for_suite(repository=repository, suite=suite)
    return TestSuiteDetail(
        summary=await _suite_summary(repository=repository, suite=suite, scope=scope),
        cases=case_summaries,
        target_binding=target,
        run_launcher=_form_metadata(
            target_options=(
                TargetOption(
                    target_type=suite.target_type.value,
                    target_id=suite.target_id,
                    label=_target_label(suite),
                    current_revision=suite.target_version or DEFAULT_TARGET_REVISION,
                    revision_status=TestBenchStatus.READY,
                    safe_summary="Authorized target metadata is repository-backed.",
                ),
            ),
            assertion_templates=case_summaries[0].assertions if case_summaries else (),
            default_safe_mode=suite.default_safe_mode.value,
        ),
        recent_runs=run_summaries,
        publish_gate=publish_gate,
        audit_reference_id=f"audit-suite-detail-{suite.agent_test_suite_id}",
    )


async def _case_summary(
    *,
    repository: AgentTestRepository,
    case: AgentTestCase,
) -> TestCaseSummary:
    assertions = await repository.list_assertions_for_case(case.agent_test_case_id)
    return TestCaseSummary(
        case_id=str(case.agent_test_case_id),
        case_name=_safe_text(case.name),
        case_status=_suite_status(case.status),
        case_revision=str(case.revision),
        fixture_summary=_mapping_summary(
            case.fixture_summary, "Fixture summary unavailable."
        ),
        expected_contract_summary=_mapping_summary(
            case.expected_contract_shape,
            "Expected contract summary unavailable.",
        ),
        assertions=tuple(_assertion(assertion) for assertion in assertions),
        evaluator_summary=_safe_text(
            case.evaluator_prompt_ref or "No evaluator prompt reference."
        ),
        threshold_contribution=case.pass_threshold,
        order=case.case_order,
        audit_reference_id=f"audit-case-{case.agent_test_case_id}",
        authorized_actions=(
            AdminAction(
                action_id="edit-case",
                label="Save case",
                method=AdminActionMethod.POST,
                href=f"/admin/app/test-bench/suites/{case.agent_test_suite_id}/cases",
                requires_idempotency_key=True,
            ),
        ),
    )


def _assertion(assertion: AgentTestAssertion) -> AssertionDefinition:
    return AssertionDefinition(
        assertion_id=str(assertion.agent_test_assertion_id),
        label=_safe_text(assertion.description or assertion.kind.value.title()),
        kind=assertion.kind.value,
        path_summary=_safe_text(assertion.path or "whole output"),
        comparator=_safe_text(assertion.comparator or "equals"),
        expected_summary=_expected_summary(assertion),
        severity=_safe_text(assertion.severity),
        threshold_weight=assertion.weight,
        validation_status=TestBenchStatus.READY,
    )


async def _run_summary(
    *,
    repository: AgentTestRepository,
    run: AgentTestRun,
    suite: AgentTestSuite | None,
    scope: ReactAdminScope,
) -> TestRunSummary:
    steps = await repository.list_run_steps(run.agent_test_run_id)
    case_total = len(steps)
    case_passed = sum(1 for step in steps if step.status is AgentTestRunStatus.PASSED)
    case_failed = sum(
        1
        for step in steps
        if step.status
        in {
            AgentTestRunStatus.FAILED,
            AgentTestRunStatus.ERROR,
            AgentTestRunStatus.BLOCKED,
        }
    )
    return TestRunSummary(
        run_id=str(run.agent_test_run_id),
        suite_id=str(run.agent_test_suite_id),
        suite_name=_safe_text(suite.name if suite is not None else "Unavailable suite"),
        target_revision=run.target_version or DEFAULT_TARGET_REVISION,
        safe_mode=run.safe_mode.value,
        status=_run_status(run.status),
        pass_rate=case_passed / case_total
        if case_total
        else (1.0 if run.status is AgentTestRunStatus.PASSED else 0.0),
        failure_category=_run_failure_category(run),
        started_label=_timestamp_label(run.started_at or run.created_at),
        finished_label=_timestamp_label(run.completed_at) if run.completed_at else None,
        actor_label=_safe_text(run.triggered_by_principal_id),
        case_total=case_total,
        case_passed=case_passed,
        case_failed=case_failed,
        usage_summary=_usage_summary(run.usage_summary),
        latency_summary=f"{run.latency_ms} ms total",
        audit_reference_id=f"audit-run-{run.agent_test_run_id}",
        authorized_actions=(
            AdminAction(
                action_id="open-run",
                label="Open run",
                method=AdminActionMethod.GET,
                href=f"/admin/app/test-bench/runs/{run.agent_test_run_id}.json",
            ),
        ),
    )


async def _run_detail(
    *,
    repository: AgentTestRepository,
    run: AgentTestRun,
    suite: AgentTestSuite | None,
    scope: ReactAdminScope,
) -> TestRunDetail:
    steps = await repository.list_run_steps(run.agent_test_run_id)
    cases = (
        await repository.list_cases_for_suite(run.agent_test_suite_id)
        if suite is not None
        else []
    )
    artifacts = await repository.list_artifacts_for_run(
        run_id=run.agent_test_run_id,
        tenant_id=run.tenant_id,
        limit=10,
    )
    summary = await _run_summary(
        repository=repository,
        run=run,
        suite=suite,
        scope=scope,
    )
    completed_cases = sum(
        1 for step in steps if step.status is not AgentTestRunStatus.RUNNING
    )
    return TestRunDetail(
        summary=summary,
        progress=TestRunProgressSnapshot(
            status=_run_status(run.status),
            summary="Backend run state reports the current persisted status.",
            completed_cases=completed_cases,
            total_cases=len(steps) or len(cases),
            next_poll_seconds=10 if run.status is AgentTestRunStatus.RUNNING else 0,
            audit_reference_id=f"audit-progress-{run.agent_test_run_id}",
        ),
        case_results=tuple(
            [
                await _case_result_summary(
                    repository=repository,
                    case=case,
                    steps=steps,
                )
                for case in cases
            ]
        ),
        trace_steps=tuple(_trace_step(step) for step in steps),
        assertion_diagnostics=tuple(_diagnostics(steps, run)),
        artifacts=tuple(_artifact_summary(artifact) for artifact in artifacts),
        publish_gate=await _gate_for_run(repository=repository, run=run, suite=suite),
        redaction_summary=_redaction_summary(run.redaction_summary),
        blocked_side_effects=tuple(_blocked_effects(steps)),
        audit_reference_id=f"audit-detail-{run.agent_test_run_id}",
    )


async def _case_result_summary(
    *,
    repository: AgentTestRepository,
    case: AgentTestCase,
    steps: Sequence[AgentTestRunStep],
) -> TestCaseSummary:
    summary = await _case_summary(repository=repository, case=case)
    matching = [
        step for step in steps if step.agent_test_case_id == case.agent_test_case_id
    ]
    if matching:
        return summary.model_copy(
            update={"case_status": _run_status(matching[0].status)}
        )
    return summary


def _trace_step(step: AgentTestRunStep) -> TraceStepSummary:
    token_usage = step.token_usage or {}
    artifact_refs = step.artifact_refs or []
    return TraceStepSummary(
        step_id=str(step.agent_test_run_step_id),
        case_id=str(step.agent_test_case_id or "run-level"),
        step_label=_safe_text(step.step_name),
        runtime_role="agent test case",
        status=_run_status(step.status),
        latency_ms=int(step.latency_ms or 0),
        token_usage=_safe_text(_token_usage_label(token_usage)),
        model_label=_safe_text(step.model_id or "No live provider"),
        provider_label=_safe_text(step.model_provider or "mock"),
        prompt_version_label=_safe_text(step.prompt_version_id or "No prompt version"),
        profile_version_label=_safe_text(
            step.profile_version_id or "No profile version"
        ),
        skill_version_labels=tuple(
            _safe_text(str(item)) for item in (step.skill_version_refs or [])
        ),
        safe_transcript_excerpt=_mapping_summary(
            step.redacted_transcript or {},
            "Redacted transcript summary unavailable.",
        ),
        blocked_side_effects=tuple(_blocked_effects((step,))),
        gateway_decision="blocked_side_effect"
        if step.blocked_side_effects
        else "safe_mode",
        redaction_class="safe-summary",
        artifact_reference_ids=tuple(_safe_text(str(item)) for item in artifact_refs),
    )


def _diagnostics(
    steps: Sequence[AgentTestRunStep],
    run: AgentTestRun,
) -> tuple[DiagnosticFinding, ...]:
    findings: list[DiagnosticFinding] = []
    for step in steps:
        results = step.assertion_results or []
        for index, item in enumerate(results):
            if not isinstance(item, Mapping):
                continue
            passed = bool(item.get("passed"))
            findings.append(
                DiagnosticFinding(
                    finding_id=f"finding-{step.agent_test_run_step_id}-{index}",
                    category=TestBenchStatus.PASSED
                    if passed
                    else TestBenchStatus.FAILED_ASSERTION,
                    label=_safe_text(
                        str(item.get("safe_message") or "Assertion result")
                    ),
                    expected_summary=_safe_text(
                        str(item.get("expected") or "Expected value summarized.")
                    ),
                    actual_summary=_safe_text(
                        str(item.get("actual") or "Actual value summarized.")
                    ),
                    comparator=_safe_text(str(item.get("comparator") or "comparison")),
                    path_summary=_safe_text(str(item.get("path") or "output")),
                    severity=_safe_text(str(item.get("severity") or "blocking")),
                    remediation="Review case expectations and rerun the suite."
                    if not passed
                    else "No action needed.",
                )
            )
    if findings:
        return tuple(findings[:10])
    return (
        DiagnosticFinding(
            finding_id=f"finding-{run.agent_test_run_id}",
            category=_run_status(run.status),
            label=_safe_text(run.failure_summary or "Run status summary"),
            expected_summary="Persisted run evidence is available.",
            actual_summary=_safe_text(run.pass_status),
            comparator="status",
            path_summary="run.pass_status",
            severity="info" if run.status is AgentTestRunStatus.PASSED else "warning",
            remediation="No action needed."
            if run.status is AgentTestRunStatus.PASSED
            else "Review persisted run steps.",
        ),
    )


def _artifact_summary(artifact: AgentTestArtifact) -> ArtifactReferenceSummary:
    checksum = (
        artifact.checksum_sha256 or f"sha256:{artifact.agent_test_artifact_id.hex[:16]}"
    )
    return ArtifactReferenceSummary(
        artifact_reference_id=str(artifact.agent_test_artifact_id),
        label=_safe_text(_artifact_label(artifact)),
        content_class=_safe_text(artifact.artifact_type),
        checksum=_safe_text(checksum),
        size_label=f"{artifact.size_bytes or 0} bytes",
        retention_state=TestBenchStatus.READY
        if artifact.retention_state in {"retained", "ready"}
        else TestBenchStatus.ARTIFACT_UNAVAILABLE,
        redaction_class=_safe_text(artifact.redaction_classification),
        access_status=TestBenchStatus.READY
        if artifact.retention_state in {"retained", "ready"}
        else TestBenchStatus.ARTIFACT_UNAVAILABLE,
        safe_summary=_mapping_summary(
            artifact.safe_summary,
            "Artifact metadata is available by governed reference only.",
        ),
        authorized_href=f"/admin/app/test-bench/artifacts/{artifact.agent_test_artifact_id}.json",
        audit_reference_id=f"audit-artifact-{artifact.agent_test_artifact_id}",
    )


async def _gate_for_suite(
    *,
    repository: AgentTestRepository,
    suite: AgentTestSuite,
) -> PublishGateEvidence:
    run = await repository.latest_run_for_suite(
        suite_id=suite.agent_test_suite_id,
        tenant_id=suite.tenant_id,
        target_type=suite.target_type.value,
        target_id=suite.target_id,
        target_version=suite.target_version,
        match_target_version=suite.target_version is not None,
    )
    return _gate_evidence(suite=suite, run=run, target_revision=suite.target_version)


async def _gate_for_run(
    *,
    repository: AgentTestRepository,
    run: AgentTestRun,
    suite: AgentTestSuite | None,
) -> PublishGateEvidence:
    if suite is None:
        suite = await repository.get_suite_for_tenant(
            suite_id=run.agent_test_suite_id,
            tenant_id=run.tenant_id,
        )
    if suite is None:
        return _missing_gate(
            target_type=run.target_type.value,
            target_id=run.target_id,
            target_revision=run.target_version,
        )
    return _gate_evidence(suite=suite, run=run, target_revision=run.target_version)


async def _gate_evidence_for_requirements(
    *,
    repository: AgentTestRepository,
    requirements: Sequence[AgentTestPublicationRequirement],
    suites_by_id: Mapping[UUID, AgentTestSuite],
    target_revision: str | None = None,
) -> list[PublishGateEvidence]:
    gates: list[PublishGateEvidence] = []
    for requirement in requirements:
        suite = suites_by_id.get(requirement.agent_test_suite_id)
        if suite is None:
            gates.append(
                _missing_gate(
                    target_type=requirement.target_type.value,
                    target_id=requirement.target_id,
                    target_revision=target_revision,
                )
            )
            continue
        run = await repository.latest_run_for_suite(
            suite_id=suite.agent_test_suite_id,
            tenant_id=suite.tenant_id,
            target_type=requirement.target_type.value,
            target_id=requirement.target_id,
            target_version=target_revision or suite.target_version,
            match_target_version=bool(target_revision or suite.target_version),
        )
        gates.append(
            _gate_evidence(
                suite=suite,
                run=run,
                target_revision=target_revision or suite.target_version,
            )
        )
    return gates


def _gate_evidence(
    *,
    suite: AgentTestSuite,
    run: AgentTestRun | None,
    target_revision: str | None,
) -> PublishGateEvidence:
    evidence_status = TestBenchStatus.MISSING
    if run is not None:
        evidence_status = _run_status(run.status)
        if (
            run.status is AgentTestRunStatus.PASSED
            and target_revision
            and run.target_version != target_revision
        ):
            evidence_status = TestBenchStatus.STALE
    return PublishGateEvidence(
        gate_id=f"gate-{suite.agent_test_suite_id}",
        target_type=suite.target_type.value,
        target_label=_target_label(suite),
        target_revision=target_revision
        or suite.target_version
        or DEFAULT_TARGET_REVISION,
        required_suite_id=str(suite.agent_test_suite_id),
        required_suite_label=_safe_text(suite.name),
        evidence_status=evidence_status,
        latest_run_id=str(run.agent_test_run_id) if run else None,
        latest_run_revision=run.target_version if run else None,
        latest_run_status=_run_status(run.status) if run else None,
        reason=_gate_reason(evidence_status),
        remediation=_gate_remediation(evidence_status),
        audit_reference_id=f"audit-gate-{suite.agent_test_suite_id}",
        artifact_references=(),
        authorized_actions=(
            AdminAction(
                action_id="run-suite",
                label="Run suite",
                method=AdminActionMethod.POST,
                href=f"/admin/app/test-bench/suites/{suite.agent_test_suite_id}/runs",
                variant=ReactAdminPageActionVariant.PRIMARY,
                requires_idempotency_key=True,
            ),
        ),
    )


def _missing_gate(
    *,
    target_type: str,
    target_id: str,
    target_revision: str | None,
) -> PublishGateEvidence:
    return PublishGateEvidence(
        gate_id=f"gate-missing-{_slug(target_id)}",
        target_type=_safe_text(target_type),
        target_label=_safe_text(target_id),
        target_revision=_safe_text(target_revision or DEFAULT_TARGET_REVISION),
        required_suite_id="missing",
        required_suite_label="Missing required suite",
        evidence_status=TestBenchStatus.MISSING,
        reason="No live suite evidence exists for this publication requirement.",
        remediation=(
            "Create or restore the required suite and run it for the current revision."
        ),
        audit_reference_id=f"audit-gate-missing-{_slug(target_id)}",
    )


def _target_binding(suite: AgentTestSuite) -> TargetRevisionBinding:
    revision = suite.target_version or DEFAULT_TARGET_REVISION
    return TargetRevisionBinding(
        target_type=suite.target_type.value,
        target_id=suite.target_id,
        target_label=_target_label(suite),
        current_revision=revision,
        selected_revision=revision,
        revision_status=TestBenchStatus.READY,
        source_links=(),
        remediation="Run the required suite after any target revision changes.",
    )


def _form_metadata(
    *,
    target_options: tuple[TargetOption, ...] = (),
    assertion_templates: tuple[AssertionDefinition, ...] = (),
    default_safe_mode: str = AgentTestSafeMode.MOCK_MODEL.value,
) -> TestBenchFormMetadata:
    return TestBenchFormMetadata(
        target_options=target_options,
        safe_modes=_safe_modes(),
        assertion_templates=assertion_templates,
        run_reason_options=(
            "Release confidence",
            "Regression check",
            "Publish gate recovery",
        ),
        default_safe_mode=default_safe_mode,
        default_pass_threshold=0.9,
    )


def _safe_modes() -> tuple[SafeExecutionModeOption, ...]:
    return (
        SafeExecutionModeOption(
            mode_id=AgentTestSafeMode.MOCK_MODEL.value,
            label="Mock model",
            side_effect_posture="No external side effects",
            model_behavior="Deterministic mocked model response",
            tool_behavior="No real tool calls",
            credential_behavior="No credential resolution",
            allowed_status=TestBenchStatus.READY,
            policy_reason="Default local and CI validation mode.",
            audit_reference_id="audit-safe-mode-mock-model",
        ),
        SafeExecutionModeOption(
            mode_id=AgentTestSafeMode.REAL_MODEL_SIDE_EFFECTS_DISABLED.value,
            label="Side-effect-disabled gateway",
            side_effect_posture="Provider and connector side effects blocked",
            model_behavior="Gateway metadata is summarized",
            tool_behavior="Skill gateway records blocked side effects",
            credential_behavior="Credential references remain unresolved in browser",
            allowed_status=TestBenchStatus.WARNING,
            policy_reason="Explicit mode for gateway policy evidence.",
            audit_reference_id="audit-safe-mode-side-effect-disabled",
        ),
        SafeExecutionModeOption(
            mode_id=AgentTestSafeMode.APPROVED_REAL_PROBE.value,
            label="Approved real dependency probe",
            side_effect_posture="External dependencies require approval",
            model_behavior="Unavailable in local QA",
            tool_behavior="Unavailable without approval evidence",
            credential_behavior="Requires durable approval reference",
            allowed_status=TestBenchStatus.BLOCKED,
            policy_reason="Policy approval is required before execution.",
            requires_approval=True,
            approval_reference_id="approval-required",
            audit_reference_id="audit-safe-mode-approved-probe",
        ),
    )


def _audit_records(
    *,
    scope: ReactAdminScope,
    suites: Sequence[AgentTestSuite],
    runs: Sequence[AgentTestRun],
    requirements: Sequence[AgentTestPublicationRequirement],
) -> tuple[TestBenchAuditRecord, ...]:
    records: list[TestBenchAuditRecord] = []
    for suite in suites[:5]:
        records.append(
            TestBenchAuditRecord(
                record_id=f"audit-record-suite-{suite.agent_test_suite_id}",
                domain="suite",
                tenant_scope_label=_safe_text(scope.label),
                actor_label=_safe_text(suite.created_by_principal_id),
                target_label=_target_label(suite),
                timestamp_label=_timestamp_label(suite.updated_at),
                action="suite_persisted",
                outcome=_suite_status(suite.status),
                safe_diff_summary=(
                    "Suite metadata is persisted in the agent test repository."
                ),
                redaction_class="safe-summary",
                audit_reference_id=f"audit-test-suite-{suite.agent_test_suite_id}",
            )
        )
    for run in runs[:5]:
        records.append(
            TestBenchAuditRecord(
                record_id=f"audit-record-run-{run.agent_test_run_id}",
                domain="run",
                tenant_scope_label=_safe_text(scope.label),
                actor_label=_safe_text(run.triggered_by_principal_id),
                target_label=_safe_text(run.target_id),
                timestamp_label=_timestamp_label(run.created_at),
                action="run_persisted",
                outcome=_run_status(run.status),
                safe_diff_summary=(
                    "Run progress and result evidence are repository-backed."
                ),
                redaction_class="safe-summary",
                audit_reference_id=f"audit-test-run-{run.agent_test_run_id}",
            )
        )
    for requirement in requirements[:5]:
        records.append(
            TestBenchAuditRecord(
                record_id=f"audit-record-gate-{requirement.agent_test_publication_requirement_id}",
                domain="publish_gate",
                tenant_scope_label=_safe_text(scope.label),
                actor_label=_safe_text(requirement.created_by_principal_id),
                target_label=_safe_text(requirement.target_id),
                timestamp_label=_timestamp_label(requirement.updated_at),
                action="publication_requirement_persisted",
                outcome=TestBenchStatus.READY,
                safe_diff_summary=(
                    "Required suite evidence is evaluated from live test bench records."
                ),
                redaction_class="safe-summary",
                audit_reference_id=f"audit-test-gate-{requirement.agent_test_publication_requirement_id}",
            )
        )
    return tuple(records[:12])


async def _suite_for_scope(
    *,
    repository: AgentTestRepository,
    suite_id: str,
    scope: ReactAdminScope,
) -> AgentTestSuite:
    suite = await repository.get_suite_for_tenant(
        suite_id=_uuid(suite_id),
        tenant_id=_require_tenant(scope),
    )
    if suite is None:
        raise LookupError("agent test suite not found")
    return suite


def _tenant_uuid(scope: ReactAdminScope) -> UUID | None:
    if scope.tenant_id is None:
        return None
    return UUID(str(scope.tenant_id))


def _require_tenant(scope: ReactAdminScope) -> UUID:
    tenant_id = _tenant_uuid(scope)
    if tenant_id is None:
        raise LookupError("test bench tenant scope required")
    return tenant_id


def _uuid(value: str) -> UUID:
    try:
        return UUID(str(value))
    except ValueError as exc:
        raise LookupError("live test bench record id must be a UUID") from exc


def _revision_int(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return -1


def _safe_mode(value: str) -> str:
    aliases = {
        "mock_model_tools": AgentTestSafeMode.MOCK_MODEL.value,
        "side_effect_disabled_gateway": (
            AgentTestSafeMode.REAL_MODEL_SIDE_EFFECTS_DISABLED.value
        ),
        "real_dependency_probe": AgentTestSafeMode.APPROVED_REAL_PROBE.value,
    }
    return aliases.get(value, value)


def _suite_status(status: object) -> TestBenchStatus:
    normalized = _value(status)
    return {
        AgentTestStatus.ACTIVE.value: TestBenchStatus.READY,
        AgentTestStatus.DRAFT.value: TestBenchStatus.WARNING,
        AgentTestStatus.ARCHIVED.value: TestBenchStatus.BLOCKED,
    }.get(normalized, TestBenchStatus.UNAVAILABLE)


def _run_status(status: object) -> TestBenchStatus:
    normalized = _value(status)
    return {
        AgentTestRunStatus.QUEUED.value: TestBenchStatus.QUEUED,
        AgentTestRunStatus.RUNNING.value: TestBenchStatus.RUNNING,
        AgentTestRunStatus.PASSED.value: TestBenchStatus.PASSED,
        AgentTestRunStatus.FAILED.value: TestBenchStatus.FAILED,
        AgentTestRunStatus.BLOCKED.value: TestBenchStatus.BLOCKED,
        AgentTestRunStatus.ERROR.value: TestBenchStatus.RUNTIME_ERROR,
    }.get(normalized, TestBenchStatus.UNAVAILABLE)


def _run_failure_category(run: AgentTestRun) -> TestBenchStatus | None:
    if run.status is AgentTestRunStatus.PASSED:
        return None
    if run.status is AgentTestRunStatus.BLOCKED:
        return TestBenchStatus.SAFE_MODE_BLOCK
    if run.status is AgentTestRunStatus.ERROR:
        return TestBenchStatus.RUNTIME_ERROR
    if run.status is AgentTestRunStatus.FAILED:
        return TestBenchStatus.FAILED_ASSERTION
    return None


def _gate_reason(status: TestBenchStatus) -> str:
    return {
        TestBenchStatus.MISSING: "No passing run exists for this target revision.",
        TestBenchStatus.STALE: "Latest run is tied to an older target revision.",
        TestBenchStatus.RUNNING: "Required suite is still running.",
        TestBenchStatus.FAILED: "Latest current run did not meet the pass threshold.",
        TestBenchStatus.PASSED: "Current target revision has passing evidence.",
        TestBenchStatus.BLOCKED: "Required suite is blocked by safe-mode policy.",
        TestBenchStatus.RUNTIME_ERROR: "Latest run ended with a runtime error.",
    }.get(status, "Gate evidence is summarized from live records.")


def _gate_remediation(status: TestBenchStatus) -> str:
    return {
        TestBenchStatus.MISSING: "Launch the required suite for the current target.",
        TestBenchStatus.STALE: "Rerun the suite after the latest target change.",
        TestBenchStatus.RUNNING: "Wait for backend run finalization.",
        TestBenchStatus.FAILED: "Open diagnostics and fix the failing assertion.",
        TestBenchStatus.PASSED: "Publication can use this current evidence.",
        TestBenchStatus.BLOCKED: "Use an approved safe mode before publishing.",
        TestBenchStatus.RUNTIME_ERROR: "Review run diagnostics and relaunch safely.",
    }.get(status, "Review live gate evidence.")


def _target_label(suite: AgentTestSuite) -> str:
    return _safe_text(suite.target_id.replace("-", " ").replace("_", " ").title())


def _expected_summary(assertion: AgentTestAssertion) -> str:
    if assertion.expected_value is not None:
        return _safe_text(str(assertion.expected_value))
    if assertion.expected_schema:
        return _mapping_summary(assertion.expected_schema, "Expected schema summary.")
    return "No explicit expected value."


def _assertion_payload(assertion: AssertionDefinition) -> dict[str, object]:
    return {
        "kind": "deterministic",
        "path": assertion.path_summary,
        "comparator": assertion.comparator,
        "expected_value": assertion.expected_summary,
        "severity": assertion.severity,
        "weight": assertion.threshold_weight,
        "description": assertion.label,
    }


def _mapping_summary(value: Mapping[str, object], fallback: str) -> str:
    if not value:
        return _safe_text(fallback)
    for key in ("summary", "safe_summary", "description", "label"):
        item = value.get(key)
        if isinstance(item, str) and item.strip():
            return _safe_text(item)
    if "preview" in value:
        return _safe_text(
            "Safe fixture fields: " + ", ".join(_mapping_keys(value["preview"]))
        )
    return _safe_text("Safe fields: " + ", ".join(_mapping_keys(value)))


def _mapping_keys(value: object) -> list[str]:
    if isinstance(value, Mapping):
        return sorted(str(key) for key in value.keys())[:8]
    return [str(value)[:80]]


def _usage_summary(value: Mapping[str, object]) -> str:
    total = value.get("total_tokens", 0)
    return _safe_text(f"{total} total tokens")


def _token_usage_label(value: Mapping[str, object]) -> str:
    total = value.get("total_tokens", 0)
    if isinstance(total, int | float):
        return f"{int(total)} total tokens"
    if isinstance(total, str):
        try:
            return f"{int(total)} total tokens"
        except ValueError:
            return "0 total tokens"
    return "0 total tokens"


def _redaction_summary(value: Mapping[str, object]) -> str:
    if not value:
        return "Sensitive transcript content is summarized."
    redacted = value.get("transcripts_redacted", 0)
    return _safe_text(f"{redacted} transcripts summarized; sensitive payloads hidden.")


def _blocked_effects(steps: Sequence[object]) -> list[str]:
    effects: list[str] = []
    for step in steps:
        for item in getattr(step, "blocked_side_effects", []) or []:
            if isinstance(item, Mapping):
                tool = item.get("tool_name") or item.get("tool")
                reason = item.get("reason") or "blocked by safe mode"
                effects.append(_safe_text(f"{tool}: {reason}"))
            else:
                effects.append(_safe_text(str(item)))
    return effects[:10]


def _artifact_label(artifact: AgentTestArtifact) -> str:
    label = artifact.safe_summary.get("label")
    if isinstance(label, str) and label.strip():
        return label
    return artifact.artifact_type.replace("_", " ").title()


def _provenance(**counts: int) -> ReactAdminPageProvenance:
    details = ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))
    return live_test_bench_provenance(
        source_label="Agent test bench records",
        source_detail=details or "Live repository-backed test bench projection.",
    )


def _slug(value: str) -> str:
    return "-".join(value.lower().replace("_", "-").split())


def _timestamp_label(value: datetime | None) -> str:
    if value is None:
        return "Not recorded"
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC).strftime("%Y-%m-%d %H:%M UTC")


def _value(value: object) -> str:
    raw = getattr(value, "value", value)
    return str(raw).lower()


def _safe_text(value: object) -> str:
    try:
        return safe_test_bench_text(str(value), max_length=220)
    except ValueError:
        return "Safe summary unavailable."
