from __future__ import annotations

import asyncio
from collections import deque
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from multi_agent_platform.db.models.runtime_orchestration import (
    RuntimeInteractionKind,
    RuntimeInteractionStatus,
    RuntimeRunStatus,
    RuntimeStepStatus,
)
from multi_agent_platform.runtime.orchestration.contracts import sha256_digest
from multi_agent_platform.runtime.orchestration.graph_redaction import (
    safe_graph_ref,
)
from multi_agent_platform.runtime.orchestration.graph_roles import (
    DeterministicRoleNodeExecutor,
    RoleExecutionContext,
    RoleExecutionResult,
    RoleNodeExecutor,
)
from multi_agent_platform.runtime.orchestration.interaction_evidence import (
    interaction_idempotency_key,
    record_runtime_interaction,
)


class GraphExecutionError(RuntimeError):
    pass


class GraphValidationError(GraphExecutionError):
    pass


class GraphExecutionStatus(StrEnum):
    SUCCEEDED = "succeeded"
    PAUSED = "paused"
    FAILED = "failed"
    NOOP = "noop"


class JoinDecisionType(StrEnum):
    PROCEED = "proceed"
    WAIT = "wait"
    PAUSE_MANUAL_RESOLUTION = "pause_manual_resolution"
    FAIL = "fail"


@dataclass(slots=True, frozen=True)
class GraphNode:
    node_key: str
    node_type: str
    display_name: str
    role_key: str | None = None
    join_policy_key: str | None = None
    contract_key: str | None = None
    active: bool = True


@dataclass(slots=True, frozen=True)
class GraphEdge:
    edge_key: str
    source_node_key: str
    target_node_key: str
    contract_key: str | None = None


@dataclass(slots=True, frozen=True)
class GraphRole:
    role_key: str
    role_kind: str
    profile_reference_key: str | None = None
    output_contract_key: str | None = None
    execution_mode: str | None = None
    agent_profile_version_id: UUID | None = None
    skill_installation_keys: tuple[str, ...] = field(default_factory=tuple)


@dataclass(slots=True, frozen=True)
class GraphJoinPolicy:
    join_policy_key: str
    strategy: str
    inbound_edge_keys: tuple[str, ...] = field(default_factory=tuple)
    quorum_count: int | None = None
    failure_behavior: str = "block"
    output_merge_contract_key: str | None = None


@dataclass(slots=True, frozen=True)
class BranchResult:
    node_key: str
    status: str
    output_ref: dict[str, object] | None = None
    safe_summary: str | None = None
    error_code: str | None = None


@dataclass(slots=True, frozen=True)
class JoinDecision:
    decision: JoinDecisionType
    safe_summary: str
    successful_branch_count: int
    failed_branch_count: int
    winning_branch_key: str | None = None


@dataclass(slots=True, frozen=True)
class GraphExecutionPlan:
    workflow_version_bundle_id: UUID | None
    workflow_key: str
    entry_node_key: str
    nodes_by_key: dict[str, GraphNode]
    edges_by_key: dict[str, GraphEdge]
    roles_by_key: dict[str, GraphRole]
    join_policies_by_key: dict[str, GraphJoinPolicy]
    contracts_by_key: dict[str, dict[str, object]]
    outbound_edges_by_source: dict[str, tuple[GraphEdge, ...]]
    inbound_edges_by_target: dict[str, tuple[GraphEdge, ...]]
    terminal_node_keys: tuple[str, ...]


@dataclass(slots=True, frozen=True)
class GraphExecutionResult:
    status: GraphExecutionStatus
    workflow_run_id: UUID
    executed_node_keys: tuple[str, ...] = field(default_factory=tuple)
    skipped_node_keys: tuple[str, ...] = field(default_factory=tuple)
    wave_count: int = 0
    final_output_ref: dict[str, object] | None = None
    pause_reason: str | None = None
    failure_reason: str | None = None


