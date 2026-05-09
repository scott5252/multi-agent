# Data Model: React Agent Graph Viewer For Workflow Drafts And Versions

## AgentGraphPanelState

- `graph`: Backend-owned Agent Communication Graph payload, or null while loading or denied.
- `source`: Draft or published-version source used to build route labels and provenance copy.
- `status`: Loading, ready, empty, partial, denied, not found, stale, or error.
- `selected_item_id`: The selected node or edge identifier, or null when no item is selected.
- `selected_item_kind`: Node, edge, or graph summary.
- `error_summary`: Safe problem or network summary when fetch fails.

## AgentGraphViewNode

- `node_id`: Stable graph node identifier.
- `label`: Safe backend-provided label.
- `category`: Coordinator agent, sub-agent, tool, join, approval, handoff, terminal, subworkflow, or unknown.
- `status`: Safe backend status.
- `summary`: Safe backend summary.
- `layout`: Backend layout hint used for React Flow positioning.
- `badges`: Safe status, validation, reference, or provenance badges.
- `references`: Safe reference summaries and related links.
- `accessibility_label`: Keyboard-readable label equivalent to canvas node text.

## AgentGraphViewEdge

- `edge_id`: Stable graph edge identifier.
- `source_node_id`: Source node identifier.
- `target_node_id`: Target node identifier.
- `label`: Safe directional edge label.
- `category`: Delegates, sends context, returns result, joins, hands off, failure route, retry, approval resume, or transition.
- `status`: Safe backend status.
- `summary`: Safe backend summary.
- `badges`: Safe edge badges.
- `references`: Safe edge references.
- `accessibility_label`: Keyboard-readable label equivalent to canvas edge text.

## SelectedGraphItemDetail

- `title`: Selected node or edge label.
- `kind_label`: Human-readable category label.
- `status`: Safe status.
- `summary`: Safe summary.
- `badges`: Ordered safe badges.
- `references`: Ordered safe references and links.
- `related_href`: Safe related link when provided.
- `accessibility_summary`: The keyboard-readable summary used by list alternatives.

## GraphStateMessage

- `state`: Loading, empty, partial, denied, not found, stale, or error.
- `title`: Safe user-facing title.
- `summary`: Safe user-facing summary.
- `action`: Optional safe link back to workflow registry or retry control.
- `trace_id`: Optional safe trace identifier from problem details.

## Validation Rules

- Visible text must come from generated contracts and safe backend fields.
- Unknown categories must render with neutral styling and safe labels.
- Missing nodes or edges must not be synthesized.
- A partial graph may render available safe graph content, but must display the partial state.
- Denied and not-found states must not expose draft, version, or tenant graph content.
- Selection state is local UI state and must not persist to backend storage.
