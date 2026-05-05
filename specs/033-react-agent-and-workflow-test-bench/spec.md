# Feature Specification: React Agent And Workflow Test Bench

**Feature Branch**: `codex/033-react-agent-and-workflow-test-bench`  
**Created**: 2026-05-05  
**Status**: Draft  
**Input**: User description: "Create a feature specification for a React Agent and Workflow Test Bench. Platform and tenant admins must be able to define reusable test suites and cases, select safe execution modes, launch tests against prompts, profiles, workflow drafts, subworkflows, or published workflows, inspect results, understand pass/fail diagnostics, review redacted traces and artifacts, and see publish-gate evidence tied to the current workflow draft revision or published target version. The UI must make testing understandable for non-technical admins without exposing raw prompts, completions, secrets, tools, raw connector payloads, or unauthorized tenant data."

## Clarifications

### Session 2026-05-05

- Q: How should suite and case authoring be organized for non-technical administrators? A: Use guided suite and case forms with backend-owned target, assertion, threshold, and safe-mode metadata. (autopilot)
- Q: What is the default local execution mode? A: Default to mock model and mock tools; side-effect-disabled gateway mode is explicit, and real dependency probes require policy approval. (autopilot)
- Q: How much evaluator prompt and rationale detail should React show? A: Show evaluator references, safe rationale summaries, and pass/fail thresholds only; raw evaluator prompts, raw completions, and raw transcripts stay outside browser contracts. (autopilot)
- Q: How should run progress update? A: Use backend-owned status summaries through polling or existing SSE-compatible patterns; React must not infer terminal state from local timers or partial client state. (autopilot)
- Q: How should assertion editing work? A: React edits structured assertion descriptors supplied by the backend, including comparator options, path summaries, severity, and validation errors; evaluator logic stays server-side. (autopilot)
- Q: How should artifacts be displayed? A: Render artifact references, checksums, size, retention state, redaction class, and authorized access status, never raw artifact payloads or storage paths. (autopilot)
- Q: How should target revision binding work? A: Suite runs and publish-gate evidence must bind to the current prompt/profile/workflow/subworkflow/published workflow target revision supplied by backend contracts. (autopilot)
- Q: How should stale evidence be presented? A: Missing, running, failing, stale, and current passing evidence are explicit gate states with remediation and run links; stale evidence cannot satisfy publication. (autopilot)
- Q: How should workflow publish gates link back to test evidence? A: Use authorized direct links from workflow builder and publish-gate panels to the exact suite, run, target revision, and artifact evidence. (autopilot)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Author Reusable Test Suites (Priority: P1)

Platform and tenant administrators can create and edit reusable test suites and cases through guided forms, choose a supported target, define fixture inputs, set deterministic assertions and thresholds, and understand what each case validates without reading raw JSON or runtime internals.

**Why this priority**: The test bench only creates release confidence if administrators can express expected behavior in durable suites and cases before launching runs or gating publication.

**Independent Test**: Sign in as an Acme tenant administrator, open the React test bench route, create a suite for a workflow draft, add a case with fixture metadata and assertions, save it, reload the suite detail view, and verify the suite remains tenant-scoped and redaction-safe.

**Acceptance Scenarios**:

1. **Given** a tenant administrator with access to a workflow draft, **When** they create a suite with guided defaults, **Then** the suite records the tenant scope, target type, target revision, safe execution defaults, pass threshold, and publish-gate eligibility.
2. **Given** a suite exists, **When** the administrator adds a case, **Then** the page accepts fixture metadata, expected contract shape summary, deterministic assertions, optional evaluator reference, and case threshold without rendering raw fixture bodies after save.
3. **Given** a platform administrator, **When** they create a suite for a published workflow or subworkflow, **Then** the suite records a platform-safe target summary and authorized tenant availability without exposing tenant-private run content.
4. **Given** a non-admin or cross-tenant principal, **When** they attempt to create or edit a suite, **Then** access fails closed with a safe problem summary and no suite, case, target, fixture, prompt, or assertion detail.

---

### User Story 2 - Launch Safe Test Runs (Priority: P1)

Administrators can launch test runs against prompts, runtime profiles, workflow drafts, subworkflows, or published workflows using safe execution modes. The default local mode uses mock model and mock tools, while real dependency probes are available only when policy explicitly allows them.

**Why this priority**: Runs must exercise test-bench behavior without accidentally invoking production providers, connector side effects, Telegram delivery, or credential resolution.

**Independent Test**: From a saved suite, launch one mock model/mock tools run and one side-effect-disabled gateway-mode run, verify each run records safe mode, target revision, progress, blocked side effects, and terminal pass/fail status, and confirm local QA made no live external calls.

**Acceptance Scenarios**:

