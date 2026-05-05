# Feature Specification: React Admin Data Contracts And Form Patterns

**Feature Branch**: `codex/028-react-admin-data-contracts-and-form-patterns`  
**Created**: 2026-05-04  
**Status**: Draft  
**Input**: User description: "Create a feature specification for shared React admin data contracts and form patterns. Non-technical admins need consistent filtering, table browsing, details panels, wizards, validation messages, optimistic/stale conflict recovery, safe confirmations, export flows, audit-aware mutation feedback, and loading/empty/error states across every future React admin page. The feature must define reusable browser-facing contracts without moving domain rules out of backend services."

## Clarifications

### Session 2026-05-04

- Q: What is the standard page response shape for future React admin pages? -> A: Use a safe `AdminPageEnvelope` with backend-owned scope, page metadata, state descriptors, data, filters, pagination, sorting, actions, evidence summaries, and optional polling hints (autopilot).
- Q: What error format should React consume? -> A: Use RFC-style problem details with safe reason categories, field-level validation details, retry hints, audit reference ids, and no stack traces or raw payloads (autopilot).
- Q: How should mutations be represented? -> A: Use backend-issued action tokens where needed, idempotency keys for replay-safe actions, revision tokens for optimistic concurrency, confirmation requirements for risky actions, and audit-aware result summaries (autopilot).
- Q: How should filters, sorting, and pagination behave? -> A: Backend contracts define allowed filter criteria, saved-filter summaries, cursor or bounded page pagination, sortable fields, and safe display labels; React only renders and submits allowed values (autopilot).
- Q: How should export and background progress appear? -> A: Use safe export snapshots with status, artifact references, progress labels, and polling hints; do not stream raw exported data through React shell metadata (autopilot).
- Q: What unsafe fields must be redacted before reaching React? -> A: Raw prompts, completions, memory contents, private channel messages, credential values, provider authorization headers, raw provider responses, raw external tool payloads, stack traces, and unauthorized tenant labels must be omitted or replaced with safe summaries (autopilot).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Consume Safe Page Envelopes (Priority: P1)

Future React admin pages can consume a standard backend-owned page envelope that carries metadata, state, safe records, filters, pagination, sorting, actions, evidence references, and shell-compatible page context.

**Why this priority**: Later React domain pages need one safe response shape before they can migrate without inventing incompatible contracts.

**Independent Test**: Request the sample patterns page as a tenant admin, platform admin, unauthorized user, and cross-tenant user, then verify the envelope renders only authorized safe fields and state metadata.

**Acceptance Scenarios**:

1. **Given** a local-principal tenant administrator, **When** they request the patterns page envelope, **Then** the response includes Acme scope, page metadata, safe sample records, allowed filters, pagination, sorting, and no unsafe raw payloads.
2. **Given** an Auth0-backed platform administrator in tests, **When** they request the patterns page envelope, **Then** the same contract shape is returned with platform-safe scope and authorized actions.
3. **Given** an unauthenticated request, **When** it requests the patterns page envelope, **Then** the response fails closed without rendering page data or filter metadata.
4. **Given** a tenant administrator requests another tenant scope, **When** they request the patterns page envelope, **Then** the response is denied and does not leak the other tenant display name.

---

### User Story 2 - Submit Forms With Safe Feedback (Priority: P2)

Future React admin pages can use a shared form contract and frontend helpers for field validation, confirmation prompts, dirty-state protection, idempotent submission, stale conflict recovery, safe toasts, and audit-aware mutation results.

**Why this priority**: Administrators need clear and consistent mutation feedback before risky domain workflows move into React.

**Independent Test**: Use the harmless sample form to submit valid, invalid, replayed, stale, and confirmation-required actions, then verify safe feedback and audit reference summaries.

**Acceptance Scenarios**:

1. **Given** a reviewer leaves required sample fields blank, **When** they submit, **Then** React maps backend field validation messages to the relevant form controls.
2. **Given** a reviewer submits a valid sample action, **When** the backend accepts it, **Then** React shows a safe success result with an audit reference id and no raw payload.
3. **Given** a reviewer submits with a stale revision token, **When** the backend rejects it, **Then** React shows stale conflict recovery guidance using safe current-version metadata.
4. **Given** a reviewer repeats an idempotency key, **When** the backend recognizes a replay, **Then** React shows replay metadata without applying duplicate side effects.

---

### User Story 3 - Browse, Filter, Export, And Recover Safely (Priority: P3)

Administrators can browse sample tables, apply allowed filters, review details panels, request safe exports, and understand dependency or partial-data states using reusable patterns.

**Why this priority**: Tables, filters, exports, and partial states are the common shape of the upcoming React admin domain pages.

**Independent Test**: Open `/admin/app/patterns`, apply filters, change sorting, inspect details, request a safe sample export, and verify the browser renders safe status and artifact references only.

**Acceptance Scenarios**:

1. **Given** allowed filters are available, **When** a reviewer applies a filter, **Then** the request uses backend-defined criteria and the response renders filter chips with safe labels.
2. **Given** a reviewer changes sorting or pagination, **When** the page reloads data, **Then** the backend returns bounded results and safe cursor or page metadata.
3. **Given** a sample export is requested, **When** the backend returns an export snapshot, **Then** React shows safe progress, status, and artifact reference metadata without exposing local filesystem paths.
4. **Given** a dependency summary is unavailable, **When** the sample page renders, **Then** React shows a safe partial-data or dependency-unavailable state.

