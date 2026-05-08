# Feature Specification: Workflow React Live Data

**Feature Branch**: `codex/050-workflow-react-live-data`  
**Created**: 2026-05-07  
**Status**: Draft  
**Input**: User description: "Create a feature specification for Workflow React Live Data. Replace the deterministic workflow React builders with live projections from the workflow registry, validation, publish-gate, sharing, artifact, and test-bench evidence services. The React workflow registry and builder must list real workflow lineages, drafts, revisions, validation results, published bundles, graph documents, references, publish readiness, required evidence, and sharing state. When the database has no workflows, the UI must show truthful empty states and creation actions. Save, validate, publish, restore, and copy actions must call the durable workflow services and persist or reject state through existing revision/audit/idempotency behavior."

## Clarifications

### Session 2026-05-07

- Q: What route shape should workflow live data use? -> A: (autopilot) Keep the existing React registry, create, builder, draft detail, version detail, publish-gate, and lookup surfaces; registry and lineage-oriented entry points open the latest authorized active draft, while explicit draft and version detail routes require durable IDs.
- Q: How should real workflow lists be filtered and ordered? -> A: (autopilot) Use backend-owned bounded search, status, scope, and sort metadata with latest-updated ordering by default; the browser may render and request filters but must not invent or client-filter hidden workflow records as the source of truth.
- Q: How should graph preview be produced? -> A: (autopilot) Generate graph previews from stored workflow documents through existing graph and reference validation helpers; invalid or incomplete documents return safe validation findings and unavailable states instead of fake nodes.
- Q: How should required test-bench evidence be queried? -> A: (autopilot) Use existing publish-gate and test-bench evidence records for the current draft or published bundle, distinguishing missing, stale, failing, passing, denied, and unavailable states without synthetic pass evidence.
- Q: Which QA workflows should be seeded? -> A: (autopilot) Seed one tenant-scoped Acme workflow draft with revisions, validation evidence, publish-gate evidence, and a published bundle, plus isolation records for another scope where needed; the empty QA database path remains genuinely empty.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Browse Live Workflow Records (Priority: P1)

A platform operator or tenant administrator opens the React workflow workspace and sees only authorized workflow lineages, active drafts, revision summaries, published bundles, validation status, and publish readiness that actually exist in durable state for the current scope.

**Why this priority**: The workflow registry and builder are high-traffic admin surfaces. Replacing fixed demo workflow data with live, authorized projections is the core value of this spec.

**Independent Test**: With an empty QA database, request the workflow React routes and verify a truthful empty state with creation actions. With seeded QA workflow records, request the same routes and verify the listed workflows, drafts, revisions, validation summaries, and published bundles match durable data and omit unauthorized tenants.

**Acceptance Scenarios**:

1. **Given** an authorized principal and no persisted workflows for the selected scope, **When** the workflow registry is opened, **Then** the UI shows an honest empty state and creation action without synthetic workflow rows or fixed identifiers.
2. **Given** an authorized principal and seeded workflow lineages, drafts, revisions, validation records, and published bundles, **When** the workflow registry is opened, **Then** the UI lists those live records with backend-owned provenance and no deterministic demo workflow data.
3. **Given** a principal scoped to one tenant, **When** the workflow registry is requested for another tenant, **Then** the system fails closed without exposing unauthorized workflow names, tenant labels, document contents, or artifact locations.

---

### User Story 2 - Inspect Live Drafts, Versions, Graphs, And References (Priority: P2)

A workflow author opens a real draft or published version and can inspect the stored workflow document, graph preview, role and node structure, reference catalog, validation findings, required test-bench evidence, and sharing state derived from durable services rather than a canned builder payload.

**Why this priority**: The builder must be useful once mock data disappears; users need reliable live detail views before they can safely edit or publish workflows.

**Independent Test**: Seed a workflow with a draft document, revision history, validation result, graph structure, reference metadata, required test-bench evidence, published bundle, and sharing grant. Verify the React detail route renders those live projections, and verify an unknown or unauthorized draft returns a truthful unavailable, not found, or denied state.

