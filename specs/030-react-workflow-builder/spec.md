# Feature Specification: React Workflow Builder

**Feature Branch**: `codex/030-react-workflow-builder`  
**Created**: 2026-05-05  
**Status**: Draft  
**Input**: User description: "React Workflow Builder: platform and tenant admins must create, edit, validate, review, and publish workflow drafts through guided forms and an interactive graph-oriented view without editing raw JSON."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Guided Draft Authoring (Priority: P1)

Platform and tenant administrators can open a React workflow builder, create or edit a workflow draft, complete guided metadata and role sections, choose prompt/profile/model/skill references from backend-owned readiness lists, and save an explicit semantic draft revision without editing raw JSON.

**Why this priority**: Authoring a valid draft is the minimum useful workflow-builder capability and must be safe for non-technical administrators.

**Independent Test**: Sign in with local principal as `tenant-admin-acme`, open `/admin/app/workflows`, create a draft from the guided form, edit metadata, roles, references, nodes, and edges, save the draft, and verify a backend revision response plus safe dirty/stale-state behavior.

**Acceptance Scenarios**:

1. **Given** an authorized tenant admin with Acme scope, **When** they open the React workflow builder, **Then** they see guided sections for metadata, roles, references, nodes, edges, gates, evidence, and revisions without raw JSON as the primary interface.
2. **Given** an edited draft with unsaved changes, **When** the admin saves, **Then** the backend records an explicit semantic save, returns a current revision token, clears dirty state, and emits safe audit evidence.
3. **Given** a stale revision token, **When** the admin attempts to save, **Then** the builder shows a safe stale-conflict recovery state with current revision metadata and no raw workflow document leak.
4. **Given** the same route under Auth0-shaped principal overrides, **When** a platform or tenant principal requests the builder contracts, **Then** authorization and tenant scoping match local-principal behavior.

---

### User Story 2 - Graph, Validation, And Accessible Review (Priority: P2)

Administrators can review and edit workflow structure through an interactive graph-oriented view, keyboard-accessible node and edge lists, join policy controls, approval gate controls, reusable subworkflow references, and validation panels. Backend validation remains authoritative; graph layout annotations are visual only.

**Why this priority**: Workflows are graph-shaped, and administrators need to understand fan-out, joins, gates, and validation findings before publishing.

**Independent Test**: Load a deterministic builder fixture with parallel branches and a join, edit a node and join policy, run validation, verify backend-owned findings and graph preview update, and verify the same content is reachable through keyboard-accessible lists without relying on pointer-only graph interactions.

**Acceptance Scenarios**:

1. **Given** a draft with a parallel fan-out and join, **When** the admin opens the graph view, **Then** the graph shows nodes, edges, branch labels, join policies, and approval gates while stating that execution semantics come from backend validation.
2. **Given** an admin who cannot use the graph canvas, **When** they use the node list, edge list, and validation panel, **Then** they can inspect and edit equivalent safe information.
3. **Given** a workflow with validation blockers, **When** validation runs on demand or after save, **Then** publish remains blocked and the panel shows safe finding categories, affected sections, and remediation links.
4. **Given** a large 100-node workflow fixture, **When** the builder renders graph and list views, **Then** the page remains responsive and bounded without leaking raw workflow JSON.

---

### User Story 3 - Publish Gate, Evidence, And Revision Review (Priority: P3)

Administrators can review publish readiness, repository-backed required test-suite evidence, prompt/profile/provider/skill readiness, draft revision history, immutable publish bundle summary, confirmation prompts, and read-only advanced JSON before publishing a validated workflow.

**Why this priority**: Publishing changes runtime behavior and must be explicit, evidence-backed, auditable, and safe.

**Independent Test**: Open a validated draft, inspect required test evidence, review revision history, open the collapsed read-only JSON inspector, attempt publish with missing evidence and then with ready evidence, and verify safe publish gate decisions without mutating immutable published bundles unexpectedly.

**Acceptance Scenarios**:

1. **Given** required test evidence is missing or stale, **When** the admin opens publish review, **Then** publish is blocked with repository-backed evidence status and safe remediation links.
2. **Given** validation and evidence are ready, **When** the admin confirms publish, **Then** the backend returns a publish gate decision, immutable bundle summary, audit reference, and safe success state.
3. **Given** a read-only advanced JSON inspector is opened, **When** the admin reviews the document, **Then** raw prompts, secrets, credential values, memory contents, and unauthorized tenant data remain redacted or summarized.
4. **Given** cross-tenant access is attempted, **When** an Acme admin requests Globex draft or publish data, **Then** the route fails closed and does not reveal Globex labels.

### Edge Cases

