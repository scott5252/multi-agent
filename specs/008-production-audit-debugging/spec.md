# Feature Specification: Production Audit And Debugging

**Feature Branch**: `008-production-audit-debugging`  
**Created**: 2026-04-26  
**Status**: Draft  
**Input**: User description: "Add auditing and debugging capabilities for the multi-agent platform in production. The system must capture workflow timelines, agent handoffs, contract-validation results, memory writes, tool usage, model selection, and operator-visible trace data. Admin users must be able to inspect run timelines and debug failed executions without direct database access. Include version-bundle visibility, parent-child run lineage, notification delivery state, and secret-access audit metadata. Require at least 90 percent unit-test coverage, PR review notes, testing instructions, and a README update."

## Clarifications

### Session 2026-04-26

- Q: How should the platform behave when audit or trace capture fails during run execution? → A: Fail closed for security/governance audit events; allow non-security trace gaps with an explicit unavailable marker.
- Q: What production inspection surface should this feature deliver first? → A: Admin FastAPI endpoints returning structured timeline, trace, lineage, export, and delivery-state JSON.
- Q: What response-time target should the inspection API meet for run lookup and filtered search? → A: Direct run lookup returns in p95 <= 2 seconds; filtered searches return in p95 <= 5 seconds.
- Q: How should audit and trace records handle later corrections, redactions, or supersession? → A: Audit and trace records are append-only; corrections, redactions, and supersession are recorded as later events.
- Q: Which roles may export or share debug evidence? → A: Administrators and auditors may export or share debug evidence within their tenant scope.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Inspect Run Timelines (Priority: P1)

As an administrator or production operator, I need to inspect a workflow run timeline from acceptance through completion or failure so that I can understand what happened without direct database access.

**Why this priority**: Timeline visibility is the core production debugging path. Without it, operators cannot safely diagnose failures, customer escalations, or delayed runs.

**Independent Test**: Can be fully tested by creating successful and failed workflow runs, opening each run in the administrative inspection surface, and confirming that the visible timeline explains the run sequence, current state, and failure point without requiring database access.

**Acceptance Scenarios**:

1. **Given** a workflow run has started, **When** an authorized administrator opens the run timeline, **Then** they can see the run acceptance, queued, started, waiting, resumed, completed, cancelled, or failed states in chronological order.
2. **Given** a run fails during execution, **When** an operator inspects the timeline, **Then** the failure event identifies the failed stage, safe failure reason, responsible actor or system component when known, and next recommended investigation action.
3. **Given** a run includes nested or child executions, **When** an administrator views the run, **Then** the timeline shows parent-child lineage and allows navigation between related runs within the administrator's authorization scope.
4. **Given** an unauthorized user requests a timeline, **When** access is evaluated, **Then** protected timeline details are not disclosed and the denied access attempt is auditable.
5. **Given** an authorized administrator needs production inspection data, **When** they call the admin inspection API, **Then** the response returns structured JSON for the run timeline, trace records, lineage, exports, and delivery state without requiring database access.

---

### User Story 2 - Debug Runtime Decisions And Handoffs (Priority: P2)

As a workflow maintainer or operator, I need to review agent handoffs, contract-validation results, tool usage, model selection, and memory writes so that I can determine why a run behaved the way it did.

**Why this priority**: Production failures often happen at runtime decision boundaries. Operators need structured evidence for handoffs, validations, memory changes, tools, and models before they can resolve the issue or file an actionable defect.

**Independent Test**: Can be fully tested by running a workflow that includes agent handoffs, validation pass and fail outcomes, memory writes, tool calls, and model-backed steps, then confirming each decision is visible with safe details and linked to the relevant timeline event.

**Acceptance Scenarios**:

