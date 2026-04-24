# Feature Specification: Durable Orchestration Runtime

**Feature Branch**: `004-durable-orchestration-runtime`  
**Created**: 2026-04-24  
**Status**: Draft  
**Input**: User description: "Add the durable orchestration runtime for the multi-agent AI platform. The runtime must execute published workflows with LangGraph, persist workflow state in PostgreSQL, route agent-to-agent handoffs through explicit contracts, support background workers, and survive worker or node failure by resuming from durable checkpoints. It must also support nested subworkflows, parent-child run lineage, pinned execution bundles, and pause-resume behavior for approval gates. Require at least 90 percent unit-test coverage, PR review notes, testing instructions, and a README update."

## Clarifications

### Session 2026-04-24

- Q: What should happen to active child runs when a parent workflow run is cancelled? → A: Workflow declares child cancellation policy; default is cascade-cancel.
- Q: What should happen when an agent-to-agent handoff fails contract validation? → A: Workflow declares failure route; default fails affected run path.
- Q: When should another worker be allowed to resume work after a worker claim is abandoned? → A: Workflow or tenant can configure claim expiry; default is 2 minutes.
- Q: How should paused approval gates behave if no approver responds? → A: Workflow declares approval timeout behavior; default is no automatic timeout.
- Q: How long should durable runtime records be retained? → A: Tenant-configurable retention; default 90 days for checkpoints and run payload references, retain audit and lineage indefinitely.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run Published Workflows Durably (Priority: P1)

Platform operators and product teams need published workflows to run reliably after they are started, even when the worker handling a run is interrupted or the process hosting it disappears.

**Why this priority**: Durable execution is the core runtime promise. Without it, users cannot trust long-running or multi-agent workflows in production.

**Independent Test**: Start a published workflow run, allow it to complete through multiple agent steps, interrupt execution after a checkpoint, restart processing, and verify the run resumes from the last durable state instead of restarting or losing progress.

**Acceptance Scenarios**:

1. **Given** a published workflow and a pinned execution bundle, **When** an authorized user starts a run, **Then** the runtime records the run, loads the pinned bundle, executes the workflow, and reports a terminal success or failure state.
2. **Given** a workflow run has completed at least one step and stored a checkpoint, **When** the active worker fails before completion, **Then** another worker can resume the run from the latest durable checkpoint without duplicating completed externally visible actions.
3. **Given** a workflow run reaches a terminal state, **When** users inspect the run, **Then** they can see status, start time, finish time, selected bundle, lineage, and step-level outcome history.

---

### User Story 2 - Enforce Agent Handoff Contracts (Priority: P2)

Workflow authors and reviewers need every agent-to-agent handoff to follow an explicit contract so downstream agents receive validated inputs and contract violations are visible before they corrupt a run.

**Why this priority**: Multi-agent reliability depends on predictable boundaries between agents. Contract enforcement prevents ambiguous handoffs from becoming hidden runtime failures.

**Independent Test**: Execute a workflow containing valid and invalid handoffs, then verify valid handoffs proceed and invalid handoffs follow the workflow's declared failure route, defaulting to failure of the affected run path with clear diagnostics.

**Acceptance Scenarios**:

1. **Given** a running workflow step produces an output for another agent, **When** the output satisfies the declared handoff contract, **Then** the receiving agent receives the validated payload with the expected context and lineage.
2. **Given** a running workflow step produces a payload that violates the declared handoff contract, **When** validation occurs, **Then** the runtime records the violation, prevents the invalid handoff from being consumed, and exposes actionable failure details.
3. **Given** a published workflow references a contract version, **When** a run starts, **Then** all handoffs in that run use the contract versions pinned for the selected execution bundle.

---

### User Story 3 - Pause And Resume Approval Gates (Priority: P3)

Operators and authorized approvers need workflows to pause at approval gates, preserve all run context, and continue only after an explicit approve, reject, or resume decision.