def build_graph_execution_plan(
    document: Mapping[str, object],
    *,
    workflow_version_bundle_id: UUID | None = None,
) -> GraphExecutionPlan:
    nodes = [_as_mapping(item, "node") for item in _as_sequence(document.get("nodes"))]
    roles = [_as_mapping(item, "role") for item in _as_sequence(document.get("roles"))]
    edges = [_as_mapping(item, "edge") for item in _as_sequence(document.get("edges"))]
    joins = [
        _as_mapping(item, "join policy")
        for item in _as_sequence(document.get("join_policies"))
    ]
    contracts = [
        _as_mapping(item, "contract")
        for item in _as_sequence(document.get("contracts"))
    ]
    workflow_key = str(document.get("workflow_key") or "workflow")
    entry_node_key = str(document.get("entry_node_key") or "")
    nodes_by_key = {
        str(node["node_key"]): GraphNode(
            node_key=str(node["node_key"]),
            node_type=str(node.get("node_type") or ""),
            display_name=str(node.get("display_name") or node["node_key"]),
            role_key=_optional_str(node.get("role_key")),
            join_policy_key=_optional_str(node.get("join_policy_key")),
            active=bool(node.get("active", True)),
        )
        for node in nodes
        if bool(node.get("active", True))
    }
    roles_by_key = {
        str(role["role_key"]): GraphRole(
            role_key=str(role["role_key"]),
            role_kind=str(role.get("role_kind") or "agent"),
            profile_reference_key=_optional_str(role.get("profile_reference_key")),
            output_contract_key=_optional_str(role.get("output_contract_key")),
            execution_mode=_optional_str(
                role.get("execution_mode") or role.get("role_execution_mode")
            ),
            agent_profile_version_id=_optional_uuid(
                role.get("agent_profile_version_id")
            ),
            skill_installation_keys=tuple(
                str(item) for item in _as_sequence(role.get("skill_installation_keys"))
            ),
        )
        for role in roles
    }
    edges_by_key = {
        str(edge["edge_key"]): GraphEdge(
            edge_key=str(edge["edge_key"]),
            source_node_key=str(edge["source_node_key"]),
            target_node_key=str(edge["target_node_key"]),
            contract_key=_optional_str(edge.get("contract_key")),
        )
        for edge in edges
        if str(edge.get("source_node_key")) in nodes_by_key
        and str(edge.get("target_node_key")) in nodes_by_key
    }
    join_policies_by_key = {
        str(policy["join_policy_key"]): GraphJoinPolicy(
            join_policy_key=str(policy["join_policy_key"]),
            strategy=str(policy.get("strategy") or "all_success"),
            inbound_edge_keys=tuple(
                str(item) for item in _as_sequence(policy.get("inbound_edge_keys"))
            ),
            quorum_count=_optional_int(policy.get("quorum_count")),
            failure_behavior=str(policy.get("failure_behavior") or "block"),
            output_merge_contract_key=_optional_str(
                policy.get("output_merge_contract_key")
            ),
        )
        for policy in joins
    }
    contracts_by_key = {
        str(contract["contract_key"]): dict(
            _as_mapping(contract.get("json_schema", {}), "contract schema")
        )
        for contract in contracts
    }
    outbound_edges_by_source = _group_edges(edges_by_key.values(), by_source=True)
    inbound_edges_by_target = _group_edges(edges_by_key.values(), by_source=False)
    terminal_node_keys = tuple(
        node_key
        for node_key, node in nodes_by_key.items()
        if node.node_type == "terminal"
    )
    plan = GraphExecutionPlan(
        workflow_version_bundle_id=workflow_version_bundle_id,
        workflow_key=workflow_key,
        entry_node_key=entry_node_key,
        nodes_by_key=nodes_by_key,
        edges_by_key=edges_by_key,
        roles_by_key=roles_by_key,
        join_policies_by_key=join_policies_by_key,
        contracts_by_key=contracts_by_key,
        outbound_edges_by_source=outbound_edges_by_source,
        inbound_edges_by_target=inbound_edges_by_target,
        terminal_node_keys=terminal_node_keys,
    )
    validate_graph_execution_plan(plan)
    return plan


def validate_graph_execution_plan(plan: GraphExecutionPlan) -> None:
    if not plan.entry_node_key:
        raise GraphValidationError("entry_node_key is required")
    if plan.entry_node_key not in plan.nodes_by_key:
        raise GraphValidationError("entry_node_key must reference an active node")
    if not plan.terminal_node_keys:
        raise GraphValidationError("at least one terminal node is required")
    for node in plan.nodes_by_key.values():
        if node.node_type == "role" and (
            node.role_key is None or node.role_key not in plan.roles_by_key
        ):
            raise GraphValidationError(f"role node {node.node_key} has no role")
        if node.node_type == "join":
            policy_key = node.join_policy_key
            if policy_key is None:
                inbound = plan.inbound_edges_by_target.get(node.node_key, ())
                if len(plan.join_policies_by_key) == 1:
                    policy_key = next(iter(plan.join_policies_by_key))
                elif inbound:
                    policy_key = f"{node.node_key}-join-policy"
            if policy_key is not None and policy_key not in plan.join_policies_by_key:
                raise GraphValidationError(
                    f"join node {node.node_key} references missing join policy"
                )
    _assert_acyclic(plan)


def evaluate_join_policy(
    policy: GraphJoinPolicy,
    branch_results: Sequence[BranchResult],
) -> JoinDecision:
    successful = [result for result in branch_results if result.status == "succeeded"]
    failed = [result for result in branch_results if result.status == "failed"]
    strategy = policy.strategy
    if strategy == "all_success":
        if branch_results and len(successful) == len(branch_results):
            return JoinDecision(
                decision=JoinDecisionType.PROCEED,
                safe_summary="All inbound branches succeeded.",
                successful_branch_count=len(successful),
                failed_branch_count=len(failed),
            )
    elif strategy == "quorum":
        quorum_count = policy.quorum_count or len(branch_results)
        if quorum_count < 1 or quorum_count > max(len(branch_results), 1):
            return JoinDecision(
                decision=JoinDecisionType.FAIL,
                safe_summary="Join quorum count is invalid.",
                successful_branch_count=len(successful),
                failed_branch_count=len(failed),
            )
        if len(successful) >= quorum_count:
            return JoinDecision(
                decision=JoinDecisionType.PROCEED,
                safe_summary=f"Join quorum reached with {len(successful)} branches.",
                successful_branch_count=len(successful),
                failed_branch_count=len(failed),
            )
    elif strategy == "first_success":
        if successful:
            return JoinDecision(
                decision=JoinDecisionType.PROCEED,
                safe_summary="First successful inbound branch selected.",
                successful_branch_count=len(successful),
                failed_branch_count=len(failed),
                winning_branch_key=successful[0].node_key,
            )
    elif strategy == "manual_resolution":
        return JoinDecision(
            decision=JoinDecisionType.PAUSE_MANUAL_RESOLUTION,
            safe_summary="Join requires manual resolution.",
            successful_branch_count=len(successful),
            failed_branch_count=len(failed),
        )
    else:
        return JoinDecision(
            decision=JoinDecisionType.FAIL,
            safe_summary=f"Unsupported join strategy: {strategy}",
            successful_branch_count=len(successful),
            failed_branch_count=len(failed),
        )

    if policy.failure_behavior == "manual_resolution":
        return JoinDecision(
            decision=JoinDecisionType.PAUSE_MANUAL_RESOLUTION,
            safe_summary="Join requires manual resolution because criteria failed.",
            successful_branch_count=len(successful),
            failed_branch_count=len(failed),
        )
    if failed:
        return JoinDecision(
            decision=JoinDecisionType.FAIL,
            safe_summary="Join criteria failed.",
            successful_branch_count=len(successful),
            failed_branch_count=len(failed),
        )
    return JoinDecision(
        decision=JoinDecisionType.WAIT,
        safe_summary="Join is waiting for inbound branches.",
        successful_branch_count=len(successful),
        failed_branch_count=len(failed),
    )


