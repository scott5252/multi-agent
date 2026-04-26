# Feature Specification: Model Routing And Skill Configuration

**Feature Branch**: `007-model-skill-routing`  
**Created**: 2026-04-26  
**Status**: Draft  
**Input**: User description: "Add model routing and skill configuration to the platform. Administrators must be able to set a global default LLM and override it per workflow, per agent, or per step. Agents must also have explicit skill bindings and allowed tool policies. The system must record which model and prompt version were used for every run. Secret references, outbound domain policies, and tool-specific credential requirements must also be versioned and auditable. Require at least 90 percent unit-test coverage, PR review notes, testing instructions, and a README update."

## Clarifications

### Session 2026-04-26

- Q: What scope should the "global default LLM" use? → A: One active tenant-scoped default LLM per tenant.
- Q: When should model, prompt, skill, tool, domain, secret-reference, and credential policy versions be pinned for a run? → A: Pin run-level resolvable versions at acceptance, then pin step/tool-specific versions at first use.
- Q: How should multiple applicable skill, tool, outbound domain, secret-reference, or credential policies combine when more than one policy matches a request? → A: Cumulative intersection; every applicable active policy must allow the request.
- Q: How should prompt versions be resolved when a model-backed step has no step-specific prompt version? → A: Use step, agent, then workflow prompt references only; fail if none exists.
- Q: What delivery surface is required for administrators to configure and review model routing, skill bindings, tool policies, and provenance? → A: API endpoints plus minimal admin web views for configuration preview and history review.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Configure Model Defaults And Overrides (Priority: P1)

As a platform administrator, I need to set the default LLM and define more specific overrides for workflows, agents, and steps so that every run uses an intentional model choice with a clear resolution path.

**Why this priority**: Model routing is the foundation for predictable execution, cost control, and incident analysis. Without a deterministic default and override model, runs cannot be explained or reproduced.

**Independent Test**: Can be fully tested by setting a global default, adding workflow, agent, and step overrides through the API, previewing the resolved model for each scope through API endpoints and minimal admin web views, and confirming that a run uses the most specific applicable model.

**Acceptance Scenarios**:

1. **Given** no lower-level override exists, **When** a workflow run starts, **Then** the run uses the active tenant-scoped global default LLM and records that default as the source of the model decision.
2. **Given** a workflow override exists, **When** a run starts for that workflow, **Then** the workflow override takes precedence over the global default unless an agent or step override applies.
3. **Given** workflow, agent, and step overrides exist for the same execution path, **When** a step invokes model-backed behavior, **Then** the step override takes precedence, followed by agent override, workflow override, and global default.
4. **Given** an administrator changes a model routing configuration, **When** the change is saved, **Then** the prior configuration remains reviewable and the new configuration becomes a distinct version.

---

### User Story 2 - Bind Skills And Tool Policies To Agents (Priority: P2)

As a workflow designer or administrator, I need every agent to have explicit skill bindings and allowed tool policies so that agents can only use approved skills, tools, domains, and credentials for their role.

**Why this priority**: Controlled skills and tools are required for security, tenant isolation, and predictable agent behavior. Model routing without bounded tools would leave the runtime perimeter too broad.

**Independent Test**: Can be fully tested by creating an agent with approved skills, allowed tools, outbound domain permissions, and credential requirements through the API, reviewing policy state through minimal admin web views, then verifying allowed requests succeed and disallowed skill, tool, domain, or credential requests are blocked and audited.

**Acceptance Scenarios**:

1. **Given** an agent has no explicit binding for a skill, **When** the agent attempts to use that skill, **Then** the platform blocks the attempt and records the denied decision.
2. **Given** an agent has a skill binding and an allowed tool policy, **When** the agent uses an allowed tool within its policy, **Then** the platform permits the tool use and records the policy version that authorized it.
3. **Given** a tool request targets a domain outside the active outbound domain policy, **When** the request is evaluated, **Then** the platform denies the request before outbound access occurs and records the denial reason.
4. **Given** a tool requires credentials, **When** the active policy lacks the required credential reference or the reference is not valid for the request, **Then** the platform blocks the tool use without exposing secret values.

---

### User Story 3 - Run With Pinned Model, Prompt, And Policy Provenance (Priority: P3)

As an operator or workflow reviewer, I need each run to record the exact model, prompt version, skill binding version, tool policy version, secret reference version, and outbound policy version used so that I can reproduce and audit what happened later.

**Why this priority**: Runtime provenance turns configuration into explainable execution. It is essential for replay, debugging, customer support, and security review.

