from __future__ import annotations

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
    ReactAdminScope,
    ReactAdminScopeType,
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
)
from multi_agent_platform.auth.principal import PrincipalContext

ACME_TENANT_ID = "11111111-1111-1111-1111-111111111111"
CURRENT_SUITE_REVISION = "suite-rev-qa033-current"
CURRENT_CASE_REVISION = "case-rev-qa033-current"
CURRENT_TARGET_REVISION = "workflow-draft-rev-qa033-current"
STALE_TARGET_REVISION = "workflow-draft-rev-qa033-stale"


def is_platform_admin(principal: PrincipalContext) -> bool:
    return "platform_admin" in principal.role_codes


def build_test_bench_dashboard(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
) -> TestBenchDashboard:
    platform_admin = is_platform_admin(principal)
    suite = _suite_detail(scope=scope)
    recent_runs = _run_summaries(scope=scope)
    return TestBenchDashboard(
        page_id="react-test-bench",
        title="Test Bench",
        description=(
            "Guided suite authoring, safe run launch, diagnostics, artifacts, "
            "publish gates, and governance evidence."
        ),
        scope=scope,
        sections=_sections(platform_admin=platform_admin),
        summary_cards=(
            TestBenchSummaryMetric(
                metric_id="suite-count",
                label="Suites",
                value="2",
                status=TestBenchStatus.READY,
                summary="Reusable suites are scoped to authorized targets.",
            ),
            TestBenchSummaryMetric(
                metric_id="running-runs",
                label="Running",
                value="1",
                status=TestBenchStatus.RUNNING,
                summary="Progress is read from backend snapshots.",
            ),
            TestBenchSummaryMetric(
                metric_id="failing-runs",
                label="Needs review",
                value="1",
                status=TestBenchStatus.FAILED,
                summary="Failure diagnostics are summarized safely.",
            ),
            TestBenchSummaryMetric(
                metric_id="stale-gates",
                label="Stale gates",
                value="1",
                status=TestBenchStatus.STALE,
                summary="Stale evidence cannot satisfy publication.",
            ),
        ),
        gate_alerts=(
            _gate_evidence(TestBenchStatus.STALE),
            _gate_evidence(TestBenchStatus.PASSED),
        ),
        suites=(_suite_summary(scope=scope), _secondary_suite_summary(scope=scope)),
        selected_suite=suite,
        recent_runs=recent_runs,
        audit_timeline=_audit_records(scope=scope),
        refresh=RefreshHint(
            mode="poll",
            interval_seconds=15,
        ),
        actions=(
            AdminAction(
                action_id="create-suite",
                label="Save suite",
                method=AdminActionMethod.POST,
                href="/admin/app/test-bench/suites",
                variant=ReactAdminPageActionVariant.PRIMARY,
                requires_idempotency_key=True,
            ),
            AdminAction(
                action_id="refresh-gates",
                label="Refresh gate evidence",
                method=AdminActionMethod.POST,
                href="/admin/app/test-bench/gates/qa033-required-suite/refresh",
                variant=ReactAdminPageActionVariant.SECONDARY,
                requires_idempotency_key=True,
            ),
        ),
    )


def build_test_suite_list(*, scope: ReactAdminScope) -> TestSuiteList:
    return TestSuiteList(
        scope=scope,
        suites=(_suite_summary(scope=scope), _secondary_suite_summary(scope=scope)),
        form_metadata=_form_metadata(),
    )


def build_test_suite_detail(
    *,
    suite_id: str,
    scope: ReactAdminScope,
) -> TestSuiteDetail:
    _ = suite_id
    return _suite_detail(scope=scope)


def build_suite_save_result(
    *,
    request: TestSuiteSaveRequest,
    scope: ReactAdminScope,
) -> TestBenchMutationResult:
    if request.revision and request.revision != CURRENT_SUITE_REVISION:
        return TestBenchMutationResult(
            status=AdminMutationStatus.STALE_CONFLICT,
            summary="Reload the suite before saving changes.",
            stale_conflict=RevisionConflict(
                submitted_revision=request.revision,
                current_revision=CURRENT_SUITE_REVISION,
                message="The suite has a newer safe revision.",
                reload_href="/admin/app/test-bench",
            ),
            audit_reference_id="audit-test-suite-stale-qa033",
        )
    suite = _suite_detail(scope=scope)
    return TestBenchMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Test suite saved with current target revision binding.",
        revision=suite.summary.suite_revision,
        suite=suite,
        diagnostics=(
            "Fixture and target metadata were summarized before returning to React.",
            "Publish-gate eligibility is tied to the selected target revision.",
        ),
        audit_reference_id="audit-test-suite-save-qa033",
        toast=ToastHint(
            tone=ReactAdminNotificationTone.SUCCESS,
            title="Suite saved",
            summary="Safe suite metadata is ready for test runs.",
        ),
    )