class GraphExecutionService:
    def __init__(
        self,
        repository: Any,
        *,
        role_executor: RoleNodeExecutor | None = None,
    ) -> None:
        self.repository = repository
        self.role_executor = role_executor or DeterministicRoleNodeExecutor()

    async def execute_claimed_run(
        self,
        *,
        workflow_run_id: UUID,
        worker_id: str,
    ) -> GraphExecutionResult:
        run = await self.repository.get_run_by_id(workflow_run_id=workflow_run_id)
        if run is None:
            raise GraphExecutionError("workflow run not found")
        if run.status in {
            RuntimeRunStatus.SUCCEEDED,
            RuntimeRunStatus.FAILED,
            RuntimeRunStatus.CANCELLED,
        }:
            return GraphExecutionResult(
                status=GraphExecutionStatus.NOOP,
                workflow_run_id=workflow_run_id,
            )

        try:
            bundle = await self.repository.get_execution_bundle(
                run_bundle_id=run.run_bundle_id
            )
            if bundle is None:
                raise GraphValidationError("runtime execution bundle not found")
            version = await self.repository.get_workflow_version_bundle(
                workflow_version_bundle_id=bundle.published_workflow_version_id
            )
            self._assert_tenant_compatible(run=run, version=version)
            document = await _extract_workflow_document(
                self.repository,
                bundle.workflow_version,
                version,
            )
            plan = build_graph_execution_plan(
                document,
                workflow_version_bundle_id=bundle.published_workflow_version_id,
            )
        except GraphExecutionError as exc:
            await self._fail_run(run, reason=str(exc), worker_id=worker_id)
            return GraphExecutionResult(
                status=GraphExecutionStatus.FAILED,
                workflow_run_id=workflow_run_id,
                failure_reason=str(exc),
            )

        await self._timeline(
            run,
            "graph_loaded",
            {
                "worker_id": worker_id,
                "workflow_key": plan.workflow_key,
                "node_count": len(plan.nodes_by_key),
            },
        )
        existing_steps = await self.repository.list_run_steps(
            workflow_run_id=run.workflow_run_id,
            tenant_id=run.tenant_id,
        )
        completed: dict[str, dict[str, object]] = {
            step.step_key: step.output_ref or {}
            for step in existing_steps
            if step.status is RuntimeStepStatus.SUCCEEDED
        }
        failed: dict[str, dict[str, object]] = {
            step.step_key: step.error_ref or {}
            for step in existing_steps
            if step.status is RuntimeStepStatus.FAILED
        }
        executed: list[str] = []
        skipped = sorted(completed)
        wave_count = 0

        while True:
            if any(node_key in completed for node_key in plan.terminal_node_keys):
                final_key = next(
                    node_key
                    for node_key in plan.terminal_node_keys
                    if node_key in completed
                )
                final_output = completed[final_key]
                await self.repository.update_run_status(
                    workflow_run_id=run.workflow_run_id,
                    status=RuntimeRunStatus.SUCCEEDED,
                    terminal_reason="graph execution succeeded",
                )
                await self._timeline(
                    run,
                    "graph_run_succeeded",
                    {"terminal_node_key": final_key},
                )
                return GraphExecutionResult(
                    status=GraphExecutionStatus.SUCCEEDED,
                    workflow_run_id=workflow_run_id,
                    executed_node_keys=tuple(executed),
                    skipped_node_keys=tuple(skipped),
                    wave_count=wave_count,
                    final_output_ref=final_output,
                )

            ready = self._ready_nodes(plan, completed=completed, failed=failed)
            if not ready:
                reason = "graph execution reached no ready nodes"
                await self._fail_run(run, reason=reason, worker_id=worker_id)
                return GraphExecutionResult(
                    status=GraphExecutionStatus.FAILED,
                    workflow_run_id=workflow_run_id,
                    executed_node_keys=tuple(executed),
                    skipped_node_keys=tuple(skipped),
                    wave_count=wave_count,
                    failure_reason=reason,
                )

            wave_count += 1
            await self._timeline(
                run,
                "graph_wave_scheduled",
                {
                    "wave_number": wave_count,
                    "ready_node_keys": [node.node_key for node in ready],
                    "parallel_role_node_count": sum(
                        1 for node in ready if node.node_type in {"role", "subworkflow"}
                    ),
                },
            )
            role_nodes = [
                node for node in ready if node.node_type in {"role", "subworkflow"}
            ]
            decision_nodes = [
                node for node in ready if node.node_type not in {"role", "subworkflow"}
            ]
            if role_nodes:
                prepared = [
                    await self._prepare_role_node(
                        run=run,
                        plan=plan,
                        node=node,
                        completed=completed,
                    )
                    for node in role_nodes
                ]
                results = await asyncio.gather(
                    *[
                        self.role_executor.execute(context)
                        for _node, _step, context in prepared
                    ]
                )
                for (node, step, _context), result in zip(
                    prepared,
                    results,
                    strict=True,
                ):
                    await self._finalize_role_node(
                        run=run,
                        plan=plan,
                        node=node,
                        run_step_id=step.run_step_id,
                        result=result,
                    )
                    executed.append(node.node_key)
                    if result.succeeded:
                        completed[node.node_key] = _result_output_ref(
                            node_key=node.node_key,
                            result=result,
                        )
                    else:
                        failed[node.node_key] = _result_error_ref(result)

            for node in decision_nodes:
                decision_result = await self._execute_decision_node(
                    run=run,
                    plan=plan,
                    node=node,
                    completed=completed,
                    failed=failed,
                )
                executed.append(node.node_key)
                if decision_result.status is GraphExecutionStatus.PAUSED:
                    return GraphExecutionResult(
                        status=GraphExecutionStatus.PAUSED,
                        workflow_run_id=workflow_run_id,
                        executed_node_keys=tuple(executed),
                        skipped_node_keys=tuple(skipped),
                        wave_count=wave_count,
                        pause_reason=decision_result.pause_reason,
                    )
                if decision_result.status is GraphExecutionStatus.FAILED:
                    return GraphExecutionResult(
                        status=GraphExecutionStatus.FAILED,
                        workflow_run_id=workflow_run_id,
                        executed_node_keys=tuple(executed),
                        skipped_node_keys=tuple(skipped),
                        wave_count=wave_count,
                        failure_reason=decision_result.failure_reason,
                    )
                if decision_result.final_output_ref is not None:
                    completed[node.node_key] = decision_result.final_output_ref

    async def _prepare_role_node(
        self,
        *,
        run: Any,
        plan: GraphExecutionPlan,
        node: GraphNode,
        completed: Mapping[str, dict[str, object]],
    ) -> tuple[GraphNode, Any, RoleExecutionContext]:
        role = plan.roles_by_key[node.role_key or ""]
        input_summary = _input_summary(plan, node, completed)
        step = await self.repository.create_run_step(
            workflow_run_id=run.workflow_run_id,
            tenant_id=run.tenant_id,
            step_key=node.node_key,
            step_type="agent",
            status=RuntimeStepStatus.RUNNING,
            input_ref=dict(input_summary),
        )
        await self._timeline(
            run,
            "graph_node_started",
            {"node_key": node.node_key, "role_key": role.role_key},
            run_step_id=step.run_step_id,
        )
        return (
            node,
            step,
            RoleExecutionContext(
                workflow_run_id=run.workflow_run_id,
                tenant_id=run.tenant_id,
                trace_id=run.trace_id,
                node_key=node.node_key,
                role_key=role.role_key,
                role_kind=role.role_kind,
                attempt=step.attempt,
                input_summary=input_summary,
                pinned_context={
                    "profile_reference_key": role.profile_reference_key,
                    "skill_installation_keys": list(role.skill_installation_keys),
                    "output_contract_key": role.output_contract_key,
                    "output_contract_schema": dict(
                        plan.contracts_by_key.get(role.output_contract_key or "", {})
                    ),
                    "execution_mode": role.execution_mode,
                    "agent_profile_version_id": str(role.agent_profile_version_id)
                    if role.agent_profile_version_id
                    else None,
                },
                run_step_id=step.run_step_id,
                run_bundle_id=run.run_bundle_id,
                workflow_version_bundle_id=plan.workflow_version_bundle_id,
            ),
        )

    async def _finalize_role_node(
        self,
        *,
        run: Any,
        plan: GraphExecutionPlan,
        node: GraphNode,
        run_step_id: UUID,
        result: RoleExecutionResult,
    ) -> None:
        if result.succeeded:
            output_ref = _result_output_ref(node_key=node.node_key, result=result)
            await self.repository.update_run_step(
                run_step_id=run_step_id,
                status=RuntimeStepStatus.SUCCEEDED,
                output_ref=output_ref,
            )
            await self._persist_success_evidence(
                run=run,
                plan=plan,
                node=node,
                run_step_id=run_step_id,
                output_ref=output_ref,
            )
        else:
            error_ref = _result_error_ref(result)
            await self.repository.update_run_step(
                run_step_id=run_step_id,
                status=RuntimeStepStatus.FAILED,
                error_ref=error_ref,
            )
            await self._timeline(
                run,
                "graph_node_failed",
                {"node_key": node.node_key, "error_code": result.error_code},
                run_step_id=run_step_id,
            )

    async def _execute_decision_node(
        self,
        *,
        run: Any,
        plan: GraphExecutionPlan,
        node: GraphNode,
        completed: dict[str, dict[str, object]],
        failed: dict[str, dict[str, object]],
    ) -> GraphExecutionResult:
        step = await self.repository.create_run_step(
            workflow_run_id=run.workflow_run_id,
            tenant_id=run.tenant_id,
            step_key=node.node_key,
            step_type="system",
            status=RuntimeStepStatus.RUNNING,
            input_ref=_input_summary(plan, node, completed),
        )
        if node.node_type == "join":
            return await self._execute_join_node(
                run=run,
                plan=plan,
                node=node,
                run_step_id=step.run_step_id,
                completed=completed,
                failed=failed,
            )
        if node.node_type == "terminal":
            output_ref = self._terminal_output_ref(plan, node, completed)
            await self.repository.update_run_step(
                run_step_id=step.run_step_id,
                status=RuntimeStepStatus.SUCCEEDED,
                output_ref=output_ref,
            )
            await self._record_interaction(
                run=run,
                source_node_key=node.node_key,
                target_node_key=None,
                interaction_kind=RuntimeInteractionKind.RUN_COMPLETION,
                status=RuntimeInteractionStatus.COMPLETED,
                safe_summary=(
                    f"{plan.workflow_key} completed at terminal node {node.node_key}."
                ),
                stable_ref={
                    "run_step_id": str(step.run_step_id),
                    "terminal": node.node_key,
                },
                source_run_step_id=step.run_step_id,
                metadata={
                    "workflow_key": plan.workflow_key,
                    "terminal_node_key": node.node_key,
                    "output_ref": output_ref,
                },
            )
            await self._timeline(
                run,
                "graph_final_output_persisted",
                {"terminal_node_key": node.node_key},
                run_step_id=step.run_step_id,
            )
            return GraphExecutionResult(
                status=GraphExecutionStatus.SUCCEEDED,
                workflow_run_id=run.workflow_run_id,
                final_output_ref=output_ref,
            )
        if node.node_type == "approval":
            await self.repository.update_run_status(
                workflow_run_id=run.workflow_run_id,
                status=RuntimeRunStatus.PAUSED,
                pause_reason=f"approval required at {node.node_key}",
            )
            await self.repository.update_run_step(
                run_step_id=step.run_step_id,
                status=RuntimeStepStatus.PAUSED,
                output_ref={"safe_summary": "Approval node paused execution."},
            )
            await self._record_interaction(
                run=run,
                source_node_key=node.node_key,
                target_node_key=None,
                interaction_kind=RuntimeInteractionKind.APPROVAL_PAUSE,
                status=RuntimeInteractionStatus.PAUSED,
                safe_summary=f"Approval required at {node.node_key}.",
                stable_ref={
                    "run_step_id": str(step.run_step_id),
                    "approval": node.node_key,
                },
                source_run_step_id=step.run_step_id,
                metadata={
                    "approval_node_key": node.node_key,
                    "pause_reason": f"approval required at {node.node_key}",
                },
            )
            return GraphExecutionResult(
                status=GraphExecutionStatus.PAUSED,
                workflow_run_id=run.workflow_run_id,
                pause_reason=f"approval required at {node.node_key}",
            )
        output_ref = safe_graph_ref(
            source=node.node_key,
            payload={"node_key": node.node_key, "node_type": node.node_type},
            safe_summary=f"{node.node_key} completed.",
        )
        await self.repository.update_run_step(
            run_step_id=step.run_step_id,
            status=RuntimeStepStatus.SUCCEEDED,
            output_ref=output_ref,
        )
        return GraphExecutionResult(
            status=GraphExecutionStatus.SUCCEEDED,
            workflow_run_id=run.workflow_run_id,
            final_output_ref=output_ref,
        )

    async def _execute_join_node(
        self,
        *,
        run: Any,
        plan: GraphExecutionPlan,
        node: GraphNode,
        run_step_id: UUID,
        completed: dict[str, dict[str, object]],
        failed: dict[str, dict[str, object]],
    ) -> GraphExecutionResult:
        policy = _join_policy_for_node(plan, node)
        branch_results = _branch_results_for_join(
            plan,
            node,
            completed=completed,
            failed=failed,
        )
        decision = evaluate_join_policy(policy, branch_results)
        for result in branch_results:
            await self._record_interaction(
                run=run,
                source_node_key=result.node_key,
                target_node_key=node.node_key,
                interaction_kind=RuntimeInteractionKind.JOIN_CONTRIBUTION,
                status=RuntimeInteractionStatus.COMPLETED
                if result.status == "succeeded"
                else RuntimeInteractionStatus.FAILED,
                safe_summary=(
                    result.safe_summary
                    or (
                        f"{result.node_key} contributed {result.status} evidence "
                        f"to {node.node_key}."
                    )
                ),
                stable_ref={
                    "join_node_key": node.node_key,
                    "source_node_key": result.node_key,
                    "status": result.status,
                    "run_step_id": str(run_step_id),
                },
                target_run_step_id=run_step_id,
                metadata={
                    "join_node_key": node.node_key,
                    "source_node_key": result.node_key,
                    "join_policy_key": policy.join_policy_key,
                    "branch_status": result.status,
                    "output_ref": result.output_ref,
                    "error_code": result.error_code,
                },
            )
        payload = {
            "node_key": node.node_key,
            "join_policy_key": policy.join_policy_key,
            "decision": decision.decision.value,
            "successful_branch_count": decision.successful_branch_count,
            "failed_branch_count": decision.failed_branch_count,
            "winning_branch_key": decision.winning_branch_key,
        }
        await self._timeline(
            run,
            "graph_join_evaluated",
            payload,
            run_step_id=run_step_id,
        )
        if decision.decision is JoinDecisionType.PROCEED:
            output_ref = safe_graph_ref(
                source=node.node_key,
                payload={
                    "branch_results": [
                        {
                            "node_key": result.node_key,
                            "status": result.status,
                            "safe_summary": result.safe_summary,
                        }
                        for result in branch_results
                    ],
                    "decision": decision.decision.value,
                },
                safe_summary=decision.safe_summary,
            )
            await self.repository.update_run_step(
                run_step_id=run_step_id,
                status=RuntimeStepStatus.SUCCEEDED,
                output_ref=output_ref,
            )
            await self._persist_success_evidence(
                run=run,
                plan=plan,
                node=node,
                run_step_id=run_step_id,
                output_ref=output_ref,
            )
            return GraphExecutionResult(
                status=GraphExecutionStatus.SUCCEEDED,
                workflow_run_id=run.workflow_run_id,
                final_output_ref=output_ref,
            )
        if decision.decision is JoinDecisionType.PAUSE_MANUAL_RESOLUTION:
            partial = {
                "safe_summary": decision.safe_summary,
                "failed_node_keys": [
                    result.node_key
                    for result in branch_results
                    if result.status == "failed"
                ],
                "successful_node_keys": [
                    result.node_key
                    for result in branch_results
                    if result.status == "succeeded"
                ],
                "manual_resolution_required": True,
            }
            await self.repository.update_run_step(
                run_step_id=run_step_id,
                status=RuntimeStepStatus.PAUSED,
                error_ref=partial,
            )
            await self.repository.create_approval_gate(
                tenant_id=run.tenant_id,
                workflow_run_id=run.workflow_run_id,
                run_step_id=run_step_id,
                approval_key=f"{node.node_key}:manual-resolution",
                requested_action=partial,
            )
            await self.repository.update_run_status(
                workflow_run_id=run.workflow_run_id,
                status=RuntimeRunStatus.PAUSED,
                pause_reason=decision.safe_summary,
            )
            await self._record_interaction(
                run=run,
                source_node_key=node.node_key,
                target_node_key=None,
                interaction_kind=RuntimeInteractionKind.MANUAL_RESOLUTION,
                status=RuntimeInteractionStatus.PAUSED,
                safe_summary=decision.safe_summary,
                stable_ref={
                    "join_node_key": node.node_key,
                    "manual_resolution": True,
                    "run_step_id": str(run_step_id),
                },
                source_run_step_id=run_step_id,
                metadata=partial,
            )
            await self._timeline(
                run,
                "graph_manual_resolution_required",
                partial,
                run_step_id=run_step_id,
            )
            return GraphExecutionResult(
                status=GraphExecutionStatus.PAUSED,
                workflow_run_id=run.workflow_run_id,
                pause_reason=decision.safe_summary,
            )
        reason = decision.safe_summary
        await self.repository.update_run_step(
            run_step_id=run_step_id,
            status=RuntimeStepStatus.FAILED,
            error_ref={"safe_summary": reason},
        )
        await self._fail_run(run, reason=reason, worker_id="graph-executor")
        return GraphExecutionResult(
            status=GraphExecutionStatus.FAILED,
            workflow_run_id=run.workflow_run_id,
            failure_reason=reason,
        )

    def _ready_nodes(
        self,
        plan: GraphExecutionPlan,
        *,
        completed: Mapping[str, dict[str, object]],
        failed: Mapping[str, dict[str, object]],
    ) -> list[GraphNode]:
        terminal = set(completed) | set(failed)
        ready: list[GraphNode] = []
        for node in plan.nodes_by_key.values():
            if node.node_key in terminal:
                continue
            inbound = plan.inbound_edges_by_target.get(node.node_key, ())
            if node.node_key == plan.entry_node_key and not inbound:
                ready.append(node)
                continue
            if node.node_type == "join":
                if _join_can_evaluate(plan, node, completed=completed, failed=failed):
                    ready.append(node)
                continue
            if inbound and all(edge.source_node_key in completed for edge in inbound):
                ready.append(node)
        return ready

    async def _persist_success_evidence(
        self,
        *,
        run: Any,
        plan: GraphExecutionPlan,
        node: GraphNode,
        run_step_id: UUID,
        output_ref: dict[str, object],
    ) -> None:
        checkpoint_id = f"{node.node_key}:{run_step_id}"
        await self.repository.create_checkpoint_ref(
            tenant_id=run.tenant_id,
            workflow_run_id=run.workflow_run_id,
            run_step_id=run_step_id,
            checkpoint_id=checkpoint_id,
            checkpoint_kind="terminal" if node.node_type == "terminal" else "superstep",
            bundle_digest=run.bundle_digest if hasattr(run, "bundle_digest") else "",
        )
        await self._record_interaction(
            run=run,
            source_node_key=node.node_key,
            target_node_key=None,
            interaction_kind=RuntimeInteractionKind.RESULT_RETURN,
            status=RuntimeInteractionStatus.COMPLETED,
            safe_summary=f"{node.node_key} produced safe result evidence.",
            stable_ref={
                "run_step_id": str(run_step_id),
                "result": node.node_key,
            },
            source_run_step_id=run_step_id,
            metadata={
                "node_key": node.node_key,
                "node_type": node.node_type,
                "output_ref": output_ref,
            },
        )
        for edge in plan.outbound_edges_by_source.get(node.node_key, ()):
            contract_key = edge.contract_key or "handoff"
            contract_schema = plan.contracts_by_key.get(contract_key, {})
            await self.repository.create_handoff_envelope(
                tenant_id=run.tenant_id,
                workflow_run_id=run.workflow_run_id,
                sender_step_id=run_step_id,
                receiver_step_key=edge.target_node_key,
                contract_id=contract_key,
                contract_version="1.0.0",
                contract_digest=sha256_digest(contract_schema),
                payload_ref=output_ref,
            )
            await self._record_interaction(
                run=run,
                source_node_key=edge.source_node_key,
                target_node_key=edge.target_node_key,
                interaction_kind=RuntimeInteractionKind.HANDOFF,
                status=RuntimeInteractionStatus.SENT,
                safe_summary=(
                    f"{edge.source_node_key} sent safe context to "
                    f"{edge.target_node_key}."
                ),
                stable_ref={
                    "run_step_id": str(run_step_id),
                    "edge_key": edge.edge_key,
                    "kind": "handoff",
                },
                source_run_step_id=run_step_id,
                metadata={
                    "edge_key": edge.edge_key,
                    "contract_key": contract_key,
                    "contract_digest": sha256_digest(contract_schema),
                    "payload_ref": output_ref,
                },
            )
        node_role = plan.roles_by_key.get(node.role_key or "")
        if node_role is not None:
            for skill_key in node_role.skill_installation_keys:
                await self.repository.create_side_effect_intent(
                    tenant_id=run.tenant_id,
                    workflow_run_id=run.workflow_run_id,
                    run_step_id=run_step_id,
                    intent_kind="mock_skill_boundary",
                    idempotency_key=f"{run.workflow_run_id}:{node.node_key}:{skill_key}",
                    tool_policy_ref=f"mock:{skill_key}",
                    request_ref={"safe_summary": f"Mock readiness for {skill_key}"},
                    result_ref={"safe_summary": "No external call executed in QA."},
                )
        await self._timeline(
            run,
            "graph_checkpoint_recorded",
            {"node_key": node.node_key, "checkpoint_id": checkpoint_id},
            run_step_id=run_step_id,
        )
        await self._timeline(
            run,
            "graph_node_succeeded",
            {"node_key": node.node_key},
            run_step_id=run_step_id,
        )

    async def _timeline(
        self,
        run: Any,
        event_type: str,
        payload: Mapping[str, object],
        *,
        run_step_id: UUID | None = None,
    ) -> None:
        await self.repository.create_graph_timeline_event(
            tenant_id=run.tenant_id,
            workflow_run_id=run.workflow_run_id,
            run_step_id=run_step_id,
            event_type=event_type,
            payload=dict(payload),
            trace_id=run.trace_id,
        )

    async def _record_interaction(
        self,
        *,
        run: Any,
        source_node_key: str,
        target_node_key: str | None,
        interaction_kind: RuntimeInteractionKind,
        status: RuntimeInteractionStatus,
        safe_summary: str,
        stable_ref: object,
        metadata: Mapping[str, object],
        source_run_step_id: UUID | None = None,
        target_run_step_id: UUID | None = None,
        timeline_event_id: UUID | None = None,
    ) -> None:
        await record_runtime_interaction(
            self.repository,
            tenant_id=run.tenant_id,
            workflow_run_id=run.workflow_run_id,
            source_node_key=source_node_key,
            target_node_key=target_node_key,
            source_run_step_id=source_run_step_id,
            target_run_step_id=target_run_step_id,
            timeline_event_id=timeline_event_id,
            interaction_kind=interaction_kind,
            status=status,
            safe_summary=safe_summary,
            idempotency_key=interaction_idempotency_key(
                workflow_run_id=run.workflow_run_id,
                source_node_key=source_node_key,
                target_node_key=target_node_key,
                interaction_kind=interaction_kind,
                stable_ref=stable_ref,
            ),
            metadata={
                "trace_id": run.trace_id,
                "run_bundle_id": str(run.run_bundle_id),
                "instrumentation": "graph_execution",
                **dict(metadata),
            },
        )

    async def _fail_run(self, run: Any, *, reason: str, worker_id: str) -> None:
        await self.repository.update_run_status(
            workflow_run_id=run.workflow_run_id,
            status=RuntimeRunStatus.FAILED,
            terminal_reason=reason,
        )
        await self._timeline(
            run,
            "graph_run_failed",
            {"safe_reason": reason, "worker_id": worker_id},
        )

    def _terminal_output_ref(
        self,
        plan: GraphExecutionPlan,
        node: GraphNode,
        completed: Mapping[str, dict[str, object]],
    ) -> dict[str, object]:
        upstream = _input_summary(plan, node, completed)
        return safe_graph_ref(
            source=node.node_key,
            payload={
                "terminal_node_key": node.node_key,
                "upstream": upstream,
            },
            safe_summary=(
                f"{plan.workflow_key} completed at terminal node {node.node_key}."
            ),
        )

    def _assert_tenant_compatible(self, *, run: Any, version: Any | None) -> None:
        if version is None:
            return
        version_tenant_id = getattr(version, "tenant_id", None)
        version_scope_type = getattr(version, "scope_type", None)
        if version_scope_type == "tenant" and version_tenant_id != run.tenant_id:
            raise GraphValidationError("published workflow bundle tenant mismatch")
        if run.tenant_id is None and version_tenant_id is not None:
            raise GraphValidationError("platform run cannot execute tenant bundle")