**Independent Test**: Can be fully tested by starting a run, changing the active configuration while the run is active, and confirming that the run record keeps run-level resolvable versions pinned at acceptance and step/tool-specific versions pinned at first use.

**Acceptance Scenarios**:

1. **Given** a run starts successfully, **When** the platform records its execution configuration, **Then** the run includes run-level model, prompt, skill, tool, secret, credential, and outbound policy versions that were resolvable at acceptance and decision-level versions pinned at first use.
2. **Given** a configuration changes after a run is accepted or after a runtime decision is first used, **When** the run resumes or continues, **Then** the run keeps using the applicable pinned configuration versions unless an authorized migration is explicitly recorded.
3. **Given** an operator reviews a completed run through the API or minimal admin web views, **When** they inspect run provenance, **Then** they can see the model, prompt, skill, tool policy, secret reference, credential requirement, and outbound domain policy versions that governed the run.
4. **Given** a run is denied because configuration is incomplete or invalid, **When** an authorized user reviews the failure, **Then** the record identifies the missing or invalid configuration category without exposing secrets.

---

### User Story 4 - Audit Configuration History And Review Delivery (Priority: P4)

As an auditor, security reviewer, or maintainer, I need configuration history and delivery evidence to be complete so that I can approve changes with confidence and trace policy decisions over time.

**Why this priority**: Audit and review evidence are required for governance and maintainability, but they depend on the core routing and policy behavior being defined first.

**Independent Test**: Can be fully tested by reviewing configuration version history, runtime decision records, and denied policy decisions through API endpoints and minimal admin web views, plus coverage evidence, PR review notes, testing instructions, and README updates for the delivered feature.

**Acceptance Scenarios**:

1. **Given** a model, prompt, skill, tool, secret reference, credential requirement, or outbound policy configuration changes, **When** an auditor views its history, **Then** they can see the actor, timestamp, reason, prior version, new version, and affected scope.
2. **Given** a policy denial occurs during execution, **When** an auditor reviews the event, **Then** they can see the governing policy version, denied action category, affected run when known, and safe reason for denial.
3. **Given** the feature is submitted for review, **When** a maintainer evaluates the delivery, **Then** unit-test coverage, PR review notes, testing instructions, and README guidance are present and cover model routing, skills, tools, secrets, outbound policies, and run provenance.
4. **Given** a configuration version caused an operational issue, **When** an authorized administrator rolls back to a prior valid version, **Then** future runs use the reactivated version while prior and in-flight run provenance remains unchanged unless an explicit audited run migration is recorded.

### Edge Cases