**Acceptance Scenarios**:

1. **Given** a real active workflow draft, **When** the builder route is opened for that draft or its lineage, **Then** the UI shows the latest authorized draft document, graph preview, revision token, validation state, references, and action metadata from backend contracts.
2. **Given** a real published workflow version, **When** the version detail is opened, **Then** the UI shows the immutable bundle summary, published revision, sharing state, and required evidence status from durable records.
3. **Given** stored graph content contains invalid or incomplete references, **When** the builder requests the graph preview, **Then** the UI shows safe validation findings and does not invent graph nodes, roles, providers, prompts, or skills.

---

### User Story 3 - Persist Workflow Actions Through Durable Services (Priority: P3)

A workflow author creates, saves, validates, restores, copies, or publishes a workflow through React controls and receives persisted success, stale conflict, validation failure, or publish-gate denial responses from the workflow services with audit and idempotency behavior intact.

**Why this priority**: Live projections are not enough if actions still return fake success or fixed revision tokens. Mutations must prove the UI is using the real workflow backend.

**Independent Test**: Execute create, save, validate, restore, copy, and publish flows against a seeded QA database through local-principal Playwright and backend route tests, then verify the resulting draft revisions, validation records, published bundles, audit records, and stale conflict responses through API or redaction-safe database checks.

**Acceptance Scenarios**:

1. **Given** a user creates or saves a workflow draft, **When** the action succeeds, **Then** the persisted draft, latest revision token, audit summary, and returned action metadata match durable state.
2. **Given** a user validates or publishes a workflow, **When** required validation or evidence is missing, **Then** the UI shows the backend publish-gate result and does not present fake readiness or fake evidence.
3. **Given** a user submits a stale revision token, **When** the save, restore, copy, or publish action is attempted, **Then** the UI receives a stale-conflict response with safe recovery metadata and no raw workflow payload leakage.

### Edge Cases

