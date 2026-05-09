# Feature Specification: End-To-End Custom Workflow Setup Wizard And Runtime Launch

**Feature Branch**: `codex/073-end-to-end-custom-workflow-setup-wizard-and-runtime-launch`  
**Created**: 2026-05-09  
**Status**: Draft  
**Input**: User description: "End-To-End Custom Workflow Setup Wizard And Runtime Launch. After Specs 069 through 072, users need a polished guided experience that ties the pieces together: create workflow, add agents, create prompts/profiles, build graph, add tests, validate, publish, and launch or select the published workflow from supported runtime/design-review surfaces. The feature must be usable from a clean tenant, must avoid raw JSON editing, must use UI links for navigation, must provide clear progress and recovery states, and must include full QA evidence that a user can configure their own multi-agent workflow in the browser."

## Clarifications

### Session 2026-05-09

- Q: Should the final setup experience replace the advanced workflow editors? -> A: No. Add a guided checklist/wizard that coordinates the existing backend-owned editor, graph, prompt/profile, evidence, validation, publish, runtime, and design-review surfaces without hiding advanced controls. (autopilot)
- Q: How should a clean tenant reach a realistic three-agent workflow quickly? -> A: Provide visible setup controls that apply a durable three-agent starter document with prompts, profiles, graph nodes, join policy, and contracts; users can continue editing every generated field in existing controls. (autopilot)
- Q: What is the trust boundary for completion state? -> A: Browser completion state may summarize progress, but validation, publish readiness, required evidence freshness, authorization, and published runtime eligibility remain backend-owned. (autopilot)
- Q: Which runtime launch surfaces must be linked after publish? -> A: Link to the retained user run workspace and the Design Reviews workflow selector, carrying tenant scope and the published workflow id when available. (autopilot)
- Q: What counts as the full end-to-end QA path? -> A: Local-principal browser QA must sign in, create a workflow, open the created draft through visible links, apply or edit three agents, save, create and run required evidence, validate, publish, open runtime launch, select in Design Reviews, and inspect graph evidence. (autopilot)

## User Scenarios & Testing

### User Story 1 - Guided Clean-Tenant Setup (Priority: P1)

An authorized tenant admin starts from a tenant with no custom workflow draft and can create a workflow, open the draft, apply a three-agent starter, and see clear progress for metadata, agents, prompts/profiles, graph, contracts, evidence, validation, publish, and launch.

**Independent Test**: Start from local login, navigate through visible Admin links to Workflows, create a workflow, open the created draft link, apply the starter, save, reload, and verify the checklist shows agent, prompt/profile, graph, and contract progress without raw JSON editing.

**Acceptance Scenarios**:

1. **Given** a clean tenant workflow registry, **When** the admin creates a workflow and opens the created draft, **Then** the draft opens in the React workflow builder using authorized route links.
2. **Given** an empty or one-role draft, **When** the admin applies the three-agent starter, **Then** the workflow document gains at least three agent roles, ready prompt/profile references, a join node, join policy, edges, and contracts through visible controls.
3. **Given** unsaved starter edits, **When** the admin saves the draft, **Then** the backend persists the full document through the revision-token save contract and the checklist continues from durable state.

### User Story 2 - Evidence, Validation, And Publish Recovery (Priority: P2)

An authorized admin can follow guided recovery links from incomplete evidence or validation steps, create required deterministic evidence, save the requirement, launch a safe run against the current draft revision, validate, and publish only when backend-owned gates pass.

**Independent Test**: Attach a required suite from workflow setup, save, add a deterministic case, launch a run, run validation, prepare publish, confirm publish, and verify publish blockers link back to exact evidence or validation sections when incomplete.

**Acceptance Scenarios**:

1. **Given** a draft without evidence, **When** the admin opens the checklist evidence step, **Then** it targets the workflow evidence panel and never asks the user to copy suite, draft, revision, or run ids.
2. **Given** current deterministic evidence and passing validation, **When** the admin publishes, **Then** publish succeeds only through backend-owned readiness and produces a published bundle.
3. **Given** missing, stale, failed, cross-tenant, synthetic, or unsupported evidence, **When** publish readiness is checked, **Then** the gate remains blocked and links to safe recovery sections.

### User Story 3 - Runtime And Design Review Handoff (Priority: P3)

After publish, an authorized admin can launch the workflow through the user run workspace or select it in Design Reviews without manually editing URLs or copying ids.

**Independent Test**: Publish a custom workflow, open the runtime launch link, verify the workflow id is prefilled, open the Design Reviews link, verify the published workflow is selected in the workflow selector, and inspect published graph evidence.

**Acceptance Scenarios**:

1. **Given** a published custom workflow, **When** the admin opens runtime launch from the checklist, **Then** the run workspace preserves tenant scope and preselects the published workflow id or workflow key.
2. **Given** a published custom workflow, **When** the admin opens Design Reviews from the checklist, **Then** the workflow selector can choose the published workflow bundle.
3. **Given** published graph evidence exists, **When** the admin opens graph inspection, **Then** the graph panel shows keyboard-readable node and edge summaries.

### Edge Cases

- Clean tenants with no drafts must show real empty states and creation actions, not fake workflows.
- Checklist state must tolerate partial, dirty, stale, failed, denied, and loading states without claiming backend gates passed.
- Runtime links must remain usable before publish but clearly indicate publish is required for durable selection.
- Query parameters used for handoff must preserve tenant scope and must not expose secrets, raw prompts, raw completions, local paths, test transcripts, or unauthorized tenant labels.
- Browser QA must use visible links and buttons after login; direct API calls are allowed only as secondary validation.

