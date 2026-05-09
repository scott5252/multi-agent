from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol
from uuid import UUID

from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.config.service import (
    ModelSkillConfigService,
    ModelSkillServiceError,
    ModelStepResolutionRequest,
)
from multi_agent_platform.model_providers.gateway import ModelGateway
from multi_agent_platform.model_providers.models import GatewayResult, TestOutcome
from multi_agent_platform.runtime.orchestration.graph_redaction import (
    contains_sensitive_key,
    graph_payload_digest,
    redact_graph_value,
)
from multi_agent_platform.runtime.orchestration.graph_roles import (
    DeterministicRoleNodeExecutor,
    RoleExecutionContext,
    RoleExecutionResult,
    RoleNodeExecutor,
)
from multi_agent_platform.runtime.orchestration.role_output_contracts import (
    RoleOutputContractError,
    json_bytes,
    parse_model_output_content,
    validate_role_output,
)
from multi_agent_platform.runtime.versioning import build_gateway_context_from_pins
from multi_agent_platform.storage.base import StorageProvider, build_artifact_key

MODEL_BACKED_EXECUTION_MODES = frozenset(
    {"model_gateway", "mock_model_gateway", "model_backed"}
)


@dataclass(slots=True, frozen=True)
class ResolvedModelBackedRolePins:
    provider_connection_id: UUID
    model_id: str
    model_provider_key: str
    model_routing_version_id: UUID
    prompt_reference_version_id: UUID
    prompt_version_id: UUID
    prompt_digest: str
    agent_profile_version_id: UUID
    evaluated_version_ids: tuple[UUID, ...]
    safe_reason: str

    def provenance(self) -> dict[str, object]:
        return {
            "model_id": self.model_id,
            "model_provider_key": self.model_provider_key,
            "model_routing_version_id": str(self.model_routing_version_id),
            "prompt_reference_version_id": str(self.prompt_reference_version_id),
            "prompt_version_id": str(self.prompt_version_id),
            "prompt_digest": self.prompt_digest,
            "agent_profile_version_id": str(self.agent_profile_version_id),
            "evaluated_version_ids": [
                str(value) for value in self.evaluated_version_ids
            ],
            "safe_reason": self.safe_reason,
        }


class ModelBackedRoleExecutionError(RuntimeError):
    def __init__(self, code: str, safe_summary: str) -> None:
        super().__init__(safe_summary)
        self.code = code
        self.safe_summary = safe_summary


class ModelBackedRolePinResolver(Protocol):
    async def resolve(
        self, context: RoleExecutionContext
    ) -> ResolvedModelBackedRolePins:
        """Resolve governed prompt/profile/provider pins for a role node."""


