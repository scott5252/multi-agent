# Feature Specification: Design Reviewer Template, Test Bench, And Publish Gates

**Feature Branch**: `codex/064-design-reviewer-template-test-bench-and-publish-gates`  
**Created**: 2026-05-08  
**Status**: Draft  
**Input**: User description: "Add reusable Design Reviewer Council template and QA evidence support. Platform or tenant admins must be able to install or create a workflow template with lead, reviewer, quorum, synthesis, and handoff roles; attach required test-bench evidence; validate deterministic and model-backed safe-mode behavior; and publish only when current evidence passes. QA must cover four-of-five quorum success, three-of-four quorum success, revision-required outcomes, blocking issue handling, manual-resolution pause, retry/cancel behavior, approved handoff, cross-tenant denial, redaction, and Admin live-data states."

## Clarifications

### Session 2026-05-08

- Q: How should admins create the reusable template? -> A: (autopilot) Use an explicit tenant-scoped Admin install action, not a hidden fixture, seed-only path, or migration side effect.
- Q: Which evidence modes are required for local QA? -> A: (autopilot) Use deterministic local evidence plus governed model-backed safe-mode evidence that does not call live external providers.
- Q: What evidence freshness satisfies publish readiness? -> A: (autopilot) Only a passing required evidence run for the current workflow draft revision satisfies the publish gate.
- Q: How should Admin represent setup and empty states? -> A: (autopilot) Render live backend template readiness and truthful empty states without sample sessions, reviewer rows, quorum decisions, or handoffs.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Install Council Template With Evidence (Priority: P1)

A platform admin or tenant admin installs a reusable Design Reviewer Council workflow template for the active tenant. The installation creates or reuses an explicit workflow draft with lead, reviewer, quorum, synthesis, and handoff roles, then attaches required Test Bench evidence that proves the template can execute safely before it is published.

**Why this priority**: The scenario is not production-ready unless admins can create the workflow and evidence through a durable action instead of relying on hidden fixture setup.

**Independent Test**: Start from an Acme local-principal tenant with no installed council template, run the install action, and verify the workflow draft, required evidence suite, safe test run, and publish-gate response are tenant-scoped and durable.

**Acceptance Scenarios**:

1. **Given** an authorized admin scoped to a tenant, **When** the admin installs the council template, **Then** the system creates a reusable workflow draft with lead, reviewer, quorum, synthesis, and handoff roles and returns safe identifiers for the draft and evidence.
2. **Given** the same admin repeats the install with the same tenant and idempotency key, **When** the action is replayed, **Then** the system returns the same installed template summary without duplicating the workflow draft, test suite, or publish requirement.
3. **Given** the install action completes, **When** the admin inspects the Admin design-review workspace, **Then** the workspace shows the live template setup state and evidence readiness without inventing sample sessions or successful handoffs.

---

### User Story 2 - Enforce Current Publish Evidence (Priority: P2)

An admin evaluates the installed template before publication. The publish gate reports whether workflow validation and current required Test Bench evidence pass for the active draft revision, and it blocks publication when evidence is missing, stale, failed, or tenant-mismatched.

**Why this priority**: Published design-review workflows must be backed by current evidence so admins can trust the template in production-like workflows.

**Independent Test**: Install the template, evaluate the publish gate, mutate the draft to create a newer revision, and verify the gate blocks until a new safe run is recorded for the current revision.

**Acceptance Scenarios**:

1. **Given** an installed template with a passing safe evidence run for its current draft revision, **When** the publish gate is evaluated, **Then** the gate reports ready and identifies the passing evidence run.
2. **Given** the workflow draft has a newer revision than the latest evidence run, **When** the publish gate is evaluated, **Then** the gate blocks publication and explains that current evidence is required.
3. **Given** the latest evidence run failed or belongs to another tenant, **When** the publish gate is evaluated, **Then** the gate blocks publication without exposing raw execution payloads.

---

### User Story 3 - Prove Scenario Outcomes And Denials (Priority: P3)

QA operators validate the reusable template against representative council outcomes: four-of-five quorum success, three-of-four quorum success, revision-required feedback, blocking issues, manual-resolution pause, retry and cancel behavior, approved handoff, cross-tenant denial, redaction, and truthful Admin live-data states.

**Why this priority**: The template is only credible if its evidence covers the real review modes that admins will depend on during implementation handoff.

**Independent Test**: Run the QA064 validation manifest and Playwright walkthrough against a seeded local-principal database and verify every named outcome appears as durable, redaction-safe evidence.

**Acceptance Scenarios**:

1. **Given** deterministic safe-mode evidence exists, **When** QA verifies the evidence matrix, **Then** each required quorum, revision, blocking, manual, retry, cancel, handoff, denial, redaction, and Admin state outcome is represented by a safe summary or artifact reference.
2. **Given** a tenant admin from another tenant attempts to install or inspect the Acme council template, **When** the request is evaluated, **Then** the system denies access and records safe audit evidence.
3. **Given** Admin UI has no live design-review sessions, **When** the workspace loads, **Then** it shows truthful empty state plus template setup readiness rather than fake review rows.

### Edge Cases