def _result_output_ref(
    *,
    node_key: str,
    result: RoleExecutionResult,
) -> dict[str, object]:
    output_ref: dict[str, object] = {
        "source": node_key,
        "safe_summary": result.safe_summary,
        "payload_digest": result.payload_digest,
        "structured_output": result.structured_output,
    }
    if result.usage_summary:
        output_ref["usage_summary"] = dict(result.usage_summary)
    if result.provenance:
        output_ref["provenance"] = dict(result.provenance)
    if result.artifact_refs:
        output_ref["artifact_refs"] = [dict(item) for item in result.artifact_refs]
    return output_ref


def _result_error_ref(result: RoleExecutionResult) -> dict[str, object]:
    error_ref: dict[str, object] = {
        "safe_summary": result.safe_summary,
        "error_code": result.error_code or "role_node_failed",
        "payload_digest": result.payload_digest,
    }
    if result.structured_output:
        error_ref["structured_output"] = result.structured_output
    if result.provenance:
        error_ref["provenance"] = dict(result.provenance)
    return error_ref


async def _extract_workflow_document(
    repository: Any,
    workflow_version: Mapping[str, object],
    version: Any | None,
) -> Mapping[str, object]:
    candidates: list[object] = [
        workflow_version.get("document"),
        workflow_version.get("workflow_document"),
    ]
    if version is not None:
        summary_json = getattr(version, "summary_json", None)
        if isinstance(summary_json, Mapping):
            candidates.extend(
                [
                    summary_json.get("document"),
                    summary_json.get("workflow_document"),
                    summary_json.get("compiled_bundle"),
                ]
            )
            run_version_bundle = summary_json.get("run_version_bundle")
            if isinstance(run_version_bundle, Mapping):
                candidates.append(run_version_bundle.get("document"))
    for candidate in candidates:
        if isinstance(candidate, Mapping):
            document = candidate.get("document")
            if isinstance(document, Mapping):
                return document
            if "nodes" in candidate:
                return candidate
    get_revision = getattr(repository, "get_workflow_draft_revision", None)
    revision_id = getattr(version, "published_from_revision_id", None)
    if callable(get_revision) and revision_id is not None:
        revision = await get_revision(workflow_draft_revision_id=revision_id)
        if revision is not None:
            document_json = getattr(revision, "authoring_document_json", None)
            if isinstance(document_json, Mapping):
                return document_json
    raise GraphValidationError("published workflow bundle has no executable document")