def build_case_save_result(
    *,
    suite_id: str,
    request: TestCaseSaveRequest,
    scope: ReactAdminScope,
) -> TestBenchMutationResult:
    _ = suite_id, scope
    if request.revision and request.revision != CURRENT_CASE_REVISION:
        return TestBenchMutationResult(
            status=AdminMutationStatus.STALE_CONFLICT,
            summary="Reload the case before saving assertions.",
            stale_conflict=RevisionConflict(
                submitted_revision=request.revision,
                current_revision=CURRENT_CASE_REVISION,
                message="The case has a newer safe revision.",
                reload_href="/admin/app/test-bench",
            ),
            audit_reference_id="audit-test-case-stale-qa033",
        )
    case = _test_cases()[0].model_copy(
        update={
            "case_name": request.name,
            "fixture_summary": request.fixture_summary,
            "expected_contract_summary": request.expected_contract_summary,
            "assertions": request.assertions or _assertions(),
        }
    )
    return TestBenchMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Test case saved with structured assertion descriptors.",
        revision=case.case_revision,
        case=case,
        diagnostics=(
            "Raw fixture bodies and evaluator prompts were not returned.",
            "Evaluator evidence remains server-owned and display-only.",
        ),
        audit_reference_id="audit-test-case-save-qa033",
    )


def build_run_launch_result(
    *,
    suite_id: str,
    request: TestRunLaunchRequest,
    scope: ReactAdminScope,
) -> TestBenchMutationResult:
    _ = suite_id
    if request.safe_mode == "real_dependency_probe":
        return TestBenchMutationResult(
            status=AdminMutationStatus.VALIDATION_ERROR,
            summary="Real dependency probes require policy approval before execution.",
            field_errors=(
                ValidationFieldError(
                    field="safe_mode",
                    label="Safe mode",
                    message="Use mock mode or side-effect-disabled gateway mode in QA.",
                    code="probe_requires_approval",
                ),
            ),
            diagnostics=(
                "No provider, connector, Telegram, credential, or external "
                "call was made.",
            ),
            audit_reference_id="audit-test-run-probe-denied-qa033",
        )
    if request.safe_mode not in {"mock_model_tools", "side_effect_disabled_gateway"}:
        return TestBenchMutationResult(
            status=AdminMutationStatus.VALIDATION_ERROR,
            summary="Choose an allowed safe execution mode.",
            field_errors=(
                ValidationFieldError(
                    field="safe_mode",
                    label="Safe mode",
                    message="Mock mode is the default local validation mode.",
                    code="unsupported_safe_mode",
                ),
            ),
            audit_reference_id="audit-test-run-safe-mode-denied-qa033",
        )
    if request.target_revision != CURRENT_TARGET_REVISION:
        return TestBenchMutationResult(
            status=AdminMutationStatus.STALE_CONFLICT,
            summary="Run launch requires the current target revision.",
            stale_conflict=RevisionConflict(
                submitted_revision=request.target_revision,
                current_revision=CURRENT_TARGET_REVISION,
                message="The workflow draft changed after this suite was loaded.",
                reload_href="/admin/app/test-bench",
            ),
            audit_reference_id="audit-test-run-target-stale-qa033",
        )
    run = _run_detail(
        run_id="run-qa033-running",
        scope=scope,
        status=TestBenchStatus.RUNNING,
        safe_mode=request.safe_mode,
    )
    return TestBenchMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Test run queued with backend-owned progress evidence.",
        revision="run-rev-qa033-running",
        run=run,
        diagnostics=(
            "Run is idempotent for the submitted key.",
            "Blocked side effects are summarized without raw payloads.",
        ),
        audit_reference_id="audit-test-run-launch-qa033",
        toast=ToastHint(
            tone=ReactAdminNotificationTone.SUCCESS,
            title="Run queued",
            summary="Progress will refresh from backend run state.",
        ),
    )


def build_test_run_list(*, scope: ReactAdminScope) -> TestRunList:
    return TestRunList(scope=scope, runs=_run_summaries(scope=scope))


