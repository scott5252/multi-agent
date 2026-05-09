from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Mapping
from datetime import UTC, datetime
from uuid import UUID

from multi_agent_platform.admin.workflow_registry.graph_preview import (
    edge_element_id,
    node_element_id,
)
from multi_agent_platform.api.schemas.admin_agent_graph import (
    AgentCommunicationGraph,
    AgentGraphAccessibility,
    AgentGraphBadge,
    AgentGraphBadgeSeverity,
    AgentGraphBadgeSource,
    AgentGraphEdge,
    AgentGraphEdgeCategory,
    AgentGraphLayoutHint,
    AgentGraphNode,
    AgentGraphNodeCategory,
    AgentGraphProvenance,
    AgentGraphReferenceStatus,
    AgentGraphReferenceSummary,
    AgentGraphReferenceType,
    AgentGraphSource,
    AgentGraphState,
)
from multi_agent_platform.api.schemas.workflow_registry import (
    AgentRoleDefinition,
    ContractSchemaDefinition,
    PromptProfileReference,
    RoleKind,
    SkillBinding,
    SubworkflowReference,
    ValidationFindingResponse,
    WorkflowDraftDocument,
    WorkflowDraftResponse,
    WorkflowEdgeDefinition,
    WorkflowNodeDefinition,
    WorkflowNodeType,
    WorkflowVersionResponse,
)

FALLBACK_X_STEP = 240
FALLBACK_Y_STEP = 130


def build_draft_agent_graph(
    draft: WorkflowDraftResponse,
    *,
    generated_at: datetime | None = None,
) -> AgentCommunicationGraph:
    findings = tuple(
        draft.latest_validation.findings if draft.latest_validation else ()
    )
    return _build_graph(
        graph_id=f"draft:{draft.workflow_draft_id}",
        source=AgentGraphSource.DRAFT,
        document=draft.document,
        workflow_draft_id=draft.workflow_draft_id,
        workflow_version_bundle_id=None,
        workflow_lineage_id=draft.workflow_lineage_id,
        revision=str(draft.current_revision_number),
        source_revision_id=draft.latest_revision.workflow_draft_revision_id,
        source_digest=draft.latest_revision.document_sha256,
        scope_type=draft.scope_type.value,
        tenant_id=draft.tenant_id,
        findings=findings,
        generated_at=generated_at,
    )


def build_published_agent_graph(
    version: WorkflowVersionResponse,
    *,
    document: WorkflowDraftDocument | None,
    generated_at: datetime | None = None,
) -> AgentCommunicationGraph:
    if document is None:
        provenance = AgentGraphProvenance(
            source_type=AgentGraphSource.PUBLISHED_VERSION,
            workflow_draft_id=str(version.published_from_draft_id),
            workflow_version_bundle_id=str(version.workflow_version_bundle_id),
            workflow_lineage_id=str(version.workflow_lineage_id),
            workflow_key=str(version.summary_json.get("workflow_key") or version.slug),
            revision=version.display_version,
            source_revision_id=str(version.published_from_revision_id),
            source_digest=version.compiled_bundle_digest,
            scope_type=version.scope_type.value,
            tenant_id=str(version.tenant_id) if version.tenant_id else None,
            generated_at=generated_at or datetime.now(UTC),
        )
        badge = AgentGraphBadge(
            code="graph.published_document.partial",
            severity=AgentGraphBadgeSeverity.WARNING,
            label="Partial published graph",
            summary=(
                "Published bundle metadata is available, but the compiled "
                "document topology could not be loaded."
            ),
            source=AgentGraphBadgeSource.PROVENANCE,
        )
        accessibility = AgentGraphAccessibility(
            summary="Published agent graph is partial with 0 nodes and 0 edges.",
            node_summaries=(),
            edge_summaries=(),
        )
        return AgentCommunicationGraph(
            graph_id=f"published_version:{version.workflow_version_bundle_id}",
            source=AgentGraphSource.PUBLISHED_VERSION,
            state=AgentGraphState.PARTIAL,
            partial=True,
            provenance=provenance,
            nodes=(),
            edges=(),
            badges=(badge,),
            accessibility=accessibility,
        )
    return _build_graph(
        graph_id=f"published_version:{version.workflow_version_bundle_id}",
        source=AgentGraphSource.PUBLISHED_VERSION,
        document=document,
        workflow_draft_id=version.published_from_draft_id,
        workflow_version_bundle_id=version.workflow_version_bundle_id,
        workflow_lineage_id=version.workflow_lineage_id,
        revision=version.display_version,
        source_revision_id=version.published_from_revision_id,
        source_digest=version.compiled_bundle_digest,
        scope_type=version.scope_type.value,
        tenant_id=version.tenant_id,
        findings=(),
        generated_at=generated_at,
    )


