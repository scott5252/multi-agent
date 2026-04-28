# Feature Specification: Prompt Library And Agent Runtime Profiles

**Feature Branch**: `012-prompt-runtime-profiles`  
**Created**: 2026-04-28  
**Status**: Draft  
**Input**: User description: "Add a prompt library and agent runtime profile management for the multi-agent platform. Platform and tenant admins must be able to create prompt lineages, draft prompt versions, validate template variables, publish immutable prompt versions, preview safe prompt rendering with fixture values, and retire prompt versions from new use without breaking historical runs. Admins must also be able to create agent runtime profiles that bind an agent key or sub-agent key to purpose, prompt version references, model routing scope hints, memory scope policy, skill installation requirements, tool policy expectations, output contract expectations, and test-suite requirements. The feature must integrate with existing workflow registry validation and model-skill routing prompt references. Raw secret values, credential values, and unauthorized run content must never be embedded in prompt previews or audit records. Require platform and tenant scope rules, immutable versions, at least 90 percent coverage, docs, PR notes, testing instructions, and README updates. Ensure the UI is updated to allow users to use a browser to accomplish this feature."

## Clarifications

### Session 2026-04-28

- Q: Which prompt template syntax and variable rule should the platform formally validate? → A: Use `{{variable_name}}` placeholders only; variable names must match `[A-Za-z_][A-Za-z0-9_]*`; no expressions, filters, loops, or conditionals.
- Q: When a tenant workflow references an agent key or sub-agent key and both a platform-scoped active runtime profile and a tenant-scoped active runtime profile match that key, which profile should resolve for new use? → A: Tenant active profile wins over platform active profile for the same key within that tenant; platform remains the fallback when no tenant profile exists.
- Q: How should platform-scoped prompt versions and runtime profile versions become available for tenant use? → A: Platform admins grant specific published prompt versions and active runtime profile versions to an explicit tenant allowlist.
- Q: Should prompt fixture values used for preview be persisted with drafts, or treated as one-time preview input? → A: Persist sanitized, non-sensitive fixture value sets with drafts; reject unsafe values before storage or preview.
- Q: When should prompt version references and runtime profile versions be pinned for a new workflow run? → A: Pin all workflow-declared agent/profile/prompt references at run acceptance; use first-use pinning only for dynamically selected agents or sub-agents not declared upfront.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Author And Publish Prompt Versions (Priority: P1)

As a platform or tenant admin, I need to create prompt lineages, maintain editable draft versions, validate template variables, preview safe rendering with fixture values, and publish immutable prompt versions so that workflows and agents can reference approved prompts without relying on ad hoc text.

**Why this priority**: Prompt authoring and immutable publication are the foundation for reliable model-backed execution. Without them, agent profiles and workflow validation cannot safely point to prompt references.

**Independent Test**: An authorized admin can create a prompt lineage, save a draft, define required template variables, validate the draft, preview a redacted fixture rendering in the browser UI, publish the prompt as an immutable version, and verify the published version cannot be edited in place.

**Acceptance Scenarios**:

1. **Given** an authorized admin starts a new prompt lineage, **When** they add prompt metadata, content, required variables, fixture values, and scope, **Then** the system saves an editable draft that remains separate from any published version.
2. **Given** a prompt draft contains required template variables, **When** the admin runs validation, **Then** the system reports missing, unused, duplicate, or malformed variables and blocks publication until required issues are resolved.
3. **Given** a prompt draft has valid fixture values, **When** the admin previews the prompt in the browser UI, **Then** the system renders a safe preview that uses fixture values only and excludes raw secrets, credential values, and unauthorized run content.
4. **Given** a prompt draft has passed validation, **When** an authorized admin publishes it, **Then** the system creates an immutable prompt version with lineage, author, scope, validation evidence, and publication metadata.

---

### User Story 2 - Manage Prompt Lifecycle Without Breaking Runs (Priority: P2)

As an admin or operator, I need to retire prompt versions from new use while preserving historical and in-flight run references so that unsafe or obsolete prompts stop being selected without corrupting auditability or replay.

**Why this priority**: Prompt versions are part of runtime provenance. Retirement must protect future selection while preserving the meaning of existing runs and published workflows.

**Independent Test**: An authorized admin can retire a published prompt version, confirm it no longer appears as selectable for new prompt references, and confirm existing workflows, runtime profiles, and historical runs that already pinned it remain reviewable.