def build_test_run_detail(
    *,
    run_id: str,
    scope: ReactAdminScope,
) -> TestRunDetail:
    if "passing" in run_id:
        return _run_detail(
            run_id="run-qa033-passing",
            scope=scope,
            status=TestBenchStatus.PASSED,
            safe_mode="mock_model_tools",
        )
    if "running" in run_id:
        return _run_detail(
            run_id="run-qa033-running",
            scope=scope,
            status=TestBenchStatus.RUNNING,
            safe_mode="side_effect_disabled_gateway",
        )
    return _run_detail(
        run_id="run-qa033-failing",
        scope=scope,
        status=TestBenchStatus.FAILED,
        safe_mode="side_effect_disabled_gateway",
    )


def build_artifact_reference(
    *,
    artifact_reference_id: str,
) -> ArtifactReferenceSummary:
    if "unavailable" in artifact_reference_id:
        return _unavailable_artifact()
    return _artifact()


def build_publish_gate_evidence(*, scope: ReactAdminScope) -> PublishGateEvidenceList:
    return PublishGateEvidenceList(
        scope=scope,
        gates=(
            _gate_evidence(TestBenchStatus.MISSING),
            _gate_evidence(TestBenchStatus.STALE),
            _gate_evidence(TestBenchStatus.RUNNING),
            _gate_evidence(TestBenchStatus.FAILED),
            _gate_evidence(TestBenchStatus.PASSED),
            _gate_evidence(TestBenchStatus.AUDIT_UNAVAILABLE),
            _gate_evidence(TestBenchStatus.REDACTION_UNAVAILABLE),
        ),
    )


def build_gate_refresh_result(
    *,
    request: GateEvidenceRefreshRequest,
) -> TestBenchMutationResult:
    if request.target_revision != CURRENT_TARGET_REVISION:
        return TestBenchMutationResult(
            status=AdminMutationStatus.STALE_CONFLICT,
            summary="Gate evidence must match the current target revision.",
            stale_conflict=RevisionConflict(
                submitted_revision=request.target_revision,
                current_revision=CURRENT_TARGET_REVISION,
                message="Stale or copied run evidence cannot satisfy publication.",
                reload_href="/admin/app/test-bench",
            ),
            audit_reference_id="audit-test-gate-stale-qa033",
        )
    gate = _gate_evidence(TestBenchStatus.PASSED)
    return TestBenchMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Publish-gate evidence is current for the selected target revision.",
        revision=gate.target_revision,
        gate=gate,
        diagnostics=("Passing evidence is bound to the current target revision.",),
        audit_reference_id=gate.audit_reference_id,
    )


def build_test_bench_audit(*, scope: ReactAdminScope) -> TestBenchAuditList:
    return TestBenchAuditList(scope=scope, audit_timeline=_audit_records(scope=scope))


def _sections(*, platform_admin: bool) -> tuple[TestBenchSection, ...]:
    _ = platform_admin
    return (
        TestBenchSection(
            section_id="suites",
            label="Suites",
            status=TestBenchStatus.READY,
            summary="Author reusable suite and case definitions.",
        ),
        TestBenchSection(
            section_id="runs",
            label="Runs",
            status=TestBenchStatus.RUNNING,
            summary="Launch safe runs and follow backend progress.",
        ),
        TestBenchSection(
            section_id="diagnostics",
            label="Diagnostics",
            status=TestBenchStatus.FAILED,
            summary="Inspect pass and fail evidence without raw payloads.",
        ),
        TestBenchSection(
            section_id="gates",
            label="Publish gates",
            status=TestBenchStatus.STALE,
            summary="Review current target revision evidence.",
        ),
        TestBenchSection(
            section_id="audit",
            label="Audit",
            status=TestBenchStatus.READY,
            summary="Review bounded governance records and denials.",
        ),
    )


def _form_metadata() -> TestBenchFormMetadata:
    return TestBenchFormMetadata(
        target_options=(
            TargetOption(
                target_type="workflow_draft",
                target_id="workflow-draft-qa033-daily-briefing",
                label="Daily briefing draft",
                current_revision=CURRENT_TARGET_REVISION,
                revision_status=TestBenchStatus.READY,
                safe_summary="Draft target summary contains no prompt text.",
            ),
            TargetOption(
                target_type="published_workflow",
                target_id="workflow-published-qa033-support",
                label="Support triage published workflow",
                current_revision="published-workflow-rev-qa033",
                revision_status=TestBenchStatus.READY,
                safe_summary="Published workflow target is authorized for this scope.",
            ),
        ),
        safe_modes=_safe_modes(),
        assertion_templates=_assertions(),
        run_reason_options=(
            "Release confidence",
            "Regression check",
            "Publish gate recovery",
        ),
        default_safe_mode="mock_model_tools",
        default_pass_threshold=0.9,
    )