def _build_graph(
    *,
    graph_id: str,
    source: AgentGraphSource,
    document: WorkflowDraftDocument,
    workflow_draft_id: UUID | None,
    workflow_version_bundle_id: UUID | None,
    workflow_lineage_id: UUID,
    revision: str,
    source_revision_id: UUID | None,
    source_digest: str | None,
    scope_type: str,
    tenant_id: UUID | None,
    findings: Iterable[ValidationFindingResponse],
    generated_at: datetime | None,
) -> AgentCommunicationGraph:
    role_by_key = {role.role_key: role for role in document.roles}
    contract_by_key = {
        contract.contract_key: contract for contract in document.contracts
    }
    prompt_refs_by_role = _prompt_refs_by_role(document.prompt_profile_references)
    findings_by_element = _findings_by_graph_element(findings)

    nodes: list[AgentGraphNode] = []
    node_categories: dict[str, AgentGraphNodeCategory] = {}
    for index, node in enumerate(document.nodes):
        category = _node_category(node, role_by_key, contract_by_key)
        node_id = node_element_id(node.node_key)
        node_categories[node.node_key] = category
        role = role_by_key.get(node.role_key or "")
        references = _node_references(
            node=node,
            role=role,
            document=document,
            contract_by_key=contract_by_key,
            prompt_refs_by_role=prompt_refs_by_role,
        )
        badges = [
            *_status_badges_for_node(node=node, role=role),
            *findings_by_element.get(node_id, ()),
        ]
        status = _status_for_badges(
            badges,
            fallback="ready" if node.active else "inactive",
        )
        layout = _layout_for_node(node, index)
        label = node.display_name or node.node_key
        summary = _node_summary(node=node, role=role, category=category)
        accessibility_label = f"{_category_label(category)} node {label} is {status}."
        nodes.append(
            AgentGraphNode(
                node_id=node_id,
                node_key=node.node_key,
                category=category,
                label=label,
                summary=summary,
                status=status,
                role_key=node.role_key,
                layout=layout,
                references=tuple(references),
                badges=tuple(badges),
                accessibility_label=accessibility_label,
            )
        )
        if role is not None:
            nodes.extend(
                _tool_nodes_for_role_node(
                    node=node,
                    role=role,
                    base_index=len(nodes) + index,
                    findings_by_element=findings_by_element,
                )
            )

    edges = [
        _edge_projection(
            edge=edge,
            document=document,
            contract_by_key=contract_by_key,
            role_by_key=role_by_key,
            node_categories=node_categories,
            findings_by_element=findings_by_element,
        )
        for edge in document.edges
    ]
    edges.extend(_tool_edges_for_document(document))

    graph_badges = _graph_badges(document=document, nodes=nodes, edges=edges)
    state = AgentGraphState.EMPTY if not nodes else AgentGraphState.READY
    accessibility = _accessibility(nodes=nodes, edges=edges, state=state)
    provenance = AgentGraphProvenance(
        source_type=source,
        workflow_draft_id=str(workflow_draft_id) if workflow_draft_id else None,
        workflow_version_bundle_id=str(workflow_version_bundle_id)
        if workflow_version_bundle_id
        else None,
        workflow_lineage_id=str(workflow_lineage_id),
        workflow_key=document.workflow_key,
        revision=revision,
        source_revision_id=str(source_revision_id) if source_revision_id else None,
        source_digest=source_digest,
        scope_type=scope_type,
        tenant_id=str(tenant_id) if tenant_id else None,
        generated_at=generated_at or datetime.now(UTC),
    )
    return AgentCommunicationGraph(
        graph_id=graph_id,
        source=source,
        state=state,
        partial=False,
        provenance=provenance,
        nodes=tuple(nodes),
        edges=tuple(edges),
        badges=tuple(graph_badges),
        accessibility=accessibility,
    )


