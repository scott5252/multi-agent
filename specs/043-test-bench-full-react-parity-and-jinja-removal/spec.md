# Feature Specification: Test Bench Full React Parity And Jinja Removal

**Feature Branch**: `codex/043-test-bench-full-react-parity-and-jinja-removal`  
**Created**: 2026-05-06  
**Status**: Draft  
**Input**: User description: "Create a feature specification for Test Bench Full React Parity and Jinja Removal. Spec 033 added the React test bench workspace, but full removal requires React parity for suite list/detail/create/edit, case forms, assertion editing, target selection, run launch, run list/detail, progress, trace steps, result summaries, artifact metadata, publish-gate evidence, audit timeline, safe execution modes, stale evidence prevention, and all old direct links."

## Clarifications

### Session 2026-05-06

- Q: How should run progress update after the legacy progress templates are removed? A: Backend-owned polling snapshots remain acceptable; React must never infer pass/fail or terminal state from timers or partial client state. (autopilot)
- Q: How should artifact direct links work? A: Legacy artifact links redirect to React artifact metadata panels when authorized; raw payloads, storage paths, and local paths are never rendered. (autopilot)
- Q: How should suite and case edit routes behave after template deletion? A: Old suite, case, create, edit, and launch URLs redirect to React with tenant scope, ids, filters, saved-filter intent, breadcrumbs, and conflict state preserved when safe. (autopilot)
- Q: How should target revision binding be enforced? A: Suite runs and publish-gate evidence bind to backend-supplied current target revisions, and stale or copied evidence cannot satisfy publication. (autopilot)
- Q: How should workflow publish-gate links connect to test evidence? A: Workflow builder and publish-gate panels link only to authorized React test bench evidence for the exact suite, run, target revision, and artifact references. (autopilot)
- Q: How should approved real probe display be handled? A: React may display approved probe summaries and policy evidence only; local and CI validation keep real probes denied or mocked unless an existing policy approval explicitly permits them. (autopilot)
- Q: What should happen when an old route cannot safely redirect? A: Return a non-Jinja safe problem or documented retirement response without revealing whether protected data exists. (autopilot)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Manage Suites And Cases In React (Priority: P1)

Tenant and platform administrators can use the React test bench workspace to list suites, create and edit suites, open suite details, add and edit cases, manage assertions, select authorized targets, and recover from validation or stale-revision conflicts without needing any legacy server-rendered page.

**Why this priority**: The legacy templates cannot be removed until every suite and case authoring journey has an equivalent React path with the same backend-owned safety decisions.

**Independent Test**: Sign in with the local Acme admin principal, open the React test bench workspace, create a suite, add a case with structured assertions and target binding, reload through legacy suite and case URLs, and verify the user lands on the React view with tenant, filters, and safe summaries preserved.

**Acceptance Scenarios**:

1. **Given** an authorized administrator and existing suites, **When** they open the test bench suite list, **Then** React shows searchable suite summaries, target revision status, latest run status, publish-gate posture, safe actions, empty states, and denied states without rendering legacy templates.
2. **Given** an administrator creates or edits a suite, **When** they submit guided fields, **Then** the system validates tenant scope, target access, revision tokens, pass thresholds, safe execution defaults, and publish-gate eligibility before saving.
3. **Given** an administrator edits a case, **When** they configure fixture summaries, expected contract summaries, assertions, evaluator references, and thresholds, **Then** the saved view shows only safe summaries and structured validation feedback.
4. **Given** a non-admin or cross-tenant principal follows a direct suite, case, or edit URL, **When** authorization cannot be proven, **Then** the response fails closed with a safe problem or redirect and no suite, target, assertion, prompt, transcript, artifact, or tenant-private detail.

---

### User Story 2 - Launch And Monitor Runs In React (Priority: P1)

Administrators can launch deterministic test runs, choose approved safe execution modes, monitor queued and running progress, cancel or retry where allowed, and open run list or run detail views entirely in React.

**Why this priority**: Test-bench publication confidence depends on run launch and progress behavior, and these workflows are also the highest risk for accidental external side effects.

**Independent Test**: From a saved suite, launch a mock model/mock tools run, observe backend-owned progress snapshots, open the run through an old run URL, and verify terminal status, idempotency, safe mode, target revision, and blocked side-effect evidence remain visible in React.