**Acceptance Scenarios**:

1. **Given** a published prompt version is active for new use, **When** an authorized admin retires it with a reason, **Then** the prompt version is no longer selectable for new references but remains visible to authorized users reviewing historical references.
2. **Given** a workflow run already pinned a prompt version, **When** that prompt version is later retired, **Then** the run continues to identify and review the original prompt version according to authorization rules.
3. **Given** a published workflow or runtime profile references a retired prompt version, **When** an admin validates it for a new publication or activation, **Then** the system reports a blocking issue unless the reference is allowed only for historical review.

---

### User Story 3 - Configure Agent Runtime Profiles (Priority: P3)

As a platform or tenant admin, I need to create agent runtime profiles for agent keys and sub-agent keys so that each agent has an explicit purpose, prompt references, model routing scope hints, memory policy, skill requirements, tool policy expectations, output contracts, and test-suite requirements before it can be used.

**Why this priority**: Runtime profiles turn reusable prompts and model-skill routing into a coherent agent contract. They make agent behavior reviewable before workflows depend on it.

**Independent Test**: An authorized admin can create a runtime profile for an agent key, attach valid prompt version references and policy expectations, validate the profile, activate it for new use, and see workflow registry validation accept or reject workflows based on the profile.

**Acceptance Scenarios**:

1. **Given** an authorized admin creates an agent runtime profile, **When** they define the agent key, purpose, prompt version references, model routing scope hints, memory scope policy, skill installation requirements, tool policy expectations, output contract expectations, and test-suite requirements, **Then** the system saves the profile as a draft within the admin's authorized scope.
2. **Given** a runtime profile references prompt versions or policy expectations that are missing, retired, unauthorized, or incompatible, **When** validation runs, **Then** the system identifies blocking issues and prevents activation for new use.
3. **Given** a runtime profile passes validation, **When** an authorized admin activates it, **Then** future workflow validation and model-skill routing can resolve the profile while prior profile versions remain unchanged.
4. **Given** a workflow uses an agent key or sub-agent key, **When** workflow registry validation runs, **Then** it verifies the key has an active compatible runtime profile and reports clear blocking issues when it does not.

---

### User Story 4 - Use A Browser-Based Admin Experience (Priority: P4)

As a platform or tenant admin, I need browser-accessible admin screens for prompt library and runtime profile work so that I can complete authoring, validation, preview, publication, retirement, activation, and history review without editing raw records or relying on command-line access.

**Why this priority**: The feature must be usable by administrators through the product UI, not only by backend maintainers. Browser flows also make review and acceptance testing concrete.

**Independent Test**: An authorized admin can complete the primary prompt library and runtime profile workflows in a browser, including list, create, edit draft, validate, preview, publish, retire, activate, inspect history, and review validation messages.

**Acceptance Scenarios**:

1. **Given** an authorized admin opens the prompt library in a browser, **When** they search, filter, create, edit, validate, preview, publish, or retire prompt versions, **Then** each action is available with scope-aware controls and clear success or failure states.
2. **Given** an authorized admin opens runtime profile management in a browser, **When** they create, validate, activate, retire, or review a profile, **Then** the UI shows profile state, prompt references, policy expectations, test requirements, history, and blocking validation results.
3. **Given** a user lacks permission for a scope, **When** they use the browser UI, **Then** restricted actions and records are hidden or denied without exposing protected prompt content, run content, secrets, or credential values.

---

### User Story 5 - Audit, Review, And Delivery Evidence (Priority: P5)

As an auditor, maintainer, or reviewer, I need safe history, audit evidence, documentation, PR notes, testing instructions, and coverage evidence so that I can verify prompt and runtime profile governance before approving the feature.

**Why this priority**: Governance evidence is essential for production readiness, but it depends on the core prompt and profile workflows existing first.

**Independent Test**: A reviewer can inspect safe audit records and history for prompt and profile changes, confirm unauthorized content is excluded, and follow the documented acceptance tests and PR notes to verify the delivered feature.

**Acceptance Scenarios**:

1. **Given** a prompt or runtime profile changes state, **When** an auditor reviews its history, **Then** they can see actor, timestamp, reason, scope, prior version, new version, and safe summary details.
2. **Given** a preview, validation, publication, retirement, or activation attempt is denied, **When** the audit record is reviewed, **Then** it explains the safe denial category without revealing raw secrets, credential values, or unauthorized run content.
3. **Given** the feature is submitted for review, **When** a maintainer evaluates it, **Then** coverage evidence, docs, PR notes, testing instructions, README updates, and browser-flow verification are present and complete.

