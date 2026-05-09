# Feature Specification: Design Review Coordinator And Iteration Loop

**Feature Branch**: `codex/062-design-review-coordinator-and-iteration-loop`  
**Created**: 2026-05-08  
**Status**: Draft  
**Input**: User description: "Add a Design Review Coordinator that turns a design review session into successive acyclic workflow runs until the Design Reviewer Council reaches quorum or requires manual resolution. A coordinator-created round must review exactly one immutable design revision, launch a DB-backed runtime workflow run using the published Design Reviewer Council workflow, collect lead/reviewer/synthesizer outputs, evaluate four-of-five or three-of-four quorum with zero blocking issues, create a development handoff when approved, create the next design revision when revision is required, and pause for manual resolution when policy conflicts or runtime evidence is incomplete. The workflow graph must remain acyclic; iteration happens by launching another round run."

## Clarifications

### Session 2026-05-08

- Q: How does iteration happen without cyclic graph execution? -> A: Each coordinator round launches one acyclic DB-backed runtime workflow run; revision loops launch another round run rather than adding graph cycles (autopilot).
- Q: Which quorum policies are supported in this spec? -> A: Support `four_of_five_no_blockers` and `three_of_four_no_blockers`; both require zero blocking issues and enough approved verdicts to pass (autopilot).
- Q: What happens when runtime evidence is incomplete or contradictory? -> A: The coordinator records a safe quorum decision with `manual_resolution`, pauses the session, and requires a durable manual decision before continuing (autopilot).
- Q: How are revisions created after a failed quorum? -> A: The coordinator creates a new immutable design revision with safe summary, digest, previous revision reference, and author role `coordinator` when a revision is required and max rounds have not been reached (autopilot).
- Q: How should local QA launch runtime runs? -> A: Use local-principal auth, deterministic or mocked model-backed workflow bundles, and DB-backed runtime records; no live provider, Auth0, Telegram, connector, credential, or external call is required (autopilot).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Launch A Review Round From A Session (Priority: P1)

A tenant admin starts coordinator execution for an existing design review
session. The coordinator selects exactly one active immutable design revision,
creates one review round, launches one DB-backed runtime workflow run using a
published Design Reviewer Council workflow bundle, records reviewer assignments,
and moves the session into reviewing state.

**Why this priority**: Without a safe launch path, the design review domain
cannot become an executable scenario.

**Independent Test**: Create a session with a published workflow bundle, launch
the coordinator, assert one round is created for the active revision, one
runtime workflow run is runnable, assignments match enabled reviewers, and
replaying the idempotency key does not duplicate the round or run.

**Acceptance Scenarios**:

1. **Given** a design review session with an active revision and a published council workflow, **When** the coordinator launch endpoint is called, **Then** the session status becomes `reviewing`, a round is created, and a DB-backed runtime run is runnable.
2. **Given** the same launch request and idempotency key, **When** the request is replayed, **Then** the existing round and workflow run are returned without duplicate assignments or runs.
3. **Given** a missing workflow bundle, cross-tenant session, terminal session, or missing active revision, **When** launch is requested, **Then** the coordinator fails closed with a safe error and no runtime run is created.

---

### User Story 2 - Evaluate Round Completion And Iterate (Priority: P2)

After a runtime round completes, the coordinator collects safe reviewer outputs,
records verdicts, evaluates quorum, and either creates a development handoff,
creates the next revision, or pauses for manual resolution.

**Why this priority**: The core council value is the round decision loop.

**Independent Test**: Complete rounds with approved quorum, revision-required
feedback, incomplete evidence, blocking issues, and max-round exhaustion, then
verify persisted verdicts, quorum decisions, session status, handoff or next
revision, and safe failure handling.

**Acceptance Scenarios**:

