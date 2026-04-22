# Feature Specification: [FEATURE NAME]

**Feature Branch**: `[###-feature-name]`  
**Created**: [DATE]  
**Status**: Draft  
**Input**: User description: "$ARGUMENTS"

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by
  importance. Each user story/journey must be independently testable so a
  single completed story still delivers value.
-->

### User Story 1 - [Brief Title] (Priority: P1)

[Describe this user journey in plain language]

**Why this priority**: [Explain why this is the highest-value outcome]

**Independent Test**: [Describe how this story can be validated on its own]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]
2. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### User Story 2 - [Brief Title] (Priority: P2)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and ordering]

**Independent Test**: [Describe how this story can be validated on its own]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### User Story 3 - [Brief Title] (Priority: P3)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and ordering]

**Independent Test**: [Describe how this story can be validated on its own]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

[Add more user stories as needed, each with an assigned priority]

## Edge Cases *(mandatory)*

- What happens when [boundary condition]?
- How does the system recover from [error or timeout scenario]?
- What happens when tenant, auth, or quota context is missing or invalid?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST [specific capability]
- **FR-002**: System MUST [specific capability]
- **FR-003**: Users MUST be able to [key interaction]
- **FR-004**: System MUST [data or workflow requirement]
- **FR-005**: System MUST [audit, security, or observability requirement]

*Example of marking unclear requirements:*

- **FR-006**: System MUST [NEEDS CLARIFICATION: unresolved decision]

### Key Entities *(include if feature involves data)*

- **[Entity 1]**: [What it represents, key attributes without implementation]
- **[Entity 2]**: [What it represents, relationships to other entities]

## Constitution Alignment *(mandatory)*

### Durability And Recovery Impact

- [State whether the feature changes workflow state, retries, compensation,
  idempotency, or resume behavior. If not applicable, say "Not in scope" and
  why.]

### Tenant Isolation And Fair Use Impact

- [State how tenant context, quotas, fairness, or noisy-neighbor protections
  apply. If not applicable, say "Not in scope" and why.]

### Contracts, Versioning, And Lineage Impact

- [State whether schemas, workflow versions, prompt/model/tool-policy versions,
  or parent-child lineage are affected.]

### Security, Secrets, And Tooling Impact

- [State Auth0, authorization, delegated credentials, secret references,
  allowlists, or outbound egress implications.]

### Artifact And Data Storage Impact

- [State whether PostgreSQL metadata, object storage, retention, or auditability
  are affected.]

### Approval, Resume, And Human Interaction Impact

- [State whether approvals, pauses, resumes, or supplemental user input are in
  scope.]

### Observability And Audit Impact

- [State the logs, metrics, traces, audit events, lineage visibility, or replay
  surfaces users and operators need.]

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: [Measurable user or business outcome]
- **SC-002**: [Measurable scale, latency, or throughput outcome]
- **SC-003**: [Measurable quality or task-completion outcome]
- **SC-004**: [Measurable operational or support outcome]

## Assumptions

- [Assumption about target users]
- [Assumption about scope boundaries]
- [Assumption about required environment or dependencies]
- [Assumption about existing systems or data]

## Review And Delivery Guidance *(mandatory)*

### Testing Instructions

- [List required unit, integration, contract, failure-recovery, or manual test
  expectations.]
- [State any required coverage target evidence or tooling.]

### PR Review Guidance

- [Call out the highest-risk files, flows, invariants, and review focus areas.]
- [Identify any security, tenant-isolation, or operability concerns reviewers
  must verify.]

### Documentation Impact

- [State the required `README.md` updates.]
- [State the required quickstart, operator, API, or admin documentation
  updates.]