### Edge Cases

- A prompt draft uses a template variable that is not declared, declares a variable that is never used, duplicates a variable name, or uses an invalid variable name.
- A fixture value attempts to include a raw secret, credential value, protected run content, or content from a tenant the admin cannot access.
- A prompt preview is requested without all required fixture values.
- Two admins edit the same prompt draft or runtime profile draft from different revisions.
- An admin attempts to publish a prompt draft that has changed since its last successful validation.
- An admin attempts to edit the content of an already published immutable prompt version.
- A prompt version is retired while a run is queued, running, waiting for input, or under historical review.
- A workflow, model-skill routing entry, or runtime profile references a missing, retired, unauthorized, or wrong-scope prompt version.
- A tenant admin attempts to reference a platform-scoped prompt version or runtime profile version that has not been explicitly granted to that tenant.
- A platform admin changes platform-scoped defaults that tenant-scoped workflows depend on for future validation.
- A runtime profile omits a required prompt reference, model routing hint, memory policy, skill requirement, tool policy expectation, output contract, or test-suite requirement.
- A runtime profile binds the same agent key or sub-agent key to conflicting active profiles within the same scope.
- Workflow registry validation runs while prompt or profile drafts are unpublished.
- A user attempts to inspect prompt content, preview output, profile details, run content, or audit history outside their authorized scope.
- Delivery materials omit browser UI verification, coverage evidence, docs, PR notes, testing instructions, or README updates.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The platform MUST allow authorized platform admins to create and manage platform-scoped prompt lineages and authorized tenant admins to create and manage tenant-scoped prompt lineages within their tenant.
- **FR-002**: Prompt lineages MUST preserve lineage identity, owning scope, name, purpose, status, author metadata, timestamps, and relationships between draft and published versions.
- **FR-003**: Authorized admins MUST be able to create editable prompt draft versions from a new lineage, from a prior draft, or from a published prompt version without modifying the source version.
- **FR-004**: Prompt drafts MUST support prompt content, purpose, usage notes, required template variable declarations, sanitized non-sensitive fixture value sets for repeatable preview, validation state, draft revision, and scope.
- **FR-005**: Prompt draft saves MUST protect concurrent edits by rejecting stale revisions rather than overwriting newer committed draft state.
- **FR-006**: The platform MUST validate prompt template variables before publication, including required declarations, variable usage, duplicate names, malformed names, missing fixture values for preview, and variable references that are not allowed for the admin's scope. Prompt content MUST use `{{variable_name}}` placeholders only, variable names MUST match `[A-Za-z_][A-Za-z0-9_]*`, and expressions, filters, loops, conditionals, or template code execution MUST be rejected.
- **FR-007**: Prompt validation results MUST distinguish blocking issues from advisory findings and identify the prompt section, variable, or fixture field that requires attention.
- **FR-008**: Authorized admins MUST be able to preview prompt rendering with explicit fixture values before publication, using sanitized fixture value sets persisted with the draft for repeatable browser preview.
- **FR-009**: Prompt previews MUST use fixture values only and MUST NOT embed raw secret values, credential values, unauthorized run content, or protected content from another tenant or scope. Unsafe fixture values MUST be rejected before storage or preview.
- **FR-010**: Prompt preview and validation audit records MUST contain safe summaries only and MUST NOT store raw rendered prompt text when that text includes protected content or values outside the viewer's authorization.
- **FR-011**: The platform MUST prevent prompt publication when blocking validation issues remain or when the draft has changed since the last successful publication-ready validation.
- **FR-012**: Publishing a prompt draft MUST create a new immutable prompt version that records lineage, version identity, content snapshot, template variable declarations, scope, author, timestamp, validation evidence, and publication reason.
- **FR-013**: Published prompt versions MUST be immutable; changing prompt content, variables, scope, or purpose after publication MUST require a new draft and a new published version.
- **FR-014**: Authorized admins MUST be able to retire a published prompt version from new use by recording actor, timestamp, reason, scope, and retirement status without changing the immutable published content.
- **FR-015**: Retired prompt versions MUST remain available for authorized historical run review, published workflow review, profile history, and provenance review while being blocked from new prompt references unless a historical-only exception applies.
- **FR-016**: Prompt selection controls MUST show only prompt versions that are active, authorized for the user's scope, and compatible with the target workflow, agent, sub-agent, or runtime profile use. Platform-scoped prompt versions MUST be selectable for tenant use only when a platform admin has granted that specific published version to the tenant allowlist.
- **FR-017**: The platform MUST integrate prompt version references with existing model-skill routing behavior so prompt references can be resolved, validated, pinned for execution, and reviewed consistently with model routing provenance.
- **FR-018**: The platform MUST integrate prompt and runtime profile checks with workflow registry validation so drafts and publications report blocking issues for missing, retired, unauthorized, incompatible, or wrong-scope prompt and profile references.
- **FR-019**: The platform MUST allow authorized platform admins and tenant admins to create draft agent runtime profiles within their permitted platform or tenant scope.
- **FR-020**: Each runtime profile MUST bind exactly one agent key or sub-agent key within a scope to a purpose, prompt version references, model routing scope hints, memory scope policy, skill installation requirements, tool policy expectations, output contract expectations, and test-suite requirements.
- **FR-021**: Runtime profile draft saves MUST protect concurrent edits by rejecting stale revisions rather than overwriting newer committed profile draft state.
- **FR-022**: Runtime profile validation MUST verify that referenced prompt versions exist, are active for new use when required, are authorized for the profile scope, and satisfy the profile's declared prompt purposes.
- **FR-023**: Runtime profile validation MUST verify that model routing scope hints are compatible with existing model-skill routing rules and do not claim a model or prompt reference outside the profile's authorized scope.
- **FR-024**: Runtime profile validation MUST verify that the memory scope policy, skill installation requirements, tool policy expectations, output contract expectations, and test-suite requirements are present, internally consistent, and compatible with workflow registry requirements.
- **FR-025**: The platform MUST prevent activation of runtime profiles with unresolved blocking validation issues or stale validation evidence.
- **FR-026**: Activating a runtime profile MUST create an immutable active profile version for new use that records profile identity, agent key or sub-agent key, scope, purpose, prompt references, model routing hints, memory policy, skill requirements, tool policy expectations, output contract expectations, test-suite requirements, author, timestamp, validation evidence, and activation reason.
- **FR-027**: Active runtime profile versions MUST be immutable; changing any profile contract field MUST require a new draft and a new active profile version.
- **FR-028**: Authorized admins MUST be able to retire a runtime profile version from new use without changing historical runs, published workflows, or profile history that already reference it.
- **FR-029**: The platform MUST prevent conflicting active runtime profiles for the same agent key or sub-agent key within the same scope unless an explicit precedence rule already authorizes one profile for that context. For tenant workflow resolution, an active tenant-scoped runtime profile for the matching key MUST take precedence over an authorized active platform-scoped profile, and the platform-scoped profile MUST serve as fallback only when no tenant-scoped profile exists.
- **FR-030**: Workflow validation MUST require every referenced agent key and sub-agent key that needs runtime execution to resolve to an active compatible runtime profile for the workflow's scope using tenant-over-platform precedence.
- **FR-031**: Runtime run acceptance and provenance MUST record the prompt version references and runtime profile versions that govern the run or first-use decision without rewriting prior or historical runs when new versions are published later. All workflow-declared agent, profile, and prompt references MUST be pinned at run acceptance; first-use pinning is allowed only for dynamically selected agents or sub-agents that were not declared upfront.
- **FR-032**: Prompt and runtime profile administration MUST enforce platform and tenant scope boundaries for viewing, drafting, validating, previewing, publishing, retiring, activating, selecting, and auditing records.
- **FR-033**: Tenant admins MUST NOT be able to view, preview, reference, publish, retire, activate, or audit platform-scoped or other-tenant prompt and profile records unless explicit authorization grants that access. Platform-scoped published prompt versions and active runtime profile versions become available for tenant use only through explicit per-version tenant allowlist grants created by platform admins; lineage-level, key-level, or default future-version inheritance MUST NOT grant tenant visibility.
- **FR-034**: The platform MUST provide browser-accessible admin UI flows for prompt lineage listing, prompt draft creation and editing, variable validation, safe fixture preview, prompt publication, prompt retirement, prompt history, runtime profile listing, profile draft creation and editing, profile validation, profile activation or retirement, and profile history review.
- **FR-035**: Browser UI controls MUST present clear scope, status, validation, history, and authorization states and MUST prevent users from completing actions that would be rejected for missing permission, stale revision, blocking validation, retired references, or unsafe preview content.
- **FR-036**: Administrative, validation, preview, routing, registry, and runtime audit records MUST use safe summaries and MUST NOT include raw secret values, credential values, unauthorized run content, or protected prompt rendering outside the viewer's authorization.
- **FR-037**: The delivered feature MUST include test evidence demonstrating at least 90 percent coverage for submitted prompt library, prompt validation, safe preview, lifecycle, runtime profile, workflow validation integration, model-skill prompt reference integration, authorization, audit, and browser UI behavior.
- **FR-038**: The delivered feature MUST include documentation, PR review notes, testing instructions, and README updates covering prompt lifecycle, variable validation, fixture previews, immutable versions, retirement semantics, runtime profile contracts, scope rules, workflow validation integration, model-skill routing prompt references, safe audit behavior, and browser UI usage.