- A run is requested before any global default LLM is active for the run tenant; the platform prevents execution and provides a clear administrative remediation path.
- A workflow, agent, or step override references an inactive, unavailable, or unauthorized model; publishing or execution is blocked before the invalid route is used.
- A step has no prompt version of its own; the platform resolves the prompt version through step, agent, then workflow prompt references only and fails clearly if no valid prompt version exists.
- A model or prompt version is archived after a run starts; in-flight and historical runs remain explainable through their pinned versions.
- An administrator updates configuration while a run is queued, running, waiting for input, or resuming; the existing run retains run-level versions pinned at acceptance and decision-level versions already pinned at first use.
- An agent attempts to use a skill that was removed from the current configuration after the run accepted or first used that skill; the run follows its pinned configuration unless an audited migration changes it.
- A tool request matches one applicable allowed tool policy but attempts an operation, domain, or credential scope that any other applicable active policy disallows; the platform denies the request and records the policy intersection that caused the denial.
- Outbound domain rules include overlapping or wildcard entries; the platform permits access only when every applicable active outbound policy allows the destination and records the matching policy versions.
- A secret value rotates behind an existing secret reference; audit records retain the reference and version metadata without exposing secret material.
- A credential requirement is present but the credential is expired, revoked, missing, or not authorized for the tenant; tool use is blocked safely.
- A configuration version is created by an unauthorized user or outside their tenant scope; the change is rejected and audited without altering active configuration.
- A reviewer requests history for a configuration or run outside their authorization scope; the platform fails closed without disclosing protected details.
- Delivery materials omit coverage evidence, PR review notes, testing instructions, or README updates; the feature is not considered review-ready.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The platform MUST allow authorized administrators to set one active tenant-scoped global default LLM per tenant for model-backed execution.
- **FR-002**: The platform MUST allow authorized administrators or workflow owners to define model overrides at workflow, agent, and step scopes.
- **FR-003**: Model routing MUST resolve deterministically in this precedence order: step override, agent override, workflow override, then global default.
- **FR-004**: The platform MUST provide API endpoints and minimal admin web views that show the resolved model source for a workflow, agent, or step before a run is started.
- **FR-005**: The platform MUST prevent publishing or starting model-backed execution when the resolved model is missing, inactive, unauthorized, or otherwise unavailable for the requested scope.
- **FR-006**: The platform MUST require model-backed execution to resolve a prompt version along with the model selection.
- **FR-007**: Prompt version resolution MUST use this precedence order: step prompt reference, agent prompt reference, then workflow prompt reference; tenant-scoped global model defaults MUST NOT supply prompt versions.
- **FR-008**: The platform MUST prevent model-backed execution when no valid prompt version can be resolved for the workflow, agent, or step that needs one.
- **FR-009**: Every model routing configuration change MUST create a new version that preserves prior version identity, author, timestamp, reason, affected scope, and activation status.
- **FR-010**: Later configuration changes MUST NOT rewrite historical model or prompt provenance for accepted runs; preserved versions remain authoritative unless an authorized, explicit, and audited migration is performed.
- **FR-011**: Agents MUST have explicit skill bindings before they can use skills during workflow execution.
- **FR-012**: Skill bindings MUST identify the skill, applicable agent or scope, allowed use context, active status, version, author, timestamp, and prior version when changed.
- **FR-013**: Agents MUST be denied access to any skill that is not present in their active resolved skill bindings for the run.
- **FR-014**: Agents MUST have explicit allowed tool policies before they can use tools during workflow execution.
- **FR-015**: Allowed tool policies MUST identify permitted tools, permitted operations or action categories, applicable scope, active status, version, author, timestamp, and prior version when changed.
- **FR-016**: Tool use MUST be denied by default unless every applicable active resolved policy explicitly allows the requested tool and action category.
- **FR-017**: Network-capable tool use MUST be governed by explicit outbound domain policies that define allowed domains or domain patterns, applicable scope, active status, version, author, timestamp, and prior version when changed.
- **FR-018**: Outbound access MUST be denied by default unless every applicable active resolved outbound domain policy permits the requested destination.
- **FR-019**: Tool-specific credential requirements MUST define the required credential reference, allowed credential scope, applicable tool or action, active status, version, author, timestamp, and prior version when changed.
- **FR-020**: Secret references and credential requirements MUST store references and metadata only; raw secret values MUST NOT be stored in workflow definitions, routing configuration, tool policies, run provenance, logs, or audit records.
- **FR-021**: Tool use that requires credentials MUST be blocked when the required credential reference is missing, inactive, expired, revoked, unauthorized, outside the allowed scope, or disallowed by any applicable active credential policy.
- **FR-022**: Secret references, outbound domain policies, and tool-specific credential requirements MUST be versioned and auditable with the same history expectations as model routing and skill policy changes.
- **FR-023**: Every accepted run MUST record run-level resolvable model and prompt versions at acceptance, and MUST record step-specific model and prompt versions when each model-backed step first uses them.
- **FR-024**: Every accepted run MUST record run-level resolvable skill binding versions, allowed tool policy versions, outbound domain policy versions, secret reference versions, and credential requirement versions at acceptance, and MUST record tool- or step-specific versions when the governing runtime decision is first used.
- **FR-025**: Runtime policy decisions MUST record enough information to explain allowed and denied skill, tool, domain, and credential outcomes, including the applicable active policy versions evaluated as a cumulative intersection, without exposing secret values.
- **FR-026**: A run that resumes after interruption MUST continue using model, prompt, skill, tool, secret reference, credential requirement, and outbound domain policy versions already pinned at acceptance or first use unless an authorized, explicit, and audited migration is performed.
- **FR-027**: Configuration history MUST be visible to authorized administrators, auditors, and maintainers, including active version, prior versions, activation changes, actor, timestamp, reason, and affected scope.
- **FR-028**: The platform MUST enforce existing tenant and role boundaries for viewing, creating, updating, activating, deactivating, or auditing model routing, prompt references, skill bindings, tool policies, secret references, credential requirements, and outbound domain policies.
- **FR-029**: Administrative and runtime audit records MUST use safe summaries for sensitive values and MUST NOT include raw prompts, raw secrets, credential values, or unauthorized run content unless an existing authorized content view explicitly allows it.
- **FR-030**: The delivered feature MUST include unit-test evidence showing at least 90 percent coverage for the submitted model routing, skill binding, tool policy, secret reference, outbound policy, credential requirement, and run provenance behavior.
- **FR-031**: The delivered feature MUST include PR review notes covering routing precedence, version pinning, prompt provenance, skill binding enforcement, tool allow policies, outbound domain enforcement, credential requirements, secret handling, audit behavior, authorization, and known risks.
- **FR-032**: The delivered feature MUST include API endpoints and minimal admin web views for configuring and reviewing model routing, skill bindings, allowed tool policies, outbound domain policies, secret references, credential requirements, configuration history, and run provenance.
- **FR-033**: The delivered feature MUST include testing instructions that allow reviewers to verify global defaults, workflow overrides, agent overrides, step overrides, prompt version recording, skill bindings, allowed tool policies, outbound domain denials, credential requirement failures, secret-reference audit behavior, admin web views, API review endpoints, and run provenance.
- **FR-034**: The delivered feature MUST update the README with user-facing guidance for model routing precedence, skill configuration, allowed tool policies, secret references, outbound domain policies, credential requirements, run provenance, admin web views, API endpoints, and review verification steps.
- **FR-035**: The platform MUST validate model routing configurations against tenant-authorized model provider catalog entries that identify provider key, model id, availability status, tenant authorization, and supported model-backed execution capabilities.
- **FR-036**: Authorized administrators MUST be able to reactivate a prior valid configuration version for the same tenant, configuration kind, and scope through a rollback action that records actor, timestamp, reason, prior active version, new active version, and affected scope without mutating historical versions.

