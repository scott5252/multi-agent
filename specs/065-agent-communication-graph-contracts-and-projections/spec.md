# Feature Specification: Agent Communication Graph Contracts And Projections

**Feature Branch**: `codex/065-agent-communication-graph-contracts-and-projections`  
**Created**: 2026-05-09  
**Status**: Draft  
**Input**: User description: "Add backend-owned Agent Communication Graph contracts for the multi-agent platform. The feature must let authorized platform and tenant admins retrieve a safe JSON graph projection for workflow drafts and published workflow bundles. The graph must explicitly represent coordinator agents, sub-agents, tools, joins, approval gates, handoffs, and terminal nodes, plus directional communication edges such as delegates_to, sends_context_to, returns_result_to, joins_at, and hands_off_to. The projection must be derived from durable workflow registry and published bundle records, include stable node and edge identifiers, graph revision metadata, safe labels, node/edge categories, readiness/status badges, prompt/profile/provider/skill reference summaries, validation findings, and an accessibility summary. Cross-tenant access must fail closed. Empty and denied states must be truthful. Do not add a React graph canvas in this spec. Do not persist raw prompts, completions, provider responses, private channel messages, memory contents, credentials, authorization headers, or raw tool payloads."

## Clarifications

### Session 2026-05-09

- Q: Should Spec 065 add new persistence for graph records? -> A: No; derive graphs from existing draft and published bundle records only. (autopilot)
- Q: How should published bundle graphs behave when the full compiled document is unavailable? -> A: Return a partial graph state from safe published metadata without guessing topology. (autopilot)
- Q: Which authorization model should the graph endpoints use? -> A: Reuse existing workflow draft/version Admin authorization and fail closed for cross-tenant access. (autopilot)
- Q: How should unsafe renderable graph text be handled? -> A: Use existing Admin safe-text patterns and reject or normalize unsafe prompt, completion, credential, provider, memory, channel, and tool markers. (autopilot)
- Q: Is React canvas rendering part of Spec 065? -> A: No; Spec 065 is JSON contracts and backend projections only. (autopilot)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Inspect Draft Communication Graph (Priority: P1)

An authorized platform or tenant admin retrieves a safe JSON graph for a workflow draft so they can understand how coordinator agents, sub-agents, tools, approvals, joins, handoffs, and terminal outcomes are intended to communicate.

**Why this priority**: Draft graph projection is the source contract that later React and runtime graph experiences consume.

**Independent Test**: Create a tenant-scoped workflow draft with role, join, approval, handoff, and terminal nodes, then call the draft graph endpoint and verify stable node IDs, edge IDs, categories, labels, badges, references, provenance, and accessibility summary.

**Acceptance Scenarios**:

1. **Given** an authorized tenant admin and a tenant workflow draft with graph nodes, **When** the admin retrieves the draft agent graph, **Then** the response includes stable node and edge identifiers, safe labels, node and edge categories, revision metadata, references, validation badges, and an accessibility summary.
2. **Given** a draft with no graph nodes yet, **When** the admin retrieves the draft agent graph, **Then** the response truthfully identifies an empty graph state without inventing sample agents or edges.
3. **Given** a draft with validation findings tied to graph elements, **When** the graph is retrieved, **Then** the affected nodes or edges include safe validation badges and no raw payload content.

---

### User Story 2 - Inspect Published Bundle Graph (Priority: P2)

An authorized admin retrieves the agent communication graph for a published workflow bundle so reviewed and immutable runtime definitions can be inspected without reading raw bundle JSON.

**Why this priority**: Published bundle graph projection proves the contract can represent immutable workflow versions and is required before runtime graph overlays.

**Independent Test**: Publish a workflow bundle and retrieve its agent graph; verify the graph derives from the published bundle document and includes immutable version provenance rather than draft-only metadata.

**Acceptance Scenarios**:

1. **Given** an authorized admin and a published workflow bundle, **When** the admin retrieves the bundle agent graph, **Then** the graph includes published version provenance, source revision metadata, nodes, edges, references, and accessibility summary derived from durable bundle data.
2. **Given** a tenant admin without access to another tenant's bundle, **When** the admin requests the bundle graph, **Then** access fails closed without leaking the other tenant name, records, or graph content.

---

### User Story 3 - Handle Denied, Missing, And Empty States (Priority: P3)

Admins and API clients receive truthful denied, missing, and empty responses that are safe for browser rendering and operational debugging.

**Why this priority**: The graph API becomes a UI contract in later specs, so non-happy paths must be explicit and safe from the beginning.

**Independent Test**: Call graph endpoints without auth, with insufficient tenant role, with cross-tenant scope, with missing IDs, and with empty graph documents; verify status codes and response bodies are safe and consistent with existing admin API behavior.

**Acceptance Scenarios**:

1. **Given** no authorized principal, **When** a client requests a graph endpoint, **Then** the request is rejected using existing auth behavior.
2. **Given** a principal outside the workflow scope, **When** the client requests a graph endpoint, **Then** the request returns a fail-closed denial without graph content.
3. **Given** an unknown draft or version ID, **When** the graph is requested, **Then** the endpoint returns not found without exposing unrelated records.

---

### User Story 4 - Verify Safe Rendering Contracts (Priority: P4)

Backend and frontend contract consumers can rely on safe strings, bounded summaries, and generated TypeScript definitions for future graph rendering.

**Why this priority**: This spec is backend-only, but its output must be safe and stable for the React viewer in Spec 066.

**Independent Test**: Validate schema construction rejects unsafe text markers, generated TypeScript stays fresh, and OpenAPI exposes draft and version graph response models.

