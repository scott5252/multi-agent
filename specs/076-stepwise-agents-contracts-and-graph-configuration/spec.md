# Feature Specification: Stepwise Agents, Contracts, And Graph Configuration

**Feature Branch**: `codex/076-stepwise-agents-contracts-and-graph-configuration`  
**Created**: 2026-05-11  
**Status**: Draft  
**Input**: User description: "Stepwise Agents, Contracts, And Graph Configuration. bounded agent, contract, graph, join, approval, and review steps with paged collections and backend validation mapping."

## Clarifications

### Session 2026-05-11

- Q: Should this spec introduce a new backend route family? -> A: No. Compose existing React Admin and workflow APIs unless a durable backend-owned decision is otherwise impossible. (autopilot)
- Q: Should the wizard hard-code tutorial scenarios? -> A: No. The happy path must accept arbitrary scenarios and must not encode Design Reviewer Council or Daily Intelligence Briefing defaults. (autopilot)
- Q: Who owns authorization, tenant scope, validation, publish readiness, and evidence freshness? -> A: Existing backend services and envelopes own those decisions; React only renders and submits authorized actions. (autopilot)
- Q: What is the desktop layout requirement? -> A: Every wizard screen must fit within 1280 x 800 without page, shell, or wizard-body vertical scrolling; split or page content when it does not fit. (autopilot)
- Q: What evidence is required before moving past this spec? -> A: Focused frontend tests, relevant backend route tests, generated contract freshness when applicable, typecheck, build, QA docs, Spec QA, and Playwright no-scroll validation. (autopilot)

## User Scenarios & Testing

### User Story 1 - Browser-First Wizard Progress (Priority: P1)

A user refines roles, contracts, and graph shape inside the wizard without raw JSON editing or scroll-dependent lists.

**Independent Test**: Sign in with local-principal tenant admin, navigate through visible Admin UI controls, exercise bounded agent, contract, graph, join, approval, and review steps with paged collections and backend validation mapping, and verify the wizard stays tenant-scoped, bounded, and truthful without raw JSON editing.

**Acceptance Scenarios**:

1. **Given** an authorized tenant admin, **When** the admin starts from Console Home and opens onboarding, **Then** the wizard route preserves tenant scope and renders a fixed-frame step shell.
2. **Given** a clean or partial workflow draft, **When** the admin advances through the relevant step, **Then** the UI uses workflow document editor helpers, full document save, workflow lookups, graph projection links, and builder validation summaries and refreshes durable state after mutations.
3. **Given** missing, stale, denied, or unavailable state, **When** the admin reaches the affected step, **Then** the wizard shows a truthful recovery state and never claims backend gates passed from browser-only logic.

### User Story 2 - Safe Recovery And Guardrails (Priority: P2)

A reviewer can intentionally block the flow and confirm the wizard links back to the right step, keeps unsafe details hidden, and continues to use visible UI controls after local login.

**Independent Test**: Force an incomplete validation or missing evidence path for Spec 076, capture a screenshot, and verify safe summaries, no raw payloads, no secret values, no private prompts, no transcripts, and no unauthorized tenant labels appear.

**Acceptance Scenarios**:

1. **Given** a blocked backend readiness state, **When** the wizard renders the blocker, **Then** the message is safe, specific, and connected to a visible recovery action.
2. **Given** an unauthorized or cross-tenant request, **When** the browser asks for onboarding data, **Then** the backend fails closed and the UI does not leak another tenant label or identifier.
3. **Given** the 1280 x 800 desktop viewport, **When** every step is visited, **Then** the page, admin shell, wizard frame, content body, and footer do not require vertical scrolling or overlap.

### User Story 3 - Durable Completion Evidence (Priority: P3)

A developer or QA reviewer can inspect tests, validation manifests, QA guides, and status files to understand exactly what was implemented and how it was verified.

**Independent Test**: Review wizard component tests for roles, contracts, graph preview lists, save payloads, keyboard navigation, typecheck, build, and no-overlap Playwright checks, this spec directory, the autopilot status entry, and the generated QA documents for complete phase and validation evidence.

**Acceptance Scenarios**:

1. **Given** the implementation is complete, **When** tests run, **Then** the focused frontend and backend checks cover the user-visible behavior for this spec.
2. **Given** QA docs are validated, **When** a non-developer follows them, **Then** they can reproduce the browser flow without editing URLs after login.
3. **Given** final roadmap validation, **When** the queue completes, **Then** README and user_guide documentation describe the new generic wizard path.

### Edge Cases

- Clean tenants with no workflow drafts show real empty states and creation actions, not sample data.
- Existing drafts can be resumed, refreshed, or opened in advanced editors without making advanced editors mandatory.
- Stale revision tokens produce safe recovery, not silent overwrites.
- Missing prompt, profile, provider, skill, channel, or evidence readiness remains backend-owned.
- Launch or publish actions remain unavailable until backend validation and readiness allow them.
- Screens never expose raw secrets, credential values, provider headers, raw prompts, completions, memory contents, raw run payloads, external tool payloads, test transcripts, stack traces, local paths, or unauthorized tenant labels.