def _prompt_refs_by_role(
    references: Iterable[PromptProfileReference],
) -> dict[str, list[PromptProfileReference]]:
    grouped: dict[str, list[PromptProfileReference]] = defaultdict(list)
    for reference in references:
        if reference.role_key:
            grouped[reference.role_key].append(reference)
        if reference.agent_key and reference.agent_key != reference.role_key:
            grouped[reference.agent_key].append(reference)
    return grouped


def _findings_by_graph_element(
    findings: Iterable[ValidationFindingResponse],
) -> dict[str, tuple[AgentGraphBadge, ...]]:
    grouped: dict[str, list[AgentGraphBadge]] = defaultdict(list)
    for finding in findings:
        if not finding.graph_element_id:
            continue
        grouped[finding.graph_element_id].append(
            AgentGraphBadge(
                code=finding.code or finding.category,
                severity=_badge_severity(finding.severity),
                label=finding.category.replace("_", " ").title(),
                summary=finding.message,
                blocking=finding.blocking,
                source=AgentGraphBadgeSource.VALIDATION,
            )
        )
    return {key: tuple(value) for key, value in grouped.items()}


def _badge_severity(value: str) -> AgentGraphBadgeSeverity:
    normalized = value.lower()
    if normalized in {"critical", "error"}:
        return AgentGraphBadgeSeverity.CRITICAL
    if normalized in {"blocking", "failed"}:
        return AgentGraphBadgeSeverity.BLOCKING
    if normalized in {"warning", "advisory"}:
        return AgentGraphBadgeSeverity.WARNING
    return AgentGraphBadgeSeverity.INFO


def _node_category(
    node: WorkflowNodeDefinition,
    role_by_key: Mapping[str, AgentRoleDefinition],
    contract_by_key: Mapping[str, ContractSchemaDefinition],
) -> AgentGraphNodeCategory:
    if node.node_type == WorkflowNodeType.JOIN:
        return AgentGraphNodeCategory.JOIN
    if node.node_type == WorkflowNodeType.APPROVAL:
        return AgentGraphNodeCategory.APPROVAL
    if node.node_type == WorkflowNodeType.TERMINAL:
        return AgentGraphNodeCategory.TERMINAL
    if node.node_type == WorkflowNodeType.SUBWORKFLOW:
        return AgentGraphNodeCategory.SUBWORKFLOW
    role = role_by_key.get(node.role_key or "")
    if _is_handoff_node(node=node, role=role, contract_by_key=contract_by_key):
        return AgentGraphNodeCategory.HANDOFF
    if role is None:
        return AgentGraphNodeCategory.UNKNOWN
    if role.role_kind == RoleKind.SUBAGENT:
        return AgentGraphNodeCategory.SUB_AGENT
    return AgentGraphNodeCategory.COORDINATOR_AGENT


def _is_handoff_node(
    *,
    node: WorkflowNodeDefinition,
    role: AgentRoleDefinition | None,
    contract_by_key: Mapping[str, ContractSchemaDefinition],
) -> bool:
    values = [node.node_key, node.display_name, node.description or ""]
    if role is not None:
        values.extend(
            [
                role.role_key,
                role.display_name,
                role.purpose,
                role.handoff_expectations or "",
                role.input_contract_key or "",
                role.output_contract_key or "",
            ]
        )
        for contract_key in (role.input_contract_key, role.output_contract_key):
            contract = contract_by_key.get(contract_key or "")
            if contract is not None and str(contract.contract_kind) == "handoff":
                return True
            if contract is not None and "handoff" in contract.contract_key.lower():
                return True
    return any("handoff" in value.lower() for value in values)


