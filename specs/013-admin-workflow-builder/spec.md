# Feature Specification: Guided Admin Workflow Builder

**Feature Branch**: `013-admin-workflow-builder`  
**Created**: 2026-04-28  
**Status**: Draft  
**Input**: User description: "Upgrade the admin workflow studio into a guided workflow builder web UI. Platform and tenant admins must be able to define agent and sub-agent workflows through forms and graph-oriented views without editing raw JSON. The builder must support workflow metadata, roles, sub-agent roles, prompt/profile references, model routing preview links, skill installation references, contracts, nodes, edges, join policies, approval gates, reusable subworkflow references, validation findings, draft revisions, and publish actions. Publication must be blocked when required validation, prompt versions, provider routing, skill installations, or required test-suite results are missing or failing. The feature must extend the existing workflow registry storage and published bundle model rather than create a separate workflow store. Require server-rendered admin pages, small JS only where useful, tenant/platform authorization, audit records, at least 90 percent coverage, docs, PR notes, testing instructions, and README updates."

## Clarifications

### Session 2026-04-28

- Q: How should the builder handle concurrent saves to the same workflow draft? → A: Reject stale saves when the base draft revision changed; show a conflict/refresh path.
- Q: How should reusable subworkflow references resolve versions when a workflow is published? → A: Pin the exact published subworkflow bundle version selected during validation/publication.
- Q: What graph-cycle policy should validation enforce for workflow drafts? → A: Cycles are allowed only for explicit retry or approval-resume loops with configured bounds.
- Q: When a validated workflow draft is published, what should happen to the active published bundle? → A: Publication atomically creates the immutable bundle and makes it the active bundle for the selected scope.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create Workflow Drafts Without Raw JSON (Priority: P1)

A platform or tenant admin can create and revise an agent workflow through guided forms and graph-oriented views that cover metadata, roles, sub-agent roles, contracts, prompt/profile references, skill installation references, nodes, edges, join policies, approval gates, and reusable subworkflow references without editing raw JSON.

**Why this priority**: This is the core value of the builder. Admins need a safer authoring experience before validation, publication, and governance features can matter.

**Independent Test**: An authorized admin can create a new workflow draft with multiple roles, sub-agent roles, connected graph nodes, required contracts, and at least one approval gate, save it as a draft revision, then reload the draft and see the same authored structure without using a raw JSON editor.

**Acceptance Scenarios**:

1. **Given** an authorized platform admin, **When** they start a new workflow draft, **Then** the builder lets them define platform-scoped metadata, workflow roles, prompt/profile references, skill installation requirements, contracts, graph nodes, graph edges, join policies, approval gates, and reusable subworkflow references through guided controls.
2. **Given** an authorized tenant admin, **When** they create a tenant-scoped workflow draft, **Then** all selectable prompts, profiles, model routing previews, skills, reusable subworkflows, and publish destinations are limited to resources available to that tenant.
3. **Given** a workflow draft with incomplete but saveable data, **When** the admin saves progress, **Then** a new draft revision is recorded and the admin can continue editing from that revision.
4. **Given** an unauthorized admin or an admin outside the tenant scope, **When** they attempt to view or edit a workflow draft, **Then** access is denied and the attempt is recorded for review.

---

### User Story 2 - Validate Readiness Before Publication (Priority: P2)

An admin can run validation from the builder and see actionable findings that explain missing metadata, graph problems, prompt/profile issues, provider routing problems, missing skill installations, approval gate gaps, contract incompatibilities, reusable subworkflow problems, and required test-suite failures.

**Why this priority**: Guided authoring needs dependable feedback before publication. Admins should know what is wrong and how to fix it without inspecting bundle internals.

**Independent Test**: A draft with known missing prompt versions, an unreachable model route, a missing skill installation, an invalid join policy, and a failing required test suite produces blocking validation findings with clear locations and remediation guidance.

**Acceptance Scenarios**:

1. **Given** a workflow draft with unresolved required fields or disconnected graph nodes, **When** the admin runs validation, **Then** the builder displays blocking findings tied to the affected form section or graph element.
2. **Given** a workflow draft that references a missing, retired, or unauthorized prompt/profile version, **When** validation runs, **Then** the finding identifies the unavailable reference and blocks publication.
3. **Given** a workflow draft whose provider routing preview cannot resolve a usable route, **When** validation runs, **Then** the builder reports the routing issue and links the admin to the relevant routing preview.
4. **Given** a workflow draft with required test suites, **When** the latest required result is missing, failing, or stale, **Then** validation marks publication as blocked until the required result is available and passing.

