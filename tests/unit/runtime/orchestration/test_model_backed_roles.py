from __future__ import annotations

import json
from uuid import UUID, uuid4

from multi_agent_platform.model_providers.models import (
    ErrorCategory,
    GatewayResult,
    GatewayUsage,
    TestOutcome,
)
from multi_agent_platform.runtime.orchestration.graph_roles import (
    RoleExecutionContext,
)
from multi_agent_platform.runtime.orchestration.model_backed_roles import (
    CompositeRoleNodeExecutor,
    ModelBackedRoleExecutionError,
    ModelBackedRoleNodeExecutor,
    ResolvedModelBackedRolePins,
    build_safe_gateway_messages,
)
from multi_agent_platform.storage.base import ArtifactHandle

PROFILE_ID = UUID("aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa")
_MISSING_TENANT = object()


def _pins() -> ResolvedModelBackedRolePins:
    return ResolvedModelBackedRolePins(
        provider_connection_id=uuid4(),
        model_id="gpt-safe-fixture",
        model_provider_key="local",
        model_routing_version_id=uuid4(),
        prompt_reference_version_id=uuid4(),
        prompt_version_id=uuid4(),
        prompt_digest="sha256:prompt",
        agent_profile_version_id=PROFILE_ID,
        evaluated_version_ids=(uuid4(),),
        safe_reason="model and prompt resolved from pinned candidates",
    )


def _context(
    *,
    execution_mode: str | None = "model_gateway",
    tenant_id: UUID | None | object = _MISSING_TENANT,
    input_summary: dict[str, object] | None = None,
) -> RoleExecutionContext:
    tenant = uuid4() if tenant_id is _MISSING_TENANT else tenant_id
    return RoleExecutionContext(
        workflow_run_id=uuid4(),
        tenant_id=tenant if isinstance(tenant, UUID) else None,
        trace_id="trace-model-role",
        node_key="ux-reviewer-node",
        role_key="ux-reviewer",
        role_kind="agent",
        attempt=1,
        input_summary=input_summary
        or {"upstream_node_keys": ["lead"], "lead": {"safe_summary": "Safe input."}},
        pinned_context={
            "execution_mode": execution_mode,
            "output_contract_key": "reviewer-output-v1",
            "output_contract_schema": {"required": ["summary", "status"]},
            "agent_profile_version_id": str(PROFILE_ID),
        },
        run_step_id=uuid4(),
        run_bundle_id=uuid4(),
        workflow_version_bundle_id=uuid4(),
    )


class FakeResolver:
    def __init__(self, *, error: ModelBackedRoleExecutionError | None = None) -> None:
        self.error = error

    async def resolve(
        self, context: RoleExecutionContext
    ) -> ResolvedModelBackedRolePins:
        if self.error is not None:
            raise self.error
        return _pins()


class FakeGateway:
    def __init__(self, result: GatewayResult | None = None) -> None:
        self.result = result or GatewayResult(
            outcome=TestOutcome.SUCCESS,
            content=json.dumps(
                {
                    "summary": "Safe reviewer summary.",
                    "status": "approved",
                    "findings": [],
                }
            ),
            latency_ms=12,
            usage=GatewayUsage(input_tokens=10, output_tokens=5, total_tokens=15),
            safe_audit_summary={"outcome": "success"},
        )
        self.calls: list[dict[str, object]] = []

    async def invoke(self, **kwargs: object) -> GatewayResult:
        self.calls.append(dict(kwargs))
        return self.result


class FakeStorage:
    provider_name = "filesystem"

    def __init__(self) -> None:
        self.payloads: dict[str, bytes] = {}

    async def put(self, key: str, payload: bytes) -> ArtifactHandle:
        self.payloads[key] = payload
        return ArtifactHandle(
            provider=self.provider_name,
            key=key,
            url=f"artifact://{key}",
            size_bytes=len(payload),
        )

    async def get(self, key: str) -> bytes:
        return self.payloads[key]


async def test_composite_role_executor_uses_deterministic_default() -> None:
    context = _context(execution_mode=None)

    result = await CompositeRoleNodeExecutor().execute(context)

    assert result.succeeded
    assert result.structured_output["result"] == (
        "safe deterministic output for ux-reviewer"
    )


