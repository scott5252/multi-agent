# Feature Specification: Agent And Workflow Test Bench

**Feature Branch**: `codex/015-agent-workflow-test-bench`  
**Created**: 2026-05-02  
**Status**: Draft  
**Input**: User description: "Add an agent and workflow test bench for platform and tenant admins. Admins must be able to create test suites and test cases with fixture inputs, expected contract shapes, deterministic assertions, optional evaluator prompts, model/provider mode, tool/skill mode, and pass/fail thresholds. Admins must run tests against prompt versions, agent runtime profiles, workflow drafts, published subworkflows, or full published workflows. Test runs must support safe execution modes: mock model, mock tools, real model with side effects disabled, and approved real dependency probes. Test results must show step traces, model/provider choices, prompt/profile versions, skill versions, token usage, latency, contract validation results, redacted transcripts, artifacts, and pass/fail status. Workflow publication may require selected test suites to pass. Require tenant isolation, safe redaction, audit records, at least 90 percent coverage, docs, PR notes, testing instructions, and README updates."

## Autopilot Clarifications

- Q: Which real-dependency behavior is allowed by default? -> A: Real external side effects remain disabled unless an explicit approved probe mode is selected and audited; QA uses mock or mocked-provider paths only. (autopilot)
- Q: How are publication gates selected? -> A: Tenant or platform admins select required suites per workflow target, and publish is blocked only when the selected suite has no passing current result for the candidate target version. (autopilot)
- Q: What artifact content can be shown in result views? -> A: Result pages show redacted transcript summaries and metadata inline, with oversized or sensitive artifacts stored by reference under governed artifact storage. (autopilot)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Define Reusable Test Suites (Priority: P1)

Tenant and platform admins can create an agent test suite, add test cases, choose the target under test, provide fixture inputs, define expected contract shapes, configure deterministic assertions, optionally add evaluator prompts, and set pass/fail thresholds.

**Why this priority**: Without durable suites and cases, admins cannot express what "correct" means before publishing or changing prompts, profiles, skills, subworkflows, or workflows.

**Independent Test**: A tenant admin creates a suite for a workflow draft, adds two cases with fixtures and assertions, and sees the suite and case details returned through the API and rendered in the admin UI without accessing another tenant's suites.

**Acceptance Scenarios**:

1. **Given** a tenant admin with access to a workflow draft, **When** they create a suite with a fixture-backed case and deterministic assertions, **Then** the suite, case, assertions, and fixture metadata are saved under the tenant and listed on the test bench page.
2. **Given** a platform admin, **When** they create a suite for a published subworkflow, **Then** the suite records the target type, target identifier, selected version, threshold, and execution defaults.
3. **Given** a non-admin user, **When** they attempt to create or edit a suite, **Then** the request is denied and an audit-safe denial is recorded.

---

### User Story 2 - Run Tests In Safe Execution Modes (Priority: P1)

Admins can start test runs against prompt versions, agent runtime profiles, workflow drafts, published subworkflows, or published workflows using safe execution modes: mock model, mock tools, real model with side effects disabled, or approved real dependency probes.

**Why this priority**: The bench only protects production behavior if it can exercise runtime paths without leaking secrets, crossing tenant boundaries, or performing unsafe side effects.

**Independent Test**: A tenant admin starts one mock-model run and one mocked-provider real-gateway run for the same suite, and each run records the selected safe mode, target version, model/provider mode, tool/skill mode, blocked side effects, and terminal pass/fail status.

**Acceptance Scenarios**:

1. **Given** a suite with cases and assertions, **When** an admin starts a mock-model test run, **Then** the run executes with deterministic model output, mock tool responses, contract validation, assertion evaluation, usage capture, and no external dependency calls.
2. **Given** a suite configured for real model evaluation, **When** the admin selects real model with side effects disabled, **Then** the run may call the governed model gateway but blocks tool side effects and records the blocked decisions.
3. **Given** a suite that requests a real dependency probe, **When** the probe has not been approved for that tenant and target, **Then** the run is rejected before execution and the reason is visible to the admin.

---

### User Story 3 - Inspect Results And Diagnostics (Priority: P2)

Admins can inspect run results with step traces, model/provider choices, prompt/profile versions, skill versions, token usage, latency, contract validation details, evaluator results, redacted transcripts, artifact references, and pass/fail status.

**Why this priority**: Result diagnostics make test failures actionable and provide evidence for reviewers without exposing sensitive runtime data.

**Independent Test**: A failing run displays which assertion failed, which contract path was invalid, which provider/profile/prompt versions were used, which side effects were blocked, and where redacted evidence is stored.

**Acceptance Scenarios**:

1. **Given** a completed run, **When** an admin opens the run details, **Then** they see a timeline of case and step outcomes with latency, token usage, provider/model choices, version references, and redacted transcript excerpts.
2. **Given** a failed contract assertion, **When** the admin opens diagnostics, **Then** the invalid path, expected shape, actual redacted shape, and failure reason are shown.
3. **Given** a run that produced artifacts, **When** the admin reviews results, **Then** large artifacts are referenced through storage metadata rather than embedded raw payloads.

---

### User Story 4 - Gate Workflow Publication (Priority: P2)

Admins can require selected suites to pass before workflow drafts, subworkflows, or published workflow updates are published.

**Why this priority**: Publication gates prevent known regressions from becoming durable runtime definitions.

**Independent Test**: A workflow draft with a required suite cannot be published until a passing result exists for the current draft or candidate version; once the suite passes, publication can continue and records the evidence.

**Acceptance Scenarios**:

1. **Given** a workflow draft with a required suite, **When** an admin attempts to publish without a current passing result, **Then** the publish request is blocked with a clear test-bench failure reason.
2. **Given** a current passing result for the selected suite and candidate target version, **When** an admin publishes the workflow, **Then** publication succeeds and the published metadata references the passing test run.
3. **Given** a stale passing run from an earlier draft version, **When** an admin attempts to publish a newer candidate, **Then** the stale run is not accepted as gate evidence.

---

### User Story 5 - Review Governance Evidence (Priority: P3)

Auditors and admins can review audit records, redaction outcomes, tenant isolation decisions, usage summaries, and retention metadata for suites, cases, runs, result artifacts, and publication gate decisions.

**Why this priority**: The test bench becomes part of release governance and must be explainable during incident review, compliance review, and tenant support.

**Independent Test**: An auditor can view safe summaries of suite changes, run creation, side-effect blocking, result finalization, and publish gate decisions for their tenant while cross-tenant records remain inaccessible.

**Acceptance Scenarios**:

1. **Given** a completed test run, **When** an auditor reviews governance evidence, **Then** the audit timeline includes actor, tenant, target, safe mode, redaction status, usage summary, and artifact references without raw secrets.
2. **Given** a cross-tenant auditor, **When** they request another tenant's test runs, **Then** access fails closed and no target or transcript details are returned.
3. **Given** retention metadata for result artifacts, **When** an admin reviews the run, **Then** they can see which artifacts are retained, expired, or unavailable.

### Edge Cases

- A suite references a workflow draft or prompt/profile version that has been superseded, retired, or deleted from active listings.
- A test case fixture is malformed, too large for inline storage, or contains values that look like secrets.
- A deterministic assertion and evaluator assertion disagree on pass/fail status.
- A real provider probe is requested without approval, without a safe credential reference, or from a forbidden environment.
- A test run is interrupted while cases are pending and must resume without duplicating side effects or usage records.
- A publish gate is evaluated while a required test run is still in progress.
- A tenant admin attempts to use a suite, run, artifact, prompt, profile, skill, or workflow owned by another tenant.
- Result transcripts include prompt text, delegated credential names, provider messages, or tool payloads that must be redacted before display.
- Multiple admins edit the same suite or publication gate at the same time.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST allow tenant admins and platform admins to create, update, list, inspect, archive, and restore test suites scoped to a tenant and target type.
- **FR-002**: The system MUST allow admins to create, update, list, inspect, archive, and restore test cases within a suite, including fixture inputs, expected contract shapes, deterministic assertions, optional evaluator prompts, model/provider mode, tool/skill mode, and pass/fail thresholds.
- **FR-003**: The system MUST validate fixture inputs, expected contract shapes, assertion definitions, evaluator settings, thresholds, target references, and safe execution mode selections before a suite or run can be saved.
- **FR-004**: The system MUST support test targets for prompt versions, agent runtime profiles, workflow drafts, published subworkflows, and full published workflows.
- **FR-005**: The system MUST support safe execution modes for mock model, mock tools, real model with side effects disabled, and approved real dependency probes.
- **FR-006**: The system MUST block unapproved external side effects during test execution and record each blocked side-effect decision in the run result.
- **FR-007**: The system MUST start durable test runs from selected suites and targets, persist run status transitions, persist per-case and per-step outcomes, and resume interrupted runs without duplicating completed side effects or usage records.
- **FR-008**: The system MUST evaluate deterministic assertions against structured outputs and contract shapes and produce clear pass/fail diagnostics for each assertion.
- **FR-009**: The system MUST support evaluator-prompt assertions with governed model/provider routing, redacted inputs, pass/fail thresholds, and captured evaluator rationale summaries.
- **FR-010**: The system MUST record model/provider choices, prompt version references, profile version references, skill version references, workflow version references, token usage, latency, contract validation status, redacted transcript summaries, artifact references, and terminal pass/fail status for each run.
- **FR-011**: The system MUST store large fixtures, transcripts, and result artifacts outside PostgreSQL while persisting metadata, checksums, retention state, and access policy in PostgreSQL.
- **FR-012**: The system MUST redact secrets, credential references, prompt bodies when policy requires, raw provider messages, memory payloads, and sensitive tool payloads before displaying or exporting test evidence.
- **FR-013**: The system MUST enforce tenant isolation and role-based authorization across suites, cases, runs, artifacts, publication gates, audit records, and admin UI views.
- **FR-014**: The system MUST provide server-rendered admin UI views for suite management, case review, run launch, run result diagnostics, and publication gate status.
- **FR-015**: The system MUST expose API contracts for suite/case CRUD, run creation, run detail retrieval, run listing, and publish gate evaluation.
- **FR-016**: The system MUST allow admins to configure workflow publication gates that require selected suites to pass for the current candidate target version.
- **FR-017**: The system MUST block publication when required suites have no current passing result and allow publication when required suites have current passing evidence.
- **FR-018**: The system MUST emit audit records for suite changes, case changes, run creation, safe mode selection, side-effect blocking, result finalization, publish gate configuration, and publish gate decisions.
- **FR-019**: The system MUST capture usage summaries for model and evaluator calls performed in test mode without charging or aggregating them as production workflow usage.
- **FR-020**: The system MUST provide failure diagnostics that distinguish fixture validation failures, authorization failures, contract failures, deterministic assertion failures, evaluator failures, safe-mode blocks, runtime failures, and stale publish-gate evidence.
- **FR-021**: The system MUST include manual QA docs, browser QA docs, QA environment configuration, PR review notes, testing instructions, README updates, and automated test coverage of at least 90 percent for the relevant code.