**Why this priority**: Approval gates are essential for controlled automation, but they must not break durability or require manual reconstruction of run state.

**Independent Test**: Run a workflow that pauses for approval, restart workers while paused, submit approval and rejection decisions, and verify the run resumes or terminates consistently from the preserved state.

**Acceptance Scenarios**:

1. **Given** a workflow reaches an approval gate, **When** the gate is entered, **Then** the runtime pauses the run, records required approval details, and prevents downstream steps from executing.
2. **Given** a run is paused at an approval gate, **When** an authorized approver approves it, **Then** the runtime resumes from the saved state and continues with the same pinned bundle and lineage context.
3. **Given** a run is paused at an approval gate, **When** an authorized approver rejects it, **Then** the runtime records the rejection, stops the affected path, and exposes the final decision in run history.

---

### User Story 4 - Trace Nested Subworkflows (Priority: P4)

Workflow authors, operators, and auditors need nested subworkflow runs to remain connected to their parent runs so complex orchestrations can be debugged, audited, and resumed safely.

**Why this priority**: Nested orchestration expands platform capability, and lineage prevents subworkflow work from becoming opaque or detached from the business process that started it.

**Independent Test**: Execute a workflow that starts nested subworkflows, inspect the run tree, fail and resume a child run, and verify parent and child statuses remain consistent.

**Acceptance Scenarios**:

1. **Given** a parent workflow starts a subworkflow, **When** the child run is created, **Then** it records parent run, parent step, selected bundle, tenant context, and inherited execution constraints.
2. **Given** a child run completes, fails, or pauses, **When** the parent run evaluates the child result, **Then** the parent receives a contract-compliant result and records the relationship in lineage.
3. **Given** a parent or child run is inspected, **When** lineage is requested, **Then** users can traverse from parent to children and from child to parent without ambiguity.

## Edge Cases *(mandatory)*