### Key Entities

- **Prompt Lineage**: A named prompt family within a platform or tenant scope that groups editable drafts, immutable published versions, retirement history, and safe audit evidence.
- **Prompt Draft Version**: An editable prompt authoring record containing content, declared variables, fixture values, purpose, scope, validation state, and draft revision before publication.
- **Published Prompt Version**: An immutable prompt snapshot that can be referenced by workflows, runtime profiles, and model-skill routing decisions when active and authorized.
- **Prompt Template Variable**: A declared `{{variable_name}}` placeholder expected by a prompt draft or published version, including name, purpose, required status, allowed value category, and validation state. Variable names must match `[A-Za-z_][A-Za-z0-9_]*`; expressions, filters, loops, conditionals, and executable template code are not valid prompt variables.
- **Fixture Value Set**: Admin-provided sanitized non-sensitive sample values persisted with a prompt draft for repeatable safe preview without exposing raw secrets, credential values, unauthorized run content, or protected tenant content.
- **Prompt Preview**: A safe rendered representation of a prompt draft using fixture values, scoped to the viewer's authorization and excluded from unsafe audit payloads.
- **Prompt Lifecycle Status**: The availability state of a prompt version, such as draft, published for new use, retired from new use, or historical-only.
- **Agent Runtime Profile**: A governed agent or sub-agent contract that binds a key to purpose, prompt version references, model routing hints, memory policy, skill requirements, tool policy expectations, output contract expectations, and test-suite requirements.
- **Runtime Profile Draft**: An editable authoring version of an agent runtime profile that must pass validation before activation.
- **Runtime Profile Version**: An immutable profile snapshot activated for new use or retained for historical review.
- **Tenant Allowlist Grant**: A platform-admin authorization record that grants one specific platform-scoped published prompt version or active runtime profile version to one or more tenants for scoped viewing, selection, validation, and historical review.
- **Model Routing Scope Hint**: A profile-level declaration that helps model-skill routing resolve the intended model and prompt scope without overriding tenant authorization or routing precedence.
- **Memory Scope Policy**: The profile's expected memory access boundaries and persistence behavior for the associated agent or sub-agent.
- **Skill Installation Requirement**: A profile declaration identifying required skills and acceptable installation or availability state before the agent can run.
- **Tool Policy Expectation**: A profile declaration describing required tool permissions or constraints that must be satisfied by existing tool policy validation.
- **Output Contract Expectation**: A profile declaration describing the expected output shape, quality gates, or handoff obligations for the agent or sub-agent.
- **Test-Suite Requirement**: A profile declaration describing the tests that must pass before the profile is considered activation-ready or workflow-ready.
- **Safe Audit Record**: A durable, scope-aware summary of prompt or profile actions that preserves actor, time, reason, state changes, and validation outcomes without exposing protected values.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100 percent of published prompt versions are immutable and remain reviewable by authorized users after newer versions are published or the version is retired from new use.
- **SC-002**: Authorized admins can create, validate, preview, and publish a representative prompt version through the browser UI in under 7 minutes during acceptance testing.
- **SC-003**: 100 percent of prompt publication attempts with unresolved blocking variable validation issues are rejected with clear remediation messages.
- **SC-004**: 100 percent of prompt previews in acceptance tests exclude raw secret values, credential values, unauthorized run content, and protected cross-tenant content.
- **SC-005**: 100 percent of retired prompt versions are blocked from new prompt references while remaining available for authorized historical run, workflow, profile, and provenance review.
- **SC-006**: Authorized admins can create, validate, and activate a representative agent runtime profile through the browser UI in under 10 minutes during acceptance testing.
- **SC-007**: 100 percent of workflow registry validation runs that reference agent or sub-agent keys report clear pass or blocking-failure outcomes for runtime profile availability, scope, prompt references, and profile compatibility.
- **SC-008**: 100 percent of model-backed run provenance for newly accepted runs identifies the prompt version references and runtime profile versions that governed the run or first-use decision.
- **SC-009**: At least 90 percent of administrators and maintainers in acceptance testing can locate prompt history, profile history, validation results, and safe audit summaries in the browser UI without assistance.
- **SC-010**: Submitted feature behavior demonstrates at least 90 percent coverage, and reviewer materials include docs, PR notes, testing instructions, README updates, and browser UI verification.