def _node_references(
    *,
    node: WorkflowNodeDefinition,
    role: AgentRoleDefinition | None,
    document: WorkflowDraftDocument,
    contract_by_key: Mapping[str, ContractSchemaDefinition],
    prompt_refs_by_role: Mapping[str, list[PromptProfileReference]],
) -> list[AgentGraphReferenceSummary]:
    references: list[AgentGraphReferenceSummary] = []
    if role is not None:
        references.append(
            AgentGraphReferenceSummary(
                reference_id=f"role:{role.role_key}",
                reference_type=AgentGraphReferenceType.ROLE,
                label=role.display_name,
                summary=role.purpose,
                status=AgentGraphReferenceStatus.READY,
            )
        )
        for contract_key in (role.input_contract_key, role.output_contract_key):
            if contract_key:
                references.append(_contract_reference(contract_key, contract_by_key))
        for prompt_ref in prompt_refs_by_role.get(role.role_key, []):
            references.append(_prompt_profile_reference(prompt_ref))
        for binding in role.skill_bindings:
            references.append(_skill_binding_reference(binding))
        for installation_key in role.skill_installation_keys:
            installation = next(
                (
                    item
                    for item in document.skill_installations
                    if item.skill_installation_key == installation_key
                ),
                None,
            )
            if installation is not None:
                references.append(
                    AgentGraphReferenceSummary(
                        reference_id=f"skill-installation:{installation.skill_installation_key}",
                        reference_type=AgentGraphReferenceType.SKILL,
                        label=f"{installation.skill_slug} {installation.skill_version}",
                        summary=installation.policy_notes
                        or "Skill installation reference is configured.",
                        status=AgentGraphReferenceStatus.READY,
                    )
                )
    if node.join_policy_key:
        references.append(
            AgentGraphReferenceSummary(
                reference_id=f"join-policy:{node.join_policy_key}",
                reference_type=AgentGraphReferenceType.JOIN_POLICY,
                label=node.join_policy_key,
                summary="Join policy referenced by this node.",
                status=AgentGraphReferenceStatus.READY,
            )
        )
    if node.approval_gate_key:
        references.append(
            AgentGraphReferenceSummary(
                reference_id=f"approval-gate:{node.approval_gate_key}",
                reference_type=AgentGraphReferenceType.APPROVAL_GATE,
                label=node.approval_gate_key,
                summary="Approval gate referenced by this node.",
                status=AgentGraphReferenceStatus.READY,
            )
        )
    if node.subworkflow_alias:
        subworkflow = _subworkflow_by_alias(document, node.subworkflow_alias)
        references.append(_subworkflow_reference(node.subworkflow_alias, subworkflow))
    return references


def _contract_reference(
    contract_key: str,
    contract_by_key: Mapping[str, ContractSchemaDefinition],
) -> AgentGraphReferenceSummary:
    contract = contract_by_key.get(contract_key)
    return AgentGraphReferenceSummary(
        reference_id=f"contract:{contract_key}",
        reference_type=AgentGraphReferenceType.CONTRACT,
        label=(
            contract.display_name
            if contract and contract.display_name
            else contract_key
        ),
        summary=(
            f"Contract {contract.semantic_version} is referenced."
            if contract is not None
            else "Contract reference is missing from the workflow document."
        ),
        status=AgentGraphReferenceStatus.READY
        if contract is not None
        else AgentGraphReferenceStatus.MISSING,
    )


def _prompt_profile_reference(
    reference: PromptProfileReference,
) -> AgentGraphReferenceSummary:
    preview = reference.model_routing_preview
    return AgentGraphReferenceSummary(
        reference_id=f"prompt-profile:{reference.reference_key}",
        reference_type=AgentGraphReferenceType.PROMPT_PROFILE,
        label=reference.reference_key,
        summary=(
            preview.safe_summary
            if preview and preview.safe_summary
            else "Prompt/profile reference is configured."
        ),
        status=_reference_status(reference.readiness_status),
        href=preview.preview_url if preview else None,
    )


def _skill_binding_reference(binding: SkillBinding) -> AgentGraphReferenceSummary:
    return AgentGraphReferenceSummary(
        reference_id=f"skill:{binding.binding_key}",
        reference_type=AgentGraphReferenceType.SKILL,
        label=f"{binding.skill_slug} {binding.skill_version}",
        summary=binding.purpose,
        status=AgentGraphReferenceStatus.READY,
    )


def _subworkflow_reference(
    alias: str,
    reference: SubworkflowReference | None,
) -> AgentGraphReferenceSummary:
    return AgentGraphReferenceSummary(
        reference_id=f"subworkflow:{alias}",
        reference_type=AgentGraphReferenceType.SUBWORKFLOW,
        label=reference.display_name if reference and reference.display_name else alias,
        summary=(
            "Published workflow version "
            f"{reference.workflow_version_ref} is referenced."
            if reference is not None
            else "Subworkflow reference is missing from the workflow document."
        ),
        status=_reference_status(reference.compatibility_status)
        if reference is not None
        else AgentGraphReferenceStatus.MISSING,
    )