---

### User Story 3 - Publish Versioned Workflow Bundles Safely (Priority: P3)

An authorized admin can publish a validated draft into the existing workflow registry and published bundle lineage, while blocked publication attempts clearly explain the reason and leave the previously published bundle unchanged.

**Why this priority**: Publication turns builder work into runtime-ready workflow definitions. It must be safe, auditable, and aligned with the existing registry model.

**Independent Test**: A valid draft publishes as an immutable workflow bundle in the existing registry lineage, while drafts with any blocking validation condition cannot publish and produce audit evidence without changing the active published bundle.

**Acceptance Scenarios**:

1. **Given** a workflow draft with passing required validation and test results, **When** an authorized admin confirms publication, **Then** the system atomically creates a new published bundle in the existing workflow lineage and makes that bundle active for the selected scope.
2. **Given** a workflow draft with any blocking finding, **When** an admin attempts to publish, **Then** publication is refused, the active published bundle remains unchanged, and the builder shows all blocking reasons.
3. **Given** a workflow draft that reuses a published subworkflow, **When** the admin publishes, **Then** the published bundle records the exact selected subworkflow bundle version and its validated contract compatibility.
4. **Given** a tenant admin without platform publishing rights, **When** they attempt to publish a platform-scoped workflow, **Then** publication is denied and recorded for audit review.

---

### User Story 4 - Review Revisions And Audit Trail (Priority: P4)

Platform and tenant admins can review draft revision history, validation history, publication attempts, and safe audit details so they can understand how a workflow changed and why a publication was accepted or blocked.

**Why this priority**: Workflow governance depends on traceability, especially when prompts, model routing, skills, and reusable subworkflows can change over time.

**Independent Test**: After multiple edits, validation runs, a blocked publication attempt, and a successful publication, an authorized admin can review revision history and audit records that identify actors, timestamps, scopes, changed sections, validation outcomes, and publication outcomes without exposing secrets or unsafe payloads.

**Acceptance Scenarios**:

1. **Given** a workflow with multiple draft revisions, **When** an authorized admin opens revision history, **Then** they can identify who changed the workflow, when it changed, which builder sections changed, and which revision is current.
2. **Given** a blocked publish attempt, **When** an authorized admin opens audit details, **Then** the record shows the actor, scope, draft revision, blocking findings, and outcome.
3. **Given** a previously published workflow, **When** an admin reviews lineage, **Then** they can trace the published bundle back to the source draft revision and validation evidence.

### Edge Cases

