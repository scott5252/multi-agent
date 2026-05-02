from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from multi_agent_platform.db.models.agent_tests import AgentTestAssertion, AgentTestCase
from multi_agent_platform.testing.agent_bench.assertions import (
    evaluate_deterministic_assertion,
    evaluate_evaluator_assertion,
)
from multi_agent_platform.testing.agent_bench.models import (
    AgentBenchPassStatus,
    AgentBenchRunStatus,
    AgentBenchSafeMode,
    AssertionComparator,
    AssertionKind,
    BlockedSideEffect,
    ContractValidationResult,
    SandboxRunResult,
    SandboxStepResult,
)
from multi_agent_platform.testing.agent_bench.redaction import safe_transcript_summary


class AgentBenchSandboxError(RuntimeError):
    pass


class AgentBenchSandbox:
    def execute(
        self,
        *,
        safe_mode: AgentBenchSafeMode,
        cases: Sequence[tuple[AgentTestCase, Sequence[AgentTestAssertion]]],
        target_version: str | None,
        approved_probe_reference: str | None = None,
    ) -> SandboxRunResult:
        if (
            safe_mode is AgentBenchSafeMode.APPROVED_REAL_PROBE
            and not approved_probe_reference
        ):
            raise AgentBenchSandboxError(
                "approved real dependency probe requires approved probe metadata"
            )

        steps: list[SandboxStepResult] = []
        for index, (case, assertions) in enumerate(cases, start=1):
            output = _mock_output(case, target_version=target_version)
            contract = _validate_contract(output, case.expected_contract_shape)
            assertion_results = []
            for assertion in assertions:
                if str(assertion.kind.value) == AssertionKind.EVALUATOR.value:
                    assertion_results.append(
                        evaluate_evaluator_assertion(
                            assertion_id=str(assertion.agent_test_assertion_id),
                            score=0.95 if contract.passed else 0.2,
                            threshold=assertion.threshold or 0.8,
                            rationale=(
                                "Evaluator accepted redacted answer"
                                if contract.passed
                                else "Evaluator rejected redacted answer"
                            ),
                            severity=assertion.severity or "blocking",
                        )
                    )
                    continue
                comparator = AssertionComparator(assertion.comparator or "equals")
                assertion_results.append(
                    evaluate_deterministic_assertion(
                        assertion_id=str(assertion.agent_test_assertion_id),
                        comparator=comparator,
                        output=output,
                        path=assertion.path,
                        expected_value=assertion.expected_value,
                        expected_schema=assertion.expected_schema,
                        threshold=assertion.threshold,
                        severity=assertion.severity or "blocking",
                    )
                )
            blocking_failures = [
                result
                for result in assertion_results
                if not result.passed and result.severity == "blocking"
            ]
            blocked_side_effects = _blocked_side_effects(safe_mode)
            status = (
                AgentBenchRunStatus.PASSED
                if contract.passed and not blocking_failures
                else AgentBenchRunStatus.FAILED
            )
            transcript: list[Mapping[str, Any]] = [
                {"role": "system", "content": "Safe agent workflow test bench run."},
                {
                    "role": "user",
                    "content": case.fixture_summary.get("preview", {}),
                },
                {"role": "assistant", "content": output},
            ]
            steps.append(
                SandboxStepResult(
                    case_id=case.agent_test_case_id,
                    step_name=case.name,
                    status=status,
                    sequence=index,
                    model_provider=(
                        "mocked-gateway"
                        if safe_mode
                        is AgentBenchSafeMode.REAL_MODEL_SIDE_EFFECTS_DISABLED
                        else "mock"
                    ),
                    model_id=(
                        "gateway-mocked-test-model"
                        if safe_mode
                        is AgentBenchSafeMode.REAL_MODEL_SIDE_EFFECTS_DISABLED
                        else "mock-model"
                    ),
                    prompt_version_id=case.evaluator_prompt_ref,
                    profile_version_id=None,
                    skill_version_refs=["skill:test-bench:1.0"],
                    workflow_version_ref=target_version,
                    latency_ms=25 + index,
                    token_usage={
                        "prompt_tokens": 12,
                        "completion_tokens": 18,
                        "total_tokens": 30,
                        "test_mode": 1,
                    },
                    contract_validation=contract,
                    assertion_results=assertion_results,
                    blocked_side_effects=blocked_side_effects,
                    redacted_transcript=safe_transcript_summary(transcript),
                    artifact_refs=[],
                    failure_reason=(
                        None
                        if status is AgentBenchRunStatus.PASSED
                        else "One or more assertions or contract checks failed"
                    ),
                )
            )

        passed = all(step.status is AgentBenchRunStatus.PASSED for step in steps)
        total_tokens = sum(
            int(step.token_usage.get("total_tokens", 0)) for step in steps
        )
        blocked_count = sum(len(step.blocked_side_effects) for step in steps)
        return SandboxRunResult(
            status=AgentBenchRunStatus.PASSED if passed else AgentBenchRunStatus.FAILED,
            pass_status=AgentBenchPassStatus.PASSED
            if passed
            else AgentBenchPassStatus.FAILED,
            usage_summary={"total_tokens": total_tokens, "test_mode": 1},
            latency_ms=sum(step.latency_ms for step in steps),
            redaction_summary={
                "transcripts_redacted": len(steps),
                "raw_secret_values": 0,
                "raw_prompt_bodies": 0,
            },
            artifact_summary={"artifact_count": 0, "storage": "metadata-only"},
            blocked_side_effect_count=blocked_count,
            failure_summary=None if passed else "At least one test case failed",
            steps=steps,
        )


def _mock_output(
    case: AgentTestCase,
    *,
    target_version: str | None,
) -> dict[str, Any]:
    preview = case.fixture_summary.get("preview", {})
    request_text = ""
    if isinstance(preview, Mapping):
        request_text = str(preview.get("request", "intake"))
    return {
        "status": "passed",
        "contract": {
            "summary": f"safe intake summary for {request_text}",
            "target_version": target_version or "current",
        },
        "latency_ms": 25,
        "usage": {"total_tokens": 30},
    }


def _validate_contract(
    output: Mapping[str, Any],
    expected_shape: Mapping[str, Any],
) -> ContractValidationResult:
    if not expected_shape:
        return ContractValidationResult(
            passed=True,
            expected_shape={},
            actual_shape={"keys": sorted(output)},
        )
    failures: list[str] = []
    for key in expected_shape:
        if key not in output:
            failures.append(f"Missing contract field: {key}")
    return ContractValidationResult(
        passed=not failures,
        expected_shape=dict(expected_shape),
        actual_shape={"keys": sorted(output)},
        failures=failures,
    )


def _blocked_side_effects(safe_mode: AgentBenchSafeMode) -> list[BlockedSideEffect]:
    if safe_mode in {
        AgentBenchSafeMode.MOCK_TOOLS,
        AgentBenchSafeMode.REAL_MODEL_SIDE_EFFECTS_DISABLED,
    }:
        return [
            BlockedSideEffect(
                tool_name="external_dependency.write",
                reason="safe mode disables external side effects",
                safe_summary={"mode": safe_mode.value},
            )
        ]
    return []
