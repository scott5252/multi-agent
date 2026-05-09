# Feature Specification: Custom Workflow Test Evidence And Publish Setup

**Feature Branch**: `codex/072-custom-workflow-test-evidence-and-publish-setup`  
**Created**: 2026-05-09  
**Status**: Draft  
**Input**: User description: "Custom Workflow Test Evidence And Publish Setup. Users creating custom workflows need a guided way to create required Test Bench suites and cases for the current workflow draft revision, run safe deterministic evidence, inspect diagnostics, bind evidence to publish requirements, and publish only when validation and current required evidence pass. The feature must integrate Workflow Registry and Agent Tests without requiring users to manually copy workflow draft ids, revision ids, suite ids, or browser URLs. Publish readiness must remain backend-owned and must reject stale, missing, cross-tenant, failed, or synthetic evidence."

## Clarifications

### Session 2026-05-09

- Q: Should Spec 072 create a separate evidence subsystem or reuse the existing Agent Tests/Test Bench domain? -> A: Reuse the existing Test Bench services, repositories, run records, artifact references, and publish-gate evidence as the source of truth; add workflow-setup contextual adapters only where current contracts cannot create or bind evidence from an active workflow draft. (autopilot)
- Q: What makes evidence current for publish readiness? -> A: Evidence must be tied to the exact workflow draft revision and required suite/case set being published; any workflow document change, suite target change, missing required case, or older run makes the evidence stale until a new deterministic passing run is recorded. (autopilot)
- Q: Which execution modes are allowed for clean-tenant QA and workflow setup launch? -> A: Default to deterministic local safe execution modes with mocked providers/tools and backend-denied live provider or external side-effect modes unless a future spec explicitly approves a live probe path. (autopilot)
- Q: What evidence details may appear in workflow setup and QA artifacts? -> A: Show safe status, counts, requirement names, case labels, assertion summaries, and opaque artifact references only; raw transcripts, prompts, completions, provider/tool payloads, credentials, local paths, private payloads, and unauthorized labels must be omitted or redacted. (autopilot)
- Q: Where is the trust boundary for publish readiness? -> A: Workflow validation, evidence freshness, suite/case eligibility, run status, tenant scope, and publish approval remain backend-owned; browser UI may guide and refresh but cannot synthesize passing evidence or override publish blockers. (autopilot)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create Required Evidence From Workflow Setup (Priority: P1)

An authorized admin configuring a custom workflow can create or select a required Test Bench suite for the current workflow draft revision, add safe deterministic cases, and attach a workflow test requirement without copying internal ids.

**Why this priority**: A custom workflow cannot be published safely unless required test evidence is defined against the exact draft revision that will be validated and published.

**Independent Test**: From a workflow draft with roles, graph, prompts, and profiles, open the workflow setup test evidence section, create a required suite, add at least one deterministic case, save the workflow draft, reload, and verify the test requirement remains attached to the current draft revision.

**Acceptance Scenarios**:

1. **Given** a workflow draft with no required test evidence, **When** the admin creates a required suite from the workflow setup evidence section, **Then** the system creates a backend-authorized suite scoped to the active tenant and current draft revision and adds a workflow test requirement reference.
2. **Given** an existing authorized suite for the active workflow draft, **When** the admin selects it from workflow setup, **Then** the workflow document stores a safe test requirement reference without requiring manual suite ids, draft ids, revision ids, or copied browser URLs.
3. **Given** an invalid target type, stale revision, missing case coverage, unsupported live provider mode, or cross-tenant suite, **When** the admin attempts to attach evidence, **Then** backend-owned validation rejects the action with safe section-specific findings.

---

### User Story 2 - Run And Inspect Safe Evidence (Priority: P2)

An authorized admin can launch deterministic Test Bench runs for the attached suite, refresh evidence status, inspect pass/fail diagnostics, and understand which cases or assertions block publication.

**Why this priority**: Evidence must be current and understandable. Users need to launch safe runs and act on diagnostics without leaving workflow setup or exposing raw transcripts.

**Independent Test**: Launch a deterministic run for the attached suite from workflow setup, wait for completion, refresh evidence, inspect pass/fail summaries, and confirm the workflow evidence panel shows safe artifact references and diagnostics.

**Acceptance Scenarios**:

1. **Given** an attached required suite with deterministic cases, **When** the admin launches a safe evidence run, **Then** the run targets the active workflow draft revision and records backend-owned evidence status.
2. **Given** a completed passing run, **When** the admin refreshes evidence, **Then** the workflow setup UI shows current passing evidence, safe artifact references, and no raw test transcripts or unsafe payloads.
3. **Given** a failed run, partial run, stale run, missing artifact, or unsupported live provider execution mode, **When** evidence is refreshed, **Then** the UI shows safe diagnostics and keeps publish blocked until backend requirements pass.

---

### User Story 3 - Publish Only With Current Evidence (Priority: P3)

An authorized admin can validate and publish a custom workflow only when backend-owned workflow validation and required current Test Bench evidence both pass for the draft revision being published.

**Why this priority**: Publishing is the trust boundary. Stale, missing, failed, cross-tenant, or synthetic evidence must never satisfy a publish requirement.

