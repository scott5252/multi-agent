from __future__ import annotations

import platform
from uuid import UUID

from pydantic import BaseModel

from multi_agent_platform.audit.models import VersionBundleSnapshotCreate
from multi_agent_platform.config.settings import Settings
from multi_agent_platform.model_providers.models import GatewayInvocationContext
from multi_agent_platform.runtime.workflow_bundle import CompiledWorkflowBundle


class VersionBundle(BaseModel):
    service: str
    version: str
    commit_sha: str
    build_time: str
    python_version: str
    auth_policy_version: str = "2026-04-22"
    surface_policy_version: str = "2026-04-22"
    claim_mapping_version: str = "2026-04-22"


class RunVersionBundle(BaseModel):
    workflow_version_bundle_id: str
    workflow_lineage_id: str
    workflow_key: str
    compiled_bundle_digest: str
    compiler_version: str
    pinned_skill_versions: dict[str, str]
    subworkflow_version_refs: dict[str, str]
    prompt_profile_pins: list[dict[str, object]] = []


def build_gateway_context_from_pins(
    *,
    tenant_id: UUID,
    workflow_run_id: UUID | None = None,
    workflow_run_step_id: UUID | None = None,
    test_bench_run_id: UUID | None = None,
    workflow_validation_id: UUID | None = None,
    trace_id: str,
    idempotency_key: str,
    agent_key: str,
    agent_kind: str,
    agent_profile_version_id: UUID | None,
    prompt_version_ids: tuple[UUID, ...],
    prompt_reference_version_ids: tuple[UUID, ...],
    model_routing_provenance: dict[str, object],
    profile_provenance: dict[str, object] | None = None,
    memory_policy_context: dict[str, object] | None = None,
    tool_policy_expectations: dict[str, object] | None = None,
    output_contract_metadata: dict[str, object] | None = None,
) -> GatewayInvocationContext:
    if agent_profile_version_id is None or not prompt_version_ids:
        raise PermissionError("prompt/profile pins must be persisted before model work")
    if (
        workflow_run_id is None
        and test_bench_run_id is None
        and workflow_validation_id is None
    ):
        raise PermissionError("gateway context requires an execution identity")
    prefix = "runtime"
    identity_value = workflow_run_id
    if test_bench_run_id is not None:
        prefix = "test-bench"
        identity_value = test_bench_run_id
    elif workflow_validation_id is not None:
        prefix = "workflow-validation"
        identity_value = workflow_validation_id
    step_fragment = f":{workflow_run_step_id}" if workflow_run_step_id else ""
    operation_identity = (
        f"{prefix}:{tenant_id}:{identity_value}{step_fragment}:{agent_kind}:"
        f"{agent_key}:{idempotency_key}"
    )
    return GatewayInvocationContext(
        tenant_id=tenant_id,
        workflow_run_id=workflow_run_id,
        workflow_run_step_id=workflow_run_step_id,
        test_bench_run_id=test_bench_run_id,
        workflow_validation_id=workflow_validation_id,
        trace_id=trace_id,
        idempotency_key=idempotency_key,
        operation_identity=operation_identity,
        agent_key=agent_key,
        agent_kind=agent_kind,
        agent_profile_version_id=agent_profile_version_id,
        prompt_version_ids=prompt_version_ids,
        prompt_reference_version_ids=prompt_reference_version_ids,
        model_routing_provenance=model_routing_provenance,
        profile_provenance=profile_provenance or {},
        memory_policy_context=memory_policy_context or {},
        tool_policy_expectations=tool_policy_expectations or {},
        output_contract_metadata=output_contract_metadata or {},
        side_effect_boundary="before_provider_invocation",
    )


