# Feature Specification: Admin Design Review Workspace

**Feature Branch**: `codex/063-admin-design-review-workspace`  
**Created**: 2026-05-08  
**Status**: Draft  
**Input**: User description: "Add a live-data Admin workspace for Design Review sessions. Tenant admins must be able to create a Design Reviewer Council session from a safe request summary, select an authorized published workflow/template and quorum policy, monitor each review round, inspect reviewer verdict summaries, view quorum decisions, compare safe design revision summaries, perform manual-resolution actions when allowed, and view the final development handoff reference. The workspace must use backend-owned data only, show truthful empty/denied/loading/stale/error states, and avoid all implementation-framework labels in visible product copy."

## Clarifications

### Session 2026-05-08

- Q: Which records may the workspace show? -> A: Only live backend-owned design-review sessions, revisions, rounds, verdict summaries, quorum decisions, manual decisions, workflow references, and handoff references (autopilot).
- Q: How should the create flow choose a council workflow? -> A: The backend exposes authorized published workflow bundle options for the active tenant, and the UI may also create a draft session without a workflow when no option exists (autopilot).
- Q: How are manual-resolution actions represented? -> A: Show actions only when coordinator state reports manual resolution, and submit durable coordinator manual decisions with safe rationale and idempotency (autopilot).
- Q: What local QA data is acceptable? -> A: QA may seed live database rows through deterministic scripts; production routes and React test data must not invent hidden successful records (autopilot).
- Q: What visible text is disallowed? -> A: Avoid implementation-framework labels such as React, FastAPI, Pydantic, SQLAlchemy, mock, fixture, Jinja, or generated contract names in product copy (autopilot).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Review Session Workspace Overview (Priority: P1)

A tenant admin opens `/admin/app/design-reviews` and sees live session history,
status metrics, selected-session details, safe revision summaries, round history,
quorum decisions, and handoff state for the active tenant scope.

**Why this priority**: The scenario needs an inspectable live workspace before
admins can trust the coordinator loop.

**Independent Test**: Seed a tenant with an approved design review session and
open the workspace. Assert the page renders live session rows, the selected
session details, verdict summaries, quorum result, and handoff reference without
sample or unsafe data.

**Acceptance Scenarios**:

1. **Given** one or more design review sessions exist for the active tenant, **When** the workspace loads, **Then** the page shows live summaries, selected-session details, and safe state metadata.
2. **Given** no design review sessions exist, **When** the workspace loads, **Then** the page shows a truthful empty state and a create-session form.
3. **Given** a principal requests another tenant's workspace, **When** the backend envelope is requested, **Then** access fails closed or returns a denied state without leaking records.

---

### User Story 2 - Create And Launch Review Sessions (Priority: P2)

A tenant admin creates a design review session from a safe request summary,
selects a quorum policy and optional published council workflow, and launches a
coordinator review round when a workflow is available.

**Why this priority**: Admins need a browser-first path from request intake to
coordinator execution.

**Independent Test**: Submit the create form and launch action against live APIs.
Assert the session is persisted, the active revision appears, and launch creates
a round and runtime run without duplicate records on idempotent replay.

**Acceptance Scenarios**:

1. **Given** the create form has a safe summary and quorum policy, **When** the admin submits it, **Then** the persisted session appears in the workspace.
2. **Given** the selected session has an authorized workflow, **When** the admin launches a review round, **Then** the workspace refreshes with a running round and runtime run reference.
3. **Given** unsafe content or stale state is submitted, **When** the action fails, **Then** the UI shows a safe error without raw rejected payloads.

---

### User Story 3 - Manual Resolution And Handoff Inspection (Priority: P3)

When a session pauses for manual resolution, a tenant admin can record a safe
revise, approve-exception, retry, or cancel decision and inspect the resulting
handoff or next revision.

**Why this priority**: Production council loops need a clear human control
surface when automated evidence is incomplete.

**Independent Test**: Seed a manual-resolution session, submit each supported
manual action through the workspace or API, and assert state side effects,
idempotency, audit-safe rationale, and redaction.

**Acceptance Scenarios**:

1. **Given** a session is in manual resolution, **When** the admin records a revise decision, **Then** a safe next revision appears and the workspace shows revision-required state.
2. **Given** a session is in manual resolution, **When** the admin records approve-exception with accepted risk, **Then** a handoff appears and the session is approved.
3. **Given** a session is terminal, **When** manual controls are rendered, **Then** destructive or invalid actions are not shown.

### Edge Cases