## Testing, Review, And Documentation Impact

- **Testing Instructions**: Reviewer instructions must cover platform-scope and tenant-scope prompt creation, draft save, stale draft rejection, variable validation, safe fixture preview, publication immutability, retirement from new use, model-skill prompt reference resolution, workflow registry validation, runtime profile creation, profile activation, profile retirement, authorization failures, safe audit records, browser UI flows, and historical run preservation.
- **PR Review Guidance**: PR notes must call out immutable prompt and profile versions, scope rules, preview safety, redaction behavior, model-skill routing prompt reference integration, workflow registry validation integration, runtime provenance, browser UI coverage, known risks, and rollback or retirement behavior.
- **Documentation Impact**: The feature requires README and user-facing documentation updates explaining prompt lineages, draft and published versions, template variable validation, safe fixture previews, retirement semantics, runtime profile contracts, scope rules, workflow validation, model-skill prompt references, audit behavior, and browser UI usage.

## Constitution Impact

- **Durability**: Prompt versions, runtime profile versions, validation results, retirement actions, activation actions, and safe audit records must be durable before they become authoritative for selection or review.
- **Tenant Isolation And Fair Scheduling**: Prompt and profile visibility, authoring, preview, selection, validation, activation, retirement, run provenance, and audit review must enforce tenant-aware authorization and fail closed on cross-scope access.
- **Versioning**: Published prompt versions and active runtime profile versions must be immutable, and runs must preserve the prompt and profile versions pinned at acceptance or first use.
- **Secrets And Tool Access**: Prompt previews, validation results, profile records, logs, and audit summaries must never include raw secrets, credential values, or unauthorized run content.
- **Observability**: Prompt and profile lifecycle events must produce safe history and audit evidence sufficient for support, governance, and incident review.
- **Security**: Existing role and tenant authorization must govern all prompt library, runtime profile, browser UI, validation, preview, lifecycle, and audit actions.