### Key Entities

- **Model Routing Configuration**: A versioned configuration that selects the LLM for a global, workflow, agent, or step scope and records its active status, author, reason, and lineage.
- **Model Provider Catalog Entry**: A tenant-visible reference record describing an available model provider/model pair, its availability status, authorization scope, and capability metadata used to validate model routing configuration. Catalog administration is outside this feature unless already supported by existing platform behavior.
- **Global Default LLM**: The active tenant-scoped model choice used when no workflow, agent, or step override applies for that tenant.
- **Model Override**: A workflow, agent, or step-specific model choice that takes precedence over broader defaults according to the routing hierarchy.
- **Prompt Version Reference**: The immutable prompt version selected for model-backed execution from the step, agent, or workflow prompt hierarchy and recorded alongside the resolved model.
- **Skill Binding**: A versioned authorization that permits a specific agent or scope to use a named skill in an approved context.
- **Allowed Tool Policy**: A versioned policy that defines which tools and action categories an agent may use; when multiple active policies apply, all must allow the request.
- **Outbound Domain Policy**: A versioned policy that controls destinations for network-capable tool use; when multiple active policies apply, all must allow the destination.
- **Tool Credential Requirement**: A versioned requirement that identifies which credential reference and scope are required for a tool or action; when multiple active requirements apply, all must be satisfied.
- **Secret Reference**: A safe pointer to secret material stored outside workflow definitions, policies, run provenance, logs, and audit payloads.
- **Resolved Execution Configuration**: The pinned set of model, prompt, skill, tool, outbound domain, secret reference, and credential requirement versions selected at run acceptance for run-level resolvable configuration and at first use for step/tool-specific runtime decisions.
- **Runtime Policy Decision**: A recorded allow or deny outcome for model routing, skill access, tool use, outbound access, or credential resolution, including every applicable active policy version that was evaluated.
- **Configuration Audit Record**: A durable record of who changed or activated a configuration version, when it happened, why it happened, what scope it affected, and what prior version it replaced.
- **Run Provenance Record**: The reviewable evidence showing which configuration versions governed a run and each model-backed decision within it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100 percent of model-backed runs use a deterministic model routing path that can be explained as step, agent, workflow, or global default.
- **SC-002**: Authorized administrators can set or update a tenant-scoped global default LLM and verify the resolved routing outcome for a representative workflow through API endpoints and minimal admin web views in under 5 minutes during acceptance testing.
- **SC-003**: 100 percent of model-backed run records identify model and prompt versions pinned at acceptance for run-level configuration and at first use for each model-backed workflow, agent, or step decision.
- **SC-004**: 100 percent of accepted skill and tool uses can be traced to the skill binding, allowed tool policy, outbound domain policy, secret reference, and credential requirement versions pinned at acceptance or first use whose cumulative intersection authorized them.
- **SC-005**: 100 percent of disallowed skill, tool, outbound domain, or credential attempts are blocked before the unauthorized action occurs and produce a safe audit record identifying the policy intersection reason.
- **SC-006**: 100 percent of configuration changes for model routing, skill bindings, tool policies, secret references, outbound domain policies, and credential requirements create reviewable version history.
- **SC-007**: 100 percent of resumed runs continue with configuration versions already pinned at acceptance or first use unless an authorized audited migration is recorded.
- **SC-008**: At least 90 percent of administrators and maintainers in acceptance testing can locate model routing history, tool policy history, and run provenance without assistance through the delivered API endpoints and minimal admin web views.
- **SC-009**: Submitted routing, policy, secret-reference, credential, and provenance behavior demonstrates at least 90 percent unit-test coverage.
- **SC-010**: PR review notes, testing instructions, and README guidance are present and sufficient for a maintainer to verify the feature without additional verbal explanation.