**Independent Test**: Attempt to publish with missing evidence, stale evidence, failed evidence, and current passing evidence; verify each blocker or success comes from backend-owned publish readiness and is linked to the evidence section.

**Acceptance Scenarios**:

1. **Given** a workflow draft with no attached required evidence, **When** the admin attempts to publish, **Then** the publish panel blocks the action and links to the evidence setup controls.
2. **Given** evidence from an older draft revision, failed run, cross-tenant suite, or synthetic evidence marker, **When** publish readiness is checked, **Then** the backend rejects the evidence and reports a safe actionable blocker.
3. **Given** current workflow validation and required evidence both pass for the active draft revision, **When** the admin publishes, **Then** the publish action succeeds and the evidence summary is recorded without unsafe raw payloads.

### Edge Cases

- Clean tenants with no suites or cases must show truthful empty states and creation actions, not fake suites, cases, runs, artifacts, or evidence.
- Workflow setup must not require users to hand-copy workflow ids, draft ids, revision ids, suite ids, run ids, or browser URLs.
- Existing suites must appear only when backend authorization confirms they are eligible for the active tenant, principal, workflow target, and draft revision.
- Evidence tied to an older draft revision must become stale after the workflow document changes.
- Failed, cancelled, partial, timed-out, missing-case, missing-assertion, unsupported-mode, or quarantined evidence must block publish.
- Unsupported live provider or external-tool execution mode must be denied for local deterministic QA unless an explicit approved live probe path exists.
- Raw test transcripts, raw tool payloads, raw prompts, completions, memory contents, provider payloads, credentials, local filesystem paths, stack traces, and unauthorized tenant labels must never appear in UI summaries, screenshots, docs, logs, exports, or audit summaries.
- Artifact references must be safe opaque references or redacted summaries and must not expose local paths or private payloads.
- Idempotent creation and run-launch retries must not create duplicate suites, cases, requirements, or runs for the same idempotency key.
- Cross-tenant suites, runs, artifacts, cases, or publish attempts must fail closed without leaking unauthorized labels.
- Desktop and mobile layouts must keep evidence controls, diagnostics, publish blockers, and cross-links readable without overlap.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide workflow setup controls for creating a required Test Bench suite scoped to the active workflow draft revision.
- **FR-002**: The system MUST provide workflow setup controls for selecting an existing authorized suite that is eligible for the active tenant, workflow target, and draft revision.
- **FR-003**: The system MUST let authorized admins add deterministic required cases or safe case templates to the selected suite from the workflow setup flow.
- **FR-004**: The system MUST attach a workflow document test requirement reference to the current draft through backend-owned workflow document save contracts with revision tokens and idempotency keys.
- **FR-005**: The system MUST expose safe execution-mode selection and reject unsupported live provider, external tool, or side-effecting execution modes unless explicitly approved by backend policy.
- **FR-006**: The system MUST launch safe deterministic Test Bench runs for the attached suite and current draft revision without requiring copied ids or browser URLs.
- **FR-007**: The system MUST refresh evidence status and display safe pass/fail, case, assertion, diagnostic, artifact-reference, and freshness summaries.
- **FR-008**: The system MUST keep raw transcripts, raw prompts, completions, tool payloads, provider payloads, credentials, local paths, stack traces, private channel data, memory contents, and unauthorized tenant labels out of workflow setup evidence surfaces.
- **FR-009**: The system MUST detect and report stale evidence when workflow draft content or target revision changes after a run.
- **FR-010**: The system MUST reject missing, failed, stale, cross-tenant, synthetic, unsupported-mode, or incomplete evidence when computing publish readiness.
- **FR-011**: The system MUST link publish and validation blockers back to the exact workflow setup evidence section, suite, case, or requirement that can resolve the blocker.
- **FR-012**: The system MUST provide safe cross-links from Workflow Registry to Agent Tests and back while preserving active tenant scope and selected workflow context.
- **FR-013**: The system MUST reload attached suites, cases, requirements, run summaries, evidence freshness, and publish blockers from durable backend state.
- **FR-014**: The system MUST enforce Auth0-shaped and local-principal authorization for evidence creation, suite/case selection, run launch, evidence refresh, workflow requirement attachment, and publish.
- **FR-015**: The system MUST provide truthful empty, loading, dirty, saving, launching, refreshing, passing, failing, stale, conflict, denied, blocked, and error states for evidence setup and publish readiness.
- **FR-016**: The system MUST preserve idempotent replay and same-key different-payload conflict behavior for contextual suite creation, case creation, run launch, requirement attachment, and workflow save actions.
- **FR-017**: The system MUST include backend, frontend, Playwright, QA docs, generated contract, and curl regression coverage for evidence setup and publish gating.
- **FR-018**: The system MUST update curl regression coverage when any Test Bench, workflow setup, or publish route family is added or behaviorally changed.

### Key Entities *(include if feature involves data)*