## Assumptions

- Platform admins may create platform-scoped reusable prompt and profile assets, while tenant admins may create tenant-scoped assets only within their own tenant unless explicit per-version tenant allowlist grants authorize access to a specific platform-scoped published prompt version or active runtime profile version.
- Prompt previews are for design-time inspection with fixture values, not for executing live model calls or exposing live run payloads.
- Existing model-skill routing behavior remains the source of model routing precedence; runtime profiles provide scope hints and prompt references but do not bypass routing authorization. Tenant-scoped runtime profiles override authorized platform-scoped runtime profiles for the same key within that tenant, while platform-scoped profiles remain fallback defaults when no tenant profile exists.
- Existing workflow registry validation is the publication gate for workflow definitions and will consume prompt and runtime profile validation outcomes.
- Retiring a prompt or profile version affects future selection by default; historical runs and already pinned provenance continue to reference the original immutable versions. Workflow-declared agent, profile, and prompt references are pinned at run acceptance, while dynamically selected agents or sub-agents that were not declared upfront may be pinned at first use.
- Runtime profile retirement is the lifecycle action that removes an active profile version from new use while preserving historical references; "deactivate" may appear only as compatibility wording in existing APIs or UI copy and is not a separate lifecycle state.
- Test-suite requirements describe what must be satisfied for a profile to be activation-ready; detailed test execution mechanics are deferred to planning.
- Browser UI delivery is required for the primary admin workflows; alternate programmatic access may exist but is not sufficient by itself for acceptance.