## Testing, Review, And Documentation Impact

- **Testing Instructions**: Reviewer instructions must cover global default LLM setup, workflow override, agent override, step override, routing precedence, prompt version recording, run provenance, skill binding allow and deny paths, tool policy allow and deny paths, outbound domain allow and deny paths, missing or invalid credential requirements, secret-reference audit behavior, authorization failures, configuration version history, admin web views, API review endpoints, and resumed-run pinning.
- **PR Review Guidance**: PR notes must call out deterministic routing precedence, prompt provenance, version pinning, migration behavior for in-flight runs, skill binding enforcement, tool policy enforcement, outbound domain enforcement, credential requirement handling, secret hygiene, audit completeness, tenant and role boundaries, API endpoints, minimal admin web views, and known risks.
- **Documentation Impact**: The feature requires updates to `README.md` and reviewer-facing testing instructions covering model routing precedence, skill configuration, allowed tool policies, outbound domain policies, secret references, credential requirements, run provenance, audit history, admin web views, API endpoints, and verification steps.

## Constitution Impact

- **Durability**: Model routing versions, prompt references, skill bindings, tool policies, secret references, credential requirements, outbound domain policies, runtime policy decisions, and run provenance must be durable before they become authoritative for execution.
- **Tenant Isolation And Fairness**: Configuration visibility, activation, runtime resolution, tool use, credential requirements, outbound access, and audit queries must include tenant-aware authorization and fail closed on cross-tenant access.
- **Versioning**: Runs must pin run-level resolvable model configuration versions, prompt versions, skill binding versions, tool-policy versions, secret-reference versions, credential requirement versions, and outbound domain policy versions at acceptance, then pin step/tool-specific versions at first use so replay and incident analysis are possible.
- **Secrets And Tool Access**: Secret values stay outside workflow definitions, policies, run records, logs, and audits; tools require explicit allow policies, outbound domain permissions, credential requirements, and auditable decisions.
- **Artifact Storage**: This feature does not introduce new artifact storage behavior; review evidence and exported audit materials remain governed by existing artifact and documentation policies.
- **Approval And Resume**: Resumed runs must retain execution configuration already pinned at acceptance or first use unless an authorized, explicit, and audited migration is performed; any human approval required for migration must remain durable run state.
- **Observability**: Runtime routing and policy decisions must produce safe logs, metrics, traces, timeline events, and audit records sufficient to explain model selection, prompt version use, tool access, domain denials, credential failures, and secret-reference resolution.
- **Security**: Existing role and tenant authorization must govern all administrative configuration, runtime resolution, policy enforcement, provenance viewing, and audit history access.

## Assumptions

- Existing platform roles can distinguish administrators, workflow owners, operators, auditors, maintainers, and runtime actors.
- The global default LLM is tenant-scoped; tenant-specific restrictions determine which models, skills, tools, domains, or credentials are available.
- Model routing is deterministic by configuration hierarchy; automatic optimization, cost-based routing, model benchmarking, and provider fallback are out of scope unless represented as explicit configured versions.
- Prompt versions already exist or will be defined by related workflow and prompt-management behavior; this feature requires resolving and recording workflow, agent, or step prompt versions but does not define prompt authoring workflows or tenant-global prompt defaults.
- Secret material is stored in an external secret-management system; this feature records references, requirements, and audit metadata rather than secret values.
- Tool access is deny-by-default unless every applicable active resolved policy allows the skill, tool, action category, outbound destination, and credential requirement.
- Configuration changes affect future runs by default; active and historical runs retain versions already pinned at run acceptance or first use unless an explicit audited migration is approved.
- This feature defines model routing, skill configuration, tool policy, secret-reference, outbound policy, credential requirement, provenance behavior, API endpoints, and minimal admin web views; detailed storage, schema, and user-interface implementation choices are deferred to planning.