1. **Given** a suite with active cases, **When** an administrator launches a mock-mode run, **Then** the run starts with deterministic model output, mock tool results, explicit idempotency, target revision binding, and queued/running status feedback.
2. **Given** a run uses side-effect-disabled gateway mode, **When** the runtime path evaluates model or tool decisions, **Then** the page shows ModelGateway and SkillExecutionGateway safe evidence, blocked side-effect decisions, and no raw provider or connector payloads.
3. **Given** a real dependency probe is requested without approval, **When** the administrator launches the run, **Then** the launch is rejected before execution with policy reasons, audit evidence, and remediation guidance.
4. **Given** a run is already in progress, **When** the administrator refreshes the page, **Then** progress resumes from backend run state without duplicating completed side effects, usage records, or case results.

---

### User Story 3 - Inspect Results And Diagnostics (Priority: P2)

Administrators can inspect pass/fail outcomes, case and step diagnostics, assertion failures, contract validation findings, evaluator summaries, usage, latency, redacted traces, and safe artifact metadata from a run detail view.

**Why this priority**: Test results must be actionable for non-technical administrators and reviewable for release governance without revealing raw prompts, completions, connector payloads, secrets, or unauthorized tenant data.

**Independent Test**: Open a deterministic failing run, identify the failing assertion and contract path, review redacted step traces and artifact references, and verify the page distinguishes assertion failure, contract failure, safe-mode block, and runtime error categories.

**Acceptance Scenarios**:

1. **Given** a passing run exists, **When** an administrator opens run detail, **Then** the page shows suite, target revision, safe mode, pass rate, case outcomes, latency, token usage, gateway decisions, and redaction summary.
2. **Given** a failing assertion exists, **When** the administrator opens diagnostics, **Then** the page shows expected shape summary, redacted actual shape summary, comparator, failed path, severity, and remediation guidance.
3. **Given** artifacts exist, **When** the administrator reviews evidence, **Then** large or sensitive artifacts appear as authorized references with checksum, size, retention state, redaction class, and access status rather than inline payloads.
4. **Given** a run failed because of safe-mode policy, **When** the administrator views the run, **Then** the page explains blocked model, tool, connector, credential, Telegram, or external dependency behavior without exposing the blocked payload.

---

### User Story 4 - Review Publish-Gate Evidence (Priority: P2)

Administrators can see which suites are required for workflow publication, whether the latest passing evidence matches the current draft revision or published target version, and why missing, stale, running, or failing evidence blocks publication.

**Why this priority**: The React workflow builder and publish gates must make test-bench evidence understandable before workflows become durable runtime definitions.

**Independent Test**: Open a workflow draft with a required suite, confirm stale evidence blocks publication, run the suite for the current draft revision, confirm the gate becomes ready, and verify the gate evidence links to the exact run and target revision.

**Acceptance Scenarios**:

1. **Given** a required suite has no current passing run, **When** an administrator opens gate evidence, **Then** the page shows missing evidence, target revision, required suite, and a run action.
2. **Given** a prior passing run exists for an older draft, **When** the current draft changes, **Then** the page marks evidence stale and does not allow that run to satisfy publication gates.
3. **Given** a current passing run exists, **When** the gate is evaluated, **Then** the page shows ready state, passing run reference, artifact references, audit reference, and authorized links to the workflow publish flow.
4. **Given** gate evidence is unavailable because audit persistence or redaction failed, **When** publication is evaluated, **Then** the gate fails closed with safe remediation guidance.

---

### User Story 5 - Review Governance Evidence (Priority: P3)

Auditors and administrators can review safe audit timeline, side-effect posture, redaction outcomes, artifact retention, usage summaries, and denied access evidence for suites, cases, runs, and publish-gate decisions.

**Why this priority**: Test-bench decisions become release evidence, so administrators need durable, reviewable, redacted records for compliance, incident review, and tenant support.

**Independent Test**: As an auditor, open the test bench evidence timeline for Acme, review suite changes, run launches, safe-mode decisions, result finalization, and publish-gate decisions, then verify Globex evidence is inaccessible.

**Acceptance Scenarios**:

1. **Given** lifecycle events exist, **When** an authorized auditor opens evidence, **Then** the page shows bounded records with actor summary, tenant scope, target summary, action, outcome, redaction status, and audit reference.
2. **Given** a cross-tenant request is attempted, **When** authorization cannot prove scope, **Then** the response contains only a safe denial reason and no suite, target, run, prompt, transcript, artifact, or tenant detail.
3. **Given** artifacts expire or become unavailable, **When** evidence is reviewed, **Then** the page shows retention state and safe fallback messaging without leaking storage paths.

### Edge Cases

