# Feature Specification: Workflow Registry Full React Parity And Jinja Removal

**Feature Branch**: `codex/040-workflow-registry-full-react-parity-and-jinja-removal`  
**Created**: 2026-05-06  
**Status**: Draft  
**Input**: User description: "Create a feature specification for Workflow Registry Full React Parity and Jinja Removal. Spec 030 added the React workflow builder, but full Jinja removal requires React parity for every workflow browser route: workflow list, create, draft edit, field help, graph preview, validation panel, reference picker, publish gate, revision history, published version detail, sharing state, required test evidence, stale conflicts, direct links, and all safe denied/unavailable states. Existing workflow services remain authoritative."

## Clarifications

### Session 2026-05-06

- Q: Should `/admin/workflows` and `/admin/workflows/ui` remain browser-rendered pages? → A: Redirect both old workflow entry URLs to `/admin/app/workflows` while preserving authorized tenant, query, filter, saved-filter, and return intent. (autopilot)
- Q: How should create and version detail be represented in React? → A: Use stable React workflow routes for create, active draft editing, revision history, and published version detail, backed by server-owned workflow contracts. (autopilot)
- Q: How should publish-gate links preserve workflow context? → A: Preserve workflow lineage, draft, revision, published version, gate, evidence, and stale-conflict identifiers when redirecting old URLs; fail closed with a non-Jinja problem response when context is unsafe or unauthorized. (autopilot)
- Q: How is graph preview accessibility validated? → A: Validate both the visual graph preview and keyboard-readable/list alternatives so reviewers can inspect nodes, edges, validation findings, and publish blockers without relying on pointer-only interaction. (autopilot)
- Q: What happens to legacy workflow form posts and static workflow assets? → A: Convert legacy form posts to backend JSON or redirect compatibility handlers, and delete `workflow_studio.js` or workflow-only assets only after scanner and route tests prove no remaining routes reference them. (autopilot)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Use Workflow Registry Only Through React (Priority: P1)

Workflow authors and tenant administrators need the complete workflow registry, builder, validation, publish, sharing, and revision review experience to be available through React without depending on legacy workflow templates.

**Why this priority**: Workflow registry and publish flows are core admin workflows. They must reach full React parity before workflow-owned Jinja pages can be removed safely.

**Independent Test**: As Auth0-shaped and local-principal users, open workflow list, create, draft edit, validation, publish, revision history, published detail, and sharing direct links; verify every safe workflow journey is available through React or a non-Jinja compatibility response.

**Acceptance Scenarios**:

1. **Given** an authenticated workflow author opens the workflow registry, **When** they list workflows, create or resume a draft, edit fields, view graph preview, validate, and publish, **Then** the browser experience is React-backed and all authorization, validation, tenant scope, publish readiness, and audit decisions remain backend-owned.
2. **Given** an authenticated reviewer opens a workflow revision or published version direct link, **When** the route is handled, **Then** the user reaches the equivalent React detail view with revision history, published bundle metadata, required evidence, and safe breadcrumbs preserved.
3. **Given** a tenant-scoped user opens a workflow route outside their authorization scope, **When** the backend handles the request, **Then** the response fails closed with a safe denied or unavailable state that does not reveal unauthorized workflow or tenant details.

---

### User Story 2 - Preserve Workflow Direct Links And Compatibility (Priority: P2)

Operators and support staff need old workflow browser URLs, field-help links, reference-picker links, validation panels, publish-gate URLs, and stale-conflict recovery links to redirect or retire safely after templates are removed.

**Why this priority**: Workflow links appear in QA docs, support notes, audit trails, publish evidence, and user bookmarks. Removing templates without preserving link behavior would break recovery and review workflows.

**Independent Test**: Request representative old workflow URLs with tenant ids, workflow ids, draft ids, revision ids, filters, saved-filter intent, and conflict tokens; verify each route redirects to React or returns a documented non-Jinja compatibility/problem response.

**Acceptance Scenarios**:

1. **Given** an old workflow list or draft edit URL includes filters and tenant scope, **When** the URL is opened, **Then** the system preserves safe query intent while redirecting to the React workflow route.
2. **Given** an old field-help, graph-preview, reference-picker, validation-panel, or publish-gate URL cannot safely map to a React destination, **When** the route is opened, **Then** the response is a non-Jinja compatibility or retirement response with safe recovery guidance.
3. **Given** a stale draft conflict or publish gate failure is reached from a direct link, **When** the browser follows the compatibility path, **Then** the React view presents the current server-owned conflict or gate state without relying on browser-only decisions.

