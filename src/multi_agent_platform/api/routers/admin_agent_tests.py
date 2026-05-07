from __future__ import annotations

import json
from typing import Annotated, Any, cast
from urllib.parse import urlencode
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.api.deps import get_session
from multi_agent_platform.api.schemas.agent_tests import (
    AgentTestAssertionResponse,
    AgentTestCaseCreateRequest,
    AgentTestCaseResponse,
    AgentTestPublishGateSummary,
    AgentTestRunCreateRequest,
    AgentTestRunResponse,
    AgentTestRunStepResponse,
    AgentTestSuiteCreateRequest,
    AgentTestSuiteResponse,
    AgentTestSuiteUpdateRequest,
    PublishGateEvaluateRequest,
)
from multi_agent_platform.api.ui.admin_console import is_platform_admin
from multi_agent_platform.auth.dependencies import require_authorized_principal
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.db.models.agent_tests import (
    AgentTestAssertion,
    AgentTestCase,
    AgentTestRun,
    AgentTestRunStep,
    AgentTestSuite,
)
from multi_agent_platform.db.repositories.agent_tests import AgentTestRepository
from multi_agent_platform.testing.agent_bench.service import (
    AgentTestBenchError,
    AgentTestBenchService,
)

router = APIRouter(prefix="/admin/agent-tests", tags=["agent-tests"])
PrincipalDep = Annotated[PrincipalContext, Depends(require_authorized_principal)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]
SEE_OTHER = status.HTTP_303_SEE_OTHER


@router.get("/suites", response_model=list[AgentTestSuiteResponse])
async def list_agent_test_suites(
    tenant_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
) -> list[AgentTestSuiteResponse]:
    _ensure_tenant_access(principal, tenant_id)
    repository = AgentTestRepository(session)
    return [
        await _suite_response(repository, suite)
        for suite in await repository.list_suites_for_tenant(tenant_id=tenant_id)
    ]