def _safe_modes() -> tuple[SafeExecutionModeOption, ...]:
    return (
        SafeExecutionModeOption(
            mode_id="mock_model_tools",
            label="Mock model and mock tools",
            side_effect_posture="No external side effects",
            model_behavior="Deterministic mocked model response",
            tool_behavior="Deterministic mocked tool summaries",
            credential_behavior="No credential resolution",
            allowed_status=TestBenchStatus.READY,
            policy_reason="Default local and CI validation mode.",
            audit_reference_id="audit-safe-mode-mock-qa033",
        ),
        SafeExecutionModeOption(
            mode_id="side_effect_disabled_gateway",
            label="Side-effect-disabled gateway",
            side_effect_posture="Provider and connector side effects blocked",
            model_behavior="Gateway metadata is summarized",
            tool_behavior="Skill gateway records blocked side effects",
            credential_behavior="Credential references remain unresolved in browser",
            allowed_status=TestBenchStatus.WARNING,
            policy_reason="Explicit mode for gateway policy evidence.",
            audit_reference_id="audit-safe-mode-gateway-qa033",
        ),
        SafeExecutionModeOption(
            mode_id="real_dependency_probe",
            label="Real dependency probe",
            side_effect_posture="External dependencies require approval",
            model_behavior="Unavailable in local QA",
            tool_behavior="Unavailable without approval evidence",
            credential_behavior="Requires durable approval reference",
            allowed_status=TestBenchStatus.BLOCKED,
            policy_reason="Policy approval is required before execution.",
            requires_approval=True,
            approval_reference_id="approval-required",
            audit_reference_id="audit-safe-mode-probe-qa033",
        ),
    )


def _assertions() -> tuple[AssertionDefinition, ...]:
    return (
        AssertionDefinition(
            assertion_id="assertion-qa033-contract",
            label="Contract shape",
            kind="contract_shape",
            path_summary="response.summary.status",
            comparator="equals",
            expected_summary="Ready state summary",
            severity="blocking",
            threshold_weight=0.5,
            validation_status=TestBenchStatus.READY,
        ),
        AssertionDefinition(
            assertion_id="assertion-qa033-tool-block",
            label="Blocked side effects",
            kind="policy_decision",
            path_summary="gateway.blocked_side_effects",
            comparator="contains",
            expected_summary="Email delivery remains blocked",
            severity="blocking",
            threshold_weight=0.5,
            validation_status=TestBenchStatus.READY,
        ),
    )


def _suite_summary(*, scope: ReactAdminScope) -> TestSuiteSummary:
    return TestSuiteSummary(
        suite_id="suite-qa033-daily-briefing",
        suite_slug="daily-briefing-release-gate",
        suite_name="Daily briefing release gate",
        tenant_id=str(scope.tenant_id)
        if scope.tenant_id is not None
        else ACME_TENANT_ID,
        tenant_label=scope.label,
        target_type="workflow_draft",
        target_label="Daily briefing draft",
        target_revision=CURRENT_TARGET_REVISION,
        target_status=TestBenchStatus.READY,
        default_safe_mode="mock_model_tools",
        pass_threshold=0.9,
        required_for_publish=True,
        case_count=2,
        latest_run_status=TestBenchStatus.FAILED,
        latest_run_id="run-qa033-failing",
        publish_gate_status=TestBenchStatus.STALE,
        suite_revision=CURRENT_SUITE_REVISION,
        archive_status=TestBenchStatus.READY,
        audit_reference_id="audit-suite-summary-qa033",
        authorized_actions=(
            AdminAction(
                action_id="open-suite",
                label="Open suite",
                method=AdminActionMethod.GET,
                href="/admin/app/test-bench/suites/suite-qa033-daily-briefing",
            ),
            AdminAction(
                action_id="launch-run",
                label="Launch run",
                method=AdminActionMethod.POST,
                href="/admin/app/test-bench/suites/suite-qa033-daily-briefing/runs",
                variant=ReactAdminPageActionVariant.PRIMARY,
                requires_idempotency_key=True,
            ),
        ),
    )


