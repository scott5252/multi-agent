# Feature Specification: React Workflow Graph And Agent Role Builder

**Feature Branch**: `codex/070-react-workflow-graph-and-agent-role-builder`  
**Created**: 2026-05-09  
**Status**: Draft  
**Input**: User description: "React Workflow Graph And Agent Role Builder. Authorized admins need a browser UI inside Workflow Registry for creating and editing a custom workflow's agent roles, sub-agent roles, graph nodes, graph edges, contracts, join policies, approval gates, subworkflow references, and layout annotations without editing raw JSON."

## Clarifications

### Session 2026-05-09

- Q: Should graph and role edits use new narrow patch APIs or the Spec 069 full-document save contract? -> A: Use the Spec 069 full-document save contract for persistence in Spec 070; UI helpers may compute local section changes but all durable writes use the backend-owned full document mutation with revision and idempotency guarantees. (autopilot)
- Q: How much prompt/profile binding belongs in Spec 070? -> A: Spec 070 exposes role reference placeholders and safe summaries only; complete prompt/profile creation, publishing, activation, and binding flows are deferred to Spec 071. (autopilot)
- Q: What graph editing affordances are required for this slice? -> A: Provide form/list controls for roles, contracts, nodes, edges, joins, approvals, subworkflows, and layout annotations, plus a read-oriented canvas preview; direct drag-and-drop canvas editing can remain optional if equivalent controls are complete. (autopilot)
- Q: How should destructive item deletion behave when other sections reference the item? -> A: Prefer backend-owned validation and visible dependency warnings; do not silently cascade delete referenced roles, contracts, nodes, joins, approvals, or subworkflows in Spec 070. (autopilot)
- Q: What accessibility baseline applies to the graph canvas? -> A: Every graph operation and graph state must be available through keyboard-readable lists and labeled controls, with desktop and mobile Playwright evidence for nonblank canvas/list rendering and no text overlap. (autopilot)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Build Agent Roles And Contracts (Priority: P1)

An authorized tenant admin creating a custom workflow can add, edit, duplicate, reorder, and delete agent and sub-agent roles from guided browser controls, then associate each role with safe input and output contracts.

**Why this priority**: Roles and contracts are the primary authoring units for custom workflows. Without them, graph controls would only manipulate empty topology and the user could not describe useful agent responsibilities.

**Independent Test**: Create a draft through Workflow Registry, add at least three roles plus input/output contracts through visible controls, save the draft, reload the page, and verify every role and contract remains in the durable document without using a raw JSON editor.

**Acceptance Scenarios**:

1. **Given** an authorized admin and a workflow draft, **When** the admin adds three roles with names, purposes, responsibilities, role kinds, and contract selections, **Then** the role list shows the new roles, the save action persists them, and reload shows the same roles in the same intended order.
2. **Given** an existing role, **When** the admin duplicates it and edits the duplicate key and purpose, **Then** the duplicate is saved as a distinct role and validation does not confuse the two role records.
3. **Given** a role that is referenced by graph nodes, **When** the admin attempts to delete it, **Then** the UI either blocks deletion with a backend-owned validation finding or clearly shows the graph references that must be removed first.

---

### User Story 2 - Author Graph Topology And Joins (Priority: P2)

An authorized admin can build the workflow topology by adding nodes, edges, join policies, approval gates, terminal paths, subworkflow references, and layout annotations while keeping a readable graph canvas and equivalent keyboard-accessible lists.

**Why this priority**: A multi-agent workflow is not useful until the user can connect roles into execution paths, model joins or approvals, and understand the topology after saving and reloading.

**Independent Test**: Starting from a draft with saved roles, add role nodes, a join node, an approval node, a terminal node, and edges connecting at least three agents; save and reload; verify the graph canvas, node list, edge list, and join list all reflect the same durable topology.

**Acceptance Scenarios**:

1. **Given** a draft with three roles, **When** the admin adds role nodes and edges that converge through a join node, **Then** the graph preview and list alternatives show the same node and edge counts with stable labels.
2. **Given** a graph edge, **When** the admin edits its branch label, source node, target node, contract reference, or failure routing metadata, **Then** the saved document updates only the selected edge and preserves other graph entries.
3. **Given** a join policy with required branches and failure behavior, **When** the admin saves and reloads the draft, **Then** the join editor still shows the selected inbound edges, quorum behavior, timeout, and output contract references.

---

### User Story 3 - Recover From Invalid Or Stale Graph Edits (Priority: P3)

An authorized admin receives safe, section-specific validation and conflict recovery when graph or role edits are invalid, stale, oversized, unsafe, or unauthorized.

**Why this priority**: The richer editor will produce more possible invalid states. Users need precise recovery without leaking protected data or trusting browser-only validation.

**Independent Test**: Submit invalid role, node, edge, join, approval, subworkflow, and contract combinations through the browser controls, then verify the UI renders backend-owned findings beside the relevant section and does not persist invalid changes.

**Acceptance Scenarios**:

1. **Given** a graph edge that references a missing node, **When** the admin saves, **Then** the save is rejected and the validation panel points to the graph edge field that needs correction.
2. **Given** a stale browser tab, **When** the admin saves role or graph edits, **Then** the save is rejected without mutation and the UI provides a reload path that preserves safe recovery context.
3. **Given** protected text in a label or summary field, **When** the admin saves, **Then** the response contains only redaction-safe findings and the protected value is not rendered, logged, exported, or captured in QA artifacts.

### Edge Cases

- Duplicate role keys, node keys, edge keys, contract keys, join policy keys, approval gate keys, and subworkflow aliases must be rejected before persistence.
- Role nodes must reference existing roles, and graph edges must reference existing source and target nodes.
- Entry nodes, terminal paths, join inbound references, approval gate references, and subworkflow references must remain internally consistent after add, duplicate, reorder, and delete actions.
- Reordering roles, contracts, nodes, or edges must not silently change graph references.
- Deleting an item that other sections depend on must either be blocked or produce explicit backend-owned validation findings.
- Stale saves must never overwrite a newer document revision.
- Exact duplicate save retries must not create duplicate revisions.
- Oversized documents or sections must fail safely before persistence.
- Tenant admins must not access or mutate platform-scoped or cross-tenant workflow references.
- Graph canvas rendering must remain useful when the browser width is narrow, when node labels are long, or when keyboard-only users rely on node and edge lists.
- Empty states must be truthful for clean tenants and must not invent fake workflows, agents, prompts, profiles, evidence, runs, or graph records.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide browser controls for adding, editing, duplicating, reordering, and deleting workflow roles and sub-agent roles.
- **FR-002**: The system MUST allow each role to capture safe display name, role kind, purpose, responsibilities, input contract, output contract, skill binding summaries, prompt/profile reference placeholders, and graph node associations.
- **FR-003**: The system MUST provide browser controls for adding, editing, duplicating, reordering, and deleting workflow contracts used by roles, graph edges, joins, approvals, handoffs, artifacts, failures, memory, and tool access.
- **FR-004**: The system MUST provide browser controls for adding, editing, duplicating, reordering, and deleting graph nodes for role execution, joins, approvals, subworkflows, terminals, and other supported workflow topology elements.
- **FR-005**: The system MUST provide browser controls for adding, editing, duplicating, reordering, and deleting graph edges, including source node, target node, branch label, contract reference, and failure-routing metadata where supported.
- **FR-006**: The system MUST provide browser controls for join policies, including inbound edge references, required branch behavior, quorum count, timeout, failure behavior, and output merge contract references.
- **FR-007**: The system MUST provide browser controls for approval gates and subworkflow references without requiring raw JSON editing.
- **FR-008**: The system MUST save role, contract, graph, join, approval, subworkflow, and layout changes through backend-owned workflow document mutation contracts with revision tokens and idempotency keys.
- **FR-009**: The system MUST reload saved graph and role changes from durable workflow draft state and preserve stable keys and ordering.
- **FR-010**: The system MUST render a graph canvas that reflects the current durable or dirty draft topology and does not obscure controls or text at desktop or mobile viewport sizes.
- **FR-011**: The system MUST render keyboard-readable node, edge, join, approval, role, and contract lists that provide equivalent safe information to the canvas.
- **FR-012**: The system MUST surface backend-owned validation findings beside the relevant role, contract, graph, join, approval, subworkflow, or metadata section.
- **FR-013**: The system MUST preserve stale conflict recovery and idempotent replay behavior from the workflow document mutation contract.
- **FR-014**: The system MUST enforce tenant and platform authorization for every load, save, validation, and publish-readiness action.
- **FR-015**: The system MUST prevent raw secrets, credentials, provider authorization headers, raw prompts outside authorized prompt edit forms, raw completions, memory contents, private messages, raw tool payloads, raw test transcripts, local filesystem paths, stack traces, and unauthorized tenant labels from appearing in UI, redirects, exports, screenshots, logs, docs, or audit summaries.
- **FR-016**: The system MUST keep publish readiness and validation decisions backend-owned and MUST NOT rely on browser-only graph validation as publish evidence.
- **FR-017**: The system MUST provide truthfully empty, loading, dirty, saving, validation, stale, conflict, blocked, denied, and error states for graph and role authoring.
- **FR-018**: The system MUST include browser-first QA and Playwright coverage for creating a workflow with at least three agents and a join node through visible controls.
- **FR-019**: The system MUST update curl regression coverage if any workflow setup API route family is added or behaviorally changed.

### Key Entities *(include if feature involves data)*