---

### User Story 3 - Retire Workflow-Owned Jinja Assets With Evidence (Priority: P3)

Migration reviewers need a bounded deletion record showing which workflow templates, workflow view helpers, and workflow-only static assets were deleted, redirected, converted, or retained with blockers after React parity is proven.

**Why this priority**: The roadmap must remove Jinja incrementally with deletion-grade evidence. Workflow-owned files can be removed only after tests prove route parity, direct-link behavior, denied states, and redaction.

**Independent Test**: Run scanner/import checks, backend route tests, frontend tests, QA docs validation, and Playwright workflow smoke; inspect reviewer notes proving workflow-owned templates no longer render and no shared Jinja infrastructure was removed early.

**Acceptance Scenarios**:

1. **Given** workflow-owned templates have React parity, **When** the implementation finishes, **Then** those templates are deleted or retired with tests proving no workflow browser route returns TemplateResponse.
2. **Given** a workflow template or asset is shared with another domain or lacks safe parity evidence, **When** reviewer notes are generated, **Then** the item is retained with a blocker and planned removal owner rather than deleted.
3. **Given** QA artifacts and screenshots are produced, **When** reviewers inspect them, **Then** they contain no raw secrets, raw prompts, raw completions, raw tool payloads, local filesystem paths, stack traces, or unauthorized tenant labels.

### Edge Cases

- A workflow draft, revision, lineage, or published bundle id in an old URL no longer exists.
- A workflow direct link includes filters, pagination, saved-filter intent, graph-node focus, validation result anchors, or stale revision tokens.
- A publish gate references required test-bench evidence that is missing, stale, or belongs to another tenant.
- A reference picker or field-help route is reached without a valid active draft.
- A workflow graph preview is too large, contains invalid edges, or has validation errors.
- A workflow draft save or publish attempt loses a stale-revision race.
- A denied state must not reveal whether an unauthorized workflow, tenant, revision, evidence item, or sharing grant exists.
- A workflow export or evidence artifact reference is requested by a user without access.
- A route is authenticated but React bootstrap, generated contracts, or workflow services are unavailable.
- Scanner evidence shows a workflow template still imported by a non-workflow route.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide React-backed workflow list, filtering, saved-filter application, pagination, create, active draft, draft edit, field help, graph preview, validation panel, reference picker, publish gate, revision history, published version detail, sharing state, required test evidence, stale conflict recovery, and denied/unavailable states.
- **FR-002**: Existing workflow registry, builder, validation, publish, sharing, revision, test-bench evidence, tenant authorization, redaction, and audit services MUST remain the authoritative source for browser decisions.
- **FR-003**: React workflow contracts MUST be backend-owned and generated from server schemas where contracts are needed by the browser.
- **FR-004**: Old workflow browser URLs MUST redirect to equivalent React routes when route parameters, tenant scope, filters, saved-filter intent, anchors, and safe breadcrumbs can be preserved unambiguously and authorization allows it.
- **FR-005**: Old workflow browser URLs that cannot safely redirect MUST return documented non-Jinja compatibility, gone, denied, or unavailable responses without exposing protected resource existence.
- **FR-006**: Workflow list and detail views MUST preserve tenant scope, filters, pagination, sort choices, saved-filter intent, and safe direct-link recovery.
- **FR-007**: Workflow draft editing MUST preserve server-owned validation, stale conflict detection, semantic save behavior, graph preview, reference picker choices, field-help content, and publish readiness decisions.
- **FR-008**: Publish gate and published version views MUST show required test-bench evidence, validation summaries, immutable revision metadata, sharing state, and rollback or recovery guidance from backend data.
- **FR-009**: Sharing and visibility decisions MUST fail closed for cross-tenant and unauthorized principals and MUST NOT be implemented as browser-only filtering.
- **FR-010**: Graph preview and validation experiences MUST include keyboard-readable alternatives for nodes, edges, validation findings, and publish blockers.
- **FR-011**: Legacy workflow form posts MUST be converted to backend JSON or redirect compatibility handlers before their templates are deleted.
- **FR-012**: Auth0-shaped backend tests MUST cover authenticated, unauthenticated, unauthorized, cross-tenant, direct-link, redirect, and denied workflow route behavior.
- **FR-013**: Local-principal Playwright flows MUST cover platform-admin and tenant-admin workflow registry journeys in the React UI.
- **FR-014**: The implementation MUST prove that workflow-owned legacy browser routes no longer render Jinja TemplateResponse after workflow templates are deleted or converted.
- **FR-015**: The implementation MUST delete only workflow-owned templates, workflow-only browser handlers, and workflow-only static assets whose parity evidence is complete for the active spec.
- **FR-016**: The implementation MUST retain shared Jinja infrastructure, shared shell templates, non-workflow templates, and global Jinja dependencies until their later roadmap owners complete deletion-grade parity.
- **FR-017**: Reviewer notes MUST record deleted, redirected, converted, retained, and blocked workflow inventory items with evidence references and rollback guidance.
- **FR-018**: React UI, redirects, compatibility responses, exports, screenshots, QA docs, logs, and reviewer notes MUST NOT expose raw secrets, credential values, provider authorization headers, private channel messages, raw prompts or completions, memory contents, raw run payloads, raw tool payloads, raw test transcripts, full Telegram identifiers, link tokens after creation, local filesystem paths, stack traces, or unauthorized tenant labels.
- **FR-019**: QA artifacts MUST document deterministic seed data, Auth0-shaped backend route coverage, local-principal browser coverage, direct-link redirects, denied/unavailable states, redaction checks, workflow template deletion evidence, scanner results, and rollback steps.