class ModelSkillConfigRolePinResolver:
    def __init__(self, service: ModelSkillConfigService) -> None:
        self.service = service

    async def resolve(
        self, context: RoleExecutionContext
    ) -> ResolvedModelBackedRolePins:
        tenant_id = _required_uuid(context.tenant_id, "model_tenant_scope_denied")
        run_step_id = _required_uuid(context.run_step_id, "model_pin_resolution_failed")
        run_bundle_id = _required_uuid(
            context.run_bundle_id, "model_pin_resolution_failed"
        )
        agent_profile_version_id = _uuid_from_context(
            context.pinned_context.get("agent_profile_version_id"),
            code="model_pin_resolution_failed",
        )
        resolved = await self.service.repository.get_resolved_configuration_for_run(
            tenant_id=tenant_id,
            workflow_run_id=context.workflow_run_id,
        )
        if resolved is None:
            raise ModelBackedRoleExecutionError(
                "model_pin_resolution_failed",
                "Model-backed role execution requires a pinned run configuration.",
            )
        try:
            resolution = await self.service.resolve_model_step(
                principal=PrincipalContext(
                    tenant_id=tenant_id,
                    trace_id=context.trace_id,
                    principal_id="runtime-model-backed-role",
                ),
                request=ModelStepResolutionRequest(
                    tenant_id=tenant_id,
                    workflow_run_id=context.workflow_run_id,
                    run_step_id=run_step_id,
                    run_bundle_id=run_bundle_id,
                    resolved_execution_configuration_id=(
                        resolved.resolved_execution_configuration_id
                    ),
                    workflow_lineage_id=None,
                    workflow_version_bundle_id=context.workflow_version_bundle_id,
                    agent_key=context.role_key,
                    step_key=context.node_key,
                    trace_id=context.trace_id,
                    idempotency_key=_operation_idempotency_key(context),
                ),
            )
        except ModelSkillServiceError as exc:
            raise ModelBackedRoleExecutionError(
                "model_policy_denied",
                f"Model-backed role pin resolution denied: {exc}",
            ) from exc
        provider = await self.service.repository.find_provider(
            tenant_id=tenant_id,
            provider_key=resolution.model_provider_key,
            model_id=resolution.model_id,
        )
        if provider is None or provider.provider_connection_id is None:
            raise ModelBackedRoleExecutionError(
                "model_pin_resolution_failed",
                (
                    "Model-backed role execution requires a gateway-governed "
                    "provider connection."
                ),
            )
        return ResolvedModelBackedRolePins(
            provider_connection_id=provider.provider_connection_id,
            model_id=resolution.model_id,
            model_provider_key=resolution.model_provider_key,
            model_routing_version_id=resolution.model_routing_version_id,
            prompt_reference_version_id=resolution.prompt_reference_version_id,
            prompt_version_id=resolution.prompt_version_id,
            prompt_digest=resolution.prompt_digest,
            agent_profile_version_id=agent_profile_version_id,
            evaluated_version_ids=tuple(resolution.evaluated_version_ids),
            safe_reason=resolution.safe_reason,
        )


class UnavailableModelBackedRoleNodeExecutor:
    async def execute(self, context: RoleExecutionContext) -> RoleExecutionResult:
        return failed_role_result(
            context,
            code="model_pin_resolution_failed",
            safe_summary=(
                "Model-backed role execution is unavailable because gateway "
                "dependencies are not configured."
            ),
        )


class CompositeRoleNodeExecutor:
    def __init__(
        self,
        *,
        deterministic_executor: RoleNodeExecutor | None = None,
        model_backed_executor: RoleNodeExecutor | None = None,
    ) -> None:
        self.deterministic_executor = (
            deterministic_executor or DeterministicRoleNodeExecutor()
        )
        self.model_backed_executor = (
            model_backed_executor or UnavailableModelBackedRoleNodeExecutor()
        )

    async def execute(self, context: RoleExecutionContext) -> RoleExecutionResult:
        if model_backed_execution_requested(context):
            return await self.model_backed_executor.execute(context)
        return await self.deterministic_executor.execute(context)