- **Workflow Role Editor Item**: A browser-editable representation of an agent or sub-agent role with stable key, label, purpose, responsibilities, contract references, skill binding summaries, and graph associations.
- **Workflow Contract Editor Item**: A safe editable contract definition that can be referenced by roles, edges, joins, approvals, handoffs, artifacts, memory, tools, and failure outcomes.
- **Graph Node Editor Item**: A node in the workflow topology with stable key, type, label, role or subworkflow reference, approval or join reference, active state, and layout metadata.
- **Graph Edge Editor Item**: A connection between graph nodes with stable key, source, target, branch metadata, contract reference, and failure routing metadata.
- **Join Policy Editor Item**: A coordination policy for converging graph paths with inbound edge references, required branch behavior, quorum rules, timeout, failure behavior, and merge output contract.
- **Approval Gate Editor Item**: A manual or policy-controlled pause point with gate key, label, approver scope, resume behavior, and safe summaries.
- **Subworkflow Reference Item**: A reference to an authorized workflow bundle or alias that can be used by graph nodes without exposing unauthorized tenant data.
- **Layout Annotation**: Safe editor metadata used to position graph elements and remember collapsed sections without becoming the source of truth for execution.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reviewer can create a new workflow draft, add at least three roles, add contracts, connect the roles through graph nodes and edges, add a join node, save, reload, and see all graph and role data preserved.
- **SC-002**: The graph canvas and keyboard-readable lists show matching counts and labels for nodes, edges, joins, and approvals after save and reload.
- **SC-003**: Invalid graph and role edits return backend-owned section and field findings for missing nodes, duplicate keys, missing role references, invalid joins, and unsafe strings.
- **SC-004**: Stale save, duplicate idempotency replay, and same-key different-payload conflict flows continue to pass for graph and role edits.
- **SC-005**: Desktop and mobile Playwright screenshots show nonblank graph content, stable controls, no text overlap, and usable list alternatives.
- **SC-006**: Cross-tenant and unauthorized access tests deny graph and role authoring without exposing unauthorized tenant labels or raw payloads.
- **SC-007**: Frontend typecheck, workflow tests, generated contract freshness, backend focused tests, QA docs, Playwright, run_spec_qa, and multi-agent curl regression all pass before Spec 071 begins.

## Assumptions

- Spec 069 provides the backend-owned full document save contract used by this feature.
- Prompt/profile creation and complete per-agent binding authoring are deferred to Spec 071; this feature may display or reserve safe reference fields but does not need to build prompt/profile publishing flows.
- Required test evidence setup is deferred to Spec 072; this feature may show required test placeholders or validation findings but does not need to launch evidence runs.
- The graph canvas may reuse existing graph preview and agent graph patterns while adding editable controls and list alternatives.
- The persisted workflow document remains the source of truth. Browser layout annotations are editor hints only.
- Local QA uses local-principal auth, deterministic data, fake secret references, and mocked provider/model/tool paths.

## Constitution Impact

- **Durable By Default**: Every graph and role edit saves through durable workflow draft revisions with idempotency and stale conflict handling.
- **Immutable State And Memory**: Draft revisions remain explicit and replayable; browser state is not treated as authoritative.
- **Contract-First Agent Coordination**: Roles, contracts, graph nodes, edges, joins, approvals, and subworkflows are authored as explicit workflow document contracts.
- **Security With Practical Development Ergonomics**: Auth0-shaped backend behavior and local-principal QA both remain required for protected authoring flows.
- **Operability Is A Product Requirement**: Validation findings, dirty state, audit summaries, and recovery states must explain graph setup failures safely.
- **Tenant Isolation And Fair Scheduling**: Tenant and platform scope checks remain backend-owned for every authoring action and reference.
- **Secret Hygiene And Controlled Tool Access**: Protected provider, prompt, credential, tool, channel, runtime, and local path data must not leak through graph authoring surfaces.
- **Version-Pinned Execution**: Authored graph topology remains tied to the draft revision that later publish and runtime flows can pin.

## Testing Instructions

- Add focused backend/contract tests for role, contract, node, edge, join, approval, subworkflow, layout annotation, stale conflict, idempotency, invalid graph, unsafe text, oversized payload, and cross-tenant behavior.
- Add frontend tests for role/contract controls, graph node and edge controls, join controls, save/reload behavior, validation rendering, stale conflict rendering, and keyboard-readable list alternatives.
- Add Playwright desktop and mobile journeys that create a draft with at least three agents and a join node using visible UI controls.
- Add screenshot and no-overlap evidence for the graph canvas and equivalent lists.
- Update `curl_testing.md` if any new or changed route family is introduced.

## Documentation Impact

- Add Spec 070 QA guide, UI walkthrough, manual user guide, and PR notes.
- Document the browser path for creating roles, contracts, graph nodes, graph edges, joins, approvals, subworkflows, and layout annotations.
- Keep API calls as validation aids only; user setup guidance must use visible Admin navigation and controls after login.

## PR Review Guidance

- Verify that role and graph controls persist through the Spec 069 full-document save contract rather than a browser-only state store.
- Review accessibility, keyboard-readable graph alternatives, mobile layout, validation mapping, stale conflict handling, tenant isolation, redaction, generated contracts, and curl coverage.
- Confirm the UI does not synthesize fake workflows, agents, prompts, profiles, evidence, runs, or graph records in production states.