def _secondary_suite_summary(*, scope: ReactAdminScope) -> TestSuiteSummary:
    return _suite_summary(scope=scope).model_copy(
        update={
            "suite_id": "suite-qa033-support-triage",
            "suite_slug": "support-triage-smoke",
            "suite_name": "Support triage smoke",
            "target_type": "published_workflow",
            "target_label": "Support triage published workflow",
            "target_revision": "published-workflow-rev-qa033",
            "latest_run_status": TestBenchStatus.PASSED,
            "latest_run_id": "run-qa033-passing",
            "publish_gate_status": TestBenchStatus.PASSED,
            "suite_revision": "suite-rev-qa033-support",
            "audit_reference_id": "audit-suite-support-qa033",
        }
    )


def _suite_detail(*, scope: ReactAdminScope) -> TestSuiteDetail:
    summary = _suite_summary(scope=scope)
    return TestSuiteDetail(
        summary=summary,
        cases=_test_cases(),
        target_binding=_target_binding(),
        run_launcher=_form_metadata(),
        recent_runs=_run_summaries(scope=scope),
        publish_gate=_gate_evidence(TestBenchStatus.STALE),
        audit_reference_id="audit-suite-detail-qa033",
    )


def _target_binding() -> TargetRevisionBinding:
    return TargetRevisionBinding(
        target_type="workflow_draft",
        target_id="workflow-draft-qa033-daily-briefing",
        target_label="Daily briefing draft",
        current_revision=CURRENT_TARGET_REVISION,
        selected_revision=CURRENT_TARGET_REVISION,
        revision_status=TestBenchStatus.READY,
        source_links=(
            AdminAction(
                action_id="open-workflow-builder",
                label="Open workflow builder",
                method=AdminActionMethod.GET,
                href="/admin/app/workflows?workflow_draft_id=workflow-draft-qa033-daily-briefing",
            ),
        ),
        remediation="Run the required suite after any draft revision changes.",
    )


def _test_cases() -> tuple[TestCaseSummary, ...]:
    return (
        TestCaseSummary(
            case_id="case-qa033-summary",
            case_name="Briefing summary contract",
            case_status=TestBenchStatus.READY,
            case_revision=CURRENT_CASE_REVISION,
            fixture_summary=(
                "Fixture includes market, calendar, and weather metadata summaries."
            ),
            expected_contract_summary=(
                "Summary, source count, and recommendation status are required."
            ),
            assertions=_assertions(),
            evaluator_summary="Evaluator reference checks safe rationale only.",
            threshold_contribution=0.6,
            order=1,
            audit_reference_id="audit-case-summary-qa033",
            authorized_actions=(
                AdminAction(
                    action_id="edit-case",
                    label="Save case",
                    method=AdminActionMethod.POST,
                    href="/admin/app/test-bench/suites/suite-qa033-daily-briefing/cases",
                    requires_idempotency_key=True,
                ),
            ),
        ),
        TestCaseSummary(
            case_id="case-qa033-side-effects",
            case_name="Side-effect posture",
            case_status=TestBenchStatus.READY,
            case_revision="case-rev-qa033-side-effects",
            fixture_summary=(
                "Fixture summarizes a requested notification without message body."
            ),
            expected_contract_summary=(
                "Connector write attempts must be blocked in safe mode."
            ),
            assertions=(_assertions()[1],),
            evaluator_summary="No evaluator prompt is exposed to React.",
            threshold_contribution=0.4,
            order=2,
            audit_reference_id="audit-case-side-effects-qa033",
        ),
    )


def _run_summaries(*, scope: ReactAdminScope) -> tuple[TestRunSummary, ...]:
    return (
        _run_summary(
            run_id="run-qa033-passing",
            scope=scope,
            status=TestBenchStatus.PASSED,
            safe_mode="mock_model_tools",
        ),
        _run_summary(
            run_id="run-qa033-failing",
            scope=scope,
            status=TestBenchStatus.FAILED,
            safe_mode="side_effect_disabled_gateway",
        ),
        _run_summary(
            run_id="run-qa033-running",
            scope=scope,
            status=TestBenchStatus.RUNNING,
            safe_mode="side_effect_disabled_gateway",
        ),
    )