def _reference_status(value: str) -> AgentGraphReferenceStatus:
    normalized = value.lower()
    if normalized in {"ready", "available", "active", "compatible", "passed"}:
        return AgentGraphReferenceStatus.READY
    if normalized in {"blocked", "failed", "denied", "invalid"}:
        return AgentGraphReferenceStatus.BLOCKED
    if normalized in {"missing", "not_found"}:
        return AgentGraphReferenceStatus.MISSING
    if normalized in {"warning", "stale"}:
        return AgentGraphReferenceStatus.WARNING
    return AgentGraphReferenceStatus.UNKNOWN


def _subworkflow_by_alias(
    document: WorkflowDraftDocument,
    alias: str,
) -> SubworkflowReference | None:
    for reference in document.subworkflow_refs:
        if reference.alias == alias:
            return reference
    return None


def _status_badges_for_node(
    *,
    node: WorkflowNodeDefinition,
    role: AgentRoleDefinition | None,
) -> tuple[AgentGraphBadge, ...]:
    badges: list[AgentGraphBadge] = []
    if not node.active:
        badges.append(
            AgentGraphBadge(
                code="graph.node.inactive",
                severity=AgentGraphBadgeSeverity.WARNING,
                label="Inactive node",
                summary="This workflow node is marked inactive.",
                source=AgentGraphBadgeSource.STATUS,
            )
        )
    if node.node_type == WorkflowNodeType.ROLE and role is None:
        badges.append(
            AgentGraphBadge(
                code="graph.node.role_missing",
                severity=AgentGraphBadgeSeverity.BLOCKING,
                label="Missing role",
                summary="Role node does not reference a configured role.",
                blocking=True,
                source=AgentGraphBadgeSource.REFERENCE,
            )
        )
    return tuple(badges)


def _status_for_badges(
    badges: Iterable[AgentGraphBadge],
    *,
    fallback: str,
) -> str:
    severities = {badge.severity for badge in badges}
    if AgentGraphBadgeSeverity.CRITICAL in severities:
        return "critical"
    if AgentGraphBadgeSeverity.BLOCKING in severities:
        return "blocked"
    if AgentGraphBadgeSeverity.WARNING in severities:
        return "warning"
    return fallback


