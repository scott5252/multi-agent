# Feature Specification: Immutable Versioned Memory

**Feature Branch**: `005-immutable-memory`  
**Created**: 2026-04-24  
**Status**: Draft  
**Input**: User description: "Add immutable, versioned memory to the multi-agent platform. Agent memory must never be updated in place. Every change must create a new version with lineage to the prior version, and the system must support replay, diffing, audit, and current-head retrieval for workflow execution. Require at least 90 percent unit-test coverage, PR review notes, testing instructions, and a README update."

## Clarifications

### Session 2026-04-24

- Q: What canonical identity should define a `Memory Scope` for current-head uniqueness and lineage? → A: Tenant + workflow lineage + agent + memory key; memory is shared across runs of the same workflow lineage.
- Q: How should a `Memory Change Request` become an accepted `Memory Version`? → A: Authorized write creates a new version immediately; no separate memory approval state.
- Q: What should be the canonical content format for each `Memory Version`? → A: Canonical JSON snapshot per version, with explicit representation for nulls and removals.
- Q: What concurrency precondition should memory writes require? → A: Non-initial writes must include the expected current version id; initial writes must assert no current head.
- Q: How should sensitive memory content be handled in audit entries and audit views? → A: Audit entries store metadata, content hashes, and redacted change summaries only; raw content stays in memory/replay/diff views.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Preserve Every Memory Change (Priority: P1)

As a workflow operator or reviewer, I need every agent memory change to be preserved as a distinct version so that no prior memory state can be overwritten or lost.

**Why this priority**: Immutability is the core value of the feature and the foundation for replay, audit, and trustworthy workflow execution.

**Independent Test**: Can be fully tested by creating an initial memory entry, submitting multiple changes, and confirming that each change creates a new version while all prior versions remain retrievable and unchanged.

**Acceptance Scenarios**:

1. **Given** an agent memory has no versions, **When** a memory value is saved, **Then** the system creates the first version with no prior-version lineage.
2. **Given** an agent memory already has a current version, **When** a user or workflow submits a change, **Then** the system creates a new version linked to the prior current version.
3. **Given** an existing memory version, **When** a later change is made, **Then** the earlier version remains readable with its original content, metadata, and lineage.

---

### User Story 2 - Retrieve Current Memory for Execution (Priority: P2)

As a workflow execution process, I need to retrieve the current head version of relevant agent memory so that workflow decisions use the latest authorized memory state.

**Why this priority**: Workflow execution needs a single reliable current memory view while still preserving full history.

**Independent Test**: Can be fully tested by creating several memory versions for the same scope and confirming that workflow execution receives the current authorized head and its version identifier.

**Acceptance Scenarios**:

1. **Given** multiple versions exist for a memory scope, **When** workflow execution requests current memory, **Then** the system returns the current head version and its lineage identifier.
2. **Given** no memory exists for a requested scope, **When** workflow execution requests current memory, **Then** the system returns an explicit empty-memory result without fabricating a version.
3. **Given** a write is attempted from a stale current-head reference, **When** the system evaluates the change, **Then** it prevents silent replacement of the current head and requires the caller to retry from the latest head.

---

### User Story 3 - Replay and Compare Memory History (Priority: P3)

As an investigator or workflow reviewer, I need to replay memory across versions and compare two versions so that I can understand what changed and why a workflow behaved a certain way.

**Why this priority**: Replay and diffing provide explainability after the immutable history is captured and current execution can consume it.

**Independent Test**: Can be fully tested by creating a known sequence of memory changes, replaying the sequence to a selected version, and requesting a diff between two selected versions.

**Acceptance Scenarios**:

1. **Given** a sequence of memory versions, **When** a reviewer replays memory to a selected version, **Then** the reconstructed memory state matches the content recorded for that version and its ancestors.
2. **Given** two memory versions in the same lineage, **When** a reviewer requests a diff, **Then** the system identifies added, removed, and changed memory content between those versions.
3. **Given** two memory versions from incompatible scopes or unrelated lineages, **When** a reviewer requests a diff, **Then** the system explains that the comparison is invalid.

---

### User Story 4 - Audit and Review Delivery (Priority: P4)