- A run is requested for a workflow that has not been published; the runtime rejects the request and records a clear reason without creating executable work.
- A pinned execution bundle is missing, retired, incompatible, or not authorized for the tenant; the run is not started and users receive a deterministic validation result.
- A worker fails after completing a step but before acknowledging completion; resumed processing must use idempotency safeguards so completed side effects are not repeated.
- A worker stops renewing its claim before completing work; another worker may resume the work after the workflow or tenant claim expiry, defaulting to 2 minutes.
- Multiple workers attempt to resume the same eligible run at the same time; only one worker owns the active attempt and others back off without corrupting state.
- A checkpoint is stale, incomplete, or inconsistent with the selected bundle; the run moves to a recoverable failure state with diagnostics instead of continuing unsafely.
- A handoff payload fails validation or references an unavailable contract version; the receiving agent must not consume the payload, and the runtime applies the workflow's declared handoff failure route, defaulting to failure of the affected run path.
- A subworkflow fails, pauses, or is cancelled while the parent run is waiting; the parent state must reflect the child outcome according to the declared parent-child contract.
- A parent run is cancelled while child runs are active; the runtime applies the workflow's declared child cancellation policy, defaulting to cascade-cancel when no policy is declared.
- A paused approval gate receives no decision before any declared timeout; the runtime applies the workflow's declared timeout behavior, defaulting to remaining paused until approval, rejection, or cancellation.
- A paused approval gate receives a duplicate, late, unauthorized, or conflicting decision; the runtime preserves the first valid decision and records rejected attempts.
- Tenant, auth, quota, or delegated credential context is missing, expired, or invalid during start, resume, handoff, or approval; the affected action is denied and audited.
- A workflow reaches a terminal state while retry or resume work is still queued; queued work must recognize the terminal state and stop without changing the result.
- A tenant has no explicit retention policy; checkpoints and run payload references use the 90-day default while audit events and lineage remain retained indefinitely.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow authorized users or services to start runs only for published workflows.
- **FR-002**: System MUST bind each run to a pinned execution bundle before execution begins and MUST use that bundle consistently for the life of the run.
- **FR-003**: System MUST execute the steps, branches, and agent transitions defined by the published workflow while preserving tenant, authorization, and execution context.
- **FR-004**: System MUST persist run state, step outcomes, checkpoints, pending work, and terminal results durably enough to resume after worker or node failure.
- **FR-005**: System MUST resume interrupted runs from the latest valid checkpoint without restarting completed workflow progress.
- **FR-006**: System MUST support background workers that claim, execute, retry, pause, resume, and complete workflow work without requiring a user request to stay open.
- **FR-007**: System MUST prevent concurrent workers from mutating the same active run attempt in conflicting ways.
- **FR-008**: System MUST make abandoned worker claims eligible for resume after the workflow or tenant claim expiry, defaulting to 2 minutes when no expiry is declared.
- **FR-009**: System MUST validate every agent-to-agent handoff against an explicit handoff contract before the receiving agent consumes it.
- **FR-010**: System MUST record handoff contract version, validation result, sender, receiver, payload identity, and failure details for each handoff.
- **FR-011**: System MUST apply the workflow's declared handoff failure route when validation fails, defaulting to failure of the affected run path.
- **FR-012**: System MUST support nested subworkflow execution where child runs inherit required context and remain linked to their parent run and parent step.
- **FR-013**: System MUST maintain parent-child run lineage that can be queried from either direction and includes run status, bundle identity, and relationship reason.
- **FR-014**: System MUST pause runs at approval gates, expose pending approval context to authorized approvers, and block downstream execution until a valid decision is recorded.
- **FR-015**: System MUST resume approved paused runs from their saved state and MUST terminate or route rejected paused runs according to the published workflow definition.
- **FR-016**: System MUST apply the workflow's declared approval timeout behavior for paused gates, defaulting to no automatic timeout when no behavior is declared.
- **FR-017**: System MUST preserve idempotency information for resumable work so repeated claims, retries, or resumes do not duplicate completed externally visible actions.
- **FR-018**: System MUST expose run status, checkpoint status, active step, pause reason, lineage, contract failures, retry history, and terminal outcome to authorized users and operators.
- **FR-019**: System MUST audit run start, claim, checkpoint, resume, handoff, subworkflow creation, approval decision, failure, cancellation, and terminal completion events.
- **FR-020**: System MUST enforce tenant isolation, authorization, quotas, and delegated credential constraints during run start, worker execution, handoff, subworkflow execution, and approval decisions.
- **FR-021**: System MUST support cancellation of active or paused runs and apply the workflow's declared child cancellation policy, defaulting to cascade-cancel for active child runs when no policy is declared.
- **FR-022**: System MUST surface recoverable and non-recoverable runtime failures with actionable reasons suitable for operators and PR reviewers.
- **FR-023**: System MUST include unit tests demonstrating at least 90 percent coverage for the runtime scope, plus tests for contract validation, checkpoint resume, worker failure, nested lineage, and approval pause-resume behavior.
- **FR-024**: System MUST include PR review notes, testing instructions, and README documentation that explain how to operate and validate the durable runtime.
- **FR-025**: System MUST support tenant-configurable retention for durable runtime records, defaulting to 90 days for checkpoints and run payload references while retaining audit events and lineage indefinitely.

### Key Entities *(include if feature involves data)*