def _run_summary(
    *,
    run_id: str,
    scope: ReactAdminScope,
    status: TestBenchStatus,
    safe_mode: str,
) -> TestRunSummary:
    failed = status is TestBenchStatus.FAILED
    running = status is TestBenchStatus.RUNNING
    return TestRunSummary(
        run_id=run_id,
        suite_id="suite-qa033-daily-briefing",
        suite_name="Daily briefing release gate",
        target_revision=CURRENT_TARGET_REVISION
        if not failed
        else STALE_TARGET_REVISION,
        safe_mode=safe_mode,
        status=status,
        pass_rate=1.0 if status is TestBenchStatus.PASSED else 0.5 if failed else 0.25,
        failure_category=TestBenchStatus.FAILED_ASSERTION if failed else None,
        started_label="Today 09:15",
        finished_label=None if running else "Today 09:16",
        actor_label="Platform Admin"
        if scope.scope_type is ReactAdminScopeType.PLATFORM
        else "Tenant Admin",
        case_total=2,
        case_passed=2 if status is TestBenchStatus.PASSED else 1 if failed else 0,
        case_failed=0 if status is TestBenchStatus.PASSED else 1 if failed else 0,
        usage_summary="124 input tokens, 42 output tokens",
        latency_summary="1.8 seconds p95",
        audit_reference_id=f"audit-{run_id}",
        authorized_actions=(
            AdminAction(
                action_id="open-run",
                label="Open run",
                method=AdminActionMethod.GET,
                href=f"/admin/app/test-bench/runs/{run_id}.json",
            ),
        ),
    )


def _run_detail(
    *,
    run_id: str,
    scope: ReactAdminScope,
    status: TestBenchStatus,
    safe_mode: str,
) -> TestRunDetail:
    summary = _run_summary(
        run_id=run_id,
        scope=scope,
        status=status,
        safe_mode=safe_mode,
    )
    failed = status is TestBenchStatus.FAILED
    return TestRunDetail(
        summary=summary,
        progress=TestRunProgressSnapshot(
            status=status,
            summary="Backend run state reports the current terminal status."
            if status is not TestBenchStatus.RUNNING
            else "Backend run state reports one case still running.",
            completed_cases=2 if status is not TestBenchStatus.RUNNING else 1,
            total_cases=2,
            next_poll_seconds=0 if status is not TestBenchStatus.RUNNING else 10,
            audit_reference_id=f"audit-progress-{run_id}",
        ),
        case_results=_case_results(failed=failed),
        trace_steps=_trace_steps(failed=failed),
        assertion_diagnostics=_diagnostics(failed=failed),
        artifacts=(_artifact(),),
        publish_gate=_gate_evidence(
            TestBenchStatus.FAILED if failed else TestBenchStatus.PASSED
        ),
        redaction_summary=(
            "Sensitive model, connector, transcript, and file-location evidence "
            "was summarized before rendering."
        ),
        blocked_side_effects=(
            "Email delivery blocked by side-effect-disabled gateway",
            "Telegram notification blocked in QA mode",
        )
        if safe_mode == "side_effect_disabled_gateway"
        else (),
        audit_reference_id=f"audit-detail-{run_id}",
    )


def _case_results(*, failed: bool) -> tuple[TestCaseSummary, ...]:
    cases = list(_test_cases())
    if failed:
        cases[1] = cases[1].model_copy(
            update={"case_status": TestBenchStatus.FAILED_ASSERTION}
        )
    else:
        cases = [
            case.model_copy(update={"case_status": TestBenchStatus.PASSED})
            for case in cases
        ]
    return tuple(cases)


def _trace_steps(*, failed: bool) -> tuple[TraceStepSummary, ...]:
    return (
        TraceStepSummary(
            step_id="step-qa033-model",
            case_id="case-qa033-summary",
            step_label="Model response summary",
            runtime_role="briefing agent",
            status=TestBenchStatus.PASSED,
            latency_ms=820,
            token_usage="86 input, 30 output",
            model_label="Mock OpenAI-compatible model",
            provider_label="Local deterministic provider",
            prompt_version_label="prompt version qa033",
            profile_version_label="profile version qa033",
            skill_version_labels=("daily-briefing-connectors 1.4.0",),
            safe_transcript_excerpt=(
                "Summary was produced from deterministic QA evidence."
            ),
            blocked_side_effects=(),
            gateway_decision="mocked model result",
            redaction_class="safe-summary",
            artifact_reference_ids=("artifact-qa033-summary",),
        ),
        TraceStepSummary(
            step_id="step-qa033-side-effect",
            case_id="case-qa033-side-effects",
            step_label="Connector side-effect decision",
            runtime_role="tool gateway",
            status=TestBenchStatus.FAILED_ASSERTION
            if failed
            else TestBenchStatus.PASSED,
            latency_ms=240,
            token_usage="0 model tokens",
            model_label="No live provider",
            provider_label="SkillExecutionGateway",
            prompt_version_label="prompt version qa033",
            profile_version_label="profile version qa033",
            skill_version_labels=("daily-briefing-connectors 1.4.0",),
            safe_transcript_excerpt="Gateway summarized a blocked write decision.",
            blocked_side_effects=("email.send", "telegram.send_message"),
            gateway_decision="blocked_side_effect",
            redaction_class="safe-summary",
            artifact_reference_ids=("artifact-qa033-gateway",),
        ),
    )