## Requirements

### Functional Requirements

- **FR-001**: The implementation MUST deliver bounded agent, contract, graph, join, approval, and review steps with paged collections and backend validation mapping.
- **FR-002**: The implementation MUST consume workflow document editor helpers, full document save, workflow lookups, graph projection links, and builder validation summaries instead of inventing browser-only source-of-truth state.
- **FR-003**: The wizard MUST preserve tenant scope in all entry, resume, advanced editor, launch, and evidence links.
- **FR-004**: The wizard MUST keep authorization, tenant scope, validation, publish readiness, evidence freshness, redaction, and runtime eligibility backend-owned.
- **FR-005**: The wizard MUST fit every step in 1280 x 800 without vertical scrolling, clipped controls, hidden footer actions, or text overlap.
- **FR-006**: The wizard MUST expose visible recovery actions for denied, loading, dependency unavailable, no-draft, stale, missing evidence, failed validation, and blocked publish states.
- **FR-007**: Any generated workflow document state MUST remain editable in existing workflow editors and durable through existing revision-token save APIs.
- **FR-008**: QA flows MUST use visible UI links and controls after the initial local login entry point.
- **FR-009**: Screenshots, docs, tests, logs, and exported evidence MUST omit raw prompts, completions, credentials, secrets, private payloads, tool payloads, transcripts, memory contents, stack traces, local paths, and unauthorized labels.
- **FR-010**: The implementation MUST include focused frontend tests, relevant backend tests, generated contract checks when applicable, typecheck, build, QA docs, Spec QA, and Playwright validation.
- **FR-011**: curl_testing.md MUST be updated or an explicit no-new-route-family decision MUST be recorded when public JSON or admin JSON changes.
- **FR-012**: README and user_guide updates MUST describe the completed generic wizard flow after all roadmap specs complete.

### Key Entities

- **Onboarding Wizard Step**: A bounded React step that represents one recoverable setup decision.
- **Workflow Scenario Intake**: Neutral user-provided workflow identity, purpose, inputs, outputs, coordination, approval, channel, and evidence preferences.
- **Generic Blueprint Document**: Editable workflow document scaffolding produced from scenario intake and persisted through workflow draft APIs.
- **Readiness Summary**: Backend-owned prompt, profile, provider, skill, channel, validation, evidence, publish, or runtime status rendered by the wizard.
- **Launch Handoff**: Tenant-scoped visible Admin link to runtime, Design Reviews, operations, or graph evidence surfaces.

## Success Criteria

- **SC-001**: A QA reviewer can complete the Spec 076 browser path from local login through visible UI controls.
- **SC-002**: Focused tests prove arbitrary scenario support and no hard-coded tutorial defaults for the implemented slice.
- **SC-003**: The 1280 x 800 Playwright screenshot shows no vertical scroll, overlap, clipped controls, or hidden footer actions.
- **SC-004**: Backend-owned blockers remain authoritative for validation, evidence, publish, and runtime eligibility.
- **SC-005**: No unsafe raw payloads, secrets, transcripts, prompts, completions, local paths, stack traces, or unauthorized labels appear in UI, docs, screenshots, or logs.

## Assumptions

- Specs 001 through 073 provide the workflow registry, builder, full document save, validation, publish gate, test bench, runtime, operations, graph, and React Admin foundations.
- Local QA uses AUTH_MODE=local_principal and deterministic local data only.
- No live provider, Auth0, Telegram, connector, credential, or outbound call is required for this roadmap.
- Existing advanced workspaces remain available as escape hatches, but the wizard happy path does not require raw JSON editing.

## Constitution Impact

- **Durable By Default**: Draft, validation, evidence, publish, and launch readiness are derived from durable backend state.
- **Contract-First Agent Coordination**: Workflow roles, contracts, edges, joins, approvals, and evidence remain explicit.
- **Security With Practical Development Ergonomics**: Local-principal QA proves behavior without live external systems.
- **Operability Is A Product Requirement**: Progress, blockers, recovery links, and validation evidence are visible.
- **Tenant Isolation And Secret Hygiene**: Tenant scope is explicit and unsafe details are redacted everywhere.

## Testing Instructions

- Run wizard component tests for roles, contracts, graph preview lists, save payloads, keyboard navigation, typecheck, build, and no-overlap Playwright checks.
- Run generated React type freshness check when contracts are generated or touched.
- Run frontend typecheck, focused Vitest coverage, frontend build, QA document validation, Spec QA, and Playwright UI validation.
- Run Ruff, Ruff format check, mypy, full coverage, and multi-agent-curl-test as part of final roadmap stability gate.
