# Feature Specification: Test Bench React Live Data

**Feature Branch**: `codex/053-test-bench-react-live-data`  
**Created**: 2026-05-07  
**Status**: Draft  
**Input**: User description: "Create a feature specification for Test Bench React Live Data. Replace the deterministic test-bench React projection with live data from agent test suite, case, assertion, run, run step, artifact, publication requirement, publish-gate, and audit repositories/services. React must display real suites, cases, assertions, run launcher metadata, runs, progress, diagnostics, artifacts, publish-gate evidence, and audit records. Empty states must be truthful when no suites or runs exist."

## Clarifications

### Session 2026-05-07

- Q: What is the source of truth for suite, case, assertion, run, artifact, publish-gate, and audit state? → A: Use AgentTestBenchService, AgentTestRepository, artifact storage references, workflow publish-gate services, usage summaries, and audit records as the source of truth; React receives only backend-owned projections. (autopilot)
- Q: Which execution modes may local QA and browser validation launch? → A: Use mocked-safe or deterministic local execution modes only; no real provider, connector, credential, external tool, or outbound calls run unless an explicit approved artifact marks a live probe path. (autopilot)
- Q: How should target workflow, profile, and publication references be resolved? → A: Resolve only persisted, authorized, current-scope workflow, profile, suite, case, and publish-gate requirement records; missing, stale, or cross-tenant references return unavailable, stale, or denied states. (autopilot)
- Q: How should launch idempotency and progress polling behave? → A: Persist run launch requests with idempotency and revision evidence, poll durable run and step state, and show pending or unavailable progress when evidence is absent rather than fabricating completion. (autopilot)
- Q: What test evidence may React and QA artifacts display? → A: Display safe summaries, artifact references, hashes, access outcomes, timestamps, and audit references only; raw transcripts, prompts, completions, run payloads, traces, local paths, stack traces, and unsafe artifact content never render. (autopilot)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Review Live Test Bench State (Priority: P1)

A platform operator, tenant administrator, or workflow reviewer opens the test bench workspace and sees only authorized live suites, cases, assertions, run launcher choices, runs, progress, diagnostics, artifacts, publish-gate evidence, and audit records for the active scope. If the active database has no relevant records, each panel presents a truthful empty, denied, or unavailable state instead of deterministic demonstration rows.

**Why this priority**: This is the core live-data migration outcome. Reviewers need to trust that test bench state reflects durable authoring and execution evidence instead of invented suites, fake runs, fake artifacts, or fixed publish-gate results.

**Independent Test**: Can be tested by loading the test bench workspace with an empty QA database and with QA-seeded live records, then comparing the browser and JSON responses to persisted test bench state.

**Acceptance Scenarios**:

1. **Given** an authorized tenant administrator and an empty live database, **When** the administrator opens the test bench workspace, **Then** suite, case, run, artifact, publish-gate, progress, diagnostic, and audit panels show truthful empty or unavailable states with safe setup guidance.
2. **Given** an authorized tenant administrator and persisted QA test suites and cases, **When** the administrator opens the test bench workspace, **Then** suite lists, suite detail, case lists, assertion summaries, and launcher metadata match only persisted records for that tenant.
3. **Given** persisted QA test runs and run steps, **When** an authorized reviewer opens run detail, **Then** run status, progress, diagnostics, artifact references, and publish-gate evidence match durable execution records and safe artifact metadata.
4. **Given** an unauthorized or cross-tenant principal, **When** the principal requests test bench data, **Then** the response is denied or redacted without exposing suite names, case names, workflow references, run ids, artifact labels, traces, or audit details from another tenant.

---

### User Story 2 - Inspect Redaction-Safe Test Evidence (Priority: P2)

An authorized reviewer opens suite, case, assertion, run, diagnostic, artifact, publish-gate, and audit details and receives enough evidence to understand quality status without seeing raw prompts, completions, run payloads, private workflow data, raw test transcripts, local paths, stack traces, unauthorized tenant labels, or unsafe artifact content.

**Why this priority**: Test bench evidence can contain sensitive runtime and workflow-adjacent information. The workspace must remain useful for release decisions while preserving redaction and tenant boundaries.

**Independent Test**: Can be tested by seeding suites, cases, assertions, runs, artifacts, diagnostics, publish-gate evidence, and audit rows containing sensitive-adjacent source values, then verifying that React and JSON responses contain only safe summaries and artifact references.

**Acceptance Scenarios**:

