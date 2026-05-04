from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from uuid import UUID, uuid4

from multi_agent_platform.db.models.agent_tests import (
    AgentTestAssertion,
    AgentTestAssertionKind,
    AgentTestCase,
    AgentTestPublicationRequirement,
    AgentTestRun,
    AgentTestRunStatus,
    AgentTestRunStep,
    AgentTestSafeMode,
    AgentTestStatus,
    AgentTestSuite,
    AgentTestTargetType,
)
from multi_agent_platform.db.repositories.agent_tests import AgentTestRepository
from multi_agent_platform.testing.agent_bench.models import (
    AgentBenchSafeMode,
    RequiredSuiteEvidenceRequest,
    SuiteEvidenceItem,
    SuiteEvidenceSummary,
)
from multi_agent_platform.testing.agent_bench.redaction import safe_fixture_summary
from multi_agent_platform.testing.agent_bench.sandbox import (
    AgentBenchSandbox,
    AgentBenchSandboxError,
)


class AgentTestBenchError(RuntimeError):
    def __init__(self, message: str, *, status_code: int = 400) -> None:
        super().__init__(message)
        self.status_code = status_code


class AgentTestBenchService:
    def __init__(
        self,
        repository: AgentTestRepository,
        *,
        sandbox: AgentBenchSandbox | None = None,
    ) -> None:
        self.repository = repository
        self.sandbox = sandbox or AgentBenchSandbox()

    async def create_suite(
        self,
        *,
        tenant_id: UUID,
        name: str,
        target_type: str,
        target_id: str,
        actor_principal_id: str,
        description: str | None = None,
        target_version: str | None = None,
        default_safe_mode: str = "mock_model",
        model_mode: str = "mock",
        tool_mode: str = "mock",
        pass_threshold: float = 1.0,
        required_for_publish: bool = False,
    ) -> AgentTestSuite:
        suite = AgentTestSuite(
            tenant_id=tenant_id,
            name=name,
            description=description,
            target_type=AgentTestTargetType(target_type),
            target_id=target_id,
            target_version=target_version,
            default_safe_mode=AgentTestSafeMode(default_safe_mode),
            model_mode=model_mode,
            tool_mode=tool_mode,
            pass_threshold=pass_threshold,
            is_required_for_publish=required_for_publish,
            created_by_principal_id=actor_principal_id,
        )
        suite = await self.repository.add_suite(suite)
        if required_for_publish:
            await self.repository.add_publication_requirement(
                AgentTestPublicationRequirement(
                    tenant_id=tenant_id,
                    target_type=AgentTestTargetType(target_type),
                    target_id=target_id,
                    agent_test_suite_id=suite.agent_test_suite_id,
                    created_by_principal_id=actor_principal_id,
                )
            )
        return suite

    async def update_suite(
        self,
        *,
        suite_id: UUID,
        tenant_id: UUID,
        expected_revision: int,
        name: str,
        description: str | None,
        target_version: str | None,
        default_safe_mode: str,
        model_mode: str,
        tool_mode: str,
        pass_threshold: float,
        required_for_publish: bool,
    ) -> AgentTestSuite:
        suite = await self.repository.require_suite_revision(
            suite_id=suite_id,
            tenant_id=tenant_id,
            expected_revision=expected_revision,
        )
        suite.name = name
        suite.description = description
        suite.target_version = target_version
        suite.default_safe_mode = AgentTestSafeMode(default_safe_mode)
        suite.model_mode = model_mode
        suite.tool_mode = tool_mode
        suite.pass_threshold = pass_threshold
        suite.is_required_for_publish = required_for_publish
        suite.revision += 1
        return suite

    async def create_case(
        self,
        *,
        suite_id: UUID,
        tenant_id: UUID,
        name: str,
        actor_principal_id: str,
        description: str | None = None,
        fixture: dict[str, object] | None = None,
        expected_contract_shape: dict[str, object] | None = None,
        assertions: list[dict[str, object]] | None = None,
        evaluator_prompt_ref: str | None = None,
        model_mode: str = "inherit",
        tool_mode: str = "inherit",
        pass_threshold: float = 1.0,
        case_order: int = 0,
    ) -> AgentTestCase:
        suite = await self.repository.get_suite_for_tenant(
            suite_id=suite_id,
            tenant_id=tenant_id,
        )
        if suite is None:
            raise AgentTestBenchError("agent test suite not found", status_code=404)
        _ = actor_principal_id
        case = await self.repository.add_case(
            AgentTestCase(
                agent_test_suite_id=suite_id,
                tenant_id=tenant_id,
                name=name,
                description=description,
                fixture_summary=safe_fixture_summary(fixture or {}),
                expected_contract_shape=expected_contract_shape or {},
                evaluator_prompt_ref=evaluator_prompt_ref,
                model_mode=model_mode,
                tool_mode=tool_mode,
                pass_threshold=pass_threshold,
                case_order=case_order,
            )
        )
        for assertion in assertions or []:
            await self.repository.add_assertion(
                AgentTestAssertion(
                    agent_test_case_id=case.agent_test_case_id,
                    tenant_id=tenant_id,
                    kind=AgentTestAssertionKind(
                        str(assertion.get("kind") or "deterministic")
                    ),
                    path=assertion.get("path")
                    if isinstance(assertion.get("path"), str)
                    else None,
                    comparator=assertion.get("comparator")
                    if isinstance(assertion.get("comparator"), str)
                    else None,
                    expected_value=assertion.get("expected_value"),
                    expected_schema=(
                        assertion.get("expected_schema")
                        if isinstance(assertion.get("expected_schema"), dict)
                        else {}
                    ),
                    threshold=_optional_float(assertion.get("threshold")),
                    severity=str(assertion.get("severity") or "blocking"),
                    weight=_float_or_default(assertion.get("weight"), 1.0),
                    description=assertion.get("description")
                    if isinstance(assertion.get("description"), str)
                    else None,
                )
            )
        return case

    async def launch_run(
        self,
        *,
        suite_id: UUID,
        tenant_id: UUID,
        actor_principal_id: str,
        safe_mode: str,
        target_version: str | None,
        idempotency_key: str | None,
        trace_id: str | None,
        approved_probe_reference: str | None = None,
    ) -> AgentTestRun:
        suite = await self.repository.get_suite_for_tenant(
            suite_id=suite_id,
            tenant_id=tenant_id,
        )
        if suite is None:
            raise AgentTestBenchError("agent test suite not found", status_code=404)
        if suite.status is AgentTestStatus.ARCHIVED:
            raise AgentTestBenchError("archived test suites cannot be run")
        run_idempotency = idempotency_key or f"agent-test:{suite_id}:{uuid4()}"
        existing = await self.repository.get_run_by_idempotency_key(
            tenant_id=tenant_id,
            idempotency_key=run_idempotency,
        )
        if existing is not None:
            return existing
        cases = await self.repository.list_cases_for_suite(suite_id)
        if not cases:
            raise AgentTestBenchError("test suite has no active cases")
        case_inputs = [
            (
                case,
                await self.repository.list_assertions_for_case(case.agent_test_case_id),
            )
            for case in cases
        ]
        run = await self.repository.add_run(
            AgentTestRun(
                tenant_id=tenant_id,
                agent_test_suite_id=suite_id,
                target_type=suite.target_type,
                target_id=suite.target_id,
                target_version=target_version or suite.target_version,
                safe_mode=AgentTestSafeMode(safe_mode),
                status=AgentTestRunStatus.RUNNING,
                pass_status="running",
                triggered_by_principal_id=actor_principal_id,
                idempotency_key=run_idempotency,
                trace_id=trace_id,
                started_at=datetime.now(UTC),
            )
        )
        try:
            result = self.sandbox.execute(
                safe_mode=AgentBenchSafeMode(safe_mode),
                cases=case_inputs,
                target_version=run.target_version,
                approved_probe_reference=approved_probe_reference,
            )
        except AgentBenchSandboxError as exc:
            run.status = AgentTestRunStatus.BLOCKED
            run.pass_status = "blocked"
            run.failure_summary = str(exc)
            run.completed_at = datetime.now(UTC)
            return run

        run.status = AgentTestRunStatus(result.status.value)
        run.pass_status = result.pass_status.value
        run.usage_summary = result.usage_summary
        run.latency_ms = result.latency_ms
        run.redaction_summary = result.redaction_summary
        run.artifact_summary = result.artifact_summary
        run.blocked_side_effect_count = result.blocked_side_effect_count
        run.failure_summary = result.failure_summary
        run.completed_at = datetime.now(UTC)
        for step in result.steps:
            await self.repository.add_run_step(
                AgentTestRunStep(
                    agent_test_run_id=run.agent_test_run_id,
                    tenant_id=tenant_id,
                    agent_test_case_id=step.case_id,
                    step_name=step.step_name,
                    status=AgentTestRunStatus(step.status.value),
                    sequence=step.sequence,
                    model_provider=step.model_provider,
                    model_id=step.model_id,
                    prompt_version_id=step.prompt_version_id,
                    profile_version_id=step.profile_version_id,
                    skill_version_refs=step.skill_version_refs,
                    workflow_version_ref=step.workflow_version_ref,
                    latency_ms=step.latency_ms,
                    token_usage=step.token_usage,
                    contract_validation=step.contract_validation.model_dump(
                        mode="json"
                    ),
                    assertion_results=[
                        item.model_dump(mode="json") for item in step.assertion_results
                    ],
                    blocked_side_effects=[
                        item.model_dump(mode="json")
                        for item in step.blocked_side_effects
                    ],
                    redacted_transcript=step.redacted_transcript,
                    artifact_refs=step.artifact_refs,
                    failure_reason=step.failure_reason,
                )
            )
        return run

    async def evidence_summary(
        self,
        *,
        tenant_id: UUID,
        target_type: str,
        target_id: str,
        target_version: str | None,
    ) -> SuiteEvidenceSummary:
        requirements = await self.repository.list_publication_requirements(
            tenant_id=tenant_id,
            target_type=target_type,
            target_id=target_id,
        )
        summary = SuiteEvidenceSummary(required_count=len(requirements))
        for requirement in requirements:
            suite_id = requirement.agent_test_suite_id
            summary.required_suite_ids.append(str(suite_id))
            run = await self.repository.latest_passing_run_for_suite(
                suite_id=suite_id,
                tenant_id=tenant_id,
                target_version=target_version,
            )
            if run is None:
                summary.missing_count += 1
            else:
                summary.passing_count += 1
                summary.passing_run_ids.append(str(run.agent_test_run_id))
        return summary

    async def evidence_summary_for_required_suites(
        self,
        *,
        tenant_id: UUID,
        target_type: str,
        target_id: str,
        target_version: str | None,
        requirements: list[RequiredSuiteEvidenceRequest],
    ) -> SuiteEvidenceSummary:
        summary = SuiteEvidenceSummary(required_count=len(requirements))
        for requirement in requirements:
            item = await self._required_suite_evidence_item(
                tenant_id=tenant_id,
                target_type=target_type,
                target_id=target_id,
                target_version=target_version,
                requirement=requirement,
            )
            _add_evidence_item(summary, item)
        return summary

    async def _required_suite_evidence_item(
        self,
        *,
        tenant_id: UUID,
        target_type: str,
        target_id: str,
        target_version: str | None,
        requirement: RequiredSuiteEvidenceRequest,
    ) -> SuiteEvidenceItem:
        try:
            suite_id = UUID(requirement.suite_id)
        except ValueError:
            return _evidence_item(
                requirement=requirement,
                status="missing",
                target_type=target_type,
                target_id=target_id,
                target_version=target_version,
                safe_summary=(
                    "Required test evidence is unavailable for the current "
                    "workflow revision."
                ),
            )

        suite = await self.repository.get_suite_for_tenant(
            suite_id=suite_id,
            tenant_id=tenant_id,
        )
        if (
            suite is None
            or _status_value(suite.status) == AgentTestStatus.ARCHIVED.value
        ):
            return _evidence_item(
                requirement=requirement,
                status="missing",
                target_type=target_type,
                target_id=target_id,
                target_version=target_version,
                safe_summary=(
                    "Required test evidence is unavailable for the current "
                    "workflow revision."
                ),
            )

        if suite.target_type.value != target_type or suite.target_id != target_id:
            return _evidence_item(
                requirement=requirement,
                status="stale",
                target_type=target_type,
                target_id=target_id,
                target_version=target_version,
                safe_summary=(
                    "Required test suite evidence targets a different workflow."
                ),
            )

        latest_current_run = await self.repository.latest_run_for_suite(
            suite_id=suite_id,
            tenant_id=tenant_id,
            target_type=target_type,
            target_id=target_id,
            target_version=target_version,
            match_target_version=True,
        )
        if latest_current_run is not None:
            if (
                _status_value(latest_current_run.status)
                == AgentTestRunStatus.PASSED.value
            ):
                return _evidence_item(
                    requirement=requirement,
                    status="passed",
                    target_type=target_type,
                    target_id=target_id,
                    target_version=target_version,
                    evidence_run_id=str(latest_current_run.agent_test_run_id),
                    evidence_target_version=latest_current_run.target_version,
                    safe_summary=(
                        "Required test evidence is passing for the current "
                        "workflow revision."
                    ),
                    blocking=False,
                )
            return _evidence_item(
                requirement=requirement,
                status="failed",
                target_type=target_type,
                target_id=target_id,
                target_version=target_version,
                evidence_run_id=str(latest_current_run.agent_test_run_id),
                evidence_target_version=latest_current_run.target_version,
                safe_summary=(
                    "Required test evidence exists for the current workflow "
                    "revision but is not passing."
                ),
            )

        latest_target_run = await self.repository.latest_run_for_suite(
            suite_id=suite_id,
            tenant_id=tenant_id,
            target_type=target_type,
            target_id=target_id,
        )
        if latest_target_run is not None:
            return _evidence_item(
                requirement=requirement,
                status="stale",
                target_type=target_type,
                target_id=target_id,
                target_version=target_version,
                evidence_run_id=str(latest_target_run.agent_test_run_id),
                evidence_target_version=latest_target_run.target_version,
                safe_summary=(
                    "A test run exists, but not for the current workflow revision."
                ),
            )

        return _evidence_item(
            requirement=requirement,
            status="missing",
            target_type=target_type,
            target_id=target_id,
            target_version=target_version,
            safe_summary=(
                "Required test evidence is missing for the current workflow revision."
            ),
        )


