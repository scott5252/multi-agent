# Feature Specification: Runtime Agent Communication Graph For Runs

**Feature Branch**: `codex/067-runtime-agent-communication-graph-for-runs`  
**Created**: 2026-05-09  
**Status**: Draft  
**Input**: User description: "Add a Runtime Agent Communication Graph for workflow runs. Authorized users must be able to inspect how a real run moved through coordinator agents, sub-agents, tools, joins, approvals, handoffs, and terminal nodes. The runtime graph must combine the published workflow graph with durable run steps, timeline events, handoff records, lineage, gateway attempt summaries, tool-call summaries, delivery summaries, and safe artifact references. Nodes and edges must show runtime status such as queued, running, succeeded, failed, skipped, waiting, paused, retry scheduled, manual resolution required, and completed. Selecting a node or edge must show safe evidence links and summaries. Cross-tenant access must fail closed. Partial runtime data must render honestly. Do not persist message-level interaction records in this spec. Do not expose raw prompts, completions, provider payloads, credentials, private channel messages, memory contents, stack traces, or raw tool outputs."

## User Scenarios & Testing

### User Story 1 - Inspect Completed Run Communication (Priority: P1)

An authorized tenant admin opens a workflow run detail surface and sees how the run moved through the coordinator, specialist roles, tool nodes, joins, approvals, handoffs, and terminal nodes.

**Why this priority**: Run reviewers need a truthful visual summary of what happened without reconstructing execution from raw timeline JSON.

**Independent Test**: Seed a completed run with a published workflow bundle, run steps, timeline evidence, safe tool summaries, and artifacts; open the run detail graph as an authorized tenant admin; verify node and edge statuses, evidence links, and accessible list summaries match the durable run evidence.

**Acceptance Scenarios**:

1. **Given** an authorized tenant admin and a completed run with durable step and timeline evidence, **When** the admin opens the run communication graph, **Then** the graph shows the published workflow topology with runtime completion statuses overlaid on nodes and edges.
2. **Given** a completed run with safe artifact, tool, gateway, and delivery summaries, **When** the admin selects a node or edge, **Then** the detail panel lists safe evidence references and summaries for the selected item.
3. **Given** a completed run with no runtime evidence for an optional branch, **When** the graph renders, **Then** that branch is marked skipped or unavailable using safe backend status, not fabricated evidence.

---

### User Story 2 - Diagnose Failed Branch (Priority: P2)

An authorized operator reviews a failed or retrying run and can quickly identify the node or communication edge associated with the failure.

**Why this priority**: Runtime graph overlays should reduce time spent searching through timeline and operations records during incident review.

**Independent Test**: Seed a failed run with one failed role or tool step, retry scheduling evidence, and safe failure summaries; open the graph and verify failed and retry-scheduled statuses appear on the correct nodes or edges without raw stack traces.

**Acceptance Scenarios**:

1. **Given** a run with a failed node and safe failure summary, **When** the operator opens the graph, **Then** the failed node and any affected edge show failure status and safe evidence references.
2. **Given** a run with a retry scheduled after a transient error, **When** the operator inspects the graph, **Then** the relevant node or edge shows retry-scheduled status and a safe retry summary.
3. **Given** failure evidence containing protected raw payloads in storage, **When** the graph renders, **Then** protected raw content is absent from visible UI, API responses, screenshots, and QA artifacts.

---

### User Story 3 - Inspect Paused Or Manual-Resolution Run (Priority: P3)

An authorized admin opens a paused run and sees where the run is waiting for approval, handoff, or manual resolution.

**Why this priority**: Paused and waiting runs need clear operational context so humans can intervene at the correct point.

**Independent Test**: Seed a paused run with waiting approval, handoff, and manual-resolution evidence; open the graph and verify waiting, paused, and manual-resolution-required statuses appear with safe action context.

**Acceptance Scenarios**:

1. **Given** a run waiting at an approval node, **When** the admin opens the runtime graph, **Then** the approval node shows waiting or paused status and safe approval evidence.
2. **Given** a run requiring manual resolution at a join or handoff, **When** the admin selects the blocked node or edge, **Then** the detail panel shows safe manual-resolution context and timeline references.
3. **Given** a paused run with partial downstream evidence, **When** the graph renders, **Then** downstream nodes show truthful queued, waiting, skipped, or unavailable status based on durable evidence.

---

### User Story 4 - Handle Partial, Empty, Or Denied Runtime Evidence (Priority: P4)

An authorized or unauthorized user sees truthful state when runtime evidence is incomplete, missing, or outside the user scope.

**Why this priority**: Runtime graph review must fail closed and must not imply certainty where the platform has incomplete evidence.

**Independent Test**: Exercise empty run evidence, partial run evidence, not-found runs, and cross-tenant access; verify safe state messages, status codes, and UI behavior expose no protected graph content.

**Acceptance Scenarios**:

1. **Given** a run with a published workflow bundle but no step evidence yet, **When** the graph is requested, **Then** the graph reports partial or queued state and includes only safe available topology.
2. **Given** a run that does not exist or belongs to another tenant, **When** a user requests its graph, **Then** access fails closed without revealing run topology or evidence.
3. **Given** runtime evidence that cannot be mapped to a workflow graph node, **When** the graph is generated, **Then** the graph exposes a safe partial badge and evidence summary instead of inventing a graph node.

### Edge Cases

- The run exists but its published workflow bundle is missing or unavailable.
- The run has timeline events but no run step rows yet.
- The run has run step rows but no timeline events for some branches.
- The run has a waiting approval, handoff, or manual-resolution pause.
- The run has retry scheduling evidence after a failed tool or provider attempt.
- The run has skipped branches after a conditional or failed upstream path.
- The run has gateway, tool, delivery, or artifact evidence that cannot be tied to a node.
- The run has safe summaries that are longer than a graph panel can display in one line.
- A user opens the runtime graph on a narrow mobile viewport.
- A user navigates the runtime graph only with a keyboard.
- A user from a different tenant requests the run graph.
- A platform operator with allowed scope inspects tenant-owned run evidence.
- Protected raw prompt, completion, channel, memory, credential, stack trace, provider, or tool payload data is present in source records but must never render.

## Requirements

### Functional Requirements

- **FR-001**: The system MUST expose a runtime Agent Communication Graph for authorized workflow run inspection.
- **FR-002**: The runtime graph MUST combine published workflow topology with durable run evidence when both are available.
- **FR-003**: The graph MUST include coordinator agent, sub-agent, tool, join, approval, handoff, terminal, subworkflow, and unknown node categories when represented by the source topology or mapped evidence.
- **FR-004**: Nodes and edges MUST show runtime status values including queued, running, succeeded, failed, skipped, waiting, paused, retry scheduled, manual resolution required, completed, and unavailable when applicable.
- **FR-005**: The graph MUST map run steps to the safest matching workflow graph node or edge using durable identifiers or documented fallback evidence.
- **FR-006**: The graph MUST map timeline events to safe evidence references associated with relevant nodes, edges, or graph-level partial evidence.
- **FR-007**: The graph MUST include safe handoff, approval, gateway attempt, tool-call, delivery, lineage, and artifact references when available and authorized.
- **FR-008**: Selecting a runtime node or edge MUST show safe summaries, statuses, timestamps, evidence reference types, and related links for that item.
- **FR-009**: The runtime graph MUST include keyboard-readable node and edge lists equivalent to the visual graph.
- **FR-010**: The runtime graph MUST render truthful loading, empty, queued, partial, denied, not-found, stale, failed, and generic error states.
- **FR-011**: Cross-tenant and unauthorized access MUST fail closed without revealing run topology, run status, evidence counts, or source identifiers.
- **FR-012**: The graph MUST NOT persist message-level interaction records in this spec.
- **FR-013**: The graph MUST NOT display raw prompts, completions, provider payloads, credentials, private channel messages, memory contents, stack traces, or raw tool outputs.
- **FR-014**: The runtime graph MUST preserve existing run timeline, run debug, operations workbench, and user run detail behavior.
- **FR-015**: The runtime graph MUST identify partial evidence honestly when required data is missing or unmapped.
- **FR-016**: The runtime graph MUST avoid fake production run records and must use deterministic seeded data only in QA.
- **FR-017**: The runtime graph MUST support desktop and mobile review without overlapping visible text.
- **FR-018**: The runtime graph API and UI MUST be covered by deterministic local QA, browser screenshots, and curl regression coverage when public routes are added or changed.