def build_runtime_gateway_provenance(
    *,
    tenant_id: UUID,
    workflow_run_id: UUID,
    workflow_run_step_id: UUID | None,
    trace_id: str,
    agent_key: str,
    agent_kind: str,
    agent_profile_version_id: UUID,
    prompt_version_ids: tuple[UUID, ...],
    prompt_reference_version_ids: tuple[UUID, ...],
    gateway_operation_id: UUID | None,
    provider_connection_id: UUID | None,
    provider_model_definition_id: UUID | None,
    model_id: str | None,
    retry_category: str | None,
    breaker_scope: str | None,
    latency_ms: int | None,
    usage_available: bool | None,
    normalized_outcome: str | None,
    safe_summary: dict[str, object],
) -> dict[str, object]:
    metadata_available = gateway_operation_id is not None
    return {
        "tenant_id": str(tenant_id),
        "workflow_run_id": str(workflow_run_id),
        "workflow_run_step_id": str(workflow_run_step_id)
        if workflow_run_step_id
        else None,
        "trace_id": trace_id,
        "agent_key": agent_key,
        "agent_kind": agent_kind,
        "agent_profile_version_id": str(agent_profile_version_id),
        "prompt_version_ids": [str(value) for value in prompt_version_ids],
        "prompt_reference_version_ids": [
            str(value) for value in prompt_reference_version_ids
        ],
        "gateway_operation_id": str(gateway_operation_id)
        if gateway_operation_id
        else None,
        "provider_connection_id": str(provider_connection_id)
        if provider_connection_id
        else None,
        "provider_model_definition_id": str(provider_model_definition_id)
        if provider_model_definition_id
        else None,
        "model_id": model_id,
        "retry_category": retry_category,
        "breaker_scope": breaker_scope,
        "latency_ms": latency_ms,
        "usage_available": usage_available,
        "normalized_outcome": normalized_outcome,
        "safe_summary": dict(safe_summary),
        "metadata_available": metadata_available,
        "metadata_status": "available"
        if metadata_available
        else "pre_v2_metadata_unavailable",
    }


def get_version_bundle(settings: Settings) -> VersionBundle:
    return VersionBundle(
        service=settings.app_name,
        version=settings.app_version,
        commit_sha=settings.commit_sha,
        build_time=settings.build_time,
        python_version=platform.python_version(),
    )


def get_workflow_registry_compiler_version() -> str:
    return "workflow-registry-0.1"


def build_run_version_bundle(
    *,
    workflow_version_bundle_id: str,
    compiled_bundle: CompiledWorkflowBundle,
) -> RunVersionBundle:
    raw_skills = compiled_bundle.dependencies.get("skills", [])
    raw_subworkflows = compiled_bundle.dependencies.get("subworkflows", [])
    raw_prompt_profile_pins = compiled_bundle.dependencies.get(
        "prompt_profile_pins", []
    )
    skills = raw_skills if isinstance(raw_skills, list) else []
    subworkflows = raw_subworkflows if isinstance(raw_subworkflows, list) else []
    prompt_profile_pins = (
        raw_prompt_profile_pins if isinstance(raw_prompt_profile_pins, list) else []
    )
    return RunVersionBundle(
        workflow_version_bundle_id=workflow_version_bundle_id,
        workflow_lineage_id=compiled_bundle.workflow_lineage_id,
        workflow_key=compiled_bundle.workflow_key,
        compiled_bundle_digest=compiled_bundle.digest(),
        compiler_version=compiled_bundle.compiler_version,
        pinned_skill_versions={
            str(item["skill_slug"]): str(item["skill_version"])
            for item in skills
            if isinstance(item, dict)
            and "skill_slug" in item
            and "skill_version" in item
        },
        subworkflow_version_refs={
            str(item["alias"]): str(item["workflow_version_ref"])
            for item in subworkflows
            if isinstance(item, dict)
            and "alias" in item
            and "workflow_version_ref" in item
        },
        prompt_profile_pins=[
            dict(item) for item in prompt_profile_pins if isinstance(item, dict)
        ],
    )


def build_audit_version_bundle_snapshot(
    *,
    tenant_id: UUID | None,
    workflow_run_id: UUID,
    run_bundle: RunVersionBundle,
) -> VersionBundleSnapshotCreate:
    return VersionBundleSnapshotCreate(
        tenant_id=tenant_id,
        workflow_run_id=workflow_run_id,
        workflow_lineage_id=None,
        workflow_version_bundle_id=None,
        execution_bundle_id=None,
        bundle_digest=run_bundle.compiled_bundle_digest,
        workflow_version={
            "workflow_version_bundle_id": run_bundle.workflow_version_bundle_id,
            "workflow_lineage_id": run_bundle.workflow_lineage_id,
            "workflow_key": run_bundle.workflow_key,
            "compiler_version": run_bundle.compiler_version,
        },
        contract_version_refs={},
        prompt_version_refs={},
        model_config_version_refs={},
        tool_policy_version_refs=dict(run_bundle.pinned_skill_versions),
        activation_state_at_acceptance="active",
        safe_summary={
            "subworkflow_count": len(run_bundle.subworkflow_version_refs),
            "pinned_skill_count": len(run_bundle.pinned_skill_versions),
            "prompt_profile_pin_count": len(run_bundle.prompt_profile_pins),
        },
    )