- **Published Workflow**: An approved workflow definition available for execution; includes identity, version, expected inputs, handoff declarations, handoff failure routes, approval gates, approval timeout behavior, allowed subworkflows, and child cancellation policy.
- **Execution Bundle**: The pinned set of workflow, agent, prompt, model, tool policy, contract, and configuration versions used for a run.
- **Workflow Run**: A single execution of a published workflow; includes tenant context, initiating principal, status, selected bundle, timestamps, terminal result, and current checkpoint.
- **Run Step**: A unit of workflow progress within a run; includes step identity, agent or subworkflow target, status, attempts, inputs, outputs, errors, and checkpoint references.
- **Checkpoint**: Durable saved execution state that allows a run or step to resume after interruption without losing completed progress; follows tenant retention with a 90-day default.
- **Handoff Contract**: A versioned agreement describing the payload, context, and validation rules for one agent to pass work to another.
- **Handoff Event**: A recorded transfer attempt between agents; includes sender, receiver, contract version, validation outcome, and payload identity.
- **Worker Claim**: A time-bounded ownership record showing which background worker is responsible for a runnable unit of work; includes expiry policy, renewal status, and resume eligibility.
- **Approval Gate**: A paused workflow state requiring an authorized human decision; includes requested action, approver constraints, timeout behavior, decision, and decision history.
- **Run Lineage**: Parent-child relationships between workflow runs and subworkflow runs, including relationship reason, parent step, inherited context, and status propagation; retained indefinitely by default.
- **Side-effect Intent**: A durable record created before an externally visible action; includes tenant context, run step, operation kind, idempotency key, delegated credential reference, status, result reference, retry state, and optional compensation hook reference.
- **Retention Policy Metadata**: Tenant-specific or default retention settings for checkpoints, run payload references, audit events, lineage, and cleanup eligibility; defaults checkpoints and run payload references to 90 days while preserving audit events and lineage indefinitely.
- **Audit Event**: A durable record of important runtime decisions and state changes for review, compliance, and troubleshooting; retained indefinitely by default.

## Constitution Alignment *(mandatory)*

### Durability And Recovery Impact

- This feature directly changes workflow state, retries, idempotency, checkpoints, and resume behavior. Runs must survive worker and node failure by persisting resumable state, preventing unsafe duplicate work, and clearly separating recoverable failures from terminal outcomes.

### Tenant Isolation And Fair Use Impact

- Every run, worker claim, handoff, checkpoint, approval, and child run must carry tenant context. Quotas and fairness controls apply when starting runs, claiming work, creating subworkflows, and retrying failed work so one tenant cannot starve others.

### Contracts, Versioning, And Lineage Impact

- This feature introduces runtime enforcement for versioned handoff contracts, pinned execution bundles, and parent-child run lineage. Runs must retain the exact bundle and contract versions used so historical executions remain explainable after definitions change.

### Security, Secrets, And Tooling Impact

- Runtime actions must honor authentication, authorization, delegated credential linkage, tool allowlists, secret references, and outbound access constraints inherited from the published workflow and pinned bundle. Workers must never broaden privileges during resume or subworkflow execution.

### Artifact And Data Storage Impact

- Workflow run metadata, checkpoints, handoff events, approval decisions, lineage, worker claims, and audit events require durable storage and retention rules. Tenants can configure retention; when unset, checkpoints and run payload references are retained for 90 days while audit events and lineage are retained indefinitely. Large payloads may be referenced by identity when their full content is not required in run history, but run history must remain audit-ready.

### Approval, Resume, And Human Interaction Impact

- Approval gates, paused runs, manual decisions, cancellation, and resume actions are in scope. Users must have enough context to make decisions, and the runtime must resume exactly from the approved pause point.

### Observability And Audit Impact

