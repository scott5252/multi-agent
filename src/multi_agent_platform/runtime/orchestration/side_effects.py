from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from multi_agent_platform.runtime.orchestration.contracts import sha256_digest
from multi_agent_platform.runtime.orchestration.models import now_utc


class SideEffectStatus(StrEnum):
    PLANNED = "planned"
    EXECUTING = "executing"
    APPLIED = "applied"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"
    CANCELLED = "cancelled"


class SideEffectKind(StrEnum):
    TOOL_CALL = "tool_call"
    MODEL_GATEWAY_CALL = "model_gateway_call"
    HTTP_REQUEST = "http_request"
    FILE_WRITE = "file_write"
    EMAIL = "email"
    OBJECT_STORAGE_WRITE = "object_storage_write"
    DELEGATED_ACTION = "delegated_action"
    COMPENSATION = "compensation"


class SideEffectRepeatability(StrEnum):
    REPEATABLE = "repeatable"
    NON_REPEATABLE = "non_repeatable"
    COMPENSATABLE = "compensatable"
    UNKNOWN = "unknown"


def make_idempotency_key(
    *,
    tenant_id: UUID | None,
    workflow_run_id: UUID,
    run_step_id: UUID,
    bundle_digest: str,
    operation_kind: str,
    attempt: int,
) -> str:
    return sha256_digest(
        {
            "tenant_id": str(tenant_id) if tenant_id else None,
            "workflow_run_id": str(workflow_run_id),
            "run_step_id": str(run_step_id),
            "bundle_digest": bundle_digest,
            "operation_kind": operation_kind,
            "attempt": attempt,
        }
    )


@dataclass(slots=True)
class SideEffectIntent:
    tenant_id: UUID | None
    workflow_run_id: UUID
    run_step_id: UUID
    intent_kind: SideEffectKind
    idempotency_key: str
    tool_policy_ref: str
    delegated_credential_ref: str | None = None
    request_ref: dict[str, object] | None = None
    result_ref: dict[str, object] | None = None
    error_ref: dict[str, object] | None = None
    compensation_hook_ref: str | None = None
    trace_id: str | None = None
    operation_identity: str | None = None
    side_effect_boundary: str | None = None
    repeatability: SideEffectRepeatability = SideEffectRepeatability.NON_REPEATABLE
    side_effect_intent_id: UUID = field(default_factory=uuid4)
    status: SideEffectStatus = SideEffectStatus.PLANNED
    created_at: datetime = field(default_factory=now_utc)
    executed_at: datetime | None = None
    updated_at: datetime = field(default_factory=now_utc)

    def begin(self) -> None:
        if self.status is not SideEffectStatus.PLANNED:
            raise ValueError("only planned side effects can execute")
        self.status = SideEffectStatus.EXECUTING
        self.updated_at = now_utc()

    def mark_applied(self, result_ref: dict[str, object]) -> None:
        self.status = SideEffectStatus.APPLIED
        self.result_ref = result_ref
        self.executed_at = now_utc()
        self.updated_at = self.executed_at

    def reuse_applied_result(self) -> dict[str, object] | None:
        if self.status is SideEffectStatus.APPLIED:
            return self.result_ref
        return None


def build_authorized_tool_intent(
    *,
    tenant_id: UUID | None,
    workflow_run_id: UUID,
    run_step_id: UUID,
    bundle_digest: str,
    tool_policy_ref: str,
    policy_outcome: str,
    delegated_credential_ref: str | None = None,
    request_ref: dict[str, object] | None = None,
    attempt: int = 1,
) -> SideEffectIntent:
    if policy_outcome != "allow":
        raise PermissionError("tool side effect cannot start before allow decision")
    return SideEffectIntent(
        tenant_id=tenant_id,
        workflow_run_id=workflow_run_id,
        run_step_id=run_step_id,
        intent_kind=SideEffectKind.TOOL_CALL,
        idempotency_key=make_idempotency_key(
            tenant_id=tenant_id,
            workflow_run_id=workflow_run_id,
            run_step_id=run_step_id,
            bundle_digest=bundle_digest,
            operation_kind="tool_call",
            attempt=attempt,
        ),
        tool_policy_ref=tool_policy_ref,
        delegated_credential_ref=delegated_credential_ref,
        request_ref=request_ref,
    )


def build_model_gateway_intent(
    *,
    tenant_id: UUID | None,
    workflow_run_id: UUID,
    run_step_id: UUID,
    bundle_digest: str,
    model_provider_entry_id: UUID,
    trace_id: str | None = None,
    operation_identity: str | None = None,
    side_effect_boundary: str = "before_provider_invocation",
    attempt: int = 1,
) -> SideEffectIntent:
    return SideEffectIntent(
        tenant_id=tenant_id,
        workflow_run_id=workflow_run_id,
        run_step_id=run_step_id,
        intent_kind=SideEffectKind.MODEL_GATEWAY_CALL,
        idempotency_key=make_idempotency_key(
            tenant_id=tenant_id,
            workflow_run_id=workflow_run_id,
            run_step_id=run_step_id,
            bundle_digest=bundle_digest,
            operation_kind="model_gateway_call",
            attempt=attempt,
        ),
        tool_policy_ref=f"model-provider:{model_provider_entry_id}",
        repeatability=SideEffectRepeatability.UNKNOWN,
        request_ref={"model_provider_entry_id": str(model_provider_entry_id)},
        trace_id=trace_id,
        operation_identity=operation_identity,
        side_effect_boundary=side_effect_boundary,
    )


def mark_for_compensation(
    intent: SideEffectIntent, *, error_ref: dict[str, object]
) -> None:
    intent.status = SideEffectStatus.COMPENSATING
    intent.error_ref = error_ref
    intent.updated_at = now_utc()


def recovery_safety_outcome(intent: SideEffectIntent) -> str:
    if intent.status is SideEffectStatus.APPLIED:
        return "duplicate_suppressed"
    if intent.repeatability is SideEffectRepeatability.REPEATABLE:
        return "repeatable"
    if (
        intent.repeatability is SideEffectRepeatability.COMPENSATABLE
        and intent.compensation_hook_ref
    ):
        return "compensation_requested"
    return "operator_intervention_required"


def tool_usage_audit_summary(intent: SideEffectIntent) -> dict[str, object]:
    return {
        "tool_id": intent.tool_policy_ref,
        "action_category": intent.intent_kind.value,
        "policy_outcome": "allow",
        "execution_outcome": intent.status.value,
        "has_delegated_credential": intent.delegated_credential_ref is not None,
        "request_field_count": len(intent.request_ref or {}),
        "result_field_count": len(intent.result_ref or {}),
    }
