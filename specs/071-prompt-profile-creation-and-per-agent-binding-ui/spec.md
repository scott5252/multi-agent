# Feature Specification: Prompt Profile Creation And Per-Agent Binding UI

**Feature Branch**: `codex/071-prompt-profile-creation-and-per-agent-binding-ui`  
**Created**: 2026-05-09  
**Status**: Draft  
**Input**: User description: "Prompt Profile Creation And Per-Agent Binding UI. Users who create custom workflows need to configure each agent's prompt and runtime profile from the browser. The UI must let authorized admins create or select prompt lineages, edit prompt template content with variables and fixture sets, validate and publish prompts, create or select runtime profiles, bind prompt versions and model routing hints to profiles, validate and activate profiles, and attach profile/prompt references to workflow roles. The feature must work from a clean tenant and must also allow reuse of existing platform or tenant prompt/profile records when authorized. Raw prompt content must be editable only inside authorized edit forms and must not leak into summaries, previews, screenshots, audit summaries, or other safe display surfaces."

## Clarifications

### Session 2026-05-09

- Q: Should Spec 071 create new prompt/profile route families or build on existing prompt runtime contracts? -> A: Prefer existing prompt/runtime profile services and generated React contracts; add workflow-setup-specific adapters only where needed to bind prompt/profile references to workflow roles through the Spec 069 full-document save contract. (autopilot)
- Q: How should raw prompt template content be handled in the workflow setup UI and QA evidence? -> A: Raw prompt text may be entered and edited only inside authorized prompt edit controls; all summaries, graph panels, binding matrices, JSON inspectors, screenshots, audit summaries, logs, docs, and exports must use redacted safe references or omit the raw text. (autopilot)
- Q: What provider/model behavior is allowed for clean-tenant QA? -> A: Use deterministic local-principal QA data, fake secret references, and mocked/local provider readiness summaries; do not call real providers, credentials, connectors, models, or external services. (autopilot)
- Q: What exactly is persisted on workflow roles? -> A: Workflow role documents store immutable prompt version and runtime profile version references plus safe display/readiness metadata only; raw prompt templates, provider payloads, credentials, and preview outputs remain in their owning backend domains. (autopilot)
- Q: How should reuse of existing platform or tenant prompt/profile records work? -> A: Reuse is through backend-authorized safe catalogs that expose only eligible records for the active tenant/principal and preserve backend validation for stale, inactive, retired, cross-tenant, or unauthorized references. (autopilot)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create And Publish Agent Prompts (Priority: P1)

An authorized admin configuring a workflow role can create a new prompt lineage, edit its template in an authorized form, define variables and fixture sets, run backend validation, publish an immutable prompt version, or select an already authorized tenant/platform prompt version.

**Why this priority**: Workflow roles cannot be launched safely until every agent has a validated prompt version reference. Prompt creation and selection are the first required per-agent binding step for a clean tenant.

**Independent Test**: From a workflow draft with at least three roles, create or select a prompt for one role through visible controls, edit variables and fixtures, validate, publish, save the workflow draft, reload, and verify the role retains only safe prompt reference metadata outside the authorized edit form.

**Acceptance Scenarios**:

1. **Given** a clean tenant workflow role with no prompt reference, **When** the admin creates a prompt lineage, fills safe metadata, edits template content in the prompt editor, adds variables and fixtures, validates, and publishes, **Then** the role can bind the published prompt version and the workflow save persists that reference.
2. **Given** an authorized existing prompt version, **When** the admin selects it for a workflow role, **Then** the UI shows safe lineage/version metadata and does not expose raw prompt template content in summaries, graph previews, screenshots, audit summaries, or JSON inspectors.
3. **Given** invalid prompt variables, unsafe template content, stale revision data, or missing fixture coverage, **When** the admin validates or publishes, **Then** backend-owned findings point to the prompt editor fields that need correction without leaking protected text.

---

### User Story 2 - Create And Activate Runtime Profiles (Priority: P2)

An authorized admin can create or select an agent runtime profile, bind a published prompt version and model routing hints, validate readiness, activate an immutable profile version, and attach that profile version to a workflow role.

**Why this priority**: A prompt alone does not fully configure an agent. Runtime profile activation supplies execution constraints, model routing, tool policy references, and version-pinned runtime metadata needed by later publish and runtime launch flows.