- **Workflow Evidence Requirement**: A workflow document requirement that references an eligible Test Bench suite, expected target revision, required cases, and publish-readiness criteria.
- **Contextual Test Suite**: A tenant-scoped Test Bench suite created or selected from workflow setup for a specific workflow target and draft revision.
- **Required Case Template**: A safe deterministic case pattern that can be added to a contextual suite without real provider or external side effects.
- **Evidence Run Summary**: Redaction-safe run status, target revision, completion state, pass/fail counts, artifact references, and diagnostic summaries.
- **Evidence Freshness Finding**: Backend-owned determination that evidence is current, stale, missing, failed, incomplete, unsupported, cross-tenant, or synthetic.
- **Publish Evidence Gate**: The backend-owned publish-readiness decision that combines workflow validation and current required evidence.
- **Workflow/Test Bench Context Link**: A safe UI link or route state that preserves tenant scope and selected workflow context without exposing protected payloads.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reviewer can create or select a required Test Bench suite from workflow setup, add at least one deterministic case, save, reload, and see the requirement attached to the current draft revision without copying ids.
- **SC-002**: A reviewer can launch a deterministic evidence run from workflow setup and see safe pass/fail diagnostics and artifact references after refresh.
- **SC-003**: Publish readiness blocks missing, stale, failed, cross-tenant, unsupported-mode, incomplete, and synthetic evidence with actionable links to evidence setup.
- **SC-004**: Publish succeeds only when workflow validation and current required evidence both pass for the active draft revision.
- **SC-005**: Raw transcripts, raw prompts, completions, provider payloads, tool payloads, credentials, local paths, stack traces, private payloads, and unauthorized labels are absent from UI summaries, screenshots, docs, logs, exports, and audit summaries.
- **SC-006**: Desktop and mobile Playwright screenshots show nonblank evidence controls, stable layout, no text overlap, reload persistence, and visible publish blockers or passing evidence.
- **SC-007**: Focused backend tests, frontend tests, generated contract checks, QA document validation, Spec QA, Playwright UI validation, and multi-agent curl regression pass before Spec 073 begins.

## Assumptions

- Spec 069 provides the full workflow document save contract and validation mapping used to persist test requirements.
- Spec 070 provides workflow role, graph, contract, and join setup surfaces that this evidence step can sit beside.
- Spec 071 provides prompt/profile bindings required for realistic deterministic workflow cases.
- Existing Test Bench backend services and React Agent Tests components remain the source of truth for suites, cases, runs, assertions, artifacts, and publish evidence.
- Local QA uses deterministic local-principal data and mocked/safe execution modes; no real providers, credentials, connectors, models, or outbound side effects are required.
- Test evidence for custom workflows is required at publish time, but final end-to-end runtime launch remains Spec 073.

## Constitution Impact

- **Durable By Default**: Suites, cases, runs, requirements, evidence summaries, and publish gate decisions are durable backend state.
- **Immutable State And Memory**: Evidence must target immutable draft revision identifiers and becomes stale when the draft changes.
- **Contract-First Agent Coordination**: Required cases and publish evidence validate explicit workflow contracts before publish.
- **Security With Practical Development Ergonomics**: Auth0-shaped protected routes and local-principal QA are both required.
- **Operability Is A Product Requirement**: Publish blockers, stale evidence, failed runs, and diagnostics are visible and actionable.
- **Tenant Isolation And Fair Scheduling**: Evidence and run launch eligibility remain tenant-scoped and backend-authorized.
- **Secret Hygiene And Controlled Tool Access**: Raw transcripts, private payloads, provider/tool data, credentials, and local paths are never exposed.
- **Version-Pinned Execution**: Publish readiness requires current evidence for the exact draft revision that will be published.

## Testing Instructions

- Add focused backend and contract tests for contextual suite creation, case creation, requirement attachment, run launch, evidence refresh, publish readiness, stale evidence, idempotency, unsupported modes, cross-tenant denial, and redaction.
- Add frontend tests for evidence panel creation/selection, case authoring, run launch, refresh, diagnostics, reload persistence, publish blockers, cross-links, and safe error handling.
- Add Playwright desktop and mobile journeys that use visible Workflow Registry and Agent Tests navigation to create evidence, launch deterministic runs, refresh diagnostics, and confirm publish gating.
- Add screenshot evidence proving no raw transcripts, local paths, raw payloads, or unauthorized tenant labels appear.
- Update `curl_testing.md` for any new or changed Test Bench, workflow setup, evidence, or publish route family.

## Documentation Impact

- Add Spec 072 QA guide, UI walkthrough, manual user guide, QA environment file, and PR/reviewer notes.
- Document the browser path for creating required evidence, launching safe runs, reading diagnostics, resolving stale evidence, and publishing after current evidence passes.
- Keep API calls as validation aids only; user setup guidance must rely on visible Admin navigation and controls after login.

## PR Review Guidance

- Verify publish readiness remains backend-owned and rejects stale, failed, missing, cross-tenant, synthetic, and unsupported evidence.
- Review tenant isolation, Auth0-shaped tests, local-principal Playwright evidence, idempotency, stale conflict handling, generated contracts, redaction, and curl coverage.
- Confirm the UI does not synthesize fake suites, cases, runs, artifacts, evidence, workflows, prompts, profiles, or publish readiness in production states.