def _optional_float(value: object) -> float | None:
    if value is None:
        return None
    return float(str(value))


def _float_or_default(value: object, default: float) -> float:
    if value is None:
        return default
    return float(str(value))


def _status_value(value: object) -> str:
    if isinstance(value, Enum):
        return str(value.value)
    text = str(value)
    if "." in text:
        text = text.rsplit(".", maxsplit=1)[-1]
    return text.lower()


def _evidence_item(
    *,
    requirement: RequiredSuiteEvidenceRequest,
    status: str,
    target_type: str,
    target_id: str,
    target_version: str | None,
    safe_summary: str,
    blocking: bool = True,
    evidence_run_id: str | None = None,
    evidence_target_version: str | None = None,
) -> SuiteEvidenceItem:
    return SuiteEvidenceItem(
        requirement_key=requirement.requirement_key,
        suite_id=requirement.suite_id,
        status=status,
        blocking=blocking,
        target_type=target_type,
        target_id=target_id,
        target_version=target_version,
        evidence_run_id=evidence_run_id,
        evidence_target_version=evidence_target_version,
        safe_summary=safe_summary,
        freshness_policy=requirement.freshness_policy,
        field_path=requirement.field_path,
    )


def _add_evidence_item(
    summary: SuiteEvidenceSummary,
    item: SuiteEvidenceItem,
) -> None:
    summary.evidence.append(item)
    summary.required_suite_ids.append(item.suite_id)
    if item.status == "passed":
        summary.passing_count += 1
        if item.evidence_run_id is not None:
            summary.passing_run_ids.append(item.evidence_run_id)
    elif item.status == "failed":
        summary.failing_count += 1
    elif item.status == "stale":
        summary.stale_count += 1
        if item.evidence_run_id is not None:
            summary.stale_run_ids.append(item.evidence_run_id)
    else:
        summary.missing_count += 1