**Independent Test**: Starting from a role with a published prompt version, create a runtime profile through visible controls, bind the prompt version and safe routing hints, validate, activate, save the workflow draft, reload, and verify the role references the activated profile version.

**Acceptance Scenarios**:

1. **Given** a role with a published prompt version, **When** the admin creates a runtime profile and binds that prompt version plus safe model routing hints, **Then** validation confirms the profile can be activated or returns field-level blockers.
2. **Given** an authorized active profile version, **When** the admin selects it for a role, **Then** the workflow role stores the profile reference without copying raw prompt content, provider credentials, provider payloads, or private model responses.
3. **Given** a provider, routing, credential, tool, or policy readiness issue, **When** the admin validates or activates the profile, **Then** the UI displays redacted readiness summaries and keeps publish readiness backend-owned.

---

### User Story 3 - Manage Per-Agent Bindings Across The Workflow (Priority: P3)

An authorized admin can see all workflow roles and their prompt/profile binding readiness, apply safe reuse from authorized platform or tenant records, detect missing or stale bindings, and save binding references through the workflow document contract.

**Why this priority**: Custom workflows commonly have multiple agents. Users need a scannable setup surface to identify which roles are ready, which need prompt/profile work, and which references are stale before validation and publish.

**Independent Test**: Bind distinct prompts and profiles to at least three workflow roles, intentionally leave one role incomplete, save, validate, reload, and verify the binding matrix, role editor, graph summary, and validation panel all report the same safe readiness state.

**Acceptance Scenarios**:

1. **Given** a workflow with three roles, **When** the admin opens the binding workspace, **Then** each role row shows prompt status, profile status, validation status, and safe action controls.
2. **Given** a prompt or profile reference that is stale, unauthorized, retired, inactive, or cross-tenant, **When** the workflow is validated or saved, **Then** backend-owned findings identify the affected role and reference type without exposing unauthorized tenant labels or raw payloads.
3. **Given** a saved workflow draft with role bindings, **When** the admin reloads the browser, **Then** every role binding is restored from durable workflow draft state with revision, lineage, version, and activation metadata sufficient for later publish-readiness checks.

### Edge Cases