As a platform maintainer, I need memory changes and delivery artifacts to be reviewable so that releases can demonstrate coverage, auditability, and operational readiness.

**Why this priority**: Review evidence and documentation are required for maintainability, but they depend on the core memory behavior being defined first.

**Independent Test**: Can be fully tested by reviewing the generated memory audit history, test report, PR review notes, testing instructions, and README update for the delivered feature.

**Acceptance Scenarios**:

1. **Given** a memory version has been created, **When** an auditor inspects its history, **Then** the audit record identifies the memory scope, version lineage, actor or workflow source, timestamp, reason, and change summary.
2. **Given** the feature is submitted for review, **When** a maintainer evaluates the PR materials, **Then** they can find review notes, testing instructions, and README guidance covering immutable memory behavior.
3. **Given** automated checks have run for the feature, **When** a maintainer reviews coverage evidence, **Then** unit-test coverage is at least 90 percent for the submitted code.

### Edge Cases

- First memory version has no predecessor but still has a stable lineage identifier and audit record.
- A requested current head may not exist for a new agent, workflow, or memory scope.
- A proposed non-initial change may reference a stale expected current version after another change already advanced the memory.
- An initial write may race with another initial write for the same memory scope; only one may succeed because each initial write must assert no current head exists.
- Replay may target a missing, deleted, unauthorized, or unrelated version identifier.
- Diff requests may compare identical versions, adjacent versions, distant versions, or versions from unrelated lineages.
- Memory content is stored as canonical JSON snapshots, including explicit representation for nulls and removals so replay and diffing distinguish empty values from removed fields.
- Audit viewers may have permission to see metadata, content hashes, and redacted change summaries but not raw sensitive memory content.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST represent every saved agent memory state as an immutable version.
- **FR-002**: System MUST prevent in-place updates to existing memory versions, including content, lineage, creator metadata, timestamps, and audit metadata.
- **FR-003**: System MUST create a new version immediately for every authorized memory write, with no separate pending approval state for memory changes.
- **FR-004**: System MUST link each non-initial version to the immediately prior version in its lineage.
- **FR-005**: System MUST identify one current head version for each memory scope, uniquely defined by tenant, workflow lineage, agent, and memory key.
- **FR-006**: Workflow execution MUST be able to retrieve the current memory head and its version identifier for a requested memory scope.
- **FR-007**: System MUST return an explicit no-memory result when current-head retrieval is requested for a scope with no versions.
- **FR-008**: System MUST require every non-initial memory write to include the expected current version identifier and reject the write when that identifier no longer matches the current head.
- **FR-009**: System MUST require every initial memory write to assert that no current head exists for the memory scope and reject the write if a head already exists.
- **FR-010**: Each memory version MUST store memory content as a canonical JSON snapshot with explicit representation for null values and removals.
- **FR-011**: System MUST support replay of memory state to any authorized version in a lineage from the version's canonical JSON snapshot and lineage metadata.
- **FR-012**: System MUST support diffing between two authorized versions in the same compatible memory scope.
- **FR-013**: Diffs MUST identify additions, removals, and changed values in a way reviewers can understand.
- **FR-014**: System MUST record an audit entry for every memory version creation and every replay, diff, or current-head retrieval action.
- **FR-015**: Audit entries MUST include actor or workflow source, memory scope, version identifiers involved, timestamp, action type, outcome, content hashes when content changes, and redacted change summaries when summaries are available.
- **FR-016**: Audit entries and audit views MUST NOT store or display raw memory content; raw content remains available only through authorized memory, replay, and diff access paths.
- **FR-017**: System MUST enforce existing access controls so that memory content, diffs, replayed states, and audit details are visible only to authorized users or workflows.
- **FR-018**: System MUST expose enough metadata for reviewers to trace a version from the current head back through its prior versions.
- **FR-019**: The delivered feature MUST include unit-test evidence showing at least 90 percent coverage for the submitted memory behavior.
- **FR-020**: The delivered feature MUST include PR review notes that summarize immutability guarantees, lineage behavior, replay and diff behavior, audit coverage, and known risks.
- **FR-021**: The delivered feature MUST include testing instructions that allow reviewers to verify version creation, current-head retrieval, stale-head handling, replay, diffing, audit, and access behavior.
- **FR-022**: The delivered feature MUST update the README with user-facing guidance for immutable memory concepts, expected behavior, and verification steps.