- Empty workflow databases must still return actionable workflow workspace state without demo lineages, fake graph nodes, or fixed `qa030` identifiers.
- Search, sort, pagination, and scope filters must be derived from live workflow records and must preserve tenant isolation.
- Builder routes must handle unknown draft IDs, unknown lineage IDs, unknown version IDs, missing active drafts, withdrawn versions, and validation records that reference deleted or unavailable evidence.
- Graph previews must render from stored workflow documents and safe validation summaries; invalid documents must not expose stack traces or raw internal payloads.
- Publish readiness must reflect required validation and test-bench evidence records, including missing, stale, failing, and passing states.
- Sharing state must report only authorized grants and must not leak principals or tenants outside the caller's scope.
- Mutation responses must preserve idempotency, audit summaries, revision conflicts, and redaction behavior without fixed success payloads.
- QA evidence, screenshots, exports, logs, and docs must not contain raw secrets, credential values, provider authorization headers, raw prompts, raw completions, memory contents, raw run payloads, private channel messages, raw tool payloads, raw test transcripts, full Telegram identifiers, link tokens after creation, local filesystem paths, stack traces, or unauthorized tenant labels.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Workflow React registry routes MUST return live, authorized workflow lineages, draft summaries, revision summaries, validation summaries, published bundles, publish readiness, and sharing summaries from durable workflow records or truthful empty states.
- **FR-002**: Workflow React builder routes MUST return live draft, lineage, and version detail projections from stored workflow documents and related durable records, not deterministic builder constants or demo payloads.
- **FR-003**: Empty workflow states MUST include backend-owned provenance and safe empty-state metadata that explains the missing durable setup and exposes creation actions without inventing workflows, graph nodes, validation results, artifacts, or bundle IDs.
- **FR-004**: Seeded workflow states MUST include backend-owned provenance for persisted workflow data, computed graph previews, validation summaries, required evidence, sharing summaries, and any dependency-unavailable state.
- **FR-005**: Workflow list, detail, graph, validation, publish-gate, and sharing projections MUST enforce tenant and platform scope boundaries before rendering names, descriptions, identifiers, summaries, or action metadata.
- **FR-006**: Workflow list projections MUST support backend-owned bounded search, status filtering, scope filtering, pagination, and sorting over live workflow records, using latest-updated ordering by default while returning stable metadata for empty, partial, and next-page states.
- **FR-007**: Builder entry points MUST resolve the latest authorized active draft when the route targets a lineage or omits a draft identifier, and explicit draft or version detail routes MUST require durable identifiers and return not-found, empty, denied, or unavailable states when no authorized record exists.
- **FR-008**: Graph previews MUST be generated from stored workflow documents through existing graph and reference validation behavior, and MUST NOT emit fake nodes, fake edges, fake roles, fake prompts, fake providers, fake skills, fake artifacts, or raw parsing failures.
- **FR-009**: Reference catalogs exposed to the builder MUST come from existing durable prompt, profile, provider, skill, policy, and workflow records where available, or from explicit empty/unavailable states when records are absent.
- **FR-010**: Save, validate, publish, restore, and copy actions MUST call existing durable workflow services and return persisted success, validation failure, publish-gate denial, stale conflict, authorization denial, or idempotent replay responses.
- **FR-011**: Mutation responses MUST use backend revision tokens, idempotency behavior, audit summaries, and generated action metadata; production React code MUST NOT submit fixed `qa030` revision tokens, workflow IDs, publish evidence IDs, or request identifiers.
- **FR-012**: Publish readiness MUST query existing publish-gate and test-bench evidence for the current draft or published bundle and must distinguish missing, stale, failing, passing, denied, and unavailable evidence without fabricating pass results.
- **FR-013**: Sharing projections MUST report real workflow sharing grants and allowed actions for the caller's scope, and must safely omit or deny unavailable sharing data.
- **FR-014**: Generated TypeScript contracts MUST represent workflow live-data envelopes, pagination metadata, provenance/empty-state metadata, action metadata, stale conflict details, validation summaries, publish-gate summaries, graph previews, and sharing summaries.
- **FR-015**: Backend route tests MUST cover Auth0-shaped and local-principal behavior for empty databases, seeded databases, tenant isolation, platform scope, stale conflicts, publish-gate outcomes, and redaction safety.
- **FR-016**: Frontend tests MUST verify the workflow UI renders empty states, live lists, live builder detail, graph preview, publish-gate evidence, stale conflicts, and action metadata without relying on production fixture imports.
- **FR-017**: Live-data scanner checks MUST fail on unallowlisted production workflow markers such as `DEFAULT_DRAFT_ID`, `DEFAULT_LINEAGE_ID`, fixed `qa030` revisions, fake audit references, fake publish evidence, fake graph nodes, and obsolete deterministic workflow builders.
- **FR-018**: Required validation MUST include QA document validation, Spec QA, Playwright workflow create/edit/validate/publish or publish-gate flow, post-UI API/database verification, and the full multi-agent curl walkthrough before Spec 051 starts.

### Key Entities

