from __future__ import annotations

from time import perf_counter
from uuid import UUID

from multi_agent_platform.skill_execution.adapters import (
    DAILY_BRIEFING_TOOL_NAMES,
    SkillToolAdapter,
    default_adapter_registry,
)
from multi_agent_platform.skill_execution.policies import (
    SkillExecutionPolicyBundle,
    evaluate_skill_execution_policy,
)
from multi_agent_platform.skill_execution.redaction import (
    redact_payload,
    redact_text,
)
from multi_agent_platform.skill_execution.schemas import (
    DiagnosticReadiness,
    ExecutionMode,
    ExecutionStatus,
    SkillToolDiagnosticRecord,
    SkillToolExecutionRequest,
    SkillToolExecutionResult,
)


class SkillExecutionGateway:
    def __init__(
        self,
        *,
        adapters: dict[str, SkillToolAdapter] | None = None,
        policy_bundle: SkillExecutionPolicyBundle | None = None,
    ) -> None:
        self.adapters = adapters or default_adapter_registry()
        self.policy_bundle = policy_bundle
        self._history: list[SkillToolExecutionResult] = []

    async def execute(
        self,
        request: SkillToolExecutionRequest,
    ) -> SkillToolExecutionResult:
        started = perf_counter()
        adapter = self.adapters.get(request.tool_name)
        policy = self.policy_bundle or SkillExecutionPolicyBundle.local_qa_default(
            tenant_id=request.tenant_id
        )
        evaluation = evaluate_skill_execution_policy(
            request=request,
            adapter=adapter,
            adapter_skill_package=adapter.skill_package if adapter else None,
            adapter_domains=adapter.allowed_domains if adapter else (),
            adapter_read_only=adapter.read_only if adapter else False,
            adapter_credential_kind=adapter.required_credential_kind
            if adapter
            else None,
            policy_bundle=policy,
        )
        if not evaluation.allowed or adapter is None:
            result = SkillToolExecutionResult(
                status=ExecutionStatus.DENIED,
                tool_name=request.tool_name,
                execution_mode=request.execution_mode,
                output={},
                request_summary=_request_summary(request),
                response_summary=redact_text(
                    evaluation.error_message or "Tool execution was denied."
                ),
                policy_decisions=evaluation.decisions,
                credential_summary=evaluation.credential_summary,
                latency_ms=_elapsed_ms(started),
                error_code=evaluation.error_code or "tool_denied",
                error_message=redact_text(
                    evaluation.error_message or "Tool execution was denied."
                ),
            )
            self._history.append(result)
            return result

        try:
            adapter_result = await adapter.execute(request)
        except Exception as exc:
            result = SkillToolExecutionResult(
                status=ExecutionStatus.FAILED,
                tool_name=request.tool_name,
                execution_mode=request.execution_mode,
                output={},
                request_summary=_request_summary(request),
                response_summary="Adapter execution failed with safe error details.",
                policy_decisions=evaluation.decisions,
                credential_summary=evaluation.credential_summary,
                latency_ms=_elapsed_ms(started),
                error_code=exc.__class__.__name__,
                error_message="Adapter execution failed.",
            )
            self._history.append(result)
            return result

        safe_output = redact_payload(adapter_result.output)
        result = SkillToolExecutionResult(
            status=ExecutionStatus.SUCCEEDED,
            tool_name=request.tool_name,
            execution_mode=request.execution_mode,
            output=safe_output if isinstance(safe_output, dict) else {},
            request_summary=_request_summary(request),
            response_summary=redact_text(adapter_result.response_summary),
            policy_decisions=evaluation.decisions,
            credential_summary=evaluation.credential_summary,
            artifact_refs=adapter_result.artifact_refs,
            latency_ms=_elapsed_ms(started),
        )
        self._history.append(result)
        return result

    async def run_mock_diagnostics(
        self,
        *,
        tenant_id: str | UUID,
        actor_id: str,
        tool_names: tuple[str, ...] | None = None,
    ) -> tuple[SkillToolExecutionResult, ...]:
        tenant_uuid = UUID(str(tenant_id))
        selected = tool_names or DAILY_BRIEFING_TOOL_NAMES
        results: list[SkillToolExecutionResult] = []
        for tool_name in selected:
            adapter = self.adapters[tool_name]
            results.append(
                await self.execute(
                    SkillToolExecutionRequest(
                        tenant_id=tenant_uuid,
                        actor_id=actor_id,
                        skill_package=adapter.skill_package,
                        skill_version="1.0.0",
                        tool_name=tool_name,
                        execution_mode=ExecutionMode.MOCK,
                        input={
                            "date": "2026-05-04",
                            "location": "Providence",
                            "query": "AI infrastructure",
                            "origin_label": "Home",
                            "destination_label": "Downtown office",
                        },
                    )
                )
            )
        return tuple(results)

    def diagnostic_records(self) -> tuple[SkillToolDiagnosticRecord, ...]:
        latest_by_tool = {result.tool_name: result for result in self._history}
        records: list[SkillToolDiagnosticRecord] = []
        for tool_name in DAILY_BRIEFING_TOOL_NAMES:
            adapter = self.adapters[tool_name]
            latest = latest_by_tool.get(tool_name)
            records.append(
                SkillToolDiagnosticRecord(
                    tool_name=tool_name,
                    display_name=adapter.display_name,
                    mode=latest.execution_mode if latest else ExecutionMode.MOCK,
                    readiness=_readiness(latest),
                    requires_credential=bool(adapter.required_credential_kind),
                    allowed_domains=adapter.allowed_domains,
                    latest_status=latest.status if latest else None,
                    latest_summary=latest.response_summary if latest else None,
                    latest_denial=latest.error_message
                    if latest and latest.status is not ExecutionStatus.SUCCEEDED
                    else None,
                )
            )
        return tuple(records)

    def adapter_invocation_count(self, tool_name: str) -> int:
        adapter = self.adapters.get(tool_name)
        return adapter.invocation_count if adapter is not None else 0


def _elapsed_ms(started: float) -> int:
    return max(0, round((perf_counter() - started) * 1000))


def _request_summary(request: SkillToolExecutionRequest) -> str:
    input_keys = ", ".join(sorted(request.input)) or "none"
    return redact_text(
        f"{request.tool_name} requested in {request.execution_mode.value} mode "
        f"for tenant {request.tenant_id}; input keys: {input_keys}."
    )


def _readiness(result: SkillToolExecutionResult | None) -> DiagnosticReadiness:
    if result is None:
        return DiagnosticReadiness.NOT_CONFIGURED
    if result.status is ExecutionStatus.SUCCEEDED:
        return DiagnosticReadiness.READY
    return DiagnosticReadiness.BLOCKED