1. **Given** one agent hands work to another, **When** an operator inspects the run, **Then** they can see the handoff source, destination, reason, correlation details, outcome, and any safe summarized payload metadata.
2. **Given** a contract validation passes or fails, **When** an administrator reviews the timeline, **Then** they can see the contract name, validation outcome, safe error summary for failures, and the related workflow step.
3. **Given** a tool is used during a run, **When** the run is inspected, **Then** the tool event shows the tool identity, action category, outcome, duration, policy result, and safe input and output summaries.
4. **Given** a model-backed decision occurs, **When** the decision is reviewed, **Then** the visible record identifies the selected model, selection source, prompt or configuration version reference, outcome, and safe trace metadata.
5. **Given** a memory write occurs, **When** an operator inspects the run, **Then** they can see the memory scope, write intent, version or projection reference, outcome, and safe summary without exposing unauthorized memory content.

---

### User Story 3 - Audit Governance And Delivery State (Priority: P3)

As an auditor, administrator, or maintainer, I need version-bundle visibility, notification delivery state, and secret-access audit metadata so that production behavior is reviewable for governance, compliance, and incident response.

**Why this priority**: Governance evidence is required to explain which published bundle and sensitive-access decisions governed a run, and whether downstream notifications reached their intended destinations.

**Independent Test**: Can be fully tested by publishing or selecting a version bundle, executing a workflow that sends notifications and attempts secret-backed tool use, and confirming authorized reviewers can inspect bundle identity, delivery attempts, and secret-access metadata without seeing secret values.

**Acceptance Scenarios**:

1. **Given** a run executes under a published workflow or execution bundle, **When** an authorized reviewer inspects the run, **Then** they can see the bundle identity, version, activation state at run acceptance, and related configuration references.
2. **Given** notifications are sent or attempted for a run, **When** an administrator reviews delivery state, **Then** they can see destination category, delivery status, attempt count, latest attempt time, safe failure reason, and correlation to the triggering run event.
3. **Given** a runtime action requests a secret or credential reference, **When** an auditor reviews the event, **Then** they can see who or what requested access, the secret reference metadata, policy outcome, time, run context, and reason without exposing raw secret values.
4. **Given** audit data is exported or shared for review by an administrator or auditor within their tenant scope, **When** the export is generated, **Then** sensitive fields are redacted according to the viewer's authorization while retaining enough metadata to support investigation.

---

### User Story 4 - Review Delivery Evidence (Priority: P4)

As a maintainer reviewing the feature, I need coverage evidence, PR review notes, testing instructions, and README guidance so that I can verify the delivery and operate the feature after merge.

**Why this priority**: Review and operational documentation ensure the feature is maintainable and verifiable, but they depend on the core audit and debugging behavior being defined first.

**Independent Test**: Can be fully tested by reviewing the submitted delivery package and confirming that coverage, PR notes, testing instructions, and README content cover the required audit and debugging capabilities.

**Acceptance Scenarios**:

1. **Given** the feature is submitted for review, **When** maintainers inspect the delivery materials, **Then** unit-test coverage evidence demonstrates at least 90 percent coverage for the submitted behavior.
2. **Given** the feature is submitted for review, **When** maintainers read the PR review notes, **Then** the notes call out timeline completeness, sensitive-data handling, authorization, retention assumptions, and known operational risks.
3. **Given** reviewers follow the testing instructions, **When** they exercise the feature, **Then** they can verify run timelines, handoffs, validation outcomes, memory writes, tool usage, model selection, notification delivery, lineage, version bundles, and secret-access audit metadata.
4. **Given** an administrator reads the README update, **When** they need to debug a production run, **Then** the guidance explains where to find run timelines, how to interpret trace fields, and how to escalate unresolved failures.

### Edge Cases