- Clean tenants with no prompts or profiles must show truthful empty states and creation actions, not fake prompt/profile records.
- Existing platform or tenant prompt/profile records must appear only when authorized for the active tenant and principal.
- Raw prompt template content may appear only inside authorized edit forms and safe validation request payloads; it must not appear in summaries, previews, screenshots, exports, audit summaries, graph panels, JSON inspectors, logs, or docs.
- Prompt fixture values and preview outputs must be redacted or summarized when displayed outside the authorized editor.
- Stale prompt drafts, prompt publish attempts, profile drafts, profile activations, and workflow saves must fail without overwriting newer versions.
- Retired prompt versions, inactive profile versions, missing model routing, missing credential readiness, and withdrawn tool policies must block activation or publish readiness through backend-owned findings.
- Exact retry of an idempotent prompt/profile mutation must not create duplicate lineages, versions, activations, or workflow revisions.
- Cross-tenant prompt/profile selection, unauthorized platform records, and unsupported role references must be denied without leaking labels or raw identifiers beyond safe opaque references.
- Browser-only validation may provide hints, but save, validation, publish readiness, prompt publishing, profile activation, and workflow binding decisions must remain backend-owned.
- Long prompt names, role names, variable names, and profile labels must not overlap controls on desktop or mobile screens.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide browser controls inside the workflow setup experience for creating a new prompt lineage for a selected workflow role.
- **FR-002**: The system MUST provide browser controls for selecting authorized existing tenant or platform prompt versions for a workflow role.
- **FR-003**: The system MUST allow authorized admins to edit prompt template content, prompt variables, fixture sets, safe metadata, and validation notes only inside authorized prompt edit forms.
- **FR-004**: The system MUST validate prompt drafts through backend-owned prompt validation contracts and display section-specific findings without exposing protected prompt content outside the edit form.
- **FR-005**: The system MUST publish validated prompt drafts as immutable prompt versions and expose only safe lineage/version summaries to workflow role binding surfaces.
- **FR-006**: The system MUST provide browser controls for creating a new runtime profile for a selected workflow role.
- **FR-007**: The system MUST provide browser controls for selecting authorized existing active tenant or platform runtime profile versions for a workflow role.
- **FR-008**: The system MUST allow authorized admins to bind prompt versions, model routing hints, runtime settings, safe tool policy references, and credential readiness expectations to runtime profiles.
- **FR-009**: The system MUST validate runtime profile drafts and activation readiness through backend-owned profile validation contracts.
- **FR-010**: The system MUST activate validated runtime profiles as immutable profile versions and expose only safe activation summaries to workflow role binding surfaces.
- **FR-011**: The system MUST attach prompt and profile references to workflow roles through the backend-owned workflow document save contract with revision tokens and idempotency keys.
- **FR-012**: The system MUST reload saved prompt/profile role bindings from durable workflow draft state and preserve stable role keys, lineage ids, version ids, activation status, and safe labels.
- **FR-013**: The system MUST render a per-agent binding matrix showing prompt, profile, validation, activation, and save readiness for every workflow role.
- **FR-014**: The system MUST surface backend-owned workflow validation findings for missing, stale, retired, inactive, unauthorized, or cross-tenant prompt/profile references beside the relevant role and binding controls.
- **FR-015**: The system MUST preserve stale conflict recovery and idempotent replay behavior for prompt creation, prompt publishing, profile creation, profile activation, and workflow save actions.
- **FR-016**: The system MUST enforce tenant, platform, and role authorization for every prompt/profile lookup, create, validate, publish, activate, bind, and save action.
- **FR-017**: The system MUST prevent raw secrets, credentials, provider authorization headers, provider payloads, raw prompts outside authorized edit forms, raw completions, memory contents, private messages, raw tool payloads, raw test transcripts, local filesystem paths, stack traces, and unauthorized tenant labels from appearing in UI, redirects, exports, screenshots, logs, docs, or audit summaries.
- **FR-018**: The system MUST keep workflow publish readiness, prompt publish readiness, profile activation readiness, provider readiness, and credential readiness backend-owned.
- **FR-019**: The system MUST provide truthful empty, loading, dirty, saving, validating, publishing, activating, stale, conflict, blocked, denied, and error states for prompt/profile binding.
- **FR-020**: The system MUST include browser-first QA and Playwright coverage for creating or selecting prompt/profile records and binding them to at least three workflow roles through visible controls.
- **FR-021**: The system MUST update curl regression coverage if any prompt/profile or workflow setup API route family is added or behaviorally changed.

### Key Entities *(include if feature involves data)*

- **Prompt Lineage Selection**: An authorized prompt family that can be newly created or reused for a workflow role.
- **Prompt Draft Editor State**: Safe editable prompt metadata, template content, variable definitions, fixture sets, validation findings, revision token, and dirty state held only inside the authorized edit form.
- **Prompt Version Binding Reference**: Immutable prompt version metadata attached to a workflow role, including lineage id, version id, safe label, status, scope, and freshness evidence.
- **Runtime Profile Draft Editor State**: Safe editable runtime profile metadata, prompt version binding, model routing hints, tool policy references, credential readiness expectations, validation findings, revision token, and dirty state.
- **Runtime Profile Version Binding Reference**: Immutable active profile version metadata attached to a workflow role, including profile id, version id, safe label, status, scope, and activation evidence.
- **Per-Agent Binding Row**: A workflow role plus its prompt/profile references, readiness statuses, validation blockers, and action controls.
- **Binding Readiness Finding**: Backend-owned role-specific finding for missing, stale, inactive, unauthorized, retired, invalid, or unsafe prompt/profile state.
- **Safe Prompt/Profile Catalog Item**: Redacted prompt or profile summary made available to the active tenant without raw prompt text, provider payloads, credentials, or unauthorized tenant labels.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reviewer can start from a clean tenant workflow draft, create prompts for at least three roles, publish prompt versions, bind them to the roles, save, reload, and see safe prompt references preserved.
- **SC-002**: A reviewer can create runtime profiles for at least three roles, bind published prompt versions and safe routing hints, activate profile versions, save, reload, and see safe profile references preserved.
- **SC-003**: The per-agent binding matrix shows complete, incomplete, stale, denied, and blocked states consistently with workflow validation findings after save and reload.
- **SC-004**: Raw prompt content is visible only in authorized edit forms and is absent from prompt/profile summaries, graph previews, screenshots, JSON inspectors, audit summaries, exports, logs, and QA docs.
- **SC-005**: Stale conflict, idempotent replay, same-key different-payload conflict, invalid prompt, invalid profile, unauthorized catalog selection, and cross-tenant role binding flows all return safe backend-owned findings.
- **SC-006**: Desktop and mobile Playwright screenshots show nonblank prompt/profile binding controls, stable layout, no text overlap, and visible reload persistence for at least three role bindings.
- **SC-007**: Frontend typecheck, workflow/governance tests, generated contract freshness, backend focused tests, QA docs, Playwright, run_spec_qa, and multi-agent curl regression all pass before Spec 072 begins.