async def test_model_backed_mode_fails_closed_when_dependencies_missing() -> None:
    result = await CompositeRoleNodeExecutor().execute(_context())

    assert not result.succeeded
    assert result.error_code == "model_pin_resolution_failed"


async def test_model_backed_executor_calls_gateway_with_safe_context() -> None:
    gateway = FakeGateway()
    executor = ModelBackedRoleNodeExecutor(
        model_gateway=gateway,
        pin_resolver=FakeResolver(),
    )

    result = await executor.execute(_context())

    assert result.succeeded
    assert result.structured_output["summary"] == "Safe reviewer summary."
    assert result.usage_summary["total_tokens"] == 15
    assert result.provenance["model_id"] == "gpt-safe-fixture"
    assert gateway.calls
    gateway_context = gateway.calls[0]["context"]
    assert gateway_context.workflow_run_step_id is not None
    assert gateway_context.prompt_version_ids


async def test_model_backed_executor_fails_without_tenant_context() -> None:
    executor = ModelBackedRoleNodeExecutor(
        model_gateway=FakeGateway(),
        pin_resolver=FakeResolver(),
    )

    result = await executor.execute(_context(tenant_id=None))

    assert not result.succeeded
    assert result.error_code == "model_tenant_scope_denied"


async def test_model_backed_executor_fails_on_pin_denial_before_gateway() -> None:
    gateway = FakeGateway()
    executor = ModelBackedRoleNodeExecutor(
        model_gateway=gateway,
        pin_resolver=FakeResolver(
            error=ModelBackedRoleExecutionError(
                "model_policy_denied",
                "model-backed role execution denied by policy",
            )
        ),
    )

    result = await executor.execute(_context())

    assert not result.succeeded
    assert result.error_code == "model_policy_denied"
    assert gateway.calls == []


async def test_model_backed_executor_maps_gateway_failure() -> None:
    executor = ModelBackedRoleNodeExecutor(
        model_gateway=FakeGateway(
            GatewayResult(
                outcome=TestOutcome.FAILURE,
                normalized_error_category=ErrorCategory.PROVIDER_UNAVAILABLE,
            )
        ),
        pin_resolver=FakeResolver(),
    )

    result = await executor.execute(_context())

    assert not result.succeeded
    assert result.error_code == "model_gateway_failed"
    assert result.provenance["gateway_error_category"] == "provider_unavailable"


async def test_model_backed_executor_rejects_contract_invalid_output() -> None:
    executor = ModelBackedRoleNodeExecutor(
        model_gateway=FakeGateway(
            GatewayResult(
                outcome=TestOutcome.SUCCESS,
                content=json.dumps({"summary": "Safe reviewer summary."}),
            )
        ),
        pin_resolver=FakeResolver(),
    )

    result = await executor.execute(_context())

    assert not result.succeeded
    assert result.error_code == "model_output_contract_invalid"


async def test_model_backed_executor_stores_large_allowed_output_as_artifact() -> None:
    storage = FakeStorage()
    executor = ModelBackedRoleNodeExecutor(
        model_gateway=FakeGateway(
            GatewayResult(
                outcome=TestOutcome.SUCCESS,
                content=json.dumps(
                    {
                        "summary": "Safe reviewer summary.",
                        "status": "approved",
                        "recommendations": ["safe " * 40],
                    }
                ),
            )
        ),
        pin_resolver=FakeResolver(),
        storage_provider=storage,
        inline_output_limit_bytes=80,
    )

    result = await executor.execute(_context())

    assert result.succeeded
    assert result.artifact_refs
    assert result.structured_output["artifact_refs"][0]["key"].startswith(
        "model-backed-roles/"
    )
    assert storage.payloads


def test_build_safe_gateway_messages_rejects_unsafe_input_keys() -> None:
    try:
        build_safe_gateway_messages(
            _context(input_summary={"raw_payload": {"secret": "hidden"}})
        )
    except ModelBackedRoleExecutionError as exc:
        assert exc.code == "model_output_redaction_failed"
    else:
        raise AssertionError("unsafe input should fail")