@router.post(
    "/suites",
    response_model=AgentTestSuiteResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_agent_test_suite(
    request: AgentTestSuiteCreateRequest,
    principal: PrincipalDep,
    session: SessionDep,
) -> AgentTestSuiteResponse:
    _ensure_tenant_access(principal, request.tenant_id)
    service = AgentTestBenchService(AgentTestRepository(session))
    suite = await service.create_suite(
        tenant_id=request.tenant_id,
        name=request.name,
        description=request.description,
        target_type=request.target_type,
        target_id=request.target_id,
        target_version=request.target_version,
        default_safe_mode=request.default_safe_mode,
        model_mode=request.model_mode,
        tool_mode=request.tool_mode,
        pass_threshold=request.pass_threshold,
        required_for_publish=request.required_for_publish,
        actor_principal_id=principal.principal_id,
    )
    return await _suite_response(service.repository, suite)


@router.get("/suites/{suite_id}", response_model=AgentTestSuiteResponse)
async def get_agent_test_suite(
    suite_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
) -> AgentTestSuiteResponse:
    repository = AgentTestRepository(session)
    suite = await _require_suite_for_principal(repository, suite_id, principal)
    return await _suite_response(repository, suite)


@router.patch("/suites/{suite_id}", response_model=AgentTestSuiteResponse)
async def update_agent_test_suite(
    suite_id: UUID,
    request: AgentTestSuiteUpdateRequest,
    principal: PrincipalDep,
    session: SessionDep,
) -> AgentTestSuiteResponse:
    _ensure_tenant_access(principal, request.tenant_id)
    service = AgentTestBenchService(AgentTestRepository(session))
    try:
        suite = await service.update_suite(
            suite_id=suite_id,
            tenant_id=request.tenant_id,
            expected_revision=request.revision,
            name=request.name,
            description=request.description,
            target_version=request.target_version,
            default_safe_mode=request.default_safe_mode,
            model_mode=request.model_mode,
            tool_mode=request.tool_mode,
            pass_threshold=request.pass_threshold,
            required_for_publish=request.required_for_publish,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="suite not found") from exc
    return await _suite_response(service.repository, suite)


@router.post(
    "/suites/{suite_id}/cases",
    response_model=AgentTestCaseResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_agent_test_case(
    suite_id: UUID,
    request: AgentTestCaseCreateRequest,
    principal: PrincipalDep,
    session: SessionDep,
) -> AgentTestCaseResponse:
    repository = AgentTestRepository(session)
    suite = await _require_suite_for_principal(repository, suite_id, principal)
    service = AgentTestBenchService(repository)
    try:
        case = await service.create_case(
            suite_id=suite_id,
            tenant_id=suite.tenant_id,
            name=request.name,
            description=request.description,
            fixture=request.fixture,
            expected_contract_shape=request.expected_contract_shape,
            assertions=[item.model_dump(mode="json") for item in request.assertions],
            evaluator_prompt_ref=request.evaluator_prompt_ref,
            model_mode=request.model_mode,
            tool_mode=request.tool_mode,
            pass_threshold=request.pass_threshold,
            case_order=request.case_order,
            actor_principal_id=principal.principal_id,
        )
    except AgentTestBenchError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    return await _case_response(repository, case)


@router.post(
    "/suites/{suite_id}/runs",
    response_model=AgentTestRunResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_agent_test_run(
    suite_id: UUID,
    request: AgentTestRunCreateRequest,
    principal: PrincipalDep,
    session: SessionDep,
) -> AgentTestRunResponse:
    repository = AgentTestRepository(session)
    suite = await _require_suite_for_principal(repository, suite_id, principal)
    service = AgentTestBenchService(repository)
    try:
        run = await service.launch_run(
            suite_id=suite_id,
            tenant_id=suite.tenant_id,
            actor_principal_id=principal.principal_id,
            safe_mode=request.safe_mode,
            target_version=request.target_version,
            idempotency_key=request.idempotency_key,
            trace_id=principal.trace_id,
            approved_probe_reference=request.approved_probe_reference,
        )
    except AgentTestBenchError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    return await _run_response(repository, run)


@router.get("/runs", response_model=list[AgentTestRunResponse])
async def list_agent_test_runs(
    suite_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
) -> list[AgentTestRunResponse]:
    repository = AgentTestRepository(session)
    suite = await _require_suite_for_principal(repository, suite_id, principal)
    runs = await repository.list_runs_for_suite(
        suite_id=suite.agent_test_suite_id,
        tenant_id=suite.tenant_id,
    )
    return [await _run_response(repository, run) for run in runs]


@router.get("/runs/{run_id}", response_model=AgentTestRunResponse)
async def get_agent_test_run(
    run_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
) -> AgentTestRunResponse:
    repository = AgentTestRepository(session)
    run = await repository.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run not found")
    _ensure_tenant_access(principal, run.tenant_id)
    return await _run_response(repository, run)


@router.post(
    "/publish-gates/evaluate",
    response_model=AgentTestPublishGateSummary,
)
async def evaluate_agent_test_publish_gate(
    request: PublishGateEvaluateRequest,
    principal: PrincipalDep,
    session: SessionDep,
) -> AgentTestPublishGateSummary:
    _ensure_tenant_access(principal, request.tenant_id)
    summary = await AgentTestBenchService(
        AgentTestRepository(session)
    ).evidence_summary(
        tenant_id=request.tenant_id,
        target_type=request.target_type,
        target_id=request.target_id,
        target_version=request.target_version,
    )
    safe_reasons = []
    if summary.missing_count:
        safe_reasons.append("Required test evidence is missing.")
    if summary.stale_count:
        safe_reasons.append("Required test evidence is stale.")
    return AgentTestPublishGateSummary(
        status="ready" if summary.ready else "blocked",
        required_count=summary.required_count,
        passing_count=summary.passing_count,
        failing_count=summary.failing_count,
        missing_count=summary.missing_count,
        stale_count=summary.stale_count,
        required_suite_ids=summary.required_suite_ids,
        passing_run_ids=summary.passing_run_ids,
        stale_run_ids=summary.stale_run_ids,
        safe_reasons=safe_reasons,
    )


@router.get("/ui", response_model=None)
async def agent_test_bench_index(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
) -> RedirectResponse:
    _ = request, session
    return _react_redirect(
        principal=principal,
        request=request,
    )


@router.get("/ui/suites/new", response_model=None)
async def new_agent_test_suite_form(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
) -> RedirectResponse:
    _ = session
    return _react_redirect(
        principal=principal,
        request=request,
        extra={"mode": "create-suite"},
    )


@router.post("/ui/suites", response_model=None)
async def create_agent_test_suite_from_form(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
) -> RedirectResponse:
    form = await request.form()
    tenant_id = _form_tenant_id(form.get("tenant_id"), principal)
    _ensure_tenant_access(principal, tenant_id)
    service = AgentTestBenchService(AgentTestRepository(session))
    suite = await service.create_suite(
        tenant_id=tenant_id,
        name=str(form.get("name") or "Untitled suite"),
        description=str(form.get("description") or ""),
        target_type=str(form.get("target_type") or "workflow_draft"),
        target_id=str(form.get("target_id") or "qa015-draft-triage"),
        target_version=str(form.get("target_version") or "draft-rev-1"),
        default_safe_mode=str(form.get("default_safe_mode") or "mock_model"),
        model_mode=str(form.get("model_mode") or "mock"),
        tool_mode=str(form.get("tool_mode") or "mock"),
        pass_threshold=float(str(form.get("pass_threshold") or "1.0")),
        required_for_publish=bool(form.get("required_for_publish")),
        actor_principal_id=principal.principal_id,
    )
    return RedirectResponse(
        _react_test_bench_href(
            tenant_id=suite.tenant_id,
            extra={
                "suite_id": suite.agent_test_suite_id,
                "mutation": "created",
            },
        ),
        status_code=SEE_OTHER,
    )


@router.get("/ui/suites/{suite_id}", response_model=None)
async def agent_test_suite_detail(
    suite_id: UUID,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
) -> RedirectResponse:
    repository = AgentTestRepository(session)
    suite = await _require_suite_for_principal(repository, suite_id, principal)
    return _react_redirect(
        principal=principal,
        request=request,
        tenant_id=suite.tenant_id,
        extra={"suite_id": suite_id},
    )


@router.post(
    "/ui/suites/{suite_id}/cases",
    response_model=None,
)
async def create_agent_test_case_from_form(
    suite_id: UUID,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
) -> RedirectResponse:
    form = await request.form()
    repository = AgentTestRepository(session)
    suite = await _require_suite_for_principal(repository, suite_id, principal)
    fixture = _json_form_object(form.get("fixture_json"))
    contract = _json_form_object(form.get("expected_contract_shape"))
    assertions = _json_form_list(form.get("assertions_json"))
    await AgentTestBenchService(repository).create_case(
        suite_id=suite_id,
        tenant_id=suite.tenant_id,
        name=str(form.get("name") or "Untitled case"),
        description=str(form.get("description") or ""),
        fixture=fixture,
        expected_contract_shape=contract,
        assertions=assertions,
        evaluator_prompt_ref=str(form.get("evaluator_prompt_ref") or "") or None,
        actor_principal_id=principal.principal_id,
    )
    return RedirectResponse(
        _react_test_bench_href(
            tenant_id=suite.tenant_id,
            extra={
                "suite_id": suite_id,
                "mutation": "case-created",
            },
        ),
        status_code=SEE_OTHER,
    )


@router.post(
    "/ui/suites/{suite_id}/runs",
    response_model=None,
)
async def create_agent_test_run_from_form(
    suite_id: UUID,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
) -> RedirectResponse:
    form = await request.form()
    repository = AgentTestRepository(session)
    suite = await _require_suite_for_principal(repository, suite_id, principal)
    run = await AgentTestBenchService(repository).launch_run(
        suite_id=suite_id,
        tenant_id=suite.tenant_id,
        actor_principal_id=principal.principal_id,
        safe_mode=str(form.get("safe_mode") or suite.default_safe_mode.value),
        target_version=str(form.get("target_version") or suite.target_version or ""),
        idempotency_key=str(form.get("idempotency_key") or "") or None,
        trace_id=principal.trace_id,
        approved_probe_reference=str(form.get("approved_probe_reference") or "")
        or None,
    )
    return RedirectResponse(
        _react_test_bench_href(
            tenant_id=suite.tenant_id,
            extra={
                "run_id": run.agent_test_run_id,
                "mutation": "run-launched",
            },
        ),
        status_code=SEE_OTHER,
    )


@router.get("/ui/runs/{run_id}", response_model=None)
async def agent_test_run_detail(
    run_id: UUID,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
) -> RedirectResponse:
    repository = AgentTestRepository(session)
    run = await repository.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run not found")
    _ensure_tenant_access(principal, run.tenant_id)
    return _react_redirect(
        principal=principal,
        request=request,
        tenant_id=run.tenant_id,
        extra={"run_id": run_id},
    )


async def _require_suite_for_principal(
    repository: AgentTestRepository,
    suite_id: UUID,
    principal: PrincipalContext,
) -> AgentTestSuite:
    suite = await repository.get_suite(suite_id)
    if suite is None:
        raise HTTPException(status_code=404, detail="suite not found")
    _ensure_tenant_access(principal, suite.tenant_id)
    return suite


def _ensure_tenant_access(principal: PrincipalContext, tenant_id: UUID) -> None:
    if is_platform_admin(principal):
        return
    if principal.tenant_id != tenant_id or "tenant_admin" not in principal.role_codes:
        raise HTTPException(status_code=403, detail="agent test access denied")


def _react_redirect(
    *,
    principal: PrincipalContext,
    request: Request,
    tenant_id: UUID | None = None,
    extra: dict[str, object] | None = None,
) -> RedirectResponse:
    return RedirectResponse(
        _react_test_bench_href(
            tenant_id=_redirect_tenant_id(principal=principal, request=request)
            if tenant_id is None
            else tenant_id,
            extra=extra,
        ),
        status_code=SEE_OTHER,
    )


def _redirect_tenant_id(
    *,
    principal: PrincipalContext,
    request: Request,
) -> UUID | None:
    query_tenant_id = request.query_params.get("tenant_id")
    if query_tenant_id:
        try:
            tenant_id = UUID(query_tenant_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="invalid tenant_id") from exc
        _ensure_tenant_access(principal, tenant_id)
        return tenant_id
    return principal.tenant_id


def _react_test_bench_href(
    *,
    tenant_id: UUID | None,
    extra: dict[str, object] | None = None,
) -> str:
    query: dict[str, str] = {}
    if tenant_id is not None:
        query["tenant_id"] = str(tenant_id)
    for key, value in (extra or {}).items():
        if value is not None:
            query[key] = str(value)
    if not query:
        return "/admin/app/test-bench"
    return f"/admin/app/test-bench?{urlencode(query)}"


def _form_tenant_id(value: object, principal: PrincipalContext) -> UUID:
    if value:
        return UUID(str(value))
    if principal.tenant_id is not None:
        return principal.tenant_id
    raise HTTPException(status_code=400, detail="tenant_id is required")


def _json_form_object(value: object) -> dict[str, Any]:
    if not value:
        return {}
    parsed = json.loads(str(value))
    if not isinstance(parsed, dict):
        raise HTTPException(status_code=400, detail="expected JSON object")
    return cast(dict[str, Any], parsed)


def _json_form_list(value: object) -> list[dict[str, Any]]:
    if not value:
        return []
    parsed = json.loads(str(value))
    if not isinstance(parsed, list):
        raise HTTPException(status_code=400, detail="expected JSON array")
    return [dict(item) for item in parsed if isinstance(item, dict)]


async def _suite_response(
    repository: AgentTestRepository,
    suite: AgentTestSuite,
) -> AgentTestSuiteResponse:
    cases = await repository.list_cases_for_suite(suite.agent_test_suite_id)
    runs = await repository.list_runs_for_suite(
        suite_id=suite.agent_test_suite_id,
        tenant_id=suite.tenant_id,
    )
    return AgentTestSuiteResponse(
        suite_id=suite.agent_test_suite_id,
        tenant_id=suite.tenant_id,
        name=suite.name,
        description=suite.description,
        target_type=suite.target_type.value,
        target_id=suite.target_id,
        target_version=suite.target_version,
        default_safe_mode=suite.default_safe_mode.value,
        model_mode=suite.model_mode,
        tool_mode=suite.tool_mode,
        pass_threshold=suite.pass_threshold,
        required_for_publish=suite.is_required_for_publish,
        status=suite.status.value,
        revision=suite.revision,
        case_count=len(cases),
        latest_run_status=runs[0].status.value if runs else None,
    )


async def _case_response(
    repository: AgentTestRepository,
    case: AgentTestCase,
) -> AgentTestCaseResponse:
    assertions = await repository.list_assertions_for_case(case.agent_test_case_id)
    return AgentTestCaseResponse(
        case_id=case.agent_test_case_id,
        suite_id=case.agent_test_suite_id,
        tenant_id=case.tenant_id,
        name=case.name,
        description=case.description,
        fixture_summary=case.fixture_summary,
        expected_contract_shape=case.expected_contract_shape,
        assertions=[_assertion_response(assertion) for assertion in assertions],
        pass_threshold=case.pass_threshold,
        status=case.status.value,
        revision=case.revision,
    )


def _assertion_response(assertion: AgentTestAssertion) -> AgentTestAssertionResponse:
    return AgentTestAssertionResponse(
        assertion_id=assertion.agent_test_assertion_id,
        kind=assertion.kind.value,
        path=assertion.path,
        comparator=assertion.comparator,
        expected_value=assertion.expected_value,
        expected_schema=assertion.expected_schema,
        threshold=assertion.threshold,
        severity=assertion.severity,
        description=assertion.description,
    )


async def _run_response(
    repository: AgentTestRepository,
    run: AgentTestRun,
) -> AgentTestRunResponse:
    steps = await repository.list_run_steps(run.agent_test_run_id)
    return AgentTestRunResponse(
        run_id=run.agent_test_run_id,
        tenant_id=run.tenant_id,
        suite_id=run.agent_test_suite_id,
        target_type=run.target_type.value,
        target_id=run.target_id,
        target_version=run.target_version,
        safe_mode=run.safe_mode.value,
        status=run.status.value,
        pass_status=run.pass_status,
        trace_id=run.trace_id,
        usage_summary=run.usage_summary,
        latency_ms=run.latency_ms,
        redaction_summary=run.redaction_summary,
        artifact_summary=run.artifact_summary,
        blocked_side_effect_count=run.blocked_side_effect_count,
        failure_summary=run.failure_summary,
        steps=[_step_response(step) for step in steps],
    )


def _step_response(step: AgentTestRunStep) -> AgentTestRunStepResponse:
    return AgentTestRunStepResponse(
        step_id=step.agent_test_run_step_id,
        run_id=step.agent_test_run_id,
        case_id=step.agent_test_case_id,
        step_name=step.step_name,
        status=step.status.value,
        sequence=step.sequence,
        model_provider=step.model_provider,
        model_id=step.model_id,
        prompt_version_id=step.prompt_version_id,
        profile_version_id=step.profile_version_id,
        skill_version_refs=step.skill_version_refs,
        workflow_version_ref=step.workflow_version_ref,
        latency_ms=step.latency_ms,
        token_usage=step.token_usage,
        contract_validation=step.contract_validation,
        assertion_results=step.assertion_results,
        blocked_side_effects=step.blocked_side_effects,
        redacted_transcript=step.redacted_transcript,
        artifact_refs=step.artifact_refs,
        failure_reason=step.failure_reason,
    )