**Acceptance Scenarios**:

1. **Given** unsafe markers such as raw prompts, completions, credentials, or raw tool payload labels, **When** graph schemas validate response content, **Then** unsafe renderable text is rejected or safely normalized.
2. **Given** the OpenAPI generation command, **When** TypeScript contracts are refreshed and checked, **Then** the Agent Communication Graph types are present and deterministic.

### Edge Cases

- Workflow drafts with zero nodes or zero edges must return a truthful empty or partial graph summary without synthetic sample data.
- Workflows with role nodes that lack role metadata must render safe fallback summaries and mark references as missing or unknown.
- Workflows with validation findings that reference unknown graph elements must not attach badges to unrelated nodes or edges.
- Published bundle summaries that lack a full document must return a partial graph state rather than guessing topology.
- Cross-tenant and insufficient-role requests must fail closed and avoid tenant names, private payloads, raw prompts, completions, secrets, headers, and tool outputs.
- Graph labels, summaries, reference labels, badges, and accessibility text must remain bounded and safe for future browser rendering.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a tenant-scoped Admin JSON endpoint for retrieving a workflow draft Agent Communication Graph.
- **FR-002**: The system MUST expose a tenant-scoped Admin JSON endpoint for retrieving a published workflow bundle Agent Communication Graph.
- **FR-003**: The graph response MUST include graph provenance with source type, workflow identifiers, revision/version identifiers, digest or revision metadata when available, scope type, tenant identifier when applicable, and generated timestamp.
- **FR-004**: The graph response MUST include stable node identifiers and edge identifiers derived from existing workflow node and edge keys.
- **FR-005**: The graph response MUST classify nodes into coordinator_agent, sub_agent, tool, join, approval, handoff, terminal, subworkflow, or unknown categories using existing workflow role, node, skill, approval, join, handoff, and subworkflow metadata.
- **FR-006**: The graph response MUST classify communication edges into delegates_to, sends_context_to, returns_result_to, joins_at, hands_off_to, failure_routes_to, retries, approval_resumes, or transitions_to categories using existing workflow edge metadata.
- **FR-007**: The graph response MUST include safe labels, safe summaries, role summaries, status badges, validation badges, and safe prompt/profile/provider/skill/subworkflow/contract reference summaries without exposing raw prompts, completions, provider payloads, private channel content, memory contents, credentials, authorization headers, stack traces, or raw tool payloads.
- **FR-008**: The graph response MUST include layout hints derived from existing editor positions when available and deterministic fallback positions otherwise.
- **FR-009**: The graph response MUST include an accessibility summary plus keyboard-readable node and edge text summaries equivalent to the graph topology.
- **FR-010**: The draft graph projection MUST derive from the durable workflow draft document and latest validation findings already stored in the workflow registry.
- **FR-011**: The published graph projection MUST derive from the durable published bundle document or published bundle metadata and must mark the graph partial when the full document is unavailable.
- **FR-012**: Cross-tenant, missing-auth, insufficient-role, and not-found cases MUST use existing fail-closed Admin API behavior and must not leak unauthorized graph content.
- **FR-013**: Empty draft or bundle graph states MUST be explicit, safe, and truthful, with no production sample agents, sample edges, or fabricated runtime evidence.
- **FR-014**: Generated TypeScript contracts MUST include the new graph schemas and remain fresh under the repository's generated-contract check.
- **FR-015**: The feature MUST update API regression coverage in `curl_testing.md` for every new public JSON route introduced by this spec.

### Key Entities *(include if feature involves data)*

- **Agent Communication Graph**: A safe JSON projection containing provenance, nodes, edges, accessibility text, graph state, and status/readiness metadata.
- **Agent Graph Node**: A rendered-safe graph element derived from a workflow node, role, skill binding, join policy, approval gate, subworkflow reference, or terminal state.
- **Agent Graph Edge**: A rendered-safe directional communication or transition edge derived from workflow edge metadata.
- **Graph Badge**: A safe status or validation annotation attached to a graph, node, edge, or reference.
- **Graph Reference Summary**: A safe prompt/profile/provider/skill/subworkflow/contract reference attached to a node or edge.
- **Graph Provenance**: Metadata describing whether the graph came from a draft or published bundle and which durable revision/version produced it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For a workflow draft containing coordinator, sub-agent, join, approval, handoff, and terminal nodes, the graph endpoint returns all graph nodes and edges with deterministic IDs in one request.
- **SC-002**: For a published workflow bundle with a stored document, the graph endpoint returns a graph with published version provenance and the same durable topology reviewed at publish time.
- **SC-003**: Unauthorized, cross-tenant, missing draft, and missing version cases are covered by automated tests and reveal no unauthorized tenant names or graph content.
- **SC-004**: Safe-text tests cover at least one blocked marker for raw prompts, completions, credentials, provider payloads, private messages, memory contents, and raw tool outputs.
- **SC-005**: Generated OpenAPI/TypeScript checks, focused backend tests, QA document validation, Playwright smoke validation, and multi-agent curl regression pass before Spec 066 begins.

## Assumptions

- Existing workflow registry draft documents, validation findings, published bundle metadata, and compiled bundle documents are sufficient for design-time and published graph projection, so no database migration is expected for Spec 065.
- The first graph contract is read-only and JSON-only; React graph rendering starts in Spec 066.
- Runtime run status overlays and runtime evidence links are out of scope for Spec 065 and begin in Spec 067.
- Deterministic fallback layout is acceptable when workflow nodes do not have editor positions.
- Local QA uses local-principal authorization and deterministic database setup; no real provider, Telegram, Auth0, connector, model, or external side-effect call is required.
