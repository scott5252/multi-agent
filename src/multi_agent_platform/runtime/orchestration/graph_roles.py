from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Protocol
from uuid import UUID

from multi_agent_platform.runtime.orchestration.graph_redaction import (
    graph_payload_digest,
    redact_graph_value,
)


@dataclass(slots=True, frozen=True)
class RoleExecutionContext:
    workflow_run_id: UUID
    tenant_id: UUID | None
    trace_id: str
    node_key: str
    role_key: str
    role_kind: str
    attempt: int
    input_summary: Mapping[str, object]
    pinned_context: Mapping[str, object] = field(default_factory=dict)
    run_step_id: UUID | None = None
    run_bundle_id: UUID | None = None
    workflow_version_bundle_id: UUID | None = None


@dataclass(slots=True, frozen=True)
class RoleExecutionResult:
    status: str
    safe_summary: str
    structured_output: dict[str, object]
    payload_digest: str
    error_code: str | None = None
    usage_summary: Mapping[str, object] = field(default_factory=dict)
    provenance: Mapping[str, object] = field(default_factory=dict)
    artifact_refs: tuple[dict[str, object], ...] = field(default_factory=tuple)

    @property
    def succeeded(self) -> bool:
        return self.status == "succeeded"


class RoleNodeExecutor(Protocol):
    async def execute(self, context: RoleExecutionContext) -> RoleExecutionResult:
        """Execute one role node and return a safe structured result."""


class DeterministicRoleNodeExecutor:
    def __init__(
        self,
        *,
        fail_node_keys: set[str] | None = None,
        output_overrides: Mapping[str, Mapping[str, object]] | None = None,
    ) -> None:
        self.fail_node_keys = fail_node_keys or set()
        self.output_overrides = output_overrides or {}

    async def execute(self, context: RoleExecutionContext) -> RoleExecutionResult:
        if context.node_key in self.fail_node_keys:
            failure_payload: dict[str, object] = {
                "node_key": context.node_key,
                "role_key": context.role_key,
                "role_kind": context.role_kind,
                "error_code": "deterministic_role_failure",
            }
            return RoleExecutionResult(
                status="failed",
                safe_summary=(
                    f"{context.role_key} failed with deterministic QA error."
                ),
                structured_output=failure_payload,
                payload_digest=graph_payload_digest(failure_payload),
                error_code="deterministic_role_failure",
            )

        upstream_node_keys = context.input_summary.get("upstream_node_keys", [])
        if isinstance(upstream_node_keys, Sequence) and not isinstance(
            upstream_node_keys, (str, bytes, bytearray)
        ):
            safe_upstream_node_keys = list(upstream_node_keys)
        else:
            safe_upstream_node_keys = []

        payload: dict[str, object] = {
            "node_key": context.node_key,
            "role_key": context.role_key,
            "role_kind": context.role_kind,
            "result": f"safe deterministic output for {context.role_key}",
            "upstream_node_keys": safe_upstream_node_keys,
        }
        payload.update(dict(self.output_overrides.get(context.node_key, {})))
        safe_payload = redact_graph_value(payload)
        structured = (
            safe_payload if isinstance(safe_payload, dict) else {"value": safe_payload}
        )
        return RoleExecutionResult(
            status="succeeded",
            safe_summary=f"{context.role_key} completed with deterministic QA output.",
            structured_output=structured,
            payload_digest=graph_payload_digest(payload),
        )
