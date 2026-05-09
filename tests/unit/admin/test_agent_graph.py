from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from multi_agent_platform.admin.workflow_registry.agent_graph import (
    _badge_severity,
    _node_by_key,
    _reference_status,
    _subworkflow_by_alias,
    build_draft_agent_graph,
    build_published_agent_graph,
)
from multi_agent_platform.api.schemas.admin_agent_graph import (
    AgentGraphBadgeSeverity,
    AgentGraphEdgeCategory,
    AgentGraphNodeCategory,
    AgentGraphReferenceStatus,
    AgentGraphReferenceType,
    AgentGraphSource,
    AgentGraphState,
)
from multi_agent_platform.api.schemas.workflow_registry import (
    ValidationFindingResponse,
    ValidationResultResponse,
    WorkflowDraftDocument,
    WorkflowDraftResponse,
    WorkflowDraftRevisionResponse,
    WorkflowScopeType,
    WorkflowVersionResponse,
)


def _document() -> WorkflowDraftDocument:
    return WorkflowDraftDocument.model_validate(
        {
            "workflow_key": "agent-review",
            "display_name": "Agent Review",
            "description": "Coordinate specialist review and handoff.",
            "workflow_kind": "main_workflow",
            "entry_node_key": "coordinator",
            "roles": [
                {
                    "role_key": "coordinator",
                    "display_name": "Coordinator",
                    "role_kind": "agent",
                    "purpose": "Coordinate specialist work.",
                    "input_contract_key": "request",
                    "output_contract_key": "brief",
                    "skill_bindings": [
                        {
                            "binding_key": "coordinator-tool",
                            "skill_slug": "coordinator-tool",
                            "skill_version": "2026.05.0",
                            "purpose": "Prepare safe context.",
                        }
                    ],
                    "graph_node_keys": ["coordinator"],
                },
                {
                    "role_key": "specialist",
                    "display_name": "Specialist",
                    "role_kind": "subagent",
                    "purpose": "Review the request.",
                    "input_contract_key": "brief",
                    "output_contract_key": "result",
                    "graph_node_keys": ["specialist"],
                },
                {
                    "role_key": "handoff",
                    "display_name": "Handoff",
                    "purpose": "Prepare development handoff.",
                    "input_contract_key": "handoff",
                    "output_contract_key": "handoff",
                    "graph_node_keys": ["handoff"],
                },
            ],
            "contracts": [
                {"contract_key": "request", "json_schema": {"type": "object"}},
                {"contract_key": "brief", "json_schema": {"type": "object"}},
                {"contract_key": "result", "json_schema": {"type": "object"}},
                {
                    "contract_key": "handoff",
                    "contract_kind": "handoff",
                    "json_schema": {"type": "object"},
                },
            ],
            "nodes": [
                {
                    "node_key": "coordinator",
                    "node_type": "role",
                    "display_name": "Coordinator",
                    "role_key": "coordinator",
                    "editor_position": {"x": 10, "y": 20},
                },
                {
                    "node_key": "specialist",
                    "node_type": "role",
                    "display_name": "Specialist",
                    "role_key": "specialist",
                },
                {
                    "node_key": "join",
                    "node_type": "join",
                    "display_name": "Join",
                    "join_policy_key": "join-all",
                },
                {
                    "node_key": "approval",
                    "node_type": "approval",
                    "display_name": "Approval",
                    "approval_gate_key": "manager",
                },
                {
                    "node_key": "handoff",
                    "node_type": "role",
                    "display_name": "Development handoff",
                    "role_key": "handoff",
                },
                {
                    "node_key": "done",
                    "node_type": "terminal",
                    "display_name": "Done",
                },
            ],
            "edges": [
                {
                    "edge_key": "edge-coordinator-specialist",
                    "source_node_key": "coordinator",
                    "target_node_key": "specialist",
                    "contract_key": "brief",
                },
                {
                    "edge_key": "edge-specialist-join",
                    "source_node_key": "specialist",
                    "target_node_key": "join",
                    "contract_key": "result",
                },
                {
                    "edge_key": "edge-join-approval",
                    "source_node_key": "join",
                    "target_node_key": "approval",
                },
                {
                    "edge_key": "edge-approval-handoff",
                    "source_node_key": "approval",
                    "target_node_key": "handoff",
                    "contract_key": "handoff",
                },
                {
                    "edge_key": "edge-handoff-done",
                    "source_node_key": "handoff",
                    "target_node_key": "done",
                    "contract_key": "handoff",
                },
            ],
            "join_policies": [
                {
                    "join_policy_key": "join-all",
                    "strategy": "all_success",
                    "inbound_edge_keys": ["edge-specialist-join"],
                }
            ],
            "approval_gates": [
                {
                    "approval_gate_key": "manager",
                    "display_name": "Manager approval",
                    "approver_scope": "tenant_admin",
                    "resume_behavior": "resume_origin",
                }
            ],
            "subworkflow_refs": [],
        }
    )