- A suite target points to a prompt, profile, workflow draft, subworkflow, or published workflow version that was superseded, withdrawn, deleted, or is not authorized for the active tenant.
- A fixture, expected contract shape, assertion definition, evaluator configuration, or threshold is malformed, too large, unsafe, or includes secret-like text.
- A run launch is submitted with a stale suite revision, stale target revision, duplicate idempotency key, archived suite, no active cases, or unsupported execution mode.
- Mock mode passes but gateway side-effect-disabled mode fails because a tool or connector side effect is blocked.
- A real dependency probe is requested in local or CI validation or without explicit approval metadata.
- A run is interrupted while queued or running and must resume without duplicating side effects, usage records, artifacts, or audit events.
- A publish gate evaluates while a required run is queued, running, failed, stale, missing, or tied to a different target revision.
- Redacted traces contain prompt text, completion text, memory content, private channel messages, connector payloads, stack traces, local paths, or credential-like strings.
- Another tenant attempts to open a suite, case, run, artifact, target summary, publish gate, or audit record by direct URL.
- JavaScript is unavailable; existing Jinja test bench pages remain available during migration.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a protected additive React test bench route while preserving existing Jinja test bench and publish-gate routes as fallbacks until migration hardening retires them.
- **FR-002**: System MUST expose backend-owned JSON contracts for suite list, suite detail, suite form metadata, case form metadata, assertion editing, target selection, safe execution modes, run launch, run list, run detail, progress, diagnostics, artifact metadata, publish-gate status, audit timeline, mutation results, and denied states.
- **FR-003**: System MUST generate TypeScript contracts from backend schemas and React MUST consume generated contracts rather than hand-maintained browser models for protected test bench data.
- **FR-004**: System MUST support local-principal and Auth0-shaped principal validation for React test bench routes and protected actions.
- **FR-005**: System MUST fail closed when authorization, tenant scope, target access, suite revision, target revision, safe-mode policy, credential policy, external dependency policy, redaction, or audit persistence cannot be proven.
- **FR-006**: System MUST provide guided suite and case forms for non-technical administrators, including safe summaries for fixtures, expected contracts, assertions, evaluator configuration, pass thresholds, target revision binding, and publish-gate eligibility.
- **FR-007**: System MUST allow administrators to select targets from authorized prompt versions, runtime profile versions, workflow drafts, published subworkflows, and published workflows without exposing unauthorized target names or raw prompts.
- **FR-008**: System MUST provide a safe execution mode selector where mock model and mock tools are the default local mode, side-effect-disabled gateway mode is explicit, and real dependency probes require policy approval.
- **FR-009**: System MUST launch durable test runs with idempotency keys, safe mode, selected target revision, actor, tenant scope, queued/running/terminal status, and resume-safe progress evidence.
- **FR-010**: System MUST provide polling or existing SSE-compatible progress updates using backend-owned status summaries and MUST avoid browser-side inference of run state.
- **FR-011**: System MUST distinguish passed, failed assertion, contract failure, evaluator failure, safe-mode block, runtime error, canceled, timed out, and unavailable run states.
- **FR-012**: System MUST show run detail with case outcomes, step traces, assertion diagnostics, contract diagnostics, evaluator summaries, model/provider choices, prompt/profile/workflow/skill versions, token usage, latency, blocked side effects, redaction summary, and audit references.
- **FR-013**: System MUST render redacted transcript and trace excerpts only as safe summaries and MUST store oversized or sensitive artifacts by governed artifact reference.
- **FR-014**: System MUST provide artifact metadata with checksum, size, content class, retention state, access policy, redaction class, and authorized links without exposing storage paths or raw payloads.
- **FR-015**: System MUST provide publish-gate evidence tied to the current workflow draft revision or published target version, including missing, stale, running, failing, passing, audit-unavailable, and redaction-unavailable states.
- **FR-016**: System MUST link test bench gate evidence to workflow builder and publish flows only when those destinations are authorized for the active principal.
- **FR-017**: System MUST prevent stale or manually copied run evidence from satisfying publish gates for a changed target revision.
- **FR-018**: System MUST provide safe audit timeline and governance evidence for suite changes, case changes, run launch, safe-mode selection, side-effect blocking, result finalization, artifact access, redaction, denied access, and publish-gate decisions.
- **FR-019**: System MUST redact raw secrets, credential values, authorization headers, provider tokens, raw prompts, raw completions, private channel messages, memory contents, connector request/response payloads, raw tool outputs, stack traces, local paths, storage paths, and unauthorized tenant labels before rendering, logging, exporting, or storing QA artifacts.
- **FR-020**: System MUST ensure local and CI validation use deterministic mocks or fixtures for model, tool, connector, artifact, and gateway evidence unless a spec explicitly marks an approved live probe path.
- **FR-021**: System MUST provide loading, empty, denied, validation error, stale conflict, confirmation, queued, running, canceled, timeout, failed, partial, artifact unavailable, redaction unavailable, and audit unavailable states.
- **FR-022**: System MUST produce QA documents, Playwright screenshots, backend tests, frontend tests, generated contract checks, and full Spec QA evidence before advancing to the next spec.

