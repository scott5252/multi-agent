from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from multi_agent_platform.api.schemas.workflow_editor import (
    GraphPreviewEdge,
    GraphPreviewNode,
    GraphPreviewResponse,
    GraphPreviewSummary,
    GraphValidationBadge,
)
from multi_agent_platform.api.schemas.workflow_registry import WorkflowDraftDocument


def build_graph_preview(
    document: WorkflowDraftDocument,
    *,
    findings: Iterable[dict[str, object]] = (),
) -> GraphPreviewResponse:
    """Build the server-owned graph projection used by UI and validation."""

    badges_by_element: dict[str, list[GraphValidationBadge]] = defaultdict(list)
    for finding in findings:
        graph_element_id = finding.get("graph_element_id")
        if not isinstance(graph_element_id, str) or not graph_element_id:
            continue
        badges_by_element[graph_element_id].append(
            GraphValidationBadge(
                code=str(finding.get("code") or finding.get("category") or "finding"),
                severity=str(finding.get("severity") or "advisory"),
                message=str(finding.get("message") or "Validation finding"),
                blocking=bool(finding.get("blocking", False)),
            )
        )

    nodes: list[GraphPreviewNode] = []
    field_to_graph: dict[str, str] = {}
    for index, node in enumerate(document.nodes):
        node_id = node_element_id(node.node_key)
        field_path = f"nodes[{index}]"
        field_to_graph[field_path] = node_id
        nodes.append(
            GraphPreviewNode(
                id=node_id,
                node_key=node.node_key,
                node_type=node.node_type.value,
                label=node.display_name,
                field_path=field_path,
                role_key=node.role_key,
                terminal=node.node_type.value == "terminal",
                badges=badges_by_element.get(node_id, []),
            )
        )

    edges: list[GraphPreviewEdge] = []
    for index, edge in enumerate(document.edges):
        edge_id = edge_element_id(edge.edge_key)
        field_path = f"edges[{index}]"
        field_to_graph[field_path] = edge_id
        edges.append(
            GraphPreviewEdge(
                id=edge_id,
                edge_key=edge.edge_key,
                source=node_element_id(edge.source_node_key),
                target=node_element_id(edge.target_node_key),
                label=f"{edge.source_node_key} -> {edge.target_node_key}",
                field_path=field_path,
                contract_key=edge.contract_key,
                edge_type=edge.edge_type,
                badges=badges_by_element.get(edge_id, []),
            )
        )

    disconnected_node_ids = _disconnected_node_ids(document)
    cycle_summaries = _cycle_summaries(document)
    summary = GraphPreviewSummary(
        entry_node_id=node_element_id(document.entry_node_key)
        if document.nodes
        else None,
        terminal_node_ids=[
            node_element_id(node.node_key)
            for node in document.nodes
            if node.node_type.value == "terminal"
        ],
        node_count=len(nodes),
        edge_count=len(edges),
        disconnected_node_ids=disconnected_node_ids,
        cycle_summaries=cycle_summaries,
        join_summaries=[
            f"{policy.join_policy_key}:{policy.strategy}"
            for policy in document.join_policies
        ],
        approval_loop_summaries=[
            f"{gate.approval_gate_key}:{gate.resume_behavior}"
            for gate in document.approval_gates
            if gate.resume_behavior
        ],
    )
    return GraphPreviewResponse(
        nodes=nodes,
        edges=edges,
        summary=summary,
        field_to_graph=field_to_graph,
    )


def validate_graph_policy(document: WorkflowDraftDocument) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    outgoing: dict[str, list[object]] = defaultdict(list)
    incoming: dict[str, int] = defaultdict(int)
    for edge in document.edges:
        outgoing[edge.source_node_key].append(edge)
        incoming[edge.target_node_key] += 1
        if edge.loop_type and edge.loop_type not in {"retry", "approval_resume"}:
            edge_index = _edge_index(document, edge.edge_key)
            findings.append(
                _graph_blocking(
                    category="graph_policy",
                    code="graph.loop_type.invalid",
                    field_path=f"edges[{edge_index}].loop_type",
                    graph_element_id=edge_element_id(edge.edge_key),
                    message="Loop type must be retry or approval_resume.",
                    remediation="Choose a supported bounded loop type or remove it.",
                )
            )
        if edge.source_node_key == edge.target_node_key and not _is_bounded_loop(edge):
            edge_index = _edge_index(document, edge.edge_key)
            findings.append(
                _graph_blocking(
                    category="graph_policy",
                    code="graph.self_cycle.unbounded",
                    field_path=f"edges[{edge_index}]",
                    graph_element_id=edge_element_id(edge.edge_key),
                    message=(
                        "Self cycles must declare bounded retry or approval-resume "
                        "semantics."
                    ),
                    remediation="Add loop_type with max_attempts or timeout_seconds.",
                )
            )

    reachable = _reachable_nodes(document.entry_node_key, outgoing)
    for index, node in enumerate(document.nodes):
        node_id = node_element_id(node.node_key)
        if node.active and node.node_key not in reachable:
            findings.append(
                _graph_blocking(
                    category="graph_policy",
                    code="graph.node.disconnected",
                    field_path=f"nodes[{index}]",
                    graph_element_id=node_id,
                    message="Active graph nodes must be reachable from the entry node.",
                    remediation=(
                        "Connect the node to the entry path or mark it inactive."
                    ),
                )
            )
        if (
            node.active
            and node.node_type.value != "terminal"
            and not outgoing.get(node.node_key)
            and (document.edges or len(document.nodes) > 1)
        ):
            findings.append(
                _graph_blocking(
                    category="graph_policy",
                    code="graph.node.missing_outgoing",
                    field_path=f"nodes[{index}]",
                    graph_element_id=node_id,
                    message="Non-terminal graph nodes need at least one outgoing edge.",
                    remediation=(
                        "Add a success, failure, retry, or approval-resume edge."
                    ),
                )
            )
        if node.node_type.value == "join" and node.join_policy_key is None:
            findings.append(
                _graph_blocking(
                    category="join_policy",
                    code="graph.join.missing_policy",
                    field_path=f"nodes[{index}].join_policy_key",
                    graph_element_id=node_id,
                    message="Join nodes must reference a join policy.",
                    remediation="Select a join policy for this node.",
                )
            )

    for cycle in _find_cycles(document, outgoing):
        if not _cycle_is_allowed(cycle, document):
            findings.append(
                _graph_blocking(
                    category="graph_policy",
                    code="graph.cycle.unbounded",
                    field_path="edges",
                    graph_element_id=edge_element_id(cycle[-1]),
                    message="Arbitrary graph cycles are blocked before publish.",
                    remediation=(
                        "Model the loop as a bounded retry or approval-resume path."
                    ),
                )
            )
    return findings


