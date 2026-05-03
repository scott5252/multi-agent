from __future__ import annotations

from datetime import UTC, datetime
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


def _optional_float(value: object) -> float | None:
    if value is None:
        return None
    return float(str(value))


def _float_or_default(value: object, default: float) -> float:
    if value is None:
        return default
    return float(str(value))