def _layout_for_node(node: WorkflowNodeDefinition, index: int) -> AgentGraphLayoutHint:
    x = node.editor_position.get("x")
    y = node.editor_position.get("y")
    if isinstance(x, int | float) and isinstance(y, int | float):
        return AgentGraphLayoutHint(x=int(x), y=int(y))
    return AgentGraphLayoutHint(
        x=(index % 4) * FALLBACK_X_STEP,
        y=(index // 4) * FALLBACK_Y_STEP,
    )


def _node_summary(
    *,
    node: WorkflowNodeDefinition,
    role: AgentRoleDefinition | None,
    category: AgentGraphNodeCategory,
) -> str:
    if role is not None:
        return role.purpose
    if node.description:
        return node.description
    return f"{_category_label(category)} graph node."


def _tool_nodes_for_role_node(
    *,
    node: WorkflowNodeDefinition,
    role: AgentRoleDefinition,
    base_index: int,
    findings_by_element: Mapping[str, tuple[AgentGraphBadge, ...]],
) -> list[AgentGraphNode]:
    tool_nodes: list[AgentGraphNode] = []
    for offset, binding in enumerate(role.skill_bindings):
        tool_node_id = _tool_node_id(node.node_key, binding.binding_key)
        badges = findings_by_element.get(tool_node_id, ())
        status = _status_for_badges(badges, fallback="ready")
        label = binding.skill_slug
        tool_nodes.append(
            AgentGraphNode(
                node_id=tool_node_id,
                node_key=f"{node.node_key}:{binding.binding_key}",
                category=AgentGraphNodeCategory.TOOL,
                label=label,
                summary=binding.purpose,
                status=status,
                role_key=role.role_key,
                layout=AgentGraphLayoutHint(
                    x=((base_index + offset) % 4) * FALLBACK_X_STEP + 120,
                    y=((base_index + offset) // 4) * FALLBACK_Y_STEP + 80,
                ),
                references=(_skill_binding_reference(binding),),
                badges=badges,
                accessibility_label=f"Tool node {label} is {status}.",
            )
        )
    return tool_nodes


def _tool_edges_for_document(document: WorkflowDraftDocument) -> list[AgentGraphEdge]:
    edges: list[AgentGraphEdge] = []
    for node in document.nodes:
        role = next(
            (role for role in document.roles if role.role_key == node.role_key),
            None,
        )
        if role is None:
            continue
        for binding in role.skill_bindings:
            edge_id = _tool_edge_id(node.node_key, binding.binding_key)
            label = "uses tool"
            summary = f"{node.display_name} uses {binding.skill_slug}."
            edges.append(
                AgentGraphEdge(
                    edge_id=edge_id,
                    edge_key=f"{node.node_key}:{binding.binding_key}",
                    source_node_id=node_element_id(node.node_key),
                    target_node_id=_tool_node_id(node.node_key, binding.binding_key),
                    category=AgentGraphEdgeCategory.SENDS_CONTEXT_TO,
                    label=label,
                    summary=summary,
                    contract_key=None,
                    badges=(),
                    accessibility_label=summary,
                )
            )
    return edges


def _edge_projection(
    *,
    edge: WorkflowEdgeDefinition,
    document: WorkflowDraftDocument,
    contract_by_key: Mapping[str, ContractSchemaDefinition],
    role_by_key: Mapping[str, AgentRoleDefinition],
    node_categories: Mapping[str, AgentGraphNodeCategory],
    findings_by_element: Mapping[str, tuple[AgentGraphBadge, ...]],
) -> AgentGraphEdge:
    source = _node_by_key(document, edge.source_node_key)
    target = _node_by_key(document, edge.target_node_key)
    category = _edge_category(
        edge=edge,
        source=source,
        target=target,
        contract_by_key=contract_by_key,
        role_by_key=role_by_key,
        node_categories=node_categories,
    )
    badges = findings_by_element.get(edge_element_id(edge.edge_key), ())
    label = _edge_label(category)
    summary = (
        f"{source.display_name if source else edge.source_node_key} {label} "
        f"{target.display_name if target else edge.target_node_key}."
    )
    return AgentGraphEdge(
        edge_id=edge_element_id(edge.edge_key),
        edge_key=edge.edge_key,
        source_node_id=node_element_id(edge.source_node_key),
        target_node_id=node_element_id(edge.target_node_key),
        category=category,
        label=label,
        summary=summary,
        contract_key=edge.contract_key,
        badges=badges,
        accessibility_label=summary,
    )


def _edge_category(
    *,
    edge: WorkflowEdgeDefinition,
    source: WorkflowNodeDefinition | None,
    target: WorkflowNodeDefinition | None,
    contract_by_key: Mapping[str, ContractSchemaDefinition],
    role_by_key: Mapping[str, AgentRoleDefinition],
    node_categories: Mapping[str, AgentGraphNodeCategory],
) -> AgentGraphEdgeCategory:
    edge_type = edge.edge_type.lower()
    if edge.failure_path or "failure" in edge_type:
        return AgentGraphEdgeCategory.FAILURE_ROUTES_TO
    if edge.loop_type == "retry":
        return AgentGraphEdgeCategory.RETRIES
    if edge.loop_type == "approval_resume":
        return AgentGraphEdgeCategory.APPROVAL_RESUMES
    if target is not None and target.node_type == WorkflowNodeType.JOIN:
        return AgentGraphEdgeCategory.JOINS_AT
    if _edge_has_handoff(edge=edge, target=target, contract_by_key=contract_by_key):
        return AgentGraphEdgeCategory.HANDS_OFF_TO
    source_category = node_categories.get(edge.source_node_key)
    target_category = node_categories.get(edge.target_node_key)
    if (
        source_category == AgentGraphNodeCategory.COORDINATOR_AGENT
        and target_category == AgentGraphNodeCategory.SUB_AGENT
    ):
        return AgentGraphEdgeCategory.DELEGATES_TO
    if (
        source_category == AgentGraphNodeCategory.SUB_AGENT
        and target_category == AgentGraphNodeCategory.COORDINATOR_AGENT
    ):
        return AgentGraphEdgeCategory.RETURNS_RESULT_TO
    if (
        _role_kind(source, role_by_key) == RoleKind.SUBAGENT
        and _role_kind(target, role_by_key) == RoleKind.AGENT
    ):
        return AgentGraphEdgeCategory.RETURNS_RESULT_TO
    if edge.contract_key:
        return AgentGraphEdgeCategory.SENDS_CONTEXT_TO
    return AgentGraphEdgeCategory.TRANSITIONS_TO


def _edge_has_handoff(
    *,
    edge: WorkflowEdgeDefinition,
    target: WorkflowNodeDefinition | None,
    contract_by_key: Mapping[str, ContractSchemaDefinition],
) -> bool:
    values = [edge.edge_key, edge.edge_type, edge.contract_key or ""]
    if target is not None:
        values.extend([target.node_key, target.display_name, target.description or ""])
    contract = contract_by_key.get(edge.contract_key or "")
    if contract is not None:
        values.extend([contract.contract_key, str(contract.contract_kind)])
    return any("handoff" in value.lower() for value in values)


def _role_kind(
    node: WorkflowNodeDefinition | None,
    role_by_key: Mapping[str, AgentRoleDefinition],
) -> RoleKind | None:
    if node is None or node.role_key is None:
        return None
    role = role_by_key.get(node.role_key)
    return role.role_kind if role else None


def _node_by_key(
    document: WorkflowDraftDocument,
    node_key: str,
) -> WorkflowNodeDefinition | None:
    for node in document.nodes:
        if node.node_key == node_key:
            return node
    return None


def _graph_badges(
    *,
    document: WorkflowDraftDocument,
    nodes: Iterable[AgentGraphNode],
    edges: Iterable[AgentGraphEdge],
) -> tuple[AgentGraphBadge, ...]:
    node_count = len(tuple(nodes))
    edge_count = len(tuple(edges))
    if not document.nodes:
        return (
            AgentGraphBadge(
                code="graph.empty",
                severity=AgentGraphBadgeSeverity.INFO,
                label="Empty graph",
                summary="Workflow document has no graph nodes yet.",
                source=AgentGraphBadgeSource.STATUS,
            ),
        )
    return (
        AgentGraphBadge(
            code="graph.projected",
            severity=AgentGraphBadgeSeverity.INFO,
            label="Projected graph",
            summary=(
                f"Graph projection includes {node_count} nodes and {edge_count} edges."
            ),
            source=AgentGraphBadgeSource.PROVENANCE,
        ),
    )


def _accessibility(
    *,
    nodes: Iterable[AgentGraphNode],
    edges: Iterable[AgentGraphEdge],
    state: AgentGraphState,
) -> AgentGraphAccessibility:
    node_summaries = tuple(node.accessibility_label for node in nodes)
    edge_summaries = tuple(edge.accessibility_label for edge in edges)
    summary = (
        f"Agent graph is {state.value} with {len(node_summaries)} nodes "
        f"and {len(edge_summaries)} edges."
    )
    return AgentGraphAccessibility(
        summary=summary,
        node_summaries=node_summaries,
        edge_summaries=edge_summaries,
    )


def _tool_node_id(node_key: str, binding_key: str) -> str:
    return f"tool:{node_key}:{binding_key}"


def _tool_edge_id(node_key: str, binding_key: str) -> str:
    return f"edge:tool:{node_key}:{binding_key}"


def _edge_label(category: AgentGraphEdgeCategory) -> str:
    return {
        AgentGraphEdgeCategory.DELEGATES_TO: "delegates to",
        AgentGraphEdgeCategory.SENDS_CONTEXT_TO: "sends context to",
        AgentGraphEdgeCategory.RETURNS_RESULT_TO: "returns result to",
        AgentGraphEdgeCategory.JOINS_AT: "joins at",
        AgentGraphEdgeCategory.HANDS_OFF_TO: "hands off to",
        AgentGraphEdgeCategory.FAILURE_ROUTES_TO: "routes failure to",
        AgentGraphEdgeCategory.RETRIES: "retries",
        AgentGraphEdgeCategory.APPROVAL_RESUMES: "resumes approval at",
        AgentGraphEdgeCategory.TRANSITIONS_TO: "transitions to",
    }[category]


def _category_label(category: AgentGraphNodeCategory) -> str:
    return category.value.replace("_", " ")