### Key Entities *(include if feature involves data)*

- **Agent Test Suite**: A tenant-scoped collection of test cases for a specific target type, target identifier, target version selection, execution defaults, pass threshold, publication gate eligibility, archive state, and revision token.
- **Agent Test Case**: A suite-owned scenario with fixture metadata, expected contract shape, deterministic assertions, evaluator assertion configuration, model/provider mode, tool/skill mode, order, and archive state.
- **Agent Test Assertion**: A deterministic or evaluator-backed condition with an assertion kind, path, comparator, expected value or schema, severity, threshold contribution, and diagnostic text.
- **Agent Test Run**: A durable execution record for a suite and target version with safe mode, actor, status, pass/fail summary, usage summary, artifact metadata, redaction status, and idempotency key.
- **Agent Test Run Step**: A per-case or per-runtime-step result containing status, latency, token usage, model/provider/profile/prompt/skill references, blocked side effects, contract validation details, redacted transcript excerpts, and artifact references.
- **Publication Gate Requirement**: A workflow or subworkflow target rule that requires one or more suites to have current passing evidence before publication.
- **Test Bench Artifact**: Metadata for fixture, transcript, evaluator, or result payloads stored in governed artifact storage, including checksum, size, retention state, redaction classification, and access policy.
- **Test Bench Audit Record**: Append-only evidence for admin actions, safe-mode decisions, denied access, redaction outcomes, and publish gate decisions.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A tenant admin can create a suite with two cases, fixture metadata, contract expectations, assertions, and thresholds in under five minutes using the admin UI.
- **SC-002**: A mock-mode test run for a suite with at least two cases completes deterministically and reports pass/fail status, assertion diagnostics, usage summary, and redacted transcript metadata in under 30 seconds on a local QA environment.
- **SC-003**: Unauthorized suite, run, artifact, and gate access attempts return denial responses without leaking cross-tenant target names, transcript content, prompt content, or artifact paths.
- **SC-004**: Publication gating blocks stale or missing test evidence and accepts only a passing result tied to the current candidate target version in 100 percent of automated gate tests.
- **SC-005**: Redaction checks find zero raw fake secret values, raw delegated credential values, raw provider prompts, or unredacted tool payloads in API responses, UI pages, audit summaries, and stored inline run results.
- **SC-006**: Automated tests for the feature pass with the repository coverage gate of at least 90 percent.
- **SC-007**: Manual QA reviewers can follow the QA guide and browser guide from a fresh checkout without using production hosts, real credentials, or real provider keys.

## Assumptions

- Existing admin authentication, local-principal test mode, tenant scoping, audit helpers, workflow registry, prompt library, agent runtime profile catalog, skill registry, model gateway, and object-storage abstractions are reused.
- QA and automated tests use deterministic mock or mocked-provider behavior; no validation step requires real external credentials or production endpoints.
- Approved real dependency probes are represented by explicit metadata and authorization checks in this feature, while production-grade external probe orchestration can be extended later without changing the safe-mode contract.
- Workflow publication already has a validation or gate hook that can be extended to include test bench evidence.
- PostgreSQL stores transactional metadata and object storage stores large fixtures, transcripts, and artifacts.
- Server-rendered admin UI is sufficient for the first implementation; richer visual builders or asynchronous live trace streaming are out of scope for this slice.