class ModelBackedRoleNodeExecutor:
    def __init__(
        self,
        *,
        model_gateway: ModelGateway,
        pin_resolver: ModelBackedRolePinResolver,
        storage_provider: StorageProvider | None = None,
        inline_output_limit_bytes: int = 4096,
    ) -> None:
        self.model_gateway = model_gateway
        self.pin_resolver = pin_resolver
        self.storage_provider = storage_provider
        self.inline_output_limit_bytes = inline_output_limit_bytes

    async def execute(self, context: RoleExecutionContext) -> RoleExecutionResult:
        if not model_backed_execution_requested(context):
            return failed_role_result(
                context,
                code="model_execution_mode_disabled",
                safe_summary="Model-backed role execution mode was not selected.",
            )
        try:
            _validate_model_context(context)
            tenant_id = _required_uuid(context.tenant_id, "model_tenant_scope_denied")
            pins = await self.pin_resolver.resolve(context)
            messages = build_safe_gateway_messages(context)
            gateway_context = build_gateway_context_from_pins(
                tenant_id=tenant_id,
                workflow_run_id=context.workflow_run_id,
                workflow_run_step_id=context.run_step_id,
                trace_id=context.trace_id,
                idempotency_key=_operation_idempotency_key(context),
                agent_key=context.role_key,
                agent_kind=context.role_kind,
                agent_profile_version_id=pins.agent_profile_version_id,
                prompt_version_ids=(pins.prompt_version_id,),
                prompt_reference_version_ids=(pins.prompt_reference_version_id,),
                model_routing_provenance={
                    "model_routing_version_id": str(pins.model_routing_version_id),
                    "provider_key": pins.model_provider_key,
                },
                output_contract_metadata={
                    "output_contract_key": _output_contract_key(context),
                },
            )
            gateway_result = await self.model_gateway.invoke(
                connection_id=pins.provider_connection_id,
                model_id=pins.model_id,
                messages=messages,
                context=gateway_context,
            )
            if gateway_result.outcome is not TestOutcome.SUCCESS:
                return failed_role_result(
                    context,
                    code="model_gateway_failed",
                    safe_summary=(
                        f"{context.role_key} failed through governed model gateway."
                    ),
                    provenance={
                        **pins.provenance(),
                        "gateway_error_category": (
                            gateway_result.normalized_error_category.value
                        ),
                    },
                )
            payload = parse_model_output_content(gateway_result.content)
            validation = validate_role_output(
                payload,
                contract_schema=_output_contract_schema(context),
                inline_limit_bytes=self.inline_output_limit_bytes,
            )
            artifact_refs: tuple[dict[str, object], ...] = ()
            structured_output = dict(validation.structured_output)
            if validation.requires_artifact:
                artifact_refs = (
                    await self._store_output_artifact(
                        context=context,
                        payload=validation.structured_output,
                        payload_digest=validation.payload_digest,
                    ),
                )
                structured_output = {
                    "summary": validation.safe_summary,
                    "status": structured_output.get("status", "succeeded"),
                    "artifact_refs": [dict(item) for item in artifact_refs],
                    "payload_digest": validation.payload_digest,
                }
            usage_summary = _usage_summary(gateway_result)
            provenance = {
                **pins.provenance(),
                "gateway_safe_summary": dict(gateway_result.safe_audit_summary),
                "execution_mode": _execution_mode(context),
            }
            structured_output.setdefault("usage", usage_summary)
            structured_output.setdefault("provenance", provenance)
            return RoleExecutionResult(
                status="succeeded",
                safe_summary=(
                    f"{context.role_key} completed with model-backed output."
                ),
                structured_output=structured_output,
                payload_digest=validation.payload_digest,
                usage_summary=usage_summary,
                provenance=provenance,
                artifact_refs=artifact_refs,
            )
        except RoleOutputContractError as exc:
            return failed_role_result(
                context,
                code=exc.code,
                safe_summary=exc.safe_summary,
            )
        except ModelBackedRoleExecutionError as exc:
            return failed_role_result(
                context,
                code=exc.code,
                safe_summary=exc.safe_summary,
            )
        except PermissionError as exc:
            return failed_role_result(
                context,
                code="model_policy_denied",
                safe_summary=str(exc),
            )

    async def _store_output_artifact(
        self,
        *,
        context: RoleExecutionContext,
        payload: Mapping[str, Any],
        payload_digest: str,
    ) -> dict[str, object]:
        if self.storage_provider is None:
            raise ModelBackedRoleExecutionError(
                "model_output_artifact_failed",
                (
                    "Model-backed role output required artifact storage, but "
                    "storage was unavailable."
                ),
            )
        key = build_artifact_key(
            "model-backed-roles",
            str(context.tenant_id),
            str(context.workflow_run_id),
            f"{context.node_key}-{context.attempt}.json",
        )
        handle = await self.storage_provider.put(key, json_bytes(payload))
        return {
            "provider": handle.provider,
            "key": handle.key,
            "size_bytes": handle.size_bytes,
            "payload_digest": payload_digest,
        }


def build_role_node_executor(
    *,
    model_gateway: ModelGateway | None = None,
    pin_resolver: ModelBackedRolePinResolver | None = None,
    storage_provider: StorageProvider | None = None,
) -> CompositeRoleNodeExecutor:
    model_executor: RoleNodeExecutor | None = None
    if model_gateway is not None and pin_resolver is not None:
        model_executor = ModelBackedRoleNodeExecutor(
            model_gateway=model_gateway,
            pin_resolver=pin_resolver,
            storage_provider=storage_provider,
        )
    return CompositeRoleNodeExecutor(model_backed_executor=model_executor)