1. **Given** four of five or three of four enabled reviewers approve and report zero blockers, **When** the round is completed, **Then** quorum passes and a development handoff is created for the reviewed revision.
2. **Given** quorum does not pass but feedback is complete and max rounds remain, **When** the round is completed, **Then** a revision-required decision is recorded and the next immutable design revision is created.
3. **Given** runtime evidence is missing, contradictory, contains unsafe content, or max rounds are exhausted, **When** completion is evaluated, **Then** the session enters manual resolution with safe rationale.

---

### User Story 3 - Apply Durable Manual Decisions (Priority: P3)

An authorized tenant admin can resolve a paused design review session by
recording a durable manual decision to revise, approve by exception, retry, or
cancel. The coordinator applies the decision to session state without exposing
raw reviewer payloads.

**Why this priority**: Production review loops need a human escape path when
automated evidence is incomplete or policy conflicts occur.

**Independent Test**: Record each manual decision type against a paused session
and verify session status, handoff/revision side effects, idempotency, audit
safe rationale, and tenant isolation.

**Acceptance Scenarios**:

1. **Given** a manual-resolution session, **When** a revise decision is recorded, **Then** the coordinator creates a next revision and marks the session `revision_required`.
2. **Given** a manual-resolution session, **When** an approve-exception decision with accepted risk is recorded, **Then** the coordinator creates a development handoff and marks the session `approved`.
3. **Given** a manual-resolution session, **When** retry or cancel is recorded, **Then** the session moves to a retry-ready reviewing state or a terminal cancelled state respectively.

### Edge Cases

- A coordinator-created round must always reference exactly one design revision.
- A session must not have two active reviewing rounds for the same revision.
- The coordinator must fail closed when the workflow bundle belongs to another tenant or is missing executable graph metadata.
- Runtime run creation must be idempotent and tenant-scoped.
- Quorum evaluation must ignore disabled reviewers and must not pass when any blocking issue count is above zero.
- A passed quorum must create at most one handoff for the session.
- A revision-required decision must not mutate the previous revision.
- Manual decisions must be durable, idempotent, and audit-safe.
- Cross-tenant requests must return a denial without revealing whether the target session exists.
- No raw prompts, completions, model payloads, secrets, private messages, memory contents, or raw external tool payloads may appear in coordinator records, responses, logs, screenshots, or QA artifacts.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a coordinator service that launches review rounds for existing design review sessions.
- **FR-002**: A launched round MUST reference exactly one existing active design revision for the session.
- **FR-003**: A launched round MUST create one DB-backed `runtime_workflow_runs` record and one `runtime_execution_bundles` record using the selected published workflow bundle.
- **FR-004**: The coordinator MUST record enabled reviewer assignments for the round using safe reviewer keys, role keys, prompt/profile references, and provider references.
- **FR-005**: Round launch MUST be idempotent by tenant and idempotency key and MUST not duplicate runtime runs, rounds, assignments, or timeline evidence.
- **FR-006**: The coordinator MUST evaluate `four_of_five_no_blockers` and `three_of_four_no_blockers` quorum policies with zero blocking issues required for pass.
- **FR-007**: The coordinator MUST record safe reviewer verdicts with score, blocking issue count, safe feedback summary, digest, optional artifact reference, usage metadata, and idempotency.
- **FR-008**: The coordinator MUST create a quorum decision for each completed round with status, approval count, blocking issue count, next action, policy version, and safe rationale.
- **FR-009**: When quorum passes, the coordinator MUST create a development handoff for the reviewed revision and mark the session approved.
- **FR-010**: When quorum does not pass and another round is allowed, the coordinator MUST create the next immutable design revision and mark the session revision-required.
- **FR-011**: When evidence is incomplete, policy conflicts occur, unsafe content is detected, or max rounds are exhausted, the coordinator MUST pause the session for manual resolution.
- **FR-012**: Manual decisions MUST support revise, approve-exception, retry, and cancel actions and update session state through safe durable records.
- **FR-013**: Coordinator API responses MUST expose live persisted state only and must not invent sample rounds, verdicts, revisions, or handoffs.
- **FR-014**: Coordinator operations MUST enforce tenant isolation and platform-admin explicit tenant scope.
- **FR-015**: Coordinator operations MUST produce audit-safe and timeline-safe evidence without raw secrets, prompts, completions, provider payloads, memory contents, private channel messages, unauthorized payloads, or raw external tool payloads.
- **FR-016**: The implementation MUST provide unit, contract, integration, QA, Playwright, and curl regression evidence.