**Acceptance Scenarios**:

1. **Given** a suite has active cases, **When** an administrator launches a mock-mode run, **Then** the run records tenant scope, actor, idempotency, target revision, safe mode, queued/running status, and deterministic execution evidence.
2. **Given** a run uses side-effect-disabled gateway mode, **When** runtime decisions are summarized, **Then** React shows safe model and tool gateway evidence, blocked side-effect reasons, and policy outcomes without raw provider or connector payloads.
3. **Given** a run is queued or running, **When** the user refreshes or follows a direct run link, **Then** progress resumes from backend state without duplicated side effects, duplicated artifacts, or client-inferred terminal status.
4. **Given** a real dependency probe is unavailable, unapproved, or disallowed in local or CI validation, **When** a launch request asks for it, **Then** the system rejects the request before execution with safe remediation guidance and audit evidence.

---

### User Story 3 - Inspect Results, Traces, And Artifacts In React (Priority: P2)

Administrators and auditors can inspect pass/fail results, assertion diagnostics, contract findings, redacted trace steps, usage summaries, latency, result summaries, safe artifact metadata, and audit references in React.

**Why this priority**: Removing legacy result templates is safe only when React makes failures understandable without leaking raw prompts, completions, transcripts, connector payloads, storage paths, or unauthorized tenant labels.

**Independent Test**: Open one passing and one failing deterministic run, review result summaries, failed assertion paths, trace steps, artifact references, and audit records, and verify unsafe text is absent from the browser, screenshots, exports, and QA artifacts.

**Acceptance Scenarios**:

1. **Given** a passing run exists, **When** an administrator opens the run detail view, **Then** React shows suite, case outcomes, pass rate, target revision, safe mode, usage, latency, trace status, artifact metadata, redaction status, and audit references.
2. **Given** a failing assertion or contract validation exists, **When** diagnostics are opened, **Then** the page shows comparator, safe expected and actual summaries, path summaries, severity, remediation, and result category without raw completions or connector payloads.
3. **Given** artifact references exist, **When** an authorized user reviews evidence, **Then** React shows label, checksum, size, content class, retention state, access status, and redaction class without inline payloads or filesystem/storage paths.
4. **Given** audit or redaction evidence is unavailable, **When** result detail is rendered, **Then** the page marks evidence unavailable and fails closed for publish-gate readiness.

---

### User Story 4 - Prove Publish-Gate And Direct-Link Parity (Priority: P2)

Administrators can review workflow publish-gate evidence, distinguish missing, stale, running, failing, and passing evidence, and follow all old test-bench direct links safely into React or a documented non-Jinja compatibility response.

**Why this priority**: Stale test evidence must never satisfy workflow publication, and every removed template needs deletion-grade route evidence.

**Independent Test**: Open workflow publish-gate evidence for a current draft, verify stale evidence blocks publication, run the required suite for the current target revision, confirm the gate becomes ready, and test old suite, case, run, artifact, gate, audit, launch, create, and edit links after template removal.

**Acceptance Scenarios**:

1. **Given** required evidence is missing, stale, running, failing, or tied to a different target revision, **When** gate status is evaluated, **Then** React explains the blocker and prevents the evidence from satisfying publication.
2. **Given** current passing evidence exists, **When** a publish gate is viewed, **Then** React shows the required suite, target revision, latest passing run, artifact references, audit references, and authorized workflow links.
3. **Given** a legacy browser URL is used, **When** the route can safely map to React, **Then** the authenticated redirect preserves tenant id, safe route parameters, filters, saved-filter intent, breadcrumbs, and conflict state.
4. **Given** a legacy browser URL cannot safely redirect, **When** it is requested, **Then** the handler returns a non-Jinja safe problem or documented retirement response without exposing whether protected data exists.

### Edge Cases