def model_backed_execution_requested(context: RoleExecutionContext) -> bool:
    return _execution_mode(context) in MODEL_BACKED_EXECUTION_MODES


def build_safe_gateway_messages(
    context: RoleExecutionContext,
) -> tuple[dict[str, str], ...]:
    if contains_sensitive_key(context.input_summary):
        raise ModelBackedRoleExecutionError(
            "model_output_redaction_failed",
            "Model-backed role input contained unsafe field names.",
        )
    safe_input = redact_graph_value(dict(context.input_summary))
    if not isinstance(safe_input, Mapping):
        safe_input = {"value": safe_input}
    payload = {
        "workflow_run_id": str(context.workflow_run_id),
        "node_key": context.node_key,
        "role_key": context.role_key,
        "role_kind": context.role_kind,
        "output_contract_key": _output_contract_key(context),
        "safe_input_summary": safe_input,
    }
    return (
        {
            "role": "system",
            "content": (
                "Execute the governed workflow role node. Return JSON that "
                "matches the role output contract using safe summaries only."
            ),
        },
        {"role": "user", "content": json_bytes(payload).decode("utf-8")},
    )


def failed_role_result(
    context: RoleExecutionContext,
    *,
    code: str,
    safe_summary: str,
    provenance: Mapping[str, object] | None = None,
) -> RoleExecutionResult:
    payload: dict[str, object] = {
        "node_key": context.node_key,
        "role_key": context.role_key,
        "error_code": code,
        "safe_reason": safe_summary,
    }
    return RoleExecutionResult(
        status="failed",
        safe_summary=safe_summary,
        structured_output=payload,
        payload_digest=graph_payload_digest(payload),
        error_code=code,
        provenance=dict(provenance or {}),
    )


def _validate_model_context(context: RoleExecutionContext) -> None:
    _required_uuid(context.tenant_id, "model_tenant_scope_denied")
    _required_uuid(context.run_step_id, "model_pin_resolution_failed")
    _required_uuid(context.run_bundle_id, "model_pin_resolution_failed")
    if not _output_contract_key(context):
        raise ModelBackedRoleExecutionError(
            "model_output_contract_invalid",
            "Model-backed role execution requires an output contract key.",
        )


def _execution_mode(context: RoleExecutionContext) -> str:
    value = context.pinned_context.get("execution_mode") or context.pinned_context.get(
        "role_execution_mode"
    )
    return str(value or "deterministic").strip().lower()


def _output_contract_key(context: RoleExecutionContext) -> str:
    value = context.pinned_context.get("output_contract_key")
    return str(value or "").strip()


def _output_contract_schema(context: RoleExecutionContext) -> Mapping[str, object]:
    value = context.pinned_context.get("output_contract_schema")
    return value if isinstance(value, Mapping) else {}


def _operation_idempotency_key(context: RoleExecutionContext) -> str:
    step_id = context.run_step_id or "missing-step"
    return (
        f"runtime:{context.workflow_run_id}:step:{step_id}:node:"
        f"{context.node_key}:attempt:{context.attempt}"
    )


def _usage_summary(result: GatewayResult) -> dict[str, object]:
    usage = result.usage.model_dump(mode="json")
    return {
        "usage_available": usage.get("availability"),
        "input_tokens": usage.get("input_tokens"),
        "output_tokens": usage.get("output_tokens"),
        "total_tokens": usage.get("total_tokens"),
        "provider_billable_units": usage.get("provider_billable_units"),
        "latency_ms": result.latency_ms,
    }


def _required_uuid(value: UUID | None, code: str) -> UUID:
    if value is None:
        raise ModelBackedRoleExecutionError(
            code,
            "Model-backed role execution requires tenant-scoped runtime context.",
        )
    return value


def _uuid_from_context(value: object, *, code: str) -> UUID:
    if isinstance(value, UUID):
        return value
    if value is None or str(value).strip() == "":
        raise ModelBackedRoleExecutionError(
            code,
            "Model-backed role execution requires an active profile version pin.",
        )
    try:
        return UUID(str(value))
    except ValueError as exc:
        raise ModelBackedRoleExecutionError(
            code,
            "Model-backed role execution received an invalid profile version pin.",
        ) from exc