- A run fails before a workflow step starts; the timeline still records acceptance, failure state, safe failure reason, and available correlation identifiers.
- A run is cancelled, times out, waits for approval, resumes after interruption, or is retried; the timeline preserves each state transition in order.
- A child run outlives its parent run or a parent fails while children are still active; lineage remains visible and each run retains its own status.
- A handoff or tool event emits malformed, oversized, or sensitive payload details; the visible trace uses safe summaries and stores only permitted metadata.
- Contract validation fails with multiple errors; the inspection surface shows a prioritized safe summary and preserves the full authorized error detail where permitted.
- A memory write is rejected, superseded, archived, or linked to a prior version; the audit record distinguishes requested, accepted, rejected, and effective memory states.
- A trace or audit record needs correction, redaction, or supersession after capture; the original record remains append-only and the later correction, redaction, or supersession event is linked to it.
- A model selection decision cannot resolve a valid model or configuration reference; the run failure identifies the missing or invalid selection category without exposing protected prompt or secret content.
- Notification delivery is delayed, retried, partially delivered, permanently failed, or suppressed by policy; the delivery state remains attached to the triggering event.
- A secret access request is denied, uses a rotated reference, or is made by an unauthorized actor; the audit record captures reference metadata and denial reason without secret values.
- Security or governance audit capture fails during execution; the platform fails closed for the affected run or access decision, while non-security trace capture gaps remain visible as unavailable trace data.
- An administrator searches for a run outside their tenant or role scope; the system fails closed and audits the denied inspection attempt.
- Audit records are generated at high volume; direct run lookup still returns in p95 <= 2 seconds and filtered searches still return in p95 <= 5 seconds during acceptance testing.
- Delivery materials omit coverage evidence, PR review notes, testing instructions, or README guidance; the feature is not considered review-ready.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The platform MUST provide administrator FastAPI inspection endpoints that return structured JSON for authorized users to review production workflow runs without direct database access.
- **FR-002**: The inspection experience MUST show a chronological workflow timeline that includes run acceptance, queueing, start, wait, resume, completion, cancellation, failure, retry, and timeout events when those events occur.
- **FR-003**: Timeline events MUST include event time, event category, run status after the event, actor or system origin when known, correlation identifiers, and safe summary details.
- **FR-004**: Failed run inspection MUST identify the failed stage, safe failure reason, related event, and recommended next investigation category when enough information is available.
- **FR-005**: The platform MUST record and preserve authorized lineage visibility between top-level runs, child runs, retries, resumptions, and delegated executions, including parent and child navigation where those relationships exist.
- **FR-006**: The platform MUST record agent handoffs, including source agent, destination agent, handoff reason, correlation details, outcome, time, and safe payload metadata.
- **FR-007**: The platform MUST record contract-validation results, including contract identity, related workflow step, validation outcome, safe error summary, and time.
- **FR-008**: The platform MUST record memory write attempts and outcomes, including memory scope, write intent, version or projection reference when applicable, outcome, time, and safe summary.
- **FR-009**: The platform MUST record tool usage, including tool identity, action category, policy outcome, execution outcome, duration, related run step, and safe input and output summaries.
- **FR-010**: The platform MUST record model selection decisions, including selected model identity, selection source, related version references, related workflow step or agent, outcome, and safe trace metadata.
- **FR-011**: The platform MUST expose operator-visible trace data that links workflow timeline events to handoffs, validations, memory writes, tool uses, model selections, notifications, and secret-access decisions.
- **FR-012**: The platform MUST show the published version bundle or execution bundle that governed a run, including bundle identity, version, activation state at run acceptance, and related configuration references.
- **FR-013**: Lineage inspection MUST represent unauthorized related runs as redacted boundary nodes without disclosing protected tenant, workflow, or run details.
- **FR-014**: The platform MUST record notification delivery state for run-related notifications, including destination category, delivery status, attempt count, latest attempt time, safe failure reason, and triggering event.
- **FR-015**: The platform MUST record secret-access audit metadata for secret or credential reference requests, including requester, reference metadata, policy outcome, time, run context, and reason without exposing raw secret values.
- **FR-016**: The platform MUST prevent raw secret values, credential values, unauthorized prompt content, and unauthorized memory content from appearing in visible timelines, traces, exports, logs, or review notes.
- **FR-017**: The platform MUST enforce existing tenant and role authorization for viewing run timelines, trace data, lineage, version bundles, notifications, memory metadata, tool metadata, model decisions, and secret-access audit metadata.
- **FR-018**: The platform MUST audit denied attempts to inspect protected run, trace, lineage, notification, memory, tool, model, or secret-access information.
- **FR-019**: The platform MUST support filtering or search by run identity, workflow identity, status, failure category, time range, agent, tool, model selection source, notification status, and lineage relationship.
- **FR-020**: The platform MUST allow administrators and auditors to export or share run-debug evidence within their tenant scope with sensitive values redacted according to the recipient's authorization.
- **FR-021**: Audit and trace records MUST be durable enough for production incident review and MUST remain associated with the relevant run even after completion, failure, cancellation, retry, or retention transition.
- **FR-021a**: Audit and trace records MUST be append-only; corrections, redactions, and supersession MUST be recorded as later linked events rather than in-place mutation.
- **FR-022**: Audit and trace records MUST clearly distinguish requested, allowed, denied, succeeded, failed, retried, suppressed, redacted, and unavailable outcomes.
- **FR-023**: The platform MUST provide clear empty, partial, and unavailable states when some trace data cannot be collected or shown because of timing, retention, authorization, or redaction.
- **FR-023a**: The platform MUST fail closed when security or governance audit events cannot be durably recorded, and MAY allow non-security trace capture gaps only when the timeline marks the related trace data as unavailable.
- **FR-024**: The delivered feature MUST include unit-test evidence showing at least 90 percent coverage for submitted audit capture, timeline inspection, authorization, redaction, lineage, notification state, and secret-access audit behavior.
- **FR-025**: The delivered feature MUST include PR review notes covering timeline completeness, runtime decision capture, lineage, version-bundle visibility, notification state, secret handling, authorization, redaction, retention, operational risk, and known limitations.
- **FR-026**: The delivered feature MUST include testing instructions that let reviewers verify successful runs, failed runs, handoffs, contract-validation results, memory writes, tool usage, model selection, version-bundle visibility, parent-child lineage, notification delivery state, secret-access audit metadata, authorization failures, redaction, exports, and README guidance.
- **FR-027**: The delivered feature MUST update the README with administrator-facing guidance for inspecting run timelines, interpreting trace records, debugging failures, viewing lineage, reviewing version bundles, checking notification delivery, and understanding secret-access audit metadata.