## Assumptions

- Spec 069 provides the backend-owned full workflow document save contract used to persist role prompt/profile references.
- Spec 070 provides workflow role, graph, contract, and join editors that this feature can extend with prompt/profile binding controls.
- Existing prompt runtime and profile services remain the source of truth for prompt validation/publish and profile validation/activation.
- Existing governance APIs may be extended or wrapped for workflow setup, but browser controls must consume generated backend-owned JSON contracts.
- Prompt/profile creation in this spec may use deterministic local provider/model readiness summaries in QA and must not call real providers or external tools.
- Required test evidence setup remains Spec 072; this spec can show publish blockers related to missing evidence but does not need to create evidence suites.

## Constitution Impact

- **Durable By Default**: Prompt/profile lineages, versions, activations, and role binding references are persisted through durable backend services and workflow draft revisions.
- **Immutable State And Memory**: Published prompts and activated profiles are immutable versioned references; browser drafts are not execution truth.
- **Contract-First Agent Coordination**: Agent roles bind explicit prompt and runtime profile contracts that later validation, publish, and runtime launch can pin.
- **Security With Practical Development Ergonomics**: Auth0-shaped authorization and local-principal QA both remain required for protected prompt/profile actions.
- **Operability Is A Product Requirement**: Readiness, validation, stale conflict, and activation errors must be visible, actionable, and redaction-safe.
- **Tenant Isolation And Fair Scheduling**: Tenant/platform grants control prompt/profile catalog visibility and binding eligibility.
- **Secret Hygiene And Controlled Tool Access**: Raw prompt, provider, credential, tool, channel, runtime, and local path data must not leak through binding surfaces.
- **Version-Pinned Execution**: Workflow roles store immutable prompt/profile version references suitable for later publish and runtime pinning.

## Testing Instructions

- Add focused backend/contract tests for prompt catalog lookup, prompt create/edit/validate/publish, profile create/edit/validate/activate, role binding save, stale conflicts, idempotency, unsafe content redaction, inactive/retired references, and cross-tenant denial.
- Add frontend tests for prompt creation, prompt selection, variable/fixture editing, profile creation, prompt-to-profile binding, model routing hints, role binding matrix, save/reload behavior, validation rendering, and redaction boundaries.
- Add Playwright desktop and mobile journeys that create or select prompt/profile records and bind them to at least three workflow roles through visible controls.
- Add screenshot evidence proving raw prompt content is not displayed in summaries, graph panels, JSON inspectors, or QA screenshots outside the authorized edit form.
- Update `curl_testing.md` for any new or changed prompt/profile or workflow setup route family.

## Documentation Impact

- Add Spec 071 QA guide, UI walkthrough, manual user guide, and PR notes.
- Document the browser path for creating prompts, publishing prompt versions, creating profiles, activating profile versions, and binding safe references to workflow roles.
- Keep API calls as validation aids only; user setup guidance must use visible Admin navigation and controls after login.

## PR Review Guidance

- Verify that raw prompt content is contained to authorized edit forms and never appears in safe summaries, screenshots, logs, audit summaries, exports, or JSON inspectors.
- Review tenant/platform authorization, profile readiness, provider/credential redaction, idempotency, stale conflict handling, generated contracts, Playwright evidence, and curl coverage.
- Confirm the UI does not synthesize fake workflows, prompts, profiles, evidence, runs, or provider readiness in production states.