- Operators need logs, metrics, traces, audit events, status views, retry history, checkpoint visibility, contract validation diagnostics, and lineage traversal for each run. Reviewers need evidence that failure recovery and pause-resume paths are observable and testable.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In validation testing, 100 percent of interrupted runs with a valid checkpoint resume from the latest checkpoint and reach the same final result as uninterrupted runs.
- **SC-002**: At least 99 percent of valid run-start requests for published workflows become visible with a durable initial state within 2 seconds under the Performance Validation Profile.
- **SC-003**: 100 percent of invalid handoff payloads in contract tests are blocked before receiver consumption and include an operator-readable validation reason.
- **SC-004**: 100 percent of approval-gated runs remain paused across worker restarts and resume or terminate according to the first valid approver decision.
- **SC-005**: 100 percent of nested subworkflow runs expose parent-child lineage from both parent and child inspection paths.
- **SC-006**: 100 percent of abandoned worker claims in recovery tests become eligible for another worker after their configured expiry, using a 2-minute default when unspecified.
- **SC-007**: Automated test reporting demonstrates at least 90 percent unit-test coverage for the runtime implementation scope.
- **SC-008**: README and PR review materials allow a new reviewer to run the runtime test suite and inspect failure-recovery evidence in 15 minutes or less.
- **SC-009**: 100 percent of retention-policy tests apply tenant-specific retention when configured and the 90-day checkpoint and run payload reference default when not configured, while preserving audit and lineage records.
- **SC-010**: Under the Performance Validation Profile, worker claim latency p95 remains below 200ms.
- **SC-011**: Under the Performance Validation Profile, run inspection latency p95 remains below 300ms for runs with 500 or fewer steps.
- **SC-012**: Under the Performance Validation Profile, handoff validation latency p95 remains below 100ms for normal payloads up to 256 KiB.

### Performance Validation Profile

Performance validation MUST use:

- 3 tenants with at least 25 active or paused runs per tenant.
- 10 concurrent valid run-start requests per tenant.
- Published workflows with 10-25 steps, including at least one handoff and one checkpoint.
- Handoff payloads up to 256 KiB inline or referenced by object-storage metadata.
- PostgreSQL test service configured through the project integration-test harness.

## Assumptions

- Primary users are platform operators, workflow authors, approvers, support engineers, and trusted service principals that start or monitor workflow runs.
- Only published workflows are executable; draft workflows remain out of scope for this runtime.
- The runtime relies on existing platform authentication, tenant, audit, and workflow registry concepts rather than introducing a separate identity model.
- Execution bundles are immutable once pinned to a run, and workflow definition changes affect only future runs.
- Approval decisions are made by authorized humans or approved service principals and are auditable.
- Failure recovery is bounded to deterministic replay from durable checkpoints; compensating external side effects beyond recorded idempotency safeguards are handled by workflow-specific policies.
- README updates cover operator setup, worker execution, failure-recovery testing, and approval pause-resume examples.

## Review And Delivery Guidance *(mandatory)*

### Testing Instructions

- Add unit tests for run creation, bundle pinning, worker claiming, checkpoint persistence, resume from checkpoint, duplicate worker claims, handoff contract validation, approval pause-resume, nested subworkflow lineage, cancellation, authorization denial, quota denial, and audit-event emission.
- Add failure-recovery tests that interrupt work after checkpoint creation and verify resumed runs do not repeat completed externally visible actions.
- Add contract tests proving invalid handoff payloads are blocked and valid payloads are delivered with preserved context.
- Add integration-style tests for background worker processing and paused approval gates using the project test harness.
- Report at least 90 percent unit-test coverage for the runtime scope and keep the project coverage gate at or above the existing threshold.

### PR Review Guidance

- Reviewers should focus on durability invariants, worker claim exclusivity, idempotency, checkpoint compatibility, lineage correctness, approval authorization, tenant isolation, and contract-version pinning.
- Reviewers should verify that every state transition is auditable and that failure paths produce actionable operator diagnostics.
- Reviewers should confirm that worker resume behavior cannot use stale credentials, cross tenant boundaries, or switch execution bundles after a run starts.
- PR notes must call out manual or automated evidence for checkpoint resume, background worker operation, nested subworkflow lineage, and approval pause-resume behavior.

### Documentation Impact

- Update `README.md` with how to start the runtime worker, execute a published workflow, inspect run status, test failure recovery, and exercise approval pause-resume behavior.
- Add or update operator-facing documentation for execution bundle pinning, worker claims, checkpoint recovery expectations, handoff contract failures, subworkflow lineage, and troubleshooting common paused or failed states.