- A suite, case, assertion, target binding, or run launch is submitted with a stale revision token, duplicate idempotency key, unsupported execution mode, archived suite, empty case set, malformed assertion, unsafe fixture summary, or invalid threshold.
- A target prompt, runtime profile, workflow draft, subworkflow, or published workflow has been superseded, withdrawn, deleted, unpublished, or is not authorized for the active tenant.
- A direct legacy URL includes unsafe query parameters, cross-tenant identifiers, missing tenant scope, stale saved-filter state, unknown breadcrumb intent, or a route parameter that no longer exists.
- A run is interrupted while queued or running and must resume without duplicating model calls, tool calls, usage records, side-effect intents, artifacts, or audit events.
- Mock execution passes but side-effect-disabled gateway mode fails because a provider, connector, credential, Telegram, or tool side effect is blocked by policy.
- Artifact metadata is unavailable, expired, too large, access denied, retention-blocked, or redaction-blocked.
- Audit persistence, redaction classification, target revision lookup, or publish-gate evidence refresh fails.
- A user attempts to access another tenant's suite, case, run, target summary, artifact reference, gate evidence, or audit event by direct URL.
- Old forms post to legacy endpoints after the templates are removed.
- JavaScript fails to load after the server-rendered templates are gone.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide full React coverage for test bench suite list, suite detail, suite create, suite edit, case create, case edit, assertion editing, target selection, run launch, run list, run detail, progress, diagnostics, artifact metadata, publish-gate evidence, and audit timeline.
- **FR-002**: System MUST keep backend-owned JSON APIs used by React as the only source of authorization, tenant scoping, target eligibility, validation, safe execution mode decisions, redaction, audit status, artifact access, and publish-gate readiness.
- **FR-003**: System MUST generate and validate TypeScript contracts from Pydantic schemas for all React test bench envelopes, mutations, forms, safe problems, and legacy redirect metadata.
- **FR-004**: System MUST support Auth0-shaped principal route tests and local-principal browser validation for authorized, denied, mutation, stale-conflict, direct-link, and cross-tenant behaviors.
- **FR-005**: System MUST convert old browser-rendering test bench routes to authenticated redirects, safe non-Jinja compatibility handlers, or documented retirement responses before deleting their templates.
- **FR-006**: System MUST preserve tenant id, route parameters, filters, saved-filter intent, breadcrumbs, conflict state, and safe return destinations when redirecting legacy suite, case, run, artifact, gate, audit, create, edit, and launch URLs to React.
- **FR-007**: System MUST reject unsafe redirect destinations, unsafe query parameters, unknown tenant scope, unauthorized ids, and stale route state without exposing whether protected objects exist.
- **FR-008**: System MUST keep legacy form POST behavior safe after template removal by returning mutation results, redirecting to React, or returning safe problem details with no raw payload echo.
- **FR-009**: System MUST ensure default local and CI run launch uses deterministic mock model and mock tool behavior, with side-effect-disabled gateway mode explicit and real dependency probes denied unless approved by existing policy evidence.
- **FR-010**: System MUST prevent stale, copied, manually edited, unauthorized, or different-target run evidence from satisfying workflow publish gates.
- **FR-011**: System MUST render trace steps, result summaries, evaluator summaries, usage, latency, blocked side effects, and diagnostics as safe summaries only.
- **FR-012**: System MUST render artifact evidence only as governed metadata and authorized references, never raw payloads, local paths, object storage paths, or transcript bodies.
- **FR-013**: System MUST provide loading, empty, denied, validation error, stale conflict, queued, running, canceled, timed out, failed, partial, redaction unavailable, audit unavailable, artifact unavailable, and safe retirement states.
- **FR-014**: System MUST delete only test-bench-owned Jinja templates and Jinja-only static assets with deletion-grade parity evidence for this spec.
- **FR-015**: System MUST retain global Jinja dependencies, template providers, and fallback infrastructure until the final decommission spec proves no runtime path imports them.
- **FR-016**: System MUST update documentation, QA guides, reviewer notes, route inventories, and migration ledger evidence to describe the React-only test bench browser surface.
- **FR-017**: System MUST prove removed templates through backend route tests, redirect tests, contract tests, frontend tests, route/import scanners, QA docs, and Playwright screenshots.
- **FR-018**: System MUST never render, log, export, screenshot, or document raw secrets, credential values, provider authorization headers, raw prompts, raw completions, memory contents, raw run payloads, private channel messages, raw connector payloads, raw tool payloads, raw test transcripts, local filesystem paths, storage paths, stack traces, full Telegram identifiers, link tokens after creation, or unauthorized tenant labels.

### Key Entities *(include if feature involves data)*