def _join_policy_for_node(
    plan: GraphExecutionPlan,
    node: GraphNode,
) -> GraphJoinPolicy:
    if node.join_policy_key is not None:
        return plan.join_policies_by_key[node.join_policy_key]
    if len(plan.join_policies_by_key) == 1:
        return next(iter(plan.join_policies_by_key.values()))
    fallback = plan.join_policies_by_key.get(f"{node.node_key}-join-policy")
    if fallback is not None:
        return fallback
    raise GraphValidationError(f"join node {node.node_key} has no join policy")


def _branch_results_for_join(
    plan: GraphExecutionPlan,
    node: GraphNode,
    *,
    completed: Mapping[str, dict[str, object]],
    failed: Mapping[str, dict[str, object]],
) -> list[BranchResult]:
    results: list[BranchResult] = []
    for edge in plan.inbound_edges_by_target.get(node.node_key, ()):
        if edge.source_node_key in completed:
            output_ref = completed[edge.source_node_key]
            results.append(
                BranchResult(
                    node_key=edge.source_node_key,
                    status="succeeded",
                    output_ref=output_ref,
                    safe_summary=_safe_summary(output_ref),
                )
            )
        elif edge.source_node_key in failed:
            error_ref = failed[edge.source_node_key]
            results.append(
                BranchResult(
                    node_key=edge.source_node_key,
                    status="failed",
                    safe_summary=_safe_summary(error_ref),
                    error_code=str(error_ref.get("error_code") or "branch_failed"),
                )
            )
    return results