- Empty state must not display sample sessions, sample reviewer verdicts, or fake handoffs.
- Session rows must be tenant-scoped and must not leak whether another tenant has matching IDs.
- Product copy must not expose implementation-framework labels.
- Create and manual-decision forms must send idempotency keys.
- Workflow options must come from authorized published workflow bundles only.
- Launch controls must be disabled when no workflow bundle is available.
- Manual-resolution controls must be hidden unless backend state permits them.
- Verdict panels must show safe summaries, scores, blockers, and artifact references only.
- Handoff panels must show safe summary, digest, status, and artifact reference only.
- Loading, denied, empty, stale/conflict, validation, and dependency states must be visually distinct and accessible.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST serve `/admin/app/design-reviews` through the existing React admin shell.
- **FR-002**: The system MUST provide a backend-owned JSON envelope for the workspace under `/admin/app/design-reviews/bootstrap.json`.
- **FR-003**: The envelope MUST include active scope, shell state, live session summaries, selected-session detail, revision summaries, round summaries, latest quorum decision, manual decisions, handoff state, workflow options, quorum policies, and safe action links.
- **FR-004**: The workspace MUST create sessions by calling the existing design-review session API or an equivalent backend action that persists live records.
- **FR-005**: The workspace MUST launch coordinator rounds only through live coordinator APIs and MUST not fabricate round or runtime-run state.
- **FR-006**: The workspace MUST render reviewer verdict summaries, scores, blocker counts, usage summary keys, and artifact references without raw provider or prompt payloads.
- **FR-007**: The workspace MUST render manual-resolution controls only when backend state reports manual resolution.
- **FR-008**: Manual actions MUST submit safe rationale, accepted-risk flag when relevant, decision type, optional next-revision summary, round reference, tenant scope, and idempotency key.
- **FR-009**: The workspace MUST render final handoff references from live handoff records only.
- **FR-010**: The workspace MUST include truthful empty, denied, loading, validation, stale/conflict, dependency, and unexpected-error states.
- **FR-011**: The workspace MUST preserve existing admin shell navigation, breadcrumbs, scope switching, command/search, responsive behavior, focus states, and accessible names.
- **FR-012**: The implementation MUST add focused backend route tests, React Testing Library/Vitest coverage, Playwright route evidence, QA docs, and curl regression evidence when public route coverage changes.

### Key Entities *(include if feature involves data)*

- **Design Review Workspace Envelope**: Backend-owned page data for session list, selected detail, controls, state, policies, workflow options, and provenance.
- **Session Summary**: Safe row projection for a live design review session.
- **Selected Session Detail**: Safe detail projection including revisions, rounds, quorum decision, manual decisions, verdicts, and handoff.
- **Workspace Action**: Safe action descriptor for create, launch, refresh, and manual decision flows.
- **Workflow Option**: Authorized published workflow bundle summary eligible for coordinator launch.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Opening `/admin/app/design-reviews` with seeded live records displays the seeded session, round, quorum, verdict summary, and handoff reference.
- **SC-002**: Opening the workspace for an empty tenant displays an empty state and no fabricated records.
- **SC-003**: Creating a session through the workspace persists a live session with an immutable initial revision.
- **SC-004**: Launching a round through the workspace creates a DB-backed runtime run and shows the new round after refresh.
- **SC-005**: Manual-resolution actions are available only in manual state and result in live persisted decisions.
- **SC-006**: Frontend typecheck, Vitest, backend route tests, QA docs, Playwright, run_spec_qa, and multi-agent curl regression all pass.

## Assumptions

- Spec 060 design-review domain records and APIs are available.
- Spec 062 coordinator APIs are available for launch, completion, and manual decisions.
- No new database migration is planned; the workspace is a read/write projection over existing durable records.
- Local QA may seed deterministic live rows, but production routes must not include hidden mock records.
- React admin assets are still built and served through the existing FastAPI admin shell.

## Testing Instructions

- Add backend integration coverage for workspace envelope, empty state, selected session, workflow options, and tenant denial.
- Add React tests for live session rendering, empty state, create form, launch action, and manual-resolution controls.
- Add route-level Playwright validation for `/admin/app/design-reviews`.
- Add QA seed/verify scripts that create live QA063 records and verify the workspace bootstrap envelope.
- Update `curl_testing.md` when public React workspace routes are added.

## PR Review Guidance

- Confirm the workspace uses live design-review tables and existing coordinator APIs.
- Confirm no sample sessions or fake verdicts are served in production routes.
- Confirm visible copy avoids implementation-framework labels.
- Confirm tenant isolation and redaction are enforced at both envelope and action layers.
- Confirm form controls are accessible and remain usable at mobile and desktop widths.

## Documentation Impact

- Add Spec 063 plan, research, data model, contracts, quickstart, tasks, QA guide, UI walkthrough, manual QA user guide, and PR notes.
- Update `AGENTS.md` Spec Kit pointer to this plan during planning.
- Update `curl_testing.md` for new `/admin/app/design-reviews` route coverage.