def node_element_id(node_key: str) -> str:
    return f"node:{node_key}"


def edge_element_id(edge_key: str) -> str:
    return f"edge:{edge_key}"


def _disconnected_node_ids(document: WorkflowDraftDocument) -> list[str]:
    outgoing: dict[str, list[object]] = defaultdict(list)
    for edge in document.edges:
        outgoing[edge.source_node_key].append(edge)
    reachable = _reachable_nodes(document.entry_node_key, outgoing)
    return [
        node_element_id(node.node_key)
        for node in document.nodes
        if node.active and node.node_key not in reachable
    ]


def _cycle_summaries(document: WorkflowDraftDocument) -> list[str]:
    outgoing: dict[str, list[object]] = defaultdict(list)
    for edge in document.edges:
        outgoing[edge.source_node_key].append(edge)
    return [" -> ".join(cycle) for cycle in _find_cycles(document, outgoing)]


def _reachable_nodes(
    entry_node_key: str, outgoing: dict[str, list[object]]
) -> set[str]:
    seen: set[str] = set()
    stack = [entry_node_key]
    while stack:
        current = stack.pop()
        if current in seen:
            continue
        seen.add(current)
        for edge in outgoing.get(current, []):
            target = getattr(edge, "target_node_key", None)
            if isinstance(target, str):
                stack.append(target)
    return seen


def _find_cycles(
    document: WorkflowDraftDocument,
    outgoing: dict[str, list[object]],
) -> list[list[str]]:
    cycles: list[list[str]] = []
    stack: list[str] = []
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node_key: str) -> None:
        if node_key in visiting:
            cycle_start = stack.index(node_key)
            cycles.append([*stack[cycle_start:], node_key])
            return
        if node_key in visited:
            return
        visiting.add(node_key)
        stack.append(node_key)
        for edge in outgoing.get(node_key, []):
            target = getattr(edge, "target_node_key", None)
            if isinstance(target, str):
                visit(target)
        stack.pop()
        visiting.remove(node_key)
        visited.add(node_key)

    for node in document.nodes:
        visit(node.node_key)
    return cycles


def _cycle_is_allowed(cycle: list[str], document: WorkflowDraftDocument) -> bool:
    cycle_edges = [
        edge
        for edge in document.edges
        if edge.source_node_key in cycle and edge.target_node_key in cycle
    ]
    return bool(cycle_edges) and all(_is_bounded_loop(edge) for edge in cycle_edges)


def _is_bounded_loop(edge: object) -> bool:
    loop_type = getattr(edge, "loop_type", None)
    max_attempts = getattr(edge, "max_attempts", None)
    timeout_seconds = getattr(edge, "timeout_seconds", None)
    return loop_type in {"retry", "approval_resume"} and (
        isinstance(max_attempts, int)
        and max_attempts > 0
        or isinstance(timeout_seconds, int)
        and timeout_seconds > 0
    )


def _edge_index(document: WorkflowDraftDocument, edge_key: str) -> int:
    for index, edge in enumerate(document.edges):
        if edge.edge_key == edge_key:
            return index
    return 0


def _graph_blocking(
    *,
    category: str,
    code: str,
    field_path: str,
    graph_element_id: str,
    message: str,
    remediation: str,
) -> dict[str, object]:
    return {
        "category": category,
        "severity": "blocking",
        "message": message,
        "field_path": field_path,
        "section_key": _section_for_field_path(field_path),
        "code": code,
        "remediation": remediation,
        "blocking": True,
        "graph_element_id": graph_element_id,
    }


def _section_for_field_path(field_path: str) -> str:
    if field_path.startswith("nodes") or field_path.startswith("edges"):
        return "graph"
    if field_path.startswith("join_policies"):
        return "joins"
    if field_path.startswith("approval_gates"):
        return "approvals"
    return field_path.split("[", maxsplit=1)[0]