def _draft(document: WorkflowDraftDocument | None = None) -> WorkflowDraftResponse:
    revision_id = uuid4()
    return WorkflowDraftResponse(
        workflow_draft_id=uuid4(),
        workflow_lineage_id=uuid4(),
        slug="agent-review",
        display_name="Agent Review",
        scope_type=WorkflowScopeType.TENANT,
        tenant_id=uuid4(),
        workflow_kind="main_workflow",
        status="active",
        current_revision_number=2,
        latest_revision=WorkflowDraftRevisionResponse(
            workflow_draft_revision_id=revision_id,
            revision_number=2,
            document_sha256="sha256-draft",
            created_at=datetime.now(UTC),
        ),
        latest_validation=ValidationResultResponse(
            validation_result_id=uuid4(),
            status="failed",
            blocking_issue_count=1,
            advisory_issue_count=0,
            findings=[
                ValidationFindingResponse(
                    category="graph_policy",
                    severity="blocking",
                    message="Specialist review needs a bounded retry.",
                    field_path="edges[0]",
                    section_key="graph",
                    code="graph.retry",
                    remediation="Add retry policy.",
                    blocking=True,
                    graph_element_id="edge:edge-coordinator-specialist",
                )
            ],
        ),
        document=document or _document(),
        updated_at=datetime.now(UTC),
    )


def test_draft_agent_graph_projects_nodes_edges_tools_and_badges() -> None:
    graph = build_draft_agent_graph(_draft(), generated_at=datetime.now(UTC))

    categories = {node.node_key: node.category for node in graph.nodes}
    edge_categories = {edge.edge_key: edge.category for edge in graph.edges}

    assert graph.source == AgentGraphSource.DRAFT
    assert graph.state == AgentGraphState.READY
    assert categories["coordinator"] == AgentGraphNodeCategory.COORDINATOR_AGENT
    assert categories["specialist"] == AgentGraphNodeCategory.SUB_AGENT
    assert categories["handoff"] == AgentGraphNodeCategory.HANDOFF
    assert any(node.category == AgentGraphNodeCategory.TOOL for node in graph.nodes)
    assert (
        edge_categories["edge-coordinator-specialist"]
        == AgentGraphEdgeCategory.DELEGATES_TO
    )
    assert edge_categories["edge-specialist-join"] == AgentGraphEdgeCategory.JOINS_AT
    assert (
        edge_categories["edge-approval-handoff"] == AgentGraphEdgeCategory.HANDS_OFF_TO
    )
    assert graph.nodes[0].layout.x == 10
    assert graph.nodes[0].layout.y == 20
    assert graph.edges[0].badges[0].code == "graph.retry"
    assert graph.accessibility.node_summaries
    assert "raw prompt" not in graph.model_dump_json().lower()


def test_empty_draft_agent_graph_is_truthful() -> None:
    document = WorkflowDraftDocument(
        workflow_key="empty",
        display_name="Empty",
        workflow_kind="main_workflow",
        entry_node_key="not-yet-created",
    )
    graph = build_draft_agent_graph(_draft(document), generated_at=datetime.now(UTC))

    assert graph.state == AgentGraphState.EMPTY
    assert graph.nodes == ()
    assert graph.badges[0].code == "graph.empty"