### Key Entities *(include if feature involves data)*

- **Workflow Registry Entry**: Tenant-scoped workflow lineage, draft, status, owner, sharing summary, filters, saved-filter metadata, and navigation target displayed in the React registry.
- **Workflow Draft Editing Session**: Backend-owned active draft state, editable fields, validation findings, graph preview inputs, reference selections, and stale revision markers.
- **Workflow Publish Gate**: Server-owned readiness summary, validation results, required test-bench evidence, blockers, approval state, and publish action availability.
- **Workflow Revision Detail**: Immutable revision or published bundle metadata, provenance, rollback references, sharing state, and evidence summaries.
- **Workflow Legacy Route Mapping**: Old browser route, safe React destination or compatibility response, preserved parameters, authorization behavior, and deletion evidence.
- **Workflow Retirement Evidence Record**: Reviewer-facing record of workflow templates, handlers, helpers, static assets, and direct links that were deleted, redirected, converted, retained, or blocked.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of workflow inventory items from Spec 038 and Spec 039 carry a Spec 040 outcome of deleted, redirected, converted to non-Jinja, retained with blocker, or outside active scope with evidence references.
- **SC-002**: 0 workflow-owned browser routes covered by Spec 040 return Jinja TemplateResponse in backend route tests after implementation.
- **SC-003**: Auth0-shaped backend tests cover workflow list, create, draft edit, validation, publish gate, revision detail, sharing, direct-link redirect, denied, unauthenticated, and cross-tenant cases.
- **SC-004**: Local-principal Playwright evidence proves platform-admin and tenant-admin users can complete representative React workflow registry, draft, validation, publish-readiness, revision, and denied-state journeys.
- **SC-005**: Direct-link tests cover representative old workflow URLs with tenant scope, filters, saved-filter intent, workflow ids, draft ids, revision ids, validation anchors, and stale conflict tokens.
- **SC-006**: Scanner/import checks show no remaining workflow-owned template file is rendered by workflow browser routes, and any retained shared template or helper has a documented blocker.
- **SC-007**: Redaction sweeps over workflow route responses, screenshots, QA docs, exports, and reviewer notes find 0 raw secrets, private payloads, local filesystem paths, stack traces, raw prompts, raw completions, or unauthorized tenant labels.
- **SC-008**: QA docs and reviewer notes let a reviewer reproduce the workflow React parity and workflow Jinja removal evidence within 15 minutes.

## Assumptions

- Spec 030 React workflow builder behavior and backend contracts are the baseline for workflow React parity.
- Existing workflow registry, validation, publish gate, sharing, revision, and test-bench evidence services remain authoritative and are extended only where browser parity requires safe contract coverage.
- Static Vite-built React assets and Python-generated non-Jinja compatibility responses are allowed; server-side Jinja rendering is the removal target.
- Spec 040 owns workflow registry and workflow builder browser surfaces only. Governance, skill registry, test bench, operations, channel/membership, user-facing run UI, and global Jinja infrastructure are owned by later specs.
- Local QA uses deterministic local principals and mocked-safe dependencies. Real Auth0, provider, Telegram, credential, connector, and external tool calls remain out of scope for validation.