1. **Given** a test suite with cases and assertions, **When** an authorized reviewer views suite detail, **Then** the UI shows suite identity, case coverage, assertion summaries, revision state, and safe authoring metadata without raw test payloads.
2. **Given** a completed or failed run with run steps and diagnostics, **When** a reviewer opens run detail, **Then** the UI shows safe progress, result, diagnostic, and failure summaries without raw prompts, completions, stack traces, memory contents, or run payloads.
3. **Given** persisted artifact references, **When** a reviewer opens artifact evidence, **Then** the UI shows safe artifact metadata, retention status, and access outcome without local filesystem paths or raw artifact contents.
4. **Given** publish-gate evidence for a workflow or revision, **When** a reviewer inspects release readiness, **Then** the UI explains the latest repository-backed decision, freshness, required evidence, missing evidence, and audit references without synthetic pass results.

---

### User Story 3 - Exercise Durable Test Bench Actions (Priority: P3)

An authorized user performs at least one safe visible action from the test bench workspace, and the result persists through backend services. Examples include creating or updating a suite, adding a case, launching a local-safe run, refreshing publish-gate evidence, or requesting a redaction-safe artifact view.

**Why this priority**: The live-data migration must prove that authoring and launch actions produce durable backend evidence, not browser-only or backend-fixed success messages.

**Independent Test**: Can be tested by performing a user-visible test bench action in Playwright, then verifying the persisted result through a backend API first and a redaction-safe QA database query when the API cannot expose the needed evidence.

**Acceptance Scenarios**:

1. **Given** a seeded tenant and an authorized test bench user, **When** the user creates or updates a suite or case, **Then** the mutation returns persisted revision evidence and the refreshed workspace shows the updated suite or case.
2. **Given** a seeded suite with runnable cases and local-safe execution mode, **When** the user launches a test run, **Then** the run is persisted with safe progress state and the refreshed workspace shows the new run.
3. **Given** a workflow publish gate that requires test bench evidence, **When** the user refreshes publish-gate readiness, **Then** the response is based on persisted current-revision test evidence and avoids fake passing gates.
4. **Given** a stale, denied, or unavailable test bench action, **When** the user submits it, **Then** the system returns a safe conflict, denied, or unavailable result without creating fake successful evidence.

---

### Edge Cases

- Empty suite lists, case lists, run lists, artifact lists, publish-gate evidence, diagnostics, and audit timelines all return truthful empty states.
- Suites without cases cannot appear as complete coverage for publish-gate evidence.
- Cases without assertions show unavailable assertion coverage and cannot be counted as passing evidence.
- Runs without durable step evidence show pending or unavailable progress, not fabricated completion.
- Failed runs expose safe failure summaries only and never print raw stack traces, raw prompts, raw completions, memory contents, or runtime payloads.
- Artifact records with unavailable storage metadata show unavailable artifact evidence, not synthetic artifact references.
- Publish-gate evidence that is stale relative to the current workflow or suite revision is marked stale and cannot be treated as current pass evidence.
- Launch requests in local QA use mocked-safe or deterministic local execution only and never call real providers, external tools, credentials, or outbound resources.
- Cross-tenant suite, case, run, artifact, workflow, and audit identifiers fail closed.
- Auth0-shaped principals and local-principal QA identities produce the same authorization outcomes for equivalent roles.
- Generated TypeScript contracts reject malformed test bench responses and accept empty-state envelopes.
- QA screenshots, docs, and artifacts do not include raw transcripts, prompts, completions, run payloads, local filesystem paths, stack traces, unauthorized tenant labels, or unsafe artifact contents.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST replace deterministic production test bench data with authorized live projections from durable suite, case, assertion, run, run step, artifact, publish-gate evidence, and audit records.
- **FR-002**: The system MUST return truthful empty, denied, or unavailable states when no live authorized records exist for a suite, case, run, artifact, publish-gate, diagnostic, progress, or audit panel.
- **FR-003**: The system MUST preserve role and tenant authorization for suite authoring, case authoring, run launch, run progress, artifact access, publish-gate evidence, and audit surfaces.
- **FR-004**: The system MUST expose suite lists and suite details only from persisted suite, case, assertion, revision, and authoring metadata records.
- **FR-005**: The system MUST expose run lists and run details only from persisted run, run step, progress, diagnostic, result, artifact, and audit records.
- **FR-006**: The system MUST expose run launcher metadata only from authorized persisted suites, cases, target workflow or profile references, execution-mode policy, and tenant scope records.
- **FR-007**: The system MUST expose publish-gate evidence only from repository-backed current-revision requirements and durable test bench evidence freshness checks.
- **FR-008**: The system MUST expose artifact information only as redaction-safe metadata, access decisions, hashes, retention state, and artifact references; raw artifact contents and local paths MUST NOT reach React responses.
- **FR-009**: The system MUST keep raw prompts, completions, memory contents, run payloads, private channel messages, raw test transcripts, raw tool payloads, local filesystem paths, stack traces, and unauthorized tenant labels out of React contracts, redirects, exports, screenshots, QA artifacts, logs, and docs.
- **FR-010**: The system MUST provide durable safe mutations for at least one user-visible test bench action and return persisted result evidence, safe conflicts, denied states, or unavailable states as appropriate.
- **FR-011**: The system MUST validate at least one safe test bench mutation through Playwright and post-UI API or redaction-safe database verification before the spec is marked complete.
- **FR-012**: The system MUST update generated React TypeScript contracts so frontend code accepts live empty-state test bench envelopes and rejects malformed or unsafe test bench payloads.
- **FR-013**: The system MUST validate both Auth0-shaped backend route behavior and local-principal browser behavior for tenant, platform, and cross-tenant test bench surfaces.
- **FR-014**: The system MUST update live-data scanner guardrails so former deterministic qa033/qa043 suite, run, artifact, gate, and audit markers fail when found in production test bench builders or React routes while remaining allowed in test-only and historical spec artifacts.
- **FR-015**: The system MUST produce QA environment, QA guide, UI walkthrough, manual QA user guide, reviewer notes, Playwright evidence, post-UI persistence evidence, and curl regression evidence for qa053.