def _diagnostics(*, failed: bool) -> tuple[DiagnosticFinding, ...]:
    if not failed:
        return (
            DiagnosticFinding(
                finding_id="finding-qa033-pass",
                category=TestBenchStatus.PASSED,
                label="All assertions passed",
                expected_summary="Contract and policy summaries matched.",
                actual_summary="Deterministic QA evidence matched.",
                comparator="all",
                path_summary="suite.case_results",
                severity="info",
                remediation="No action needed.",
            ),
        )
    return (
        DiagnosticFinding(
            finding_id="finding-qa033-assertion",
            category=TestBenchStatus.FAILED_ASSERTION,
            label="Blocked side-effect assertion failed",
            expected_summary="Gateway should report every blocked write attempt.",
            actual_summary="One blocked notification summary was missing.",
            comparator="contains",
            path_summary="trace_steps[side-effect].blocked_side_effects",
            severity="blocking",
            remediation="Refresh the run for the current target revision.",
        ),
        DiagnosticFinding(
            finding_id="finding-qa033-contract",
            category=TestBenchStatus.CONTRACT_FAILURE,
            label="Contract path unavailable",
            expected_summary="Expected status path is present.",
            actual_summary="Redacted actual shape omitted the status path.",
            comparator="exists",
            path_summary="response.summary.status",
            severity="warning",
            remediation="Update the case contract summary after reviewing the draft.",
        ),
    )


def _artifact() -> ArtifactReferenceSummary:
    return ArtifactReferenceSummary(
        artifact_reference_id="artifact-qa033-summary",
        label="Redacted run summary artifact",
        content_class="diagnostic_summary",
        checksum="sha256:qa033artifactsummary",
        size_label="18 KB",
        retention_state=TestBenchStatus.READY,
        redaction_class="safe-summary",
        access_status=TestBenchStatus.READY,
        safe_summary="Artifact metadata is available by governed reference only.",
        authorized_href="/admin/app/test-bench/artifacts/artifact-qa033-summary.json",
        audit_reference_id="audit-artifact-qa033-summary",
    )


def _unavailable_artifact() -> ArtifactReferenceSummary:
    return ArtifactReferenceSummary(
        artifact_reference_id="artifact-qa033-unavailable",
        label="Unavailable redacted artifact metadata",
        content_class="diagnostic_summary",
        checksum="sha256:qa033artifactunavailable",
        size_label="0 KB",
        retention_state=TestBenchStatus.ARTIFACT_UNAVAILABLE,
        redaction_class="safe-summary",
        access_status=TestBenchStatus.ARTIFACT_UNAVAILABLE,
        safe_summary=(
            "Artifact metadata is unavailable; payload access remains blocked."
        ),
        authorized_href=None,
        audit_reference_id="audit-artifact-qa033-unavailable",
    )


def _gate_evidence(status: TestBenchStatus) -> PublishGateEvidence:
    latest_run_id = "run-qa033-passing" if status is TestBenchStatus.PASSED else None
    latest_revision = (
        CURRENT_TARGET_REVISION if status is TestBenchStatus.PASSED else None
    )
    if status is TestBenchStatus.STALE:
        latest_run_id = "run-qa033-failing"
        latest_revision = STALE_TARGET_REVISION
    return PublishGateEvidence(
        gate_id=f"gate-qa033-{status.value}",
        target_type="workflow_draft",
        target_label="Daily briefing draft",
        target_revision=CURRENT_TARGET_REVISION,
        required_suite_id="suite-qa033-daily-briefing",
        required_suite_label="Daily briefing release gate",
        evidence_status=status,
        latest_run_id=latest_run_id,
        latest_run_revision=latest_revision,
        latest_run_status=TestBenchStatus.PASSED
        if status is TestBenchStatus.PASSED
        else TestBenchStatus.FAILED
        if status is TestBenchStatus.STALE
        else None,
        reason=_gate_reason(status),
        remediation=_gate_remediation(status),
        audit_reference_id=f"audit-gate-qa033-{status.value}",
        artifact_references=(_artifact(),)
        if status is TestBenchStatus.PASSED
        else (_unavailable_artifact(),)
        if status is TestBenchStatus.REDACTION_UNAVAILABLE
        else (),
        authorized_actions=(
            AdminAction(
                action_id="run-suite",
                label="Run suite",
                method=AdminActionMethod.POST,
                href="/admin/app/test-bench/suites/suite-qa033-daily-briefing/runs",
                variant=ReactAdminPageActionVariant.PRIMARY,
                requires_idempotency_key=True,
            ),
            AdminAction(
                action_id="open-workflow-publish",
                label="Open publish flow",
                method=AdminActionMethod.GET,
                href="/admin/app/workflows?workflow_draft_id=workflow-draft-qa033-daily-briefing",
            ),
        ),
    )