- **Workflow Lineage**: A durable family of workflow drafts and versions, including slug, display name, scope, active draft, latest revision, and published bundle references.
- **Workflow Draft**: An editable workflow document with revision history, revision token, validation state, graph document, references, and audit metadata.
- **Workflow Draft Revision**: A persisted immutable snapshot of a draft change with revision number, digest, changed sections, and safe summary.
- **Published Workflow Bundle**: An immutable version bundle with validation, publish-gate, activation, sharing, and evidence metadata.
- **Graph Preview**: A safe projection of nodes, edges, roles, contracts, handoffs, validation findings, and graph layout derived from stored workflow documents.
- **Reference Catalog**: Authorized prompt, profile, provider, skill, policy, contract, and test-bench references available to workflow authors.
- **Validation Result**: A durable validation outcome with findings, severity, safe messages, gate status, and timestamps.
- **Publish-Gate Evidence**: Required test-bench and validation evidence that controls whether a workflow can be published.
- **Sharing Summary**: Durable sharing grants, scope, status, and allowed actions for published workflow versions.
- **Workflow Action Result**: Persisted success, idempotent replay, stale conflict, validation failure, publish denial, or authorization denial metadata returned after a workflow mutation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Empty QA workflow databases return workflow React routes with truthful empty states and zero synthetic workflow rows, graph nodes, revision tokens, publish evidence, or bundle IDs.
- **SC-002**: Seeded QA workflow databases return registry and builder data that matches durable workflow lineages, drafts, revisions, validation results, graph documents, published bundles, required evidence, and sharing records.
- **SC-003**: Workflow create, save, validate, restore, copy, and publish or publish-gate flows persist or reject through existing durable services and can be verified through API or redaction-safe database evidence.
- **SC-004**: Auth0-shaped backend route tests and local-principal Playwright flows prove tenant isolation, empty-state behavior, live seeded data behavior, stale conflict behavior, and redaction safety.
- **SC-005**: Production source, generated contracts, and built assets contain zero unallowlisted `qa030` workflow defaults, fake workflow IDs, fake graph nodes, fake publish evidence, or deterministic workflow builder outputs introduced by this spec.
- **SC-006**: QA document validation, Spec QA, Playwright UI validation, post-UI API/database verification, and the multi-agent curl test all pass for `qa050`.

## Assumptions

- Existing workflow registry, validation, publish, sharing, artifact, and test-bench evidence services remain the durable source of truth for workflow records and actions.
- Spec 049 shared provenance, empty-state, and action metadata patterns are available for workflow contracts.
- QA seed data can be created through existing repositories, domain services, migrations intended for QA, or admin APIs without adding production-only fixture builders.
- QA seeded-state validation uses at least one tenant-scoped Acme workflow draft with revisions, validation evidence, publish-gate evidence, and a published bundle, plus cross-scope isolation data where needed; empty-state validation uses a genuinely empty workflow database path.
- The first implementation target is the React workflow registry and builder surface; governance, skill lifecycle, test bench, membership, channel, usage, and operations live-data replacement are handled by later specs.
- Test-only fixtures may remain under test paths, but production routes, production frontend code, generated contracts, and built assets must not depend on them.
- No destructive workflow data migration or deletion is required.

## Testing Instructions

- Run backend route, repository, contract, and scanner tests for empty databases, seeded databases, Auth0-shaped principals, local-principal behavior, tenant isolation, stale conflict behavior, validation/publish-gate outcomes, and redaction safety.
- Run generated TypeScript contract checks after schema changes.
- Run frontend typecheck, unit tests, and build for the workflow registry, builder, graph preview, empty states, action metadata, stale conflicts, and publish-gate evidence.
- Run QA document validation, Spec QA, Playwright local-principal workflow validation, post-UI API/database verification against `multi_agent_platform_qa050`, and the `multi-agent-curl-test` runner before marking the spec complete.

## PR Review Guidance

- Confirm workflow React routes no longer depend on deterministic workflow builders, fixed `qa030` identifiers, fake publish evidence, fake graph nodes, or fake audit references.
- Confirm live projections use durable workflow, validation, publish-gate, sharing, artifact, and test-bench evidence records with tenant-safe authorization.
- Confirm empty and unavailable states are truthful and do not mask missing live data with demo records.
- Confirm mutations persist, replay idempotently, reject stale revisions, or fail publish gates through existing durable services.
- Confirm screenshots, QA docs, logs, exports, and generated contracts remain redaction-safe.

## Documentation Impact

- Add QA050 API guide, UI walkthrough, QA environment file, manual user guide, and reviewer notes.
- Update workflow admin QA notes to describe empty live workflow state, seeded live workflow setup, live graph preview behavior, stale conflict handling, publish-gate evidence, and post-UI verification.
- Update live-data inventory or scanner documentation only if workflow builder mappings or allowlists change.