def test_draft_agent_graph_projects_optional_reference_and_edge_variants() -> None:
    payload = _document().model_dump(mode="json")
    payload["roles"][0]["skill_installation_keys"] = ["safe-install", "missing-install"]
    payload["skill_installations"] = [
        {
            "skill_installation_key": "safe-install",
            "skill_slug": "safe-tool",
            "skill_version": "2026.05.0",
            "policy_notes": "Safe installed skill.",
        }
    ]
    payload["prompt_profile_references"] = [
        {
            "reference_key": "coordinator-profile",
            "role_key": "coordinator",
            "agent_key": "coordinator-alias",
            "readiness_status": "ready",
            "model_routing_preview": {
                "preview_key": "coordinator-preview",
                "safe_summary": "Coordinator routing is ready.",
                "preview_url": "/admin/app/governance/routing",
            },
        }
    ]
    payload["roles"].append(
        {
            "role_key": "reviewer",
            "display_name": "Reviewer",
            "role_kind": "agent",
            "purpose": "Receive specialist results.",
            "graph_node_keys": ["reviewer"],
        }
    )
    payload["roles"].append(
        {
            "role_key": "named-handoff",
            "display_name": "Named handoff",
            "role_kind": "agent",
            "purpose": "Classify handoff by contract key.",
            "output_contract_key": "named-handoff-payload",
            "graph_node_keys": ["named-handoff"],
        }
    )
    payload["contracts"].append(
        {
            "contract_key": "named-handoff-payload",
            "json_schema": {"type": "object"},
        }
    )
    payload["nodes"].extend(
        [
            {
                "node_key": "unknown-role",
                "node_type": "role",
                "display_name": "Unknown role",
                "description": "Node keeps a safe description without a role.",
                "role_key": "missing",
            },
            {
                "node_key": "child-flow",
                "node_type": "subworkflow",
                "display_name": "Child flow",
                "subworkflow_alias": "child",
            },
            {
                "node_key": "inactive-coordinator",
                "node_type": "role",
                "display_name": "Inactive coordinator",
                "role_key": "coordinator",
                "active": False,
            },
            {
                "node_key": "reviewer",
                "node_type": "role",
                "display_name": "Reviewer",
                "role_key": "reviewer",
            },
            {
                "node_key": "named-handoff",
                "node_type": "role",
                "display_name": "Named handoff",
                "role_key": "named-handoff",
            },
        ]
    )
    payload["subworkflow_refs"] = [
        {
            "alias": "child",
            "workflow_version_ref": "workflow-version:child",
            "display_name": "Child workflow",
            "compatibility_status": "compatible",
        }
    ]
    payload["edges"].extend(
        [
            {
                "edge_key": "edge-specialist-coordinator-failure",
                "source_node_key": "specialist",
                "target_node_key": "coordinator",
                "edge_type": "failure",
                "failure_path": True,
            },
            {
                "edge_key": "edge-specialist-specialist-retry",
                "source_node_key": "specialist",
                "target_node_key": "specialist",
                "loop_type": "retry",
            },
            {
                "edge_key": "edge-approval-coordinator-resume",
                "source_node_key": "approval",
                "target_node_key": "coordinator",
                "loop_type": "approval_resume",
            },
            {
                "edge_key": "edge-specialist-reviewer-return",
                "source_node_key": "specialist",
                "target_node_key": "reviewer",
            },
            {
                "edge_key": "edge-coordinator-child-flow",
                "source_node_key": "coordinator",
                "target_node_key": "child-flow",
            },
        ]
    )
    draft = _draft(WorkflowDraftDocument.model_validate(payload))
    draft.latest_validation.findings.append(
        ValidationFindingResponse(
            category="general",
            severity="info",
            message="Finding without a graph target is ignored by badges.",
            field_path="document",
            section_key="overview",
            blocking=False,
        )
    )
    draft.latest_validation.findings.append(
        ValidationFindingResponse(
            category="safety",
            severity="critical",
            message="Coordinator has a critical graph finding.",
            field_path="nodes[0]",
            section_key="graph",
            code="graph.critical",
            remediation="Fix critical issue.",
            blocking=True,
            graph_element_id="node:coordinator",
        )
    )

    graph = build_draft_agent_graph(draft, generated_at=datetime.now(UTC))
    categories = {node.node_key: node.category for node in graph.nodes}
    edge_categories = {edge.edge_key: edge.category for edge in graph.edges}
    coordinator = next(node for node in graph.nodes if node.node_key == "coordinator")
    unknown_role = next(node for node in graph.nodes if node.node_key == "unknown-role")
    child_flow = next(node for node in graph.nodes if node.node_key == "child-flow")
    inactive = next(
        node for node in graph.nodes if node.node_key == "inactive-coordinator"
    )

    assert categories["unknown-role"] == AgentGraphNodeCategory.UNKNOWN
    assert categories["child-flow"] == AgentGraphNodeCategory.SUBWORKFLOW
    assert categories["named-handoff"] == AgentGraphNodeCategory.HANDOFF
    assert coordinator.status == "critical"
    assert unknown_role.summary == "Node keeps a safe description without a role."
    assert edge_categories["edge-specialist-coordinator-failure"] == (
        AgentGraphEdgeCategory.FAILURE_ROUTES_TO
    )
    assert edge_categories["edge-specialist-specialist-retry"] == (
        AgentGraphEdgeCategory.RETRIES
    )
    assert edge_categories["edge-approval-coordinator-resume"] == (
        AgentGraphEdgeCategory.APPROVAL_RESUMES
    )
    assert edge_categories["edge-specialist-reviewer-return"] == (
        AgentGraphEdgeCategory.RETURNS_RESULT_TO
    )
    assert any(
        reference.reference_type == AgentGraphReferenceType.PROMPT_PROFILE
        for reference in coordinator.references
    )
    assert any(
        reference.reference_type == AgentGraphReferenceType.SKILL
        and reference.label == "safe-tool 2026.05.0"
        for reference in coordinator.references
    )
    assert any(
        reference.reference_type == AgentGraphReferenceType.SUBWORKFLOW
        and reference.label == "Child workflow"
        for reference in child_flow.references
    )
    assert any(badge.code == "graph.node.inactive" for badge in inactive.badges)