### Edge Cases

- A request uses an unknown filter key.
- A request uses a disallowed sort field.
- A page request asks for a page size above the configured bound.
- A saved filter references a stale or unauthorized criterion.
- A mutation includes an expired action token.
- A mutation omits an idempotency key where one is required.
- A mutation repeats an idempotency key after a successful result.
- A mutation includes a stale revision token.
- A validation error references a field not rendered by the current form.
- A confirmation-required action is submitted without explicit confirmation.
- An export snapshot points at a missing or denied artifact reference.
- A dependency is unavailable while the rest of the page data is safe.
- The same sample page is requested in platform and tenant scopes.
- Auth0-shaped claims and local-principal headers produce equivalent authorization outcomes.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The backend MUST expose reusable Pydantic schemas for admin page envelopes, safe problem details, field validation, actions, mutation results, revision conflicts, filters, sorting, pagination, export snapshots, evidence summaries, delivery summaries, runtime/gateway summaries, and confirmation requirements.
- **FR-002**: The backend MUST provide a harmless sample React patterns endpoint under the protected React admin route surface so contracts can be validated without mutating domain data.
- **FR-003**: The page envelope MUST include active scope metadata and MUST be generated only after existing authentication and tenant authorization checks pass.
- **FR-004**: Error responses intended for React MUST use safe problem details with reason categories, user-safe titles, optional field errors, optional audit reference ids, and no raw exception details.
- **FR-005**: Mutation result contracts MUST include status, safe summary, optional audit reference id, idempotency replay metadata, stale conflict details, confirmation requirements, and safe toast hints.
- **FR-006**: Filter and saved-filter contracts MUST be backend-owned, list allowed criteria and operators, render safe labels, and reject unknown or unauthorized criteria.
- **FR-007**: Pagination and sorting contracts MUST enforce bounded page sizes, allowed sort fields, and safe cursor or page metadata.
- **FR-008**: Export snapshot contracts MUST expose status, safe progress, artifact reference ids, and expiry metadata without local filesystem paths or raw exported content.
- **FR-009**: Frontend generated TypeScript assertions MUST be updated from the backend schema source so browser code does not hand-maintain contract types.
- **FR-010**: Frontend helpers MUST support query loading, mutation submission, validation mapping, dirty-state protection, stale conflict recovery, safe toasts, table state, filter chips, confirmation prompts, and export progress using the generated contracts.
- **FR-011**: The sample React page MUST demonstrate the reusable patterns without migrating a major domain page.
- **FR-012**: The feature MUST validate Auth0-backed principal behavior in backend route tests and local-principal browser behavior in Playwright flows.
- **FR-013**: The implementation MUST include redaction tests proving unsafe payloads, secrets, prompts, completions, memory, provider payloads, external tool payloads, stack traces, local filesystem paths, and unauthorized tenant labels do not reach React contracts.
- **FR-014**: Existing Jinja routes and Spec 027 shell behavior MUST remain available.

### Key Entities *(include if feature involves data)*

- **Admin Page Envelope**: Backend-owned response wrapper containing scope, page metadata, state, records, filters, pagination, sorting, actions, evidence, and refresh hints.
- **Safe Problem Detail**: User-safe error contract with reason category, status, safe title, safe detail, field errors, retry hints, and audit reference id.
- **Admin Action Contract**: Backend-defined action metadata with method, href, required confirmation, action token, idempotency requirement, and enabled/disabled state.
- **Mutation Result**: Safe result metadata for accepted, rejected, replayed, stale, validation-error, dependency-unavailable, and unexpected-error outcomes.
- **Validation Field Error**: Safe field-level message mapped to a form path and display label.
- **Filter Profile**: Backend-owned allowed filter criteria, operators, values, chips, and saved-filter summaries.
- **Pagination And Sorting Model**: Bounded result navigation metadata and allowed sorting fields.
- **Export Snapshot**: Safe export status and artifact reference summary.
- **Evidence Summary**: Redacted audit or operational reference that can be shown in React without raw payloads.
- **Patterns Sample Page**: Harmless route and React view demonstrating the contracts for future specs.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of sample page envelope requests for authorized platform and tenant admins return the same typed contract shape with correct scope metadata.
- **SC-002**: 100% of unauthorized and cross-tenant sample page, form, and export requests fail closed without leaking protected tenant labels or unsafe payloads.
- **SC-003**: Form tests cover valid, invalid, stale, replayed, and confirmation-required sample actions.
- **SC-004**: Frontend tests prove generated contract assertions, validation mapping, dirty-state protection, stale conflict display, safe toasts, filter chips, table state, and export progress render consistently.
- **SC-005**: Playwright evidence shows the sample patterns page, field validation, and safe export/status flow under local-principal login.
- **SC-006**: Required QA docs, full Spec QA, frontend checks, backend checks, and Playwright validation pass before Spec 029 begins.

## Assumptions

- Spec 028 is additive and does not migrate major domain pages.
- The harmless sample patterns page can use deterministic in-memory sample records derived from authorized scope.
- Existing audit helpers can provide safe audit reference ids for sample results without creating real domain side effects.
- Existing object storage providers remain authoritative for real exports; QA028 may use safe artifact-reference samples only.
- Existing React admin shell and design tokens from Specs 026 and 027 remain the shared frame.