### Key Entities

- **Run Timeline**: The ordered production history of a workflow run, including lifecycle transitions, runtime decisions, failures, waits, resumptions, retries, and completion.
- **Timeline Event**: A timestamped event within a run timeline with category, status, origin, correlation identifiers, and safe details.
- **Runtime Trace Record**: Operator-visible evidence attached to a timeline event that explains a handoff, validation, memory write, tool use, model selection, notification, or secret-access decision.
- **Agent Handoff Record**: A trace record showing work passed from one agent to another, including source, destination, reason, outcome, and safe metadata.
- **Contract Validation Record**: A trace record showing whether an expected contract or boundary condition passed or failed for a workflow step.
- **Memory Write Audit Record**: A trace record showing requested and effective memory changes, relevant version references, and safe summaries.
- **Tool Usage Record**: A trace record showing tool identity, action category, policy and execution outcomes, duration, and safe input and output summaries.
- **Model Selection Record**: A trace record showing which model was selected, why it was selected, and which configuration or version references governed the decision.
- **Version Bundle Reference**: A visible reference to the published workflow or execution bundle that governed a run at acceptance.
- **Run Lineage Link**: A relationship between parent runs, child runs, retries, resumptions, or delegated executions.
- **Notification Delivery Record**: A trace record showing notification destination category, delivery status, attempts, latest attempt time, and safe failure reason.
- **Secret Access Audit Record**: A trace record showing secret or credential reference access metadata, requester, policy outcome, reason, and run context without secret values.
- **Debug Evidence Export**: A redacted, authorization-aware package of run timeline and trace information intended for review, support, or incident response.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Authorized administrators can locate and open a production run timeline by run identity with direct lookup returning in p95 <= 2 seconds during acceptance testing.
- **SC-001a**: Authorized administrators can filter run-debug evidence by supported criteria with filtered searches returning in p95 <= 5 seconds during acceptance testing.
- **SC-002**: 100 percent of inspected completed, failed, cancelled, waiting, resumed, retried, and timed-out runs show a chronological timeline with lifecycle state transitions.
- **SC-003**: 100 percent of failed runs in acceptance testing identify a safe failure reason, failed stage, and related timeline event.
- **SC-004**: 100 percent of runs that include agent handoffs, contract validations, memory writes, tool usage, model selection, notifications, or secret-access decisions show those records linked to timeline events.
- **SC-005**: 100 percent of runs with parent-child relationships expose authorized lineage navigation and prevent unauthorized lineage disclosure.
- **SC-006**: 100 percent of notification attempts in acceptance testing show delivery status, attempt count, latest attempt time, and safe failure reason when failed.
- **SC-007**: 100 percent of secret-access audit events in acceptance testing expose reference metadata and policy outcome while revealing zero raw secret or credential values.
- **SC-008**: At least 90 percent of administrators and maintainers in acceptance testing can debug a representative failed run without database access or additional verbal guidance.
- **SC-009**: Submitted audit and debugging behavior demonstrates at least 90 percent unit-test coverage.
- **SC-010**: PR review notes, testing instructions, and README guidance are present and sufficient for a maintainer to verify and operate the feature without additional explanation.

