# Feature Specification: React Agent Graph Viewer For Workflow Drafts And Versions

**Feature Branch**: `codex/066-react-agent-graph-viewer-for-workflow-drafts-and-versions`  
**Created**: 2026-05-09  
**Status**: Draft  
**Input**: User description: "Add a React Admin Agent Graph Viewer for workflow drafts and published versions. Authorized users must be able to open a workflow draft or published workflow version and visually inspect agent/sub-agent communication as a graph. The viewer must render coordinator agents, sub-agents, tools, joins, approval gates, handoffs, and terminal nodes from backend-owned Agent Communication Graph JSON. It must show directional edge labels such as delegates, sends context, returns result, joins, and hands off. Selecting a node or edge must show safe backend-provided details, validation badges, reference summaries, and related links without exposing raw prompts, completions, credentials, private payloads, memory content, provider responses, or raw tool outputs. The graph must include a keyboard-readable node and edge list with equivalent information. Empty, denied, loading, stale, partial, and error states must be truthful. Do not create fake production graph records."

## User Scenarios & Testing

### User Story 1 - Inspect Draft Communication Graph (Priority: P1)

A tenant admin opens a workflow draft detail page and sees a read-only communication graph that explains how the coordinator, sub-agents, tools, joins, approvals, handoffs, and terminal nodes relate to one another.

**Why this priority**: Draft authors need immediate visual confidence that a workflow routes work the way they intend before they validate or publish it.

**Independent Test**: Create a draft with each supported node category, open the draft detail page as an authorized tenant admin, and verify the graph, edge labels, status badges, and safe detail text match the backend graph response.

**Acceptance Scenarios**:

1. **Given** an authorized tenant admin and a workflow draft with graph nodes, **When** the admin opens the draft detail page, **Then** the page shows a read-only graph with the backend-provided node categories and directional edge labels.
2. **Given** a draft graph with validation badges and reference summaries, **When** the admin inspects the graph, **Then** badges and reference summaries appear as safe user-facing details without raw protected payloads.
3. **Given** an empty draft graph, **When** the admin opens the draft detail page, **Then** the page shows a truthful empty state and does not fabricate nodes.

---

### User Story 2 - Inspect Published Version Communication Graph (Priority: P2)

A tenant admin opens a published workflow version and sees the same graph viewer populated from immutable published-version graph evidence.

**Why this priority**: Reviewers need to compare published behavior against draft intent and confirm which version record produced the topology.

**Independent Test**: Publish a workflow version, open its version detail page, and verify the graph shows published provenance, safe labels, and partial-state messaging when bundle evidence is incomplete.

**Acceptance Scenarios**:

1. **Given** a published workflow version with complete graph evidence, **When** the admin opens the version detail page, **Then** the graph shows published-version provenance and the same safe topology as the backend response.
2. **Given** a published workflow version with partial graph evidence, **When** the admin opens the version detail page, **Then** the viewer reports the partial state clearly and shows any safe graph evidence that is available.
3. **Given** a published version outside the current tenant scope, **When** an admin attempts to view it, **Then** the page shows a truthful denied or not-found state without revealing graph content.

---

### User Story 3 - Select Graph Details (Priority: P3)

An admin selects a graph node or edge and sees safe backend-provided detail about the selected item, including category, status, badges, references, related links, and accessible summary text.

**Why this priority**: The graph is useful only when a reviewer can drill into why a node or communication path exists and whether it has warnings.

**Independent Test**: Select representative nodes and edges in the viewer and verify the detail panel updates to safe backend-provided content with no raw protected payloads.

**Acceptance Scenarios**:

1. **Given** a rendered graph, **When** the admin selects a node, **Then** the detail panel shows the node label, category, status, summary, badges, references, and safe related links.
2. **Given** a rendered graph, **When** the admin selects an edge, **Then** the detail panel shows the edge label, category, status, summary, badges, references, and safe related links.
3. **Given** a selected item with unsafe-looking backend text rejected by schema validation, **When** the page renders, **Then** the unsafe text is not displayed in visible UI or reviewer evidence.

---

### User Story 4 - Use Accessible List Alternative (Priority: P4)

An admin who cannot or does not want to use the canvas can review an equivalent keyboard-readable list of graph nodes and edges.

**Why this priority**: The canvas must not be the only way to understand workflow communication.

**Independent Test**: Navigate the graph viewer using only keyboard focus and verify the node and edge lists expose equivalent labels, statuses, summaries, badges, and selection behavior.

**Acceptance Scenarios**:

1. **Given** a rendered graph, **When** the admin tabs into the node list, **Then** each node can be reached and selected with keyboard controls.
2. **Given** a rendered graph, **When** the admin tabs into the edge list, **Then** each edge can be reached and selected with keyboard controls.
3. **Given** a graph with no nodes or edges, **When** the admin reaches the list alternative, **Then** the list describes the empty state without placeholder graph records.

### Edge Cases

- The graph API is loading slowly.
- The graph API returns an authorization denial.
- The graph API returns not found for a stale draft or version link.
- The graph API returns a partial graph.
- The graph API returns an empty graph.
- The graph API returns a safe error detail.
- The graph has more nodes than fit in the first viewport.
- Labels or summaries are long enough to risk overlap.
- A user navigates only with a keyboard.
- A user opens the page on a narrow mobile viewport.
- A user switches between draft and published version pages.
- The graph contains badges with multiple severities.