def _join_can_evaluate(
    plan: GraphExecutionPlan,
    node: GraphNode,
    *,
    completed: Mapping[str, dict[str, object]],
    failed: Mapping[str, dict[str, object]],
) -> bool:
    inbound = plan.inbound_edges_by_target.get(node.node_key, ())
    if not inbound:
        return True
    policy = _join_policy_for_node(plan, node)
    if policy.strategy == "first_success" and any(
        edge.source_node_key in completed for edge in inbound
    ):
        return True
    terminal = set(completed) | set(failed)
    return all(edge.source_node_key in terminal for edge in inbound)


def _input_summary(
    plan: GraphExecutionPlan,
    node: GraphNode,
    completed: Mapping[str, dict[str, object]],
) -> dict[str, object]:
    inbound = plan.inbound_edges_by_target.get(node.node_key, ())
    upstream_node_keys = [edge.source_node_key for edge in inbound]
    return {
        "node_key": node.node_key,
        "upstream_node_keys": upstream_node_keys,
        "contract_keys": [
            edge.contract_key for edge in inbound if edge.contract_key is not None
        ],
        "upstream_summaries": {
            key: _safe_summary(completed.get(key, {})) for key in upstream_node_keys
        },
    }


def _safe_summary(ref: Mapping[str, object]) -> str:
    return str(ref.get("safe_summary") or "No safe summary recorded.")