### Key Entities

- **Runtime Agent Communication Graph**: A backend-owned graph projection for a workflow run that overlays runtime evidence on a published workflow topology.
- **Runtime Graph Node**: A graph node with topology metadata, runtime status, timestamps, safe summaries, badges, and evidence references.
- **Runtime Graph Edge**: A directional communication edge with topology metadata, runtime status, safe summaries, badges, and evidence references.
- **Runtime Evidence Reference**: A safe reference to a run step, timeline event, handoff, approval, gateway attempt, tool call, delivery attempt, artifact, or lineage record.
- **Runtime Graph Partial State**: A state that indicates which required source evidence was missing, unavailable, or unmapped.
- **Runtime Graph Detail**: The selected node, edge, or graph-level evidence panel shown in the UI.

## Success Criteria

### Measurable Outcomes

- **SC-001**: In local QA, an authorized tenant admin can open a seeded completed run and identify at least six runtime node statuses from the graph or list alternative without reading raw JSON.
- **SC-002**: In local QA, selecting a failed or retrying node exposes a safe evidence summary in under one second.
- **SC-003**: In local QA, a paused or waiting run clearly identifies the blocked node or edge and its safe timeline reference.
- **SC-004**: Cross-tenant runtime graph requests return a denied or not-found result with zero topology or evidence details.
- **SC-005**: Browser validation captures desktop and mobile runtime graph screenshots with no incoherent text overlap.
- **SC-006**: QA visible-copy scans find zero raw prompt, completion, provider payload, credential, private channel, memory, stack trace, or raw tool output markers.
- **SC-007**: Curl regression includes a success-path command and at least one denied-state command for the runtime graph route family if this spec adds a public JSON route.

## Assumptions

- Spec 065 Agent Communication Graph contracts and projection helpers are available.
- Spec 066 AgentGraphPanel can be reused for runtime graphs with additive runtime evidence fields.
- Existing run steps, timeline events, handoffs, artifacts, gateway summaries, and tool summaries provide enough evidence to build a useful runtime graph without new persistence.
- Any evidence that cannot be safely mapped to a graph node or edge will be represented as graph-level partial evidence.
- Runtime graph review remains read-only.
- Durable interaction evidence remains out of scope until Spec 068 decides whether existing evidence is insufficient.

## Clarifications

### Session 2026-05-09

- Q: Where should users find the runtime graph first? -> A: (autopilot) Integrate it into existing Admin run inspection or operations workbench run detail surfaces first, with optional user-run detail reuse only when existing authorization and contracts already support it safely.
- Q: Should this spec add new runtime evidence persistence? -> A: (autopilot) No. Infer from existing durable run steps, timeline events, handoffs, artifacts, gateway attempts, tool summaries, delivery summaries, and lineage; represent gaps as partial evidence.
- Q: How should conflicting runtime statuses be summarized? -> A: (autopilot) Use the most action-relevant safe status for a node or edge, prioritizing failed, manual-resolution-required, paused/waiting, retry-scheduled, running, succeeded/completed, skipped, queued, and unavailable.
- Q: How should unmapped evidence be shown? -> A: (autopilot) Keep unmapped evidence at graph-level partial state with safe evidence counts and summaries; do not synthesize nodes or edges.
- Q: What evidence can selected details show? -> A: (autopilot) Show only safe summaries, timestamps, status, evidence reference type, IDs already authorized for the viewer, and links to existing safe run/timeline/artifact surfaces.
- Q: What validation coverage is required? -> A: (autopilot) Validate a completed runtime graph, a failed or retrying branch, a paused/manual-resolution state, a partial evidence state, and a cross-tenant denial through backend tests, QA docs, Playwright screenshots, and curl coverage for new route families.