## Requirements

### Functional Requirements

- **FR-001**: The system MUST display a read-only Agent Communication Graph on workflow draft detail pages for authorized users.
- **FR-002**: The system MUST display a read-only Agent Communication Graph on published workflow version detail pages for authorized users.
- **FR-003**: The viewer MUST use backend-owned Agent Communication Graph data as the only graph data source.
- **FR-004**: The viewer MUST render coordinator agent, sub-agent, tool, join, approval, handoff, terminal, and unknown node categories distinctly enough for users to tell them apart.
- **FR-005**: The viewer MUST render directional edge labels for delegation, context sending, result return, joins, handoffs, failure routing, retries, approval resume, and general transitions when present in graph data.
- **FR-006**: The viewer MUST show graph-level, node-level, and edge-level status badges using safe labels and severity indicators.
- **FR-007**: The viewer MUST let users select nodes and edges and inspect safe backend-provided details.
- **FR-008**: Detail views MUST include safe summaries, categories, statuses, validation badges, reference summaries, and related links when provided by the backend.
- **FR-009**: The viewer MUST include a keyboard-readable node list with information equivalent to the visual nodes.
- **FR-010**: The viewer MUST include a keyboard-readable edge list with information equivalent to the visual edges.
- **FR-011**: Users MUST be able to select graph nodes and edges from both the canvas and the list alternative.
- **FR-012**: The viewer MUST show truthful loading, empty, denied, not-found, partial, stale, and generic error states.
- **FR-013**: The viewer MUST NOT display raw prompts, completions, credentials, provider payloads, private channel payloads, memory contents, unauthorized payloads, or raw external tool outputs.
- **FR-014**: The viewer MUST NOT create, persist, or render fake production graph records.
- **FR-015**: The viewer MUST preserve existing workflow draft and version page content, including JSON inspection and validation panels.
- **FR-016**: The viewer MUST remain usable without horizontal text overlap at desktop and mobile widths.
- **FR-017**: The viewer MUST expose enough semantic names and roles for automated accessibility checks to identify graph, node list, edge list, and selected detail regions.
- **FR-018**: The viewer MUST provide deterministic local QA evidence with authorized, denied, empty, partial, and selected-item states.

### Key Entities

- **Agent Graph Viewer**: The page region that contains the read-only graph canvas, graph status, accessible lists, and selected-item detail panel.
- **Graph Node View**: A rendered node derived from backend graph data with category, status, label, summary, badges, references, layout hints, and selection state.
- **Graph Edge View**: A rendered directional edge derived from backend graph data with category, status, label, summary, badges, references, and selection state.
- **Selected Graph Item Detail**: The safe detail panel content for a selected node or edge.
- **Graph State Message**: A truthful loading, empty, denied, not-found, partial, stale, or error message shown in place of or alongside graph content.
- **Accessible Graph List**: The keyboard-readable list equivalent for graph nodes and edges.

## Success Criteria

### Measurable Outcomes

- **SC-001**: In local QA, an authorized tenant admin can open a draft detail page and identify at least seven supported node categories from the graph and list alternative within one page load.
- **SC-002**: In local QA, an authorized tenant admin can open a published version page and identify the source as a published version without inspecting raw JSON.
- **SC-003**: In local QA, selecting a node and selecting an edge updates the detail region in under one second on a seeded workflow.
- **SC-004**: In automated browser validation, the graph viewer has no overlapping visible text at desktop and mobile widths.
- **SC-005**: In automated browser validation, the node and edge list alternatives can be navigated and selected without using a mouse.
- **SC-006**: In QA artifacts and visible UI scans, zero protected raw prompt, completion, credential, provider payload, private payload, memory, or raw tool output markers appear.
- **SC-007**: In local QA, empty, denied, partial, and loading states are each demonstrated without fake graph records.

## Assumptions

- Spec 065 backend Agent Communication Graph routes and generated contracts are available before implementation starts.
- Existing Admin workflow draft and version pages remain the natural entry points for this viewer.
- Existing authorization behavior is enforced by backend graph routes; the UI reports safe outcomes rather than duplicating policy logic.
- The first viewer is read-only. Editing workflow graph topology remains in existing workflow authoring surfaces.
- Runtime execution overlays are out of scope until Spec 067.
- New durable interaction evidence is out of scope until Spec 068 determines whether it is required.

## Clarifications

- Q: Where should users find the graph viewer? A: (autopilot) Embed it in the existing workflow draft and published version detail pages, with no new top-level Admin navigation item.
- Q: Can users edit graph topology from this viewer? A: (autopilot) No. Spec 066 is read-only; graph editing remains in existing authoring surfaces.
- Q: What data source should the viewer use? A: (autopilot) Use the Spec 065 backend Agent Communication Graph endpoints through generated Admin API types and existing client helpers; do not add production graph fixtures.
- Q: How should denied, missing, partial, and error states be represented? A: (autopilot) Render safe backend response/problem-detail state directly and avoid synthesizing graph nodes to fill gaps.
- Q: What accessibility baseline is required? A: (autopilot) Keep node and edge list alternatives visible or directly reachable in the graph panel at all supported viewport widths, with keyboard selection equivalent to canvas selection.
- Q: What screenshot coverage is required? A: (autopilot) Validate desktop and mobile graph-panel screenshots, plus a selected node or edge detail state, using local-principal deterministic data.