- Prompt or profile references that were valid when saved become retired, missing, or unauthorized before publication.
- Model routing previews become unavailable, unresolved, or fail policy checks after a draft revision is created.
- A skill installation exists at platform scope but is unavailable to the tenant that owns the draft.
- Graph nodes are disconnected, contain arbitrary cycles, contain retry or approval-resume loops without configured bounds, or are connected through incompatible contracts.
- Join policies reference missing inbound edges, conflicting completion rules, or unavailable upstream outputs.
- Approval gates omit required approver roles, tenant scope, resume behavior, or timeout expectations.
- Reusable subworkflow references are unpublished, retired, unauthorized, or contract-incompatible with the parent workflow.
- Required test-suite results are missing, stale relative to the current draft revision, or failing.
- Two admins edit the same draft concurrently; stale saves based on an older draft revision are rejected with a conflict/refresh path before any new revision is recorded.
- Existing workflow registry entries created before this builder need to remain viewable and publishable through the existing lineage model.
- A publish action fails after validation passes; the atomic create-and-activate operation leaves the previously active bundle unchanged.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The builder MUST allow platform admins and tenant admins to access only the workflow drafts, reusable subworkflows, prompts, profiles, model routing previews, skills, tests, and publish scopes they are authorized to use.
- **FR-002**: The builder MUST create and update workflow drafts as revisions in the existing workflow registry lineage rather than in a separate workflow store.
- **FR-003**: Admins MUST be able to define workflow metadata, including name, description, owner, scope, status, tags, publication intent, and reviewer notes.
- **FR-004**: Admins MUST be able to define workflow roles and sub-agent roles with purpose, responsibilities, allowed references, required handoff expectations, and relationship to graph nodes.
- **FR-005**: Admins MUST be able to select prompt and runtime profile references from eligible published or otherwise allowed versions, and the builder MUST identify whether each reference is publish-ready.
- **FR-006**: The builder MUST show model routing preview links or summaries for relevant prompt/profile or role decisions so admins can inspect expected provider routing before publication.
- **FR-007**: Admins MUST be able to add required skill installation references, including scope, version or compatibility expectation, credential requirement status, and policy notes visible to reviewers.
- **FR-008**: Admins MUST be able to define workflow contracts for inputs, outputs, artifacts, handoffs, memory expectations, tool access expectations, failure outcomes, and reusable subworkflow compatibility.
- **FR-009**: Admins MUST be able to build workflows through graph-oriented views and structured forms for nodes, edges, joins, approvals, and reusable subworkflow calls without editing raw JSON.
- **FR-010**: The builder MUST support node definitions for primary agents, sub-agents, approval gates, reusable subworkflow calls, skill-backed actions, validation checkpoints, and terminal outcomes.
- **FR-011**: The builder MUST support edge definitions for sequencing, branching, handoffs, approval resumes, failure paths, and contract-based transitions.
- **FR-012**: The builder MUST support join policies that define required inbound completions, failure handling, timeout expectations, and output merging expectations.
- **FR-013**: The builder MUST support approval gates with required approver role, scope, reason, resume behavior, and blocked-state visibility.
- **FR-014**: The builder MUST support reusable subworkflow references that identify the selected published subworkflow bundle version, permitted scope, and contract compatibility status.
- **FR-015**: The builder MUST display validation findings by severity, affected builder section, affected graph element when applicable, blocking status, and remediation guidance.
- **FR-016**: Validation MUST check draft completeness, graph integrity, cycle policy compliance, role coverage, prompt/profile readiness, model routing readiness, skill installation readiness, contract compatibility, approval gate completeness, reusable subworkflow compatibility, authorization, and required test-suite status.
- **FR-017**: Publication MUST be blocked when required validation has not passed for the current draft revision.
- **FR-018**: Publication MUST be blocked when any required prompt/profile version is missing, retired, unauthorized, unpinned where a pin is required, or otherwise not publish-ready.
- **FR-019**: Publication MUST be blocked when required provider routing cannot be previewed, is unavailable, violates policy, or has a failing required health state.
- **FR-020**: Publication MUST be blocked when a required skill installation is missing, unauthorized, incompatible, or lacks required credential readiness.
- **FR-021**: Publication MUST be blocked when any required test-suite result is missing, stale for the current draft revision, or failing.
- **FR-022**: Publication MUST be blocked when required contracts, nodes, edges, join policies, approval gates, or reusable subworkflow references are incomplete or incompatible.
- **FR-023**: Successful publication MUST atomically create an immutable published workflow bundle using the existing workflow registry and published bundle model, preserve lineage from the source draft revision, and make the new bundle active for the selected scope.
- **FR-024**: Failed or blocked publication attempts MUST leave the active published bundle unchanged and show actionable reasons to the admin.
- **FR-025**: The builder MUST retain draft revision history, validation history, publication history, and restore or copy actions where allowed by scope and authorization.
- **FR-026**: The builder MUST record audit events for draft creation, draft updates, validation requests, validation outcomes, publish attempts, blocked publish attempts, successful publications, authorization denials, and revision restore or copy actions.
- **FR-027**: Audit records MUST include actor, scope, tenant when applicable, workflow lineage, draft revision, affected sections, outcome, and safe summaries without exposing secrets or unsafe payloads.
- **FR-028**: Critical save, validation, and publish actions MUST work through server-generated admin pages, with client-side enhancements used only to improve graph editing, previews, or inline feedback.
- **FR-029**: Existing workflow registry entries and published bundles MUST remain accessible through current lineage and publication behavior after the builder is introduced.
- **FR-030**: Delivery MUST include user-facing documentation, README updates, reviewer testing instructions, PR notes, and automated test evidence showing at least 90 percent coverage for submitted code.
- **FR-031**: Draft save requests MUST include the base draft revision identifier; when the stored current revision differs, the save MUST be rejected without creating a new revision and the admin MUST be shown a conflict/refresh path.
- **FR-032**: Published workflow bundles that include reusable subworkflow calls MUST pin each call to the exact published subworkflow bundle version selected during validation and publication.
- **FR-033**: Workflow graph validation MUST block arbitrary cycles and allow cycles only when they are explicit retry or approval-resume loops with configured bounds.