- A draft revision changes in another session after the page loads.
- Required test evidence exists but is stale relative to the active draft revision.
- A selected prompt, profile, model, provider, or skill becomes unavailable before save or publish.
- Graph layout positions are changed without document semantics changing.
- A validation request fails because audit persistence or dependency readiness is unavailable.
- A tenant admin attempts to use a platform-only reference.
- A large workflow approaches 100 nodes with many edges and branches.
- A read-only JSON inspector contains redacted summaries and artifact references only.
- JavaScript is unavailable; the existing Jinja editor remains the fallback during migration.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a protected React workflow builder route at `/admin/app/workflows` while preserving existing Jinja workflow routes as fallbacks until migration hardening retires them.
- **FR-002**: System MUST expose backend-owned JSON contracts for builder bootstrap, reference lookups, draft load, draft save, validation results, publish readiness, publish action, revision history, graph preview, stale conflicts, safe field help, and read-only JSON inspector content.
- **FR-003**: System MUST generate TypeScript contracts from backend schemas and React MUST consume generated contracts rather than hand-maintained browser models for protected workflow data.
- **FR-004**: System MUST support local-principal and Auth0-shaped principal validation for React workflow builder routes and protected actions.
- **FR-005**: System MUST fail closed when authorization, tenant scope, or audit persistence cannot be proven.
- **FR-006**: System MUST render guided sections for metadata, roles, sub-agent roles, prompt/profile references, model routing readiness, skill installation requirements, contracts, nodes, edges, parallel fan-out, join policies, approval gates, reusable subworkflows, Daily Intelligence Briefing graph patterns, required test suites, evidence status, validation findings, draft revisions, and publish gate decisions.
- **FR-007**: System MUST treat semantic saves as explicit backend submissions. (autopilot)
- **FR-008**: System MUST keep graph layout annotations non-authoritative; backend validation owns graph execution semantics. (autopilot)
- **FR-009**: System MUST provide a read-only advanced JSON inspector that is collapsed by default. (autopilot)
- **FR-010**: System MUST refresh validation on demand and after saves, while avoiding unbounded background polling. (autopilot)
- **FR-011**: System MUST present publish gate as a guided review with confirmation, blockers, readiness evidence, and safe audit metadata. (autopilot)
- **FR-012**: System MUST support workflows up to 100 nodes in local validation without graph/list rendering becoming unbounded. (autopilot)
- **FR-013**: System MUST provide keyboard-accessible node, edge, reference, and validation alternatives to the graph canvas.
- **FR-014**: System MUST show dirty state, save progress, stale conflict, validation running, partial data, denied, unavailable, and publish confirmation states.
- **FR-015**: System MUST integrate repository-backed required test-bench evidence from Spec 024 into publish readiness.
- **FR-016**: System MUST redact raw secrets, credential values, authorization headers, raw prompts, raw completions, memory contents, private channel messages, provider responses, Telegram updates, raw connector outputs, local paths, stack traces, and unauthorized tenant labels before rendering or exporting.
- **FR-017**: System MUST avoid live provider, Telegram, credential store, or external connector calls in local/CI validation unless explicitly marked as an approved live probe path.
- **FR-018**: System MUST preserve immutable published workflow bundle behavior and never mutate a published bundle in place.
- **FR-019**: System MUST cross-link to existing workflow registry, prompt/profile, model provider, skill registry, test bench, operations, and revision/publish evidence destinations using authorized URLs.
- **FR-020**: System MUST produce QA documents, Playwright screenshots, backend tests, frontend tests, generated contract checks, and full Spec QA evidence before advancing to the next spec.

### Key Entities

- **WorkflowBuilderBootstrap**: Authorized shell, active scope, feature flags, routes, section definitions, field help, and initial draft reference.
- **WorkflowDraftDocument**: Safe editable representation of workflow metadata, roles, graph nodes, edges, references, gates, test requirements, and revision token.
- **WorkflowReferenceOption**: Backend-owned prompt/profile/model/provider/skill/subworkflow/test-suite option with readiness and tenant eligibility.
- **WorkflowGraphPreview**: Non-authoritative graph layout, node summaries, edge summaries, branch groups, join policy summaries, and accessibility list data.
- **ValidationFinding**: Safe backend validation result with severity, category, affected section, remediation action, and evidence reference.
- **PublishReadiness**: Validation, required evidence, reference readiness, revision freshness, and confirmation metadata for publishing.
- **RevisionSummary**: Draft revision history item with actor summary, safe change category, timestamp label, audit reference, and comparison link.
- **BuilderMutationResult**: Save, validate, and publish responses with status, revision token, toast, stale conflict, confirmation, audit reference, and safe redirect links.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A tenant admin can create or edit and save a deterministic workflow draft through guided React controls without editing raw JSON.
- **SC-002**: A platform admin can validate a deterministic graph with parallel fan-out, join policy, approval gate, and required test evidence, and receive backend-owned validation findings in under two seconds in local QA.
- **SC-003**: A keyboard-only reviewer can inspect and edit node, edge, join, reference, and validation information without using the graph canvas.
- **SC-004**: Publish gate blocks missing or stale required evidence and allows a ready fixture only after explicit confirmation.
- **SC-005**: Local-principal and Auth0-shaped route tests cover authorized, denied, tenant-scoped, and cross-tenant behavior.
- **SC-006**: Playwright validation captures create/edit, validation, publish gate, stale conflict, and denied/cross-tenant evidence without unsafe text.
- **SC-007**: Full Spec QA passes with Ruff, format, mypy, coverage at or above 90 percent, generated TypeScript drift checks, frontend typecheck/tests/build, QA docs, and Playwright validation.

## Assumptions

- Existing workflow registry, draft, validation, publish gate, and revision services remain authoritative.
- The React builder is additive; existing Jinja editor routes remain available during migration. (autopilot)
- JavaScript is required for the new React builder, while Jinja fallback remains the non-React route during migration. (autopilot)
- React Flow or an equivalent proven React graph library may be used for visual graph editing after research confirms accessibility and bundle impact.
- Local QA uses deterministic mocked data paths and does not require real model, Telegram, credential, or connector calls.
- Advanced JSON is read-only and collapsed because non-technical admins should not primarily author raw workflow documents. (autopilot)