### Key Entities *(include if feature involves data)*

- **TestBenchDashboard**: Authorized route envelope with active scope, summary metrics, safe callouts, navigation sections, current gate alerts, and authorized actions.
- **TestSuiteSummary**: Tenant-scoped suite metadata with target type, target label, target revision, default safe mode, pass threshold, latest run status, publish-gate status, archive state, and revision token.
- **TestSuiteDetail**: Full safe suite view with cases, assertions, run launcher metadata, target binding, publish-gate evidence, recent runs, and audit references.
- **TestCaseSummary**: Suite-owned case with safe fixture summary, expected contract summary, deterministic assertions, evaluator reference summary, threshold contribution, order, status, and revision token.
- **AssertionDefinition**: Backend-owned assertion metadata with assertion kind, path summary, comparator, expected value summary, severity, threshold impact, and validation state.
- **TargetRevisionBinding**: Authorized target type and version binding for prompt, profile, workflow draft, subworkflow, or published workflow with stale/current evidence state.
- **SafeExecutionModeOption**: Execution mode choice with allowed status, side-effect posture, provider/tool behavior, policy reason, and approval requirement.
- **TestRunSummary**: Run list item with run id, suite, target revision, safe mode, status, pass rate, started/finished labels, actor summary, and audit reference.
- **TestRunDetail**: Run result detail with case outcomes, step traces, diagnostics, usage, latency, redaction summary, artifact references, blocked side effects, and publish-gate evidence.
- **TraceStepSummary**: Redacted step evidence with case id, step label, runtime role, status, latency, usage, model/provider/profile/prompt/skill references, blocked side effects, and safe transcript excerpt.
- **ArtifactReferenceSummary**: Governed artifact metadata with reference id, label, checksum, size, content class, retention state, access status, and redaction class.
- **PublishGateEvidence**: Required suite and target-revision evidence with current/stale/missing/failing/running/passing status, latest run reference, remediation, and authorized workflow links.
- **TestBenchMutationResult**: Safe mutation response for suite save, case save, run launch, gate update, archive/restore, cancellation, artifact access, and recovery actions.
- **TestBenchAuditRecord**: Bounded governance event with tenant scope, actor summary, target summary, action, outcome, redaction class, safe diff summary, and audit reference.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A tenant administrator can create a suite, add a case, define assertions, bind a workflow draft revision, and save without seeing raw fixture or prompt bodies.
- **SC-002**: A local QA mock-mode run completes deterministically and displays pass/fail status, diagnostics, redacted trace summaries, usage, latency, and artifact metadata in the React UI.
- **SC-003**: A failing run clearly identifies at least one failed assertion or contract path and gives remediation guidance without exposing raw completions or connector payloads.
- **SC-004**: Publish-gate evidence rejects missing, stale, running, or failing runs and accepts only a current passing run tied to the selected target revision.
- **SC-005**: Cross-tenant and unauthorized route tests return safe denials without suite names, target names, transcripts, prompt text, artifact paths, or tenant labels from another tenant.
- **SC-006**: Local-principal and Auth0-shaped route tests cover authorized, denied, mutation, cross-tenant, safe-mode, artifact, publish-gate, and redaction behavior.
- **SC-007**: Playwright validation captures denied, suite authoring, case authoring, run launch, passing/failing diagnostics, artifact metadata, publish-gate evidence, and cross-tenant denial screenshots without unsafe text.
- **SC-008**: Full Spec QA passes with Ruff, format, mypy, coverage at or above 90 percent, generated TypeScript drift checks, frontend typecheck/tests/build, QA docs, and Playwright validation.

## Assumptions

- Existing Spec 015 agent/workflow test bench services, tenant-scoped suites, cases, assertions, runs, artifacts, publish-gate evidence, audit records, and redaction helpers remain authoritative.
- Existing Spec 020 graph execution evidence, Spec 024 repository-backed publish-gate evidence, and Spec 025 ModelGateway credential-resolution behavior remain authoritative for runtime and gateway summaries.
- The React test bench experience is additive; existing Jinja/admin API test bench routes remain available during migration.
- Local QA uses deterministic mocks and fixtures and does not require real Auth0, Telegram, provider, credential, connector, artifact storage, or external dependency calls.
- Redacted transcript and artifact screens prioritize summaries, references, and authorized links over raw JSON, raw prompts, raw completions, raw connector outputs, or implementation-specific payloads.