### Key Entities

- **Workflow Lineage**: The long-lived identity for a workflow across drafts and published bundles, including scope and ownership.
- **Workflow Draft**: The editable working version of a workflow before publication.
- **Draft Revision**: A saved snapshot of a workflow draft that can be validated, reviewed, restored, copied, or published.
- **Workflow Metadata**: Name, description, owner, scope, status, tags, and publication notes.
- **Workflow Role**: A primary agent role or sub-agent role with purpose, responsibilities, allowed references, and graph participation.
- **Prompt/Profile Reference**: A selected prompt or runtime profile reference with version readiness and authorization status.
- **Model Routing Preview**: A read-only preview or link that shows expected model/provider routing and readiness for a selected reference.
- **Skill Installation Reference**: A required skill installation dependency with scope, compatibility, credential readiness, and policy status.
- **Workflow Contract**: The expected inputs, outputs, artifacts, handoffs, memory expectations, access expectations, and failure outcomes for a workflow or graph element.
- **Graph Node**: A workflow step such as an agent, sub-agent, approval gate, skill-backed action, reusable subworkflow call, validation checkpoint, or terminal outcome.
- **Graph Edge**: A transition between graph nodes with sequencing, branching, handoff, failure, approval resume, or contract expectations.
- **Join Policy**: Rules for combining inbound paths, required completions, timeout handling, failure behavior, and output expectations.
- **Approval Gate**: A human decision point with approver role, scope, reason, resume behavior, and blocked-state visibility.
- **Reusable Subworkflow Reference**: A reference to an exact published workflow bundle version that can be used as a node within another workflow.
- **Validation Finding**: A warning or blocking issue with severity, affected builder location, reason, remediation guidance, and resolution status.
- **Test Suite Result**: Evidence that required workflow tests are passing for the current draft revision.
- **Published Workflow Bundle**: The immutable workflow version made available for runtime use through the existing publication model.
- **Audit Record**: A safe record of authoring, validation, publication, or access activity.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: At least 90 percent of admins in acceptance testing can create and save a workflow draft with metadata, two agent roles, two sub-agent roles, six graph nodes, eight edges, one join policy, one approval gate, one reusable subworkflow reference, and required contracts in under 25 minutes without editing raw JSON.
- **SC-002**: 100 percent of publish attempts with unresolved blocking validation, missing prompt/profile readiness, failing provider routing readiness, missing skill installation readiness, or missing required test results are refused without changing the active published bundle.
- **SC-003**: At least 95 percent of valid publish attempts complete or show a clear retryable failure outcome within 2 minutes after admin confirmation.
- **SC-004**: At least 90 percent of admins in acceptance testing can identify the reason for a blocked publication and the next corrective action within 2 minutes of seeing the builder findings.
- **SC-005**: 100 percent of tested existing workflow registry entries remain viewable through their existing lineage and retain their published bundle history after the builder is introduced.
- **SC-006**: 100 percent of draft creation, draft update, validation, publish attempt, blocked publish, successful publish, authorization denial, and revision restore or copy actions create safe audit records.
- **SC-007**: Reviewer evidence includes passing required tests, at least 90 percent automated coverage for submitted code, README updates, user-facing documentation, PR notes, and testing instructions.

## Assumptions

- The existing workflow registry and published bundle model remain the source of truth for workflow drafts, revisions, publication lineage, and runtime-ready bundles.
- Existing admin identity, tenant scoping, and platform authorization rules remain authoritative for builder access and publish permissions.
- Existing prompt/profile, model routing, skill installation, and workflow test-suite systems remain authoritative; the builder references and validates their readiness rather than redefining them.
- Required workflow tests are the tests marked required by workflow policy, selected templates, or publication rules for the workflow scope.
- Validation can be run on demand while drafting and is always re-run or freshness-checked against the current draft revision before publication.
- Raw JSON import or export may remain available outside the primary guided admin workflow, but platform and tenant admins are not required to edit raw JSON to define or publish workflows.
- Desktop and tablet admin use are the primary targets for graph-oriented editing; smaller screens should remain usable for review and basic form actions.