### Key Entities

- **Memory Scope**: The canonical boundary that determines memory ownership and current-head uniqueness, defined by tenant, workflow lineage, agent, and memory key so memory is shared across runs of the same workflow lineage.
- **Memory Version**: An immutable canonical JSON snapshot of memory content plus metadata, linked to a lineage and optionally to a prior version.
- **Memory Lineage**: The ordered chain of versions for a memory scope, including the current head.
- **Current Head**: The latest authorized version in a memory lineage used for workflow execution.
- **Memory Change Request**: An authorized write request that proposes new memory content and immediately creates a new memory version when access and concurrency checks pass; non-initial requests include the expected current version id, and initial requests assert no current head exists.
- **Memory Diff**: A comparison result describing additions, removals, and changed values between two versions.
- **Memory Replay Result**: A reconstructed memory state at a selected version in a lineage.
- **Memory Audit Entry**: A reviewable record of version creation, retrieval, replay, diff, or access outcomes that stores metadata, content hashes, and redacted change summaries without raw memory content.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100 percent of authorized memory writes create a new version rather than modifying an existing version.
- **SC-002**: 100 percent of non-initial memory versions can be traced to their immediately prior version.
- **SC-003**: Workflow execution can retrieve the current memory head for an existing memory scope in under 1 second during normal operating conditions.
- **SC-004**: Reviewers can replay memory to any authorized version in a lineage and receive the expected reconstructed state in 100 percent of tested replay scenarios.
- **SC-005**: Reviewers can diff any two authorized versions in the same lineage and see additions, removals, and changed values in 100 percent of tested diff scenarios.
- **SC-006**: 100 percent of memory version creations and read-oriented history actions produce audit entries with the required traceability fields and no raw memory content.
- **SC-007**: Stale-head non-initial writes and racing initial writes are detected and prevented in 100 percent of tested concurrent-change scenarios.
- **SC-008**: Submitted memory behavior demonstrates at least 90 percent unit-test coverage.
- **SC-009**: PR review notes, testing instructions, and README guidance are present and sufficient for a maintainer to verify the feature without additional verbal explanation.

## Constitution Impact

- **Durability**: Memory scope, version, head, audit, runtime source, idempotency, and archival metadata must persist transactionally before memory behavior becomes authoritative.
- **Tenant Isolation And Fairness**: Every memory API, runtime call, audit query, replay, and diff must include tenant context, fail closed on cross-tenant access, and respect tenant-scoped operation budgets.
- **Versioning**: Memory versions are append-only and lineage-aware; runtime memory protocol changes must be versioned and compatibility-assessed for pinned in-flight runs.
- **Secrets And Tool Access**: Memory records, audit payloads, logs, metrics, traces, and PR evidence must not store secrets or raw sensitive memory outside authorized memory access paths.
- **Artifact Storage**: PostgreSQL stores transactional memory snapshots only within configured inline limits; oversized future attachments require object storage with PostgreSQL metadata, hashes, access control, and auditability.
- **Approval And Resume**: Memory writes have no separate memory approval state, but any workflow-level approval required before a write must remain durable runtime state and resume with the original pinned bundle.
- **Observability**: Memory behavior must define content-free logs, metrics, traces, audit events, workflow timeline events, replay support, and operator debugging surfaces.
- **Security**: Existing Auth0/RBAC or deterministic local principals must authorize memory content, history, replay, diff, audit, and runtime access with tenant predicates on every path.

## Assumptions

- Existing platform authentication and authorization rules apply to memory content, metadata, replay, diffing, and audit access.
- A memory scope has one active current head at a time for workflow execution.
- Historical versions are retained indefinitely unless a future retention policy explicitly defines otherwise.
- Sensitive memory content is excluded from audit entries and audit views; audit surfaces preserve traceability through metadata, content hashes, and redacted change summaries.
- Replay and diffing are reviewer-facing capabilities and may be restricted to maintainers, auditors, support operators, or authorized workflow owners.
- This feature defines immutable memory behavior and delivery expectations; detailed storage, schema, API, and worker implementation choices are deferred to planning.