def test_published_agent_graph_uses_document_or_partial_state() -> None:
    version = WorkflowVersionResponse(
        workflow_version_bundle_id=uuid4(),
        workflow_lineage_id=uuid4(),
        slug="agent-review",
        display_name="Agent Review",
        display_version="v1",
        scope_type=WorkflowScopeType.TENANT,
        tenant_id=uuid4(),
        status="published",
        compiled_bundle_digest="sha256-version",
        compiler_version="2026.05",
        published_from_draft_id=uuid4(),
        published_from_revision_id=uuid4(),
        summary_json={"workflow_key": "agent-review"},
        published_at=datetime.now(UTC),
    )

    full = build_published_agent_graph(
        version,
        document=_document(),
        generated_at=datetime.now(UTC),
    )
    partial = build_published_agent_graph(
        version,
        document=None,
        generated_at=datetime.now(UTC),
    )

    assert full.source == AgentGraphSource.PUBLISHED_VERSION
    assert full.state == AgentGraphState.READY
    assert partial.state == AgentGraphState.PARTIAL
    assert partial.partial is True
    assert partial.badges[0].code == "graph.published_document.partial"


def test_agent_graph_private_status_helpers_cover_reference_variants() -> None:
    document = _document()

    assert _badge_severity("error") == AgentGraphBadgeSeverity.CRITICAL
    assert _badge_severity("failed") == AgentGraphBadgeSeverity.BLOCKING
    assert _badge_severity("advisory") == AgentGraphBadgeSeverity.WARNING
    assert _badge_severity("note") == AgentGraphBadgeSeverity.INFO
    assert _reference_status("failed") == AgentGraphReferenceStatus.BLOCKED
    assert _reference_status("missing") == AgentGraphReferenceStatus.MISSING
    assert _reference_status("stale") == AgentGraphReferenceStatus.WARNING
    assert _reference_status("unknown") == AgentGraphReferenceStatus.UNKNOWN
    assert _subworkflow_by_alias(document, "missing") is None
    assert _node_by_key(document, "missing") is None