## Testing, Review, And Documentation Impact

- **Testing Instructions**: Reviewer instructions must cover successful and failed run timelines, lifecycle states, handoffs, contract-validation pass and fail outcomes, memory write accepted and rejected outcomes, tool allow and deny outcomes, model selection visibility, version-bundle visibility, parent-child lineage, notification delivery states, secret-access allow and deny metadata, authorization failures, redaction, exports, and README guidance.
- **PR Review Guidance**: PR notes must call out timeline completeness, runtime trace coverage, failure-debugging workflow, authorization boundaries, sensitive-data redaction, version-bundle visibility, run lineage, notification delivery evidence, secret-access audit metadata, retention assumptions, and known operational risks.
- **Documentation Impact**: The feature requires README updates for administrators and operators covering how to find a run, read timeline and trace fields, follow lineage, inspect failed executions, check version-bundle references, understand notification delivery state, review secret-access metadata safely, and escalate unresolved issues.

## Constitution Impact

- **Durability**: Timeline, trace, lineage, notification, version-bundle, and secret-access audit records must be durable before operators rely on them for production investigation.
- **Tenant Isolation And Fairness**: All inspection, search, export, lineage navigation, and audit views must enforce tenant and role boundaries and fail closed for unauthorized users.
- **Versioning**: Run inspection must expose the execution or version bundle that governed the run and must preserve historical references needed for incident analysis.
- **Secrets And Tool Access**: Secret and credential values must never appear in visible traces, exports, logs, audit records, or documentation; only safe reference metadata and policy outcomes are visible.
- **Artifact Storage**: Debug evidence exports must follow existing artifact access, retention, and redaction rules.
- **Approval And Resume**: Waiting, approval, resume, retry, and cancellation states must remain visible in the timeline so interrupted executions can be investigated.
- **Observability**: The feature must produce operator-visible timelines and trace records sufficient to explain lifecycle state, runtime decisions, policy denials, failures, and delivery outcomes.
- **Security**: Access to timelines, traces, lineage, notification state, version bundles, memory metadata, tool metadata, model decisions, and secret-access metadata must be authorized and audited.

## Assumptions

- Existing platform roles can distinguish administrators, operators, auditors, maintainers, workflow owners, and unauthorized users.
- Existing tenant boundaries apply to all run inspection, search, export, trace, lineage, notification, memory, tool, model, and secret-access audit views.
- Raw secret values, credential values, unauthorized prompt content, and unauthorized memory content are out of scope for inspection and must remain redacted.
- Existing workflow execution behavior already produces or can be associated with run identities, workflow identities, agent identities, step identities, tool identities, model references, notification attempts, and secret references.
- Retention policy details are governed by existing platform retention rules; this feature requires records to remain available for production incident review within those rules.
- This feature defines production audit and debugging behavior, administrator inspection, delivery evidence, and documentation expectations; detailed storage, rendering, and interface implementation choices are deferred to planning.