### Key Entities *(include if feature involves data)*

- **Agent Test Suite**: Tenant-scoped collection of test cases, revision metadata, target workflow or profile references, ownership, status, and publish-gate relevance.
- **Agent Test Case**: Suite-scoped test definition with safe input summary, expected outcome summary, execution-mode requirements, status, and revision metadata.
- **Assertion Summary**: Redaction-safe pass/fail expectation, matcher category, threshold or condition summary, and result status for a case or run.
- **Test Run**: Durable execution request with suite, case selection, launch mode, idempotency key, status, progress, result, timestamps, actor, and tenant scope.
- **Run Step**: Ordered progress event or case execution record with safe status, summary, timing, diagnostic category, and audit reference.
- **Test Artifact**: Redaction-safe reference to evidence created by a run, including artifact kind, safe label, hash or reference, retention state, access outcome, and timestamps.
- **Publish-Gate Evidence**: Repository-backed decision that links current workflow or revision requirements to qualifying test bench suites, runs, artifacts, and freshness.
- **Test Bench Audit Record**: Append-only safe event describing suite authoring, case authoring, launch, run progress, artifact, publish-gate, denial, or export activity.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In an empty qa053 database, every test bench JSON route and browser panel returns a truthful empty, denied, or unavailable state with zero deterministic suite, run, artifact, gate, or audit rows.
- **SC-002**: In a seeded qa053 database, test bench JSON routes and browser panels return only persisted records authorized for the active tenant or platform scope.
- **SC-003**: A Playwright flow performs at least one user-visible test bench action and a post-UI API or QA database check proves the resulting state persisted.
- **SC-004**: Auth0-shaped backend tests and local-principal Playwright tests cover tenant, platform, and cross-tenant test bench access.
- **SC-005**: Redaction tests confirm raw prompts, completions, memory contents, raw run payloads, raw transcripts, local paths, stack traces, unauthorized tenant labels, and unsafe artifact contents are absent from React responses, screenshots, QA docs, and artifacts.
- **SC-006**: Generated TypeScript contract checks, focused backend tests, focused frontend tests, scanner tests, QA document validation, Spec QA, Playwright validation, and multi-agent curl validation all pass before the queue advances.

## Assumptions

- Existing test bench services, repositories, workflow publish-gate services, artifact storage abstractions, audit records, and authorization policies remain the authoritative source for live test bench state.
- QA seed data may create real suites, cases, assertions, runs, run steps, artifact references, publish-gate evidence, and audit records through documented setup flows, services, repositories, public APIs, or safe scripts.
- Local QA run launches use mocked-safe or deterministic local execution modes unless an explicit artifact approves a live provider, connector, credential, or outbound probe path.
- Test fixtures with former qa033 or qa043 markers may remain under test-only or historical spec paths but must not be imported by production routes or production projection builders.
- This spec does not remove historical specs, test fixtures, or docs solely because they contain old deterministic markers.
- The dirty worktree is intentionally preserved across specs, and no Git commit is required before or after this spec while the autopilot continues.