- Repeated install attempts with the same idempotency key must return the existing durable setup and mark the response as replayed.
- Repeated install attempts with a different idempotency key but the same tenant and template key must reuse the tenant's canonical template draft instead of creating competing workflow templates.
- Cross-tenant install, inspect, evidence, and publish-gate requests must fail closed.
- Evidence runs created for older workflow draft revisions must not satisfy a current-revision publish requirement.
- Safe-mode model-backed evidence must prove gateway boundaries without storing raw prompts, completions, provider payloads, secrets, private channel messages, memory contents, or external tool payloads.
- Admin UI must distinguish not installed, installed but evidence pending, evidence failed, evidence stale, ready to publish, and published states using live backend data.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide an explicit admin action to install or create the reusable Design Reviewer Council template for the active tenant.
- **FR-002**: System MUST restrict the template install action to authorized platform or tenant admins and fail closed for unauthorized or cross-tenant requests.
- **FR-003**: System MUST create or reuse a workflow draft containing lead, reviewer, quorum, synthesis, and handoff roles with an acyclic graph and manual-resolution failure behavior for quorum joins.
- **FR-004**: System MUST make template installation idempotent by tenant, template key, and idempotency key while preventing duplicate canonical council templates for a tenant.
- **FR-005**: System MUST attach a required Test Bench suite to the workflow draft so publish evaluation can require current passing evidence.
- **FR-006**: System MUST include deterministic safe-mode test cases for four-of-five quorum success, three-of-four quorum success, revision-required outcomes, blocking issue handling, manual-resolution pause, retry/cancel behavior, approved handoff, cross-tenant denial, redaction, and Admin live-data states.
- **FR-007**: System MUST include model-backed safe-mode evidence that exercises governed model execution boundaries without making production provider calls in local QA.
- **FR-008**: System MUST evaluate publish readiness using workflow validation plus required evidence freshness for the current draft revision.
- **FR-009**: System MUST block publication when required evidence is missing, stale, failed, unauthorized, or scoped to a different tenant.
- **FR-010**: System MUST return redaction-safe installation, evidence, and publish-gate summaries with identifiers, statuses, timestamps, and artifact references only.
- **FR-011**: System MUST record auditable safe events for template installation, evidence generation, publish-gate evaluation, and denied cross-tenant attempts.
- **FR-012**: System MUST expose live template setup state in the Admin design-review workspace without rendering sample sessions, sample reviewer rows, or fake successful handoffs.
- **FR-013**: System MUST expose truthful empty, loading, denied, installed, evidence-pending, stale, ready, and published states in the Admin UI.
- **FR-014**: System MUST update API regression coverage when new or changed admin route surfaces are introduced.
- **FR-015**: System MUST keep QA artifacts free of raw prompts, raw completions, secrets, provider authorization headers, private channel payloads, memory contents, unauthorized run payloads, and raw external tool payloads.
- **FR-016**: System MUST validate tenant identity and principal scope on every template, evidence, and publish-gate route.
- **FR-017**: System MUST preserve existing workflow registry, Test Bench, design-review coordinator, and Admin workspace behavior for tenants without an installed template.
- **FR-018**: System MUST document local-principal setup, deterministic QA validation, Playwright walkthrough, and reviewer notes for this feature.

### Key Entities *(include if feature involves data)*

- **Council Template Installation**: A tenant-scoped setup result for the reusable Design Reviewer Council workflow template, including template key, idempotency evidence, workflow draft identifiers, evidence identifiers, publish-gate status, and safe summary.
- **Council Workflow Draft**: The workflow draft generated by installation, containing lead, reviewer, quorum, synthesis, and handoff roles and the graph structure required to run an acyclic review round.
- **Required Evidence Suite**: A Test Bench suite attached to the workflow draft as required evidence for publish gates.
- **Safe Evidence Run**: A deterministic or model-backed safe-mode Test Bench run scoped to the current workflow draft revision.
- **Publish Gate Summary**: A redaction-safe evaluation of validation readiness and current evidence readiness for the installed template.
- **Admin Template State**: The live Admin workspace representation of installation and evidence readiness for the active tenant.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An authorized local-principal Acme admin can install the template and receive workflow draft, required suite, evidence run, and publish-gate identifiers in one action.
- **SC-002**: Replaying the same install request does not create duplicate workflow drafts, suites, required evidence records, or evidence runs.
- **SC-003**: Publish readiness is blocked within one evaluation when evidence is missing, failed, stale, or cross-tenant.
- **SC-004**: QA064 automated validation proves all required quorum, revision, blocking, manual, retry, cancel, handoff, denial, redaction, and Admin live-data outcomes.
- **SC-005**: Admin UI Playwright validation shows live template readiness and truthful empty/session states without sample review rows.
- **SC-006**: Redaction checks find no raw prompts, raw completions, secrets, provider authorization headers, private payloads, memory contents, unauthorized payloads, or raw external tool payloads in API responses, screenshots, and QA artifacts.
- **SC-007**: Existing workflow registry, test-bench, design-review API, React admin, and curl regression tests pass after the feature lands.

## Assumptions

- The template install action will be an explicit backend action surfaced to Admin, not a hidden fixture or migration side effect.
- The workflow draft and required evidence will reuse existing workflow registry and Test Bench persistence instead of adding new tables unless implementation discovers an existing durable field is missing.
- Local QA will use deterministic and model-backed safe-mode paths that do not call live external model providers.
- The installed template remains tenant-scoped; sharing a canonical template across tenants is out of scope.
- Publishing itself continues to use the existing workflow registry publish mechanism; this feature strengthens setup and evidence readiness.
- The existing design-review coordinator remains responsible for running review sessions after a workflow is installed and published.