def _group_edges(
    edges: Sequence[GraphEdge] | Any,
    *,
    by_source: bool,
) -> dict[str, tuple[GraphEdge, ...]]:
    grouped: dict[str, list[GraphEdge]] = {}
    for edge in edges:
        key = edge.source_node_key if by_source else edge.target_node_key
        grouped.setdefault(key, []).append(edge)
    return {key: tuple(value) for key, value in grouped.items()}


def _assert_acyclic(plan: GraphExecutionPlan) -> None:
    incoming_counts = {
        node_key: len(plan.inbound_edges_by_target.get(node_key, ()))
        for node_key in plan.nodes_by_key
    }
    queue = deque(node_key for node_key, count in incoming_counts.items() if count == 0)
    visited = 0
    while queue:
        node_key = queue.popleft()
        visited += 1
        for edge in plan.outbound_edges_by_source.get(node_key, ()):
            incoming_counts[edge.target_node_key] -= 1
            if incoming_counts[edge.target_node_key] == 0:
                queue.append(edge.target_node_key)
    if visited != len(plan.nodes_by_key):
        raise GraphValidationError("workflow graph must be acyclic")


def _as_sequence(value: object) -> Sequence[object]:
    if value is None:
        return ()
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return value
    raise GraphValidationError("expected a list")


def _as_mapping(value: object, label: str) -> Mapping[str, object]:
    if isinstance(value, Mapping):
        return value
    raise GraphValidationError(f"{label} must be an object")


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    return str(value)


def _optional_int(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, str):
        return int(value)
    raise GraphValidationError("expected integer")


def _optional_uuid(value: object) -> UUID | None:
    if value is None or value == "":
        return None
    try:
        return value if isinstance(value, UUID) else UUID(str(value))
    except (TypeError, ValueError) as exc:
        raise GraphValidationError("expected UUID") from exc


def utc_now() -> datetime:
    return datetime.now(UTC)


def graph_execution_id() -> UUID:
    return uuid4()