## Requirements

### Functional Requirements

- **FR-001**: The workflow builder MUST show a guided setup checklist covering metadata, agents, prompts/profiles, graph, contracts, evidence, validation, publish, and launch.
- **FR-002**: The checklist MUST compute progress from current workflow document state plus backend validation and publish readiness summaries.
- **FR-003**: The setup flow MUST provide a visible three-agent starter action that creates at least three roles, prompt/profile references, graph nodes, edges, contracts, and a join policy.
- **FR-004**: The starter output MUST remain editable through existing workflow role, prompt/profile, graph topology, join, contract, and evidence controls.
- **FR-005**: The setup flow MUST preserve backend-owned workflow save, validation, evidence, and publish contracts and MUST NOT synthesize publish readiness in the browser.
- **FR-006**: The checklist MUST link each incomplete step to the relevant visible page section.
- **FR-007**: Runtime launch links MUST preserve tenant scope and prefill the workflow id when a workflow id is provided by the setup flow.
- **FR-008**: Design Review links MUST preserve tenant scope and select the requested published workflow when it is present in authorized workflow options.
- **FR-009**: The workflow builder MUST refresh durable state after successful publish so published graph and launch state can be inspected.
- **FR-010**: Desktop and mobile layouts MUST keep checklist, evidence, publish, runtime links, graph, and editor controls readable without overlap.
- **FR-011**: QA artifacts MUST document the full browser path and keep API calls secondary.
- **FR-012**: The implementation MUST include frontend tests, backend route/contract smoke validation where applicable, Playwright desktop/mobile journeys, generated contract checks, redaction checks, and multi-agent curl regression.

### Key Entities

- **Workflow Setup Step**: A derived UI step that maps document and backend readiness state to `complete`, `active`, or `blocked`.
- **Three-Agent Starter Document**: A workflow document transformation that adds roles, prompt/profile references, contracts, graph nodes, edges, and a join policy through visible setup controls.
- **Runtime Launch Handoff**: A tenant-scoped Admin link to the user run workspace with a safe workflow id query parameter.
- **Design Review Handoff**: A tenant-scoped Admin link to the Design Reviews workspace with a requested published workflow bundle id query parameter.
- **Published Graph Evidence**: Backend graph projection for the published workflow version, shown with visual and keyboard-readable summaries.

## Success Criteria

- **SC-001**: A QA reviewer can create a custom workflow from a clean tenant and reach a three-agent editable workflow without raw JSON editing.
- **SC-002**: The checklist correctly moves from active to complete states as document sections, evidence, validation, publish, and runtime handoff become available.
- **SC-003**: Publish readiness stays backend-owned and rejects missing/stale/failed evidence.
- **SC-004**: Runtime launch preselects the custom workflow id when opened from setup.
- **SC-005**: Design Reviews can select the custom published workflow when it is authorized.
- **SC-006**: Desktop and mobile Playwright screenshots show the guided setup, evidence, publish, launch links, and graph evidence without text overlap.
- **SC-007**: No raw prompts outside authorized editors, completions, transcripts, credentials, secrets, provider payloads, local paths, stack traces, memory contents, or unauthorized labels appear in UI, screenshots, docs, logs, or QA artifacts.

## Assumptions

- Specs 069 through 072 provide durable workflow document save, role/graph editors, prompt/profile binding, evidence setup, validation, and publish gate behavior.
- Local QA can use deterministic `mock_model` Test Bench execution without external providers or connectors.
- The retained user run workspace accepts a workflow id string and the Design Reviews workspace uses published workflow bundle ids.
- No new backend route family is required; this spec coordinates existing contracts and handoff links.

## Constitution Impact

- **Durable By Default**: Setup state is derived from durable drafts, validation, evidence, and published bundles.
- **Contract-First Agent Coordination**: The starter creates explicit contracts, roles, edges, and joins.
- **Security With Practical Development Ergonomics**: Local-principal QA proves the path without Auth0 or live provider dependencies.
- **Operability Is A Product Requirement**: Progress, blockers, and launch paths are visible and recoverable.
- **Tenant Isolation And Secret Hygiene**: Links preserve tenant scope and expose only safe identifiers.

## Testing Instructions

- Add frontend unit coverage for checklist state, three-agent starter generation, runtime query prefill, Design Review query selection, and WorkflowBuilder integration.
- Run focused workflow builder, user run, and Design Review tests.
- Run generated TypeScript freshness, frontend typecheck, frontend test suite, frontend build, backend route/contract smoke tests, Ruff, mypy, QA docs validation, Spec QA, Playwright desktop/mobile flows, and multi-agent curl regression.
- Validate screenshots for no raw prompts, completions, secrets, transcripts, local paths, stack traces, or unauthorized labels.

## Documentation Impact

- Add QA073 guide, QA073 UI walkthrough, QA073 user guide, QA environment, PR notes, and quickstart updates.
- Keep browser steps primary and API/curl checks secondary.

## PR Review Guidance

- Review checklist state for truthful progress and backend-owned readiness boundaries.
- Confirm the starter remains a visible editable document transformation, not hidden mock data.
- Confirm launch handoffs use authorized UI links and do not expose unsafe payloads.