### Key Entities *(include if feature involves data)*

- **Design Review Coordinator State**: Safe projection of a session, active revision, latest round, latest quorum decision, manual decisions, and handoff state.
- **Coordinator Launch Request**: Tenant, session, workflow bundle, reviewer set, quorum policy, max rounds, execution mode, and idempotency key used to launch one round.
- **Review Round Runtime Run**: DB-backed runtime run and bundle created for one acyclic council workflow execution.
- **Reviewer Completion Evidence**: Safe reviewer verdicts and optional synthesizer summary used to evaluate a round.
- **Quorum Evaluation Result**: Derived approval count, blocking issue count, policy status, next action, and safe rationale.
- **Manual Resolution Action**: Durable human decision that revises, approves by exception, retries, or cancels the session.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Launching a valid session creates exactly one round and one DB-backed runtime run, and replaying the launch request returns the same records.
- **SC-002**: A passed four-of-five or three-of-four zero-blocker round creates one development handoff and marks the session approved.
- **SC-003**: A non-passing complete round creates a next immutable revision while max rounds remain and never mutates prior revisions.
- **SC-004**: Incomplete evidence, blocking policy conflicts, and max-round exhaustion produce manual-resolution state with safe rationale.
- **SC-005**: Manual revise, approve-exception, retry, and cancel actions are durable, idempotent, tenant-scoped, and audit-safe.
- **SC-006**: QA docs, Playwright smoke evidence, updated curl coverage, and full curl regression prove the coordinator APIs and runtime records are live-data backed.

## Assumptions

- Spec 060 design review domain tables and APIs are available.
- Spec 061 model-backed role execution is available but local QA can still use deterministic workflow graph nodes.
- Workflow graphs remain acyclic; coordinator iteration launches new runtime runs.
- Existing runtime worker and graph execution services remain authoritative for executing DB-backed runs.
- Existing design review tables can represent coordinator state; no new migration is planned unless implementation discovers a missing durable field.
- Local QA uses local-principal authentication and mocked provider/model paths only.

## Testing Instructions

- Add unit coverage for quorum policy evaluation, revision-required behavior, approval behavior, manual-resolution behavior, max-round limits, idempotency, and unsafe evidence handling.
- Add integration coverage that creates DB-backed runtime runs, executes deterministic and mocked model-backed rounds, and verifies design-review tables update correctly.
- Add contract coverage for coordinator launch, completion, manual decision, and state projection schemas.
- Add QA docs for `qa062.md`, `qa062_ui.md`, `.env.qa062`, `qa062_user_guide.md`, and reviewer notes.
- Update `curl_testing.md` for new coordinator JSON API routes and run the full multi-agent curl regression after spec validation.

## PR Review Guidance

- Confirm round launch creates exactly one acyclic runtime run per design revision.
- Confirm quorum policies require zero blockers and enough approvals.
- Confirm revision-required loops create new immutable revisions instead of mutating existing revisions.
- Confirm manual decisions are idempotent and update safe session state.
- Confirm all coordinator responses and artifacts remain redaction-safe.

## Documentation Impact

- Add Spec 062 plan, research, data model, contracts, quickstart, tasks, QA guide, UI walkthrough, manual QA user guide, and PR notes.
- Update `curl_testing.md` with coordinator API coverage.
- Update `AGENTS.md` Spec Kit plan pointer during planning through the normal plan flow.