- **TestBenchReactWorkspace**: Protected React route envelope containing active scope, navigation, suite/run/gate summaries, migration status, and authorized actions.
- **TestSuiteSummary**: Tenant-scoped suite row with target type, target label, target revision, default safe mode, latest run status, publish-gate status, archive state, filters, and revision token.
- **TestSuiteDetail**: Safe detail view with cases, assertions, run launcher metadata, target binding, publish-gate evidence, recent runs, audit references, and mutation affordances.
- **TestCaseEditorState**: Structured form state for fixture summaries, expected contract summaries, assertion descriptors, evaluator references, thresholds, validation errors, and revision tokens.
- **AssertionDescriptor**: Backend-owned assertion metadata with kind, path summary, comparator, expected value summary, severity, threshold impact, validation state, and redaction class.
- **TargetRevisionBinding**: Authorized prompt, profile, workflow draft, subworkflow, or published workflow target with current/stale evidence state.
- **SafeExecutionMode**: Run launch choice with side-effect posture, allowed status, policy reasons, approval requirement, provider behavior, and tool behavior.
- **TestRunSummary**: Run list item with run id, suite, target revision, safe mode, status, pass rate, actor summary, started/finished labels, and audit reference.
- **TestRunDetail**: Result view with case outcomes, trace steps, diagnostics, usage, latency, artifact references, redaction status, blocked side effects, and publish-gate linkage.
- **TraceStepSummary**: Redacted step evidence with case id, step label, runtime role, status, latency, usage, gateway references, blocked side effects, and safe excerpt summary.
- **ArtifactReferenceSummary**: Governed metadata with reference id, label, checksum, size, content class, retention state, access status, redaction class, and authorized link status.
- **PublishGateEvidence**: Required suite and target-revision evidence with current, stale, missing, running, failing, passing, audit-unavailable, and redaction-unavailable states.
- **LegacyRouteCompatibilityRecord**: Route mapping from old browser URLs and form posts to React redirects, safe compatibility responses, or documented retirement responses.
- **TestBenchAuditRecord**: Safe governance event with actor summary, tenant scope, target summary, action, outcome, redaction status, safe diff summary, and audit reference.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A tenant administrator can complete suite list, suite create/edit, case create/edit, assertion editing, target selection, run launch, run detail, and publish-gate review in React without visiting any server-rendered test bench page.
- **SC-002**: Every old test bench browser route and form action is covered by tests that prove a React redirect, safe non-Jinja compatibility response, or documented retirement response after template deletion.
- **SC-003**: Current passing evidence tied to the selected target revision satisfies publish gates, while missing, stale, running, failing, copied, unauthorized, or different-target evidence does not.
- **SC-004**: Passing and failing deterministic runs display diagnostics, trace steps, usage, latency, artifact metadata, blocked side effects, and audit references without unsafe raw content.
- **SC-005**: Cross-tenant and unauthorized route tests return safe denial behavior without suite names, target names, prompts, transcripts, artifact paths, run payloads, or tenant-private labels from another tenant.
- **SC-006**: Local-principal Playwright validation captures suite management, run launch/progress, result diagnostics, artifact metadata, publish-gate evidence, old-link redirects, and denied states with nonblank screenshots.
- **SC-007**: Auth0-shaped backend tests cover authorized, denied, mutation, stale conflict, redirect, unsafe redirect, and cross-tenant behaviors for the retired legacy routes.
- **SC-008**: QA documents, route inventory updates, reviewer notes, generated contract checks, backend tests, frontend tests, Spec QA, and Playwright validation all pass before Spec 044 begins.

## Assumptions

- Existing Spec 015 test bench services, repositories, suites, cases, assertions, runs, artifacts, publish-gate evidence, audit records, and redaction helpers remain authoritative.
- Existing Spec 033 React test bench contracts and components provide the baseline, but gaps discovered during deletion-grade parity review are in scope for this spec.
- Old browser URLs should redirect into `/admin/app/test-bench` child routes when route parameters and tenant scope can be safely preserved.
- Local and CI validation use deterministic mocks and fixtures and do not require real Auth0, Telegram, provider, credential, connector, artifact storage, or external dependency calls.
- This spec deletes only test-bench-owned templates and Jinja-only assets; shared Jinja infrastructure remains for later specs.