def _gate_reason(status: TestBenchStatus) -> str:
    reasons = {
        TestBenchStatus.MISSING: "No passing run exists for this target revision.",
        TestBenchStatus.STALE: "Latest run is tied to an older draft revision.",
        TestBenchStatus.RUNNING: "Required suite is still running.",
        TestBenchStatus.FAILED: "Latest current run did not meet the pass threshold.",
        TestBenchStatus.PASSED: "Current target revision has passing evidence.",
        TestBenchStatus.UNAVAILABLE: "Audit or redaction evidence is unavailable.",
        TestBenchStatus.AUDIT_UNAVAILABLE: "Audit evidence is unavailable.",
        TestBenchStatus.REDACTION_UNAVAILABLE: (
            "Redaction evidence is unavailable for the latest run."
        ),
    }
    return reasons.get(status, "Gate evidence is being summarized.")


def _gate_remediation(status: TestBenchStatus) -> str:
    remediations = {
        TestBenchStatus.MISSING: "Launch the required suite for the current draft.",
        TestBenchStatus.STALE: "Rerun the suite after the latest draft change.",
        TestBenchStatus.RUNNING: "Wait for backend run finalization.",
        TestBenchStatus.FAILED: "Open diagnostics and fix the failing assertion.",
        TestBenchStatus.PASSED: "Publication can use this current evidence.",
        TestBenchStatus.UNAVAILABLE: "Restore audit and redaction evidence first.",
        TestBenchStatus.AUDIT_UNAVAILABLE: "Restore audit evidence before publishing.",
        TestBenchStatus.REDACTION_UNAVAILABLE: (
            "Regenerate redaction evidence before publishing."
        ),
    }
    return remediations.get(status, "Review gate evidence.")


def _audit_records(*, scope: ReactAdminScope) -> tuple[TestBenchAuditRecord, ...]:
    tenant_label = scope.label
    return (
        TestBenchAuditRecord(
            record_id="audit-record-suite-qa033",
            domain="suite",
            tenant_scope_label=tenant_label,
            actor_label="Tenant Admin",
            target_label="Daily briefing draft",
            timestamp_label="Today 09:00",
            action="saved_suite",
            outcome=TestBenchStatus.READY,
            safe_diff_summary="Suite target revision and threshold were updated.",
            redaction_class="safe-summary",
            audit_reference_id="audit-test-suite-save-qa033",
        ),
        TestBenchAuditRecord(
            record_id="audit-record-run-qa033",
            domain="run",
            tenant_scope_label=tenant_label,
            actor_label="Tenant Admin",
            target_label="Daily briefing release gate",
            timestamp_label="Today 09:15",
            action="launched_run",
            outcome=TestBenchStatus.RUNNING,
            safe_diff_summary="Mock mode run launched with idempotency evidence.",
            redaction_class="safe-summary",
            audit_reference_id="audit-test-run-launch-qa033",
        ),
        TestBenchAuditRecord(
            record_id="audit-record-denied-qa033",
            domain="denied_access",
            tenant_scope_label=tenant_label,
            actor_label="Tenant User",
            target_label="Unavailable test bench evidence",
            timestamp_label="Today 09:20",
            action="denied_cross_tenant_access",
            outcome=TestBenchStatus.DENIED,
            safe_diff_summary=(
                "Denied response excluded suite, run, target, and artifact details."
            ),
            redaction_class="safe-denial",
            audit_reference_id="audit-test-denied-qa033",
        ),
    )
