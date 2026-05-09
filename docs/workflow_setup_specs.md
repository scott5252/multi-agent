# Custom Workflow Setup UI Roadmap

Created: 2026-05-09

This document defines the Spec Kit roadmap for adding a browser-first custom
workflow setup experience. The goal is that a tenant or platform admin can use
the React Admin UI to create a new workflow from scratch, add agent and
sub-agent roles, define graph nodes and edges, define contracts and quorum/join
policies, create or select prompts and runtime profiles for each agent, validate
the draft, create required test evidence, publish the workflow, and use the
published workflow in runtime/design-review flows without editing raw JSON or
manually calling backend APIs.

This roadmap was written after reviewing `docs/react_ui2.md`. It follows the
same prompt-source pattern: each spec below includes prompts for
`/speckit.specify`, `/speckit.plan`, `/speckit.tasks`, and
`/speckit.implement`. The roadmap intentionally keeps authorization,
validation, tenant isolation, redaction, publish readiness, and audit decisions
owned by backend contracts.

## Current Capability Summary

The backend workflow registry already supports full workflow documents. The
canonical `WorkflowDraftDocument` includes:

- workflow metadata and scope
- agent and sub-agent role definitions
- prompt/profile references
- skill installation references and skill bindings
- contracts
- nodes
- edges
- join policies
- approval gates
- subworkflow references
- required test requirements
- editor annotations

The lower-level workflow API can create and save full workflow documents.
However, the current React workflow builder exposes only a narrow authoring
surface. It can create a basic draft, inspect graph previews, update limited
metadata, validate, and publish, but the React save route currently persists
only display name and description from its browser payload. The React UI does
not yet let a user add arbitrary agent roles, graph nodes, graph edges,
contracts, join policies, prompt/profile references, or per-agent prompt/profile
bindings.

Prompt and runtime profile APIs already exist for create, save, validate,
publish/activate, grant, and resolve flows. The current React governance UI is
primarily a review and mutation summary workspace, not a complete create/edit
experience for brand-new prompt/profile records. A complete custom workflow
setup UI therefore needs coordinated workflow-builder, governance, test-bench,
and generated-contract work.

## Steps Needed To Add The Ability To The UI

1. Extend the React-facing workflow builder contract so browser saves can submit
   full, validated workflow document changes, not only metadata.
2. Add backend mutation endpoints for safe graph/document patches or full
   document saves with revision tokens, idempotency keys, validation findings,
   stale conflict recovery, audit summaries, and redaction-safe error details.
3. Generate TypeScript contracts for the new workflow document editor schemas
   and update the React API client.
4. Build a React workflow setup workspace with guided sections for metadata,
   agents, prompts/profiles, contracts, graph topology, joins/quorum, tools,
   test evidence, validation, and publish readiness.
5. Add role/agent authoring controls so a user can create agent and sub-agent
   roles, set role purpose/responsibilities, choose input/output contracts, and
   associate roles with graph nodes.
6. Add graph authoring controls so a user can add role, subworkflow, approval,
   join, and terminal nodes; connect them with edges; edit edge contracts and
   branch/failure metadata; and inspect the graph through keyboard-readable
   lists.
7. Add contract authoring controls for workflow input, output, data, handoff,
   artifact, memory, tool-access, approval-decision, and failure-outcome
   schemas with safe validation and examples.
8. Add join/quorum authoring controls for inbound edges, required branches,
   quorum count, timeout, failure behavior, and output merge contracts.
9. Add prompt/profile creation and binding flows so each agent can create or
   select a prompt lineage, edit prompt template variables and fixture sets,
   validate and publish the prompt, create or select a runtime profile, bind the
   published prompt to that profile, activate the profile, and bind the profile
   reference to the workflow role.
10. Add provider/routing readiness display for per-agent profiles without
    exposing raw credentials, prompts, completions, or provider payloads.
11. Add optional skill/tool binding controls using existing skill registry
    eligibility/readiness summaries.
12. Integrate Test Bench setup so custom workflows can create required suites
    and cases, launch deterministic safe evidence, bind evidence to the current
    draft revision, and block publish on stale or missing evidence.
13. Update validation and publish panels so every custom workflow blocker points
    back to the exact UI section and field that can fix it.
14. Add guided first-run and recovery paths so a clean tenant can create and
    publish a working multi-agent workflow without templates or raw JSON.
15. Add Playwright, backend route, contract, frontend, docs, redaction,
    tenant-isolation, accessibility, and performance coverage proving the
    full custom workflow setup works end to end.

## Proposed Spec Breakdown

| Proposed spec | Name | Depends on | Purpose |
|---------------|------|------------|---------|
| 069 | Workflow Document Authoring Contracts And Mutation APIs | 030, 040, 050, 065, 066 | Add React-facing full document contracts, mutation endpoints, stale conflict recovery, audit summaries, generated types, and validation mapping. |
| 070 | React Workflow Graph And Agent Role Builder | 069, 030, 065, 066 | Add browser controls for roles, nodes, edges, contracts, joins/quorum, graph layout, keyboard lists, and safe graph previews. |
| 071 | Prompt Profile Creation And Per-Agent Binding UI | 069, 070, 031, 041, 012, 025 | Add React create/edit/validate/publish/activate flows for prompts and profiles, then bind them to workflow roles. |
| 072 | Custom Workflow Test Evidence And Publish Setup | 069, 070, 071, 033, 043, 015, 024 | Add guided Test Bench suite/case/evidence setup for custom workflows and block publish on stale or missing evidence. |
| 073 | End-To-End Custom Workflow Setup Wizard And Runtime Launch | 069-072, 020, 067, 068 | Add the finished guided workflow setup experience, runtime launch validation, docs, and full browser QA. |

When Specs 069 through 073 are complete, a user should be able to configure a
new workflow with agents from a clean tenant in the browser:

1. Sign in through local-principal or Auth0.
2. Open Workflow Registry through Admin navigation.
3. Click Create Workflow.
4. Define metadata and contracts.
5. Add agents/sub-agents and their prompts/profiles.
6. Build the graph and quorum/join rules.
7. Add required test evidence.
8. Validate and publish.
9. Launch or select the published workflow from runtime/design-review flows.

## Global Prompt Prefix

Prepend or keep in mind for every prompt below:

```text
Use the current multi-agent platform repository after Specs 001 through 068 and
after the React UI roadmap context in docs/react_ui2.md. React Admin is the
primary browser UI, and workflow registry, governance, test bench, operations,
design review, agent graph, runtime graph, and interaction replay foundations
already exist.

The goal is not to create another hard-coded scenario template. The goal is a
browser-first custom workflow setup feature where authorized users can create
and publish their own multi-agent workflows without editing raw JSON, changing
browser URLs manually, or calling API endpoints directly.

Preserve FastAPI domain services, PostgreSQL source of truth, Auth0 production
authentication, AUTH_MODE=local_principal QA, tenant isolation, audit
fail-closed behavior, redaction rules, runtime version pinning, secret hygiene,
object storage boundaries, generated TypeScript contracts, Playwright evidence,
QA docs, and at least 90 percent relevant coverage.

React must consume backend-owned JSON contracts generated from Pydantic
schemas. Do not move authorization, tenant scoping, workflow validation,
prompt/profile validation, credential readiness, publish readiness, redaction,
or audit decisions into browser-only logic. Raw secrets, credential values,
provider authorization headers, raw prompts, raw completions, memory contents,
raw run payloads, private channel messages, raw tool payloads, raw test
transcripts, link tokens after creation, local filesystem paths, stack traces,
and unauthorized tenant labels must never appear in React UI, redirects,
exports, screenshots, QA artifacts, logs, or docs.

All navigation in QA guides must use visible UI links, nav items, buttons,
menus, tabs, row actions, and in-page links after the initial local entrypoint.
Do not tell users to configure workflow setup by editing the browser URL.
```

## Spec 069 - Workflow Document Authoring Contracts And Mutation APIs

### Specify Prompt

```text
Create a feature specification for Workflow Document Authoring Contracts And
Mutation APIs. The backend workflow registry already stores full
WorkflowDraftDocument records, but the React workflow builder save route only
persists limited metadata. Authorized admins need browser-facing JSON
contracts and mutation endpoints that allow safe creation and editing of full
workflow documents, including roles, prompt/profile references, skill
references, contracts, nodes, edges, join policies, approval gates,
subworkflow references, test requirements, and editor annotations.

The feature must support revision tokens, idempotency keys, stale conflict
recovery, per-section validation findings, redaction-safe error details, audit
summaries, tenant/platform scope rules, generated TypeScript contracts, and
field-level links back to UI sections. It must preserve existing lower-level
workflow APIs while making the React-facing API capable of persisting full
document edits.
```

### Plan Prompt

```text
Plan the Workflow Document Authoring Contracts And Mutation APIs feature.
Review current workflow_registry schemas, admin_workflows lower-level routes,
admin_react workflow create/save routes, workflow_builder envelopes, generated
React API types, validation/findings mapping, audit events, and stale conflict
handling.

Design backend-owned React contracts for full document edit state, section
summaries, editable collections, validation findings, graph references, and
mutation results. Decide whether browser mutations submit full documents,
structured patches, or both; default to full document saves plus optional
section patch endpoints when needed for usability. Extend React create/save
routes so they can persist full document changes, not only name and
description. Add generated TypeScript types, API client helpers, and tests for
authorization, tenant isolation, stale revisions, invalid graph references,
duplicate keys, unsafe text, oversized payloads, and redaction.
```

### Tasks Prompt

```text
Generate implementation tasks for Workflow Document Authoring Contracts And
Mutation APIs. Include tasks for auditing current route behavior, adding
Pydantic schemas for full document editor state and mutations, extending
admin_react workflow create/save endpoints, reusing workflow registry
validation, mapping validation findings to section/field paths, adding audit
summaries, adding stale conflict responses, regenerating TypeScript contracts,
updating frontend API client helpers, adding backend route tests, adding
contract tests, adding frontend type tests, adding docs for the mutation
contract, and updating QA guidance. Include negative tests for cross-tenant
saves, platform/tenant scope mismatch, duplicate role/node/edge keys, edges
that reference missing nodes, roles that reference missing node keys, missing
entry node, unsafe strings, and oversized documents.
```

### Implement Prompt

```text
Implement Workflow Document Authoring Contracts And Mutation APIs. Keep changes
scoped to backend contracts/routes, workflow builder service adapters,
generated TypeScript contracts, frontend API helpers, and focused tests. Do not
build the full graph editor UI in this spec beyond minimal integration needed
to prove the route can round-trip full document changes.

Run ruff, mypy for touched Python surfaces, focused pytest for workflow
registry/admin_react routes/contracts, generated contract checks, frontend
typecheck for generated types, and redaction/tenant-isolation tests. Provide
evidence that the React-facing save endpoint persists changes to roles, nodes,
edges, contracts, join policies, prompt/profile references, test requirements,
and editor annotations.
```

## Spec 070 - React Workflow Graph And Agent Role Builder

### Specify Prompt

```text
Create a feature specification for React Workflow Graph And Agent Role
Builder. Authorized admins need a browser UI inside Workflow Registry for
creating and editing a custom workflow's agent roles, sub-agent roles, graph
nodes, graph edges, contracts, join policies, approval gates, subworkflow
references, and layout annotations without editing raw JSON.

The UI must expose familiar controls for adding, editing, deleting,
duplicating, reordering, and validating items. It must include a graph canvas,
keyboard-readable node/edge lists, stable responsive controls, accessible
labels, no nested-card clutter, and section-level dirty/save states. The UI
must use backend-owned mutation contracts from Spec 069 and must never infer
authorization or validation client-side.
```

### Plan Prompt

```text
Plan the React Workflow Graph And Agent Role Builder. Review existing workflow
React components, AgentGraphPanel, WorkflowGraphPanel, WorkflowSectionForm,
WorkflowReferencePicker, WorkflowValidationPanel, WorkflowPublishPanel,
generated API client, and current design system conventions. Choose a graph
implementation consistent with the project; use @xyflow/react if available or
add it only if needed and approved by package policy.

Design UI sections for metadata, agents, contracts, graph nodes, graph edges,
join/quorum policies, approval gates, subworkflows, skill bindings, and review.
Each section must have collection editors, validation state, add/remove
actions, duplicate-key handling, stable empty states, and keyboard alternatives.
Graph edits must update both visual canvas and list/detail panels. Add
Playwright checks for nonblank graph rendering, desktop/mobile framing, no text
overlap, keyboard navigation, and persisted reload after save.
```

### Tasks Prompt

```text
Generate implementation tasks for React Workflow Graph And Agent Role Builder.
Include tasks for UX/state design, component decomposition, graph canvas and
list editors, role editor, contract editor, node editor, edge editor, join
policy editor, approval gate editor, subworkflow reference editor, skill
binding editor, dirty-state handling, undo/cancel for unsaved section edits,
save integration with Spec 069 endpoints, validation finding anchors, generated
type usage, frontend tests, accessibility tests, Playwright desktop/mobile
screenshots, backend smoke tests for persisted graph changes, and docs updates.

Include negative tests for deleting referenced nodes, deleting referenced
contracts, invalid quorum count, invalid entry node, duplicate keys, graph
cycles if validation blocks them, and unsupported branch/failure combinations.
```

### Implement Prompt

```text
Implement React Workflow Graph And Agent Role Builder. Build the browser
authoring UI behind the existing Workflow Registry navigation. Use the backend
document editor contracts from Spec 069 for all persisted changes. Preserve
read-only graph preview behavior while adding editable graph sections.

Run frontend tests, typecheck, build, focused backend smoke tests, Playwright
desktop/mobile journeys for creating a workflow with at least three agents and
a join node, accessibility checks for list alternatives, redaction sweeps, and
tenant isolation tests. Confirm a saved custom graph reloads correctly and the
publish validation panel references the edited document.
```

## Spec 071 - Prompt Profile Creation And Per-Agent Binding UI

### Specify Prompt

```text
Create a feature specification for Prompt Profile Creation And Per-Agent
Binding UI. Users who create custom workflows need to configure each agent's
prompt and runtime profile from the browser. The UI must let authorized admins
create or select prompt lineages, edit prompt template content with variables
and fixture sets, validate and publish prompts, create or select runtime
profiles, bind prompt versions and model routing hints to profiles, validate
and activate profiles, and attach profile/prompt references to workflow roles.

The feature must work from a clean tenant and must also allow reuse of existing
platform or tenant prompt/profile records when authorized. Raw prompt content
must be editable only inside authorized edit forms and must not leak into
summaries, previews, screenshots, audit summaries, or other safe display
surfaces.
```

### Plan Prompt

```text
Plan Prompt Profile Creation And Per-Agent Binding UI. Review prompt APIs,
agent profile APIs, governance React dashboard, prompt/profile schemas,
prompt/profile validation and publication services, model provider readiness,
model-skill routing previews, workflow PromptProfileReference fields, and
workflow role profile_reference_key/prompt_reference_keys fields.

Design a per-agent binding workflow embedded in or linked from the workflow
builder. It must support creating prompt drafts, saving prompt templates,
validating prompt variables, previewing safe fixtures, publishing prompt
versions, creating profile drafts, selecting provider/model routing hints,
binding prompt versions to profiles, validating and activating profiles, and
writing workflow prompt_profile_references and role reference keys back to the
workflow document. Add backend React contracts where current governance React
contracts are read-only or summary-only. Preserve old prompt/profile APIs.
```

### Tasks Prompt

```text
Generate implementation tasks for Prompt Profile Creation And Per-Agent
Binding UI. Include tasks for backend React prompt create/edit/save/validate/
publish contracts, backend React profile create/edit/save/validate/activate
contracts, per-agent binding schema, workflow builder integration, prompt
template editor, variable and fixture-set editor, safe preview panel, profile
routing/provider selectors, profile activation flow, workflow role binding
mutation, generated TypeScript updates, frontend tests, backend route tests,
contract tests, Playwright clean-tenant journey, and docs.

Include security tasks for raw prompt redaction outside edit forms, provider
credential secrecy, cross-tenant prompt/profile denial, platform prompt grants,
tenant prompt reuse, profile activation stale conflicts, and safe audit
records.
```

### Implement Prompt

```text
Implement Prompt Profile Creation And Per-Agent Binding UI. Add the missing
React create/edit/publish/activate flows for prompts and runtime profiles and
connect them to workflow role binding. Ensure the custom workflow builder can
create at least one prompt and one profile per agent, then attach the resulting
references to the role and workflow document.

Run backend prompt/profile/workflow route tests, generated contract checks,
frontend tests, typecheck, Playwright clean-tenant setup flow, redaction tests
for raw prompts and credentials, tenant isolation tests, and docs validation.
Confirm that after reload, each workflow role shows its selected profile and
prompt readiness without exposing raw prompt content.
```

## Spec 072 - Custom Workflow Test Evidence And Publish Setup

### Specify Prompt

```text
Create a feature specification for Custom Workflow Test Evidence And Publish
Setup. Users creating custom workflows need a guided way to create required
Test Bench suites and cases for the current workflow draft revision, run safe
deterministic evidence, inspect diagnostics, bind evidence to publish
requirements, and publish only when validation and current required evidence
pass.

The feature must integrate Workflow Registry and Agent Tests without requiring
users to manually copy workflow draft ids, revision ids, suite ids, or browser
URLs. Publish readiness must remain backend-owned and must reject stale,
missing, cross-tenant, failed, or synthetic evidence.
```

### Plan Prompt

```text
Plan Custom Workflow Test Evidence And Publish Setup. Review current Test Bench
React components, agent test bench service, publication requirements,
workflow publish gate, required test snapshots, design reviewer template
evidence setup, and workflow validation panels.

Design workflow-builder panels for creating a required suite from the current
draft, adding common cases, selecting safe execution mode, launching runs,
refreshing evidence, inspecting pass/fail diagnostics, and attaching a
TestSuiteRequirement to the workflow document. Add UI links between Workflow
Registry and Agent Tests that preserve tenant scope and selected workflow
context. Add backend contracts if current Test Bench bootstrap is not enough
for contextual creation from the workflow builder.
```

### Tasks Prompt

```text
Generate implementation tasks for Custom Workflow Test Evidence And Publish
Setup. Include tasks for contextual required suite creation, case template
selection, custom case authoring, target revision binding, safe-mode run
launch, evidence refresh, publish-gate summary, stale evidence warnings,
workflow document test requirement updates, cross-links to Agent Tests, backend
tests, frontend tests, Playwright flow, docs, and QA guide.

Include negative tests for stale revision evidence, failed runs, cross-tenant
suites, missing required cases, invalid target type, unsupported live provider
mode, artifact reference redaction, and publish attempts before evidence is
current.
```

### Implement Prompt

```text
Implement Custom Workflow Test Evidence And Publish Setup. Add the workflow
builder evidence setup panels and any backend React contracts needed to create
and bind required Test Bench evidence from the workflow setup flow. Keep the
existing Agent Tests workspace authoritative for detailed run diagnostics.

Run focused backend tests for publication requirements, frontend tests,
generated contract checks, Playwright clean-tenant evidence setup and publish
flow, redaction sweeps for artifacts/test transcripts, tenant isolation tests,
and docs validation. Confirm a custom workflow cannot be published until its
current draft revision has passing required evidence.
```

## Spec 073 - End-To-End Custom Workflow Setup Wizard And Runtime Launch

### Specify Prompt

```text
Create a feature specification for End-To-End Custom Workflow Setup Wizard And
Runtime Launch. After Specs 069 through 072, users need a polished guided
experience that ties the pieces together: create workflow, add agents, create
prompts/profiles, build graph, add tests, validate, publish, and launch or
select the published workflow from supported runtime/design-review surfaces.

The feature must be usable from a clean tenant, must avoid raw JSON editing,
must use UI links for navigation, must provide clear progress and recovery
states, and must include full QA evidence that a user can configure their own
multi-agent workflow in the browser.
```

### Plan Prompt

```text
Plan End-To-End Custom Workflow Setup Wizard And Runtime Launch. Review the
implemented contracts and UI from Specs 069 through 072, Workflow Registry,
Design Reviews workflow dropdown, user run workspace, operations run search,
runtime graph, and interaction replay graph.

Design a guided setup wizard or checklist within Workflow Registry that helps a
user complete all required sections without hiding the advanced editors.
Define progress states for metadata, agents, prompts/profiles, graph,
contracts, evidence, validation, publish, and runtime launch. Add final
confirmation paths for launching a workflow run or selecting the published
workflow in Design Reviews. Add docs and screenshots for a clean-system
tutorial, plus API examples as secondary validation.
```

### Tasks Prompt

```text
Generate implementation tasks for End-To-End Custom Workflow Setup Wizard And
Runtime Launch. Include tasks for wizard/checklist state, section completion
rules, clean-tenant empty states, recovery links, launch/select published
workflow actions, runtime graph verification, interaction replay verification,
browser tutorial docs, API validation docs, Playwright desktop/mobile journeys,
accessibility checks, performance checks, frontend tests, backend route tests,
contract tests, redaction scans, tenant isolation tests, and PR notes.

The main Playwright journey must start from local login, use only visible UI
links after login, create a custom workflow with at least three agents, create
or select prompts/profiles for each agent, build a graph with a join node,
create required evidence, validate, publish, launch or select the workflow,
and inspect runtime graph evidence.
```

### Implement Prompt

```text
Implement End-To-End Custom Workflow Setup Wizard And Runtime Launch. Integrate
the completed document editor, graph builder, prompt/profile binding, evidence
setup, validation, publish, and runtime launch/select paths into a coherent
browser-first setup experience.

Run the full clean-tenant Playwright journey, focused backend route tests,
frontend tests, typecheck, build, generated contract checks, redaction sweeps,
tenant isolation tests, accessibility checks, performance checks, docs
validation, and API smoke validation. Confirm that a user can configure their
own workflow with agents and prompts through the UI without editing raw JSON,
editing the browser URL, or using direct API calls.
```

## Completion Review Checklist

Before considering this roadmap complete, verify all of the following:

- React Workflow Registry exposes a create-from-scratch flow, not only the
  built-in Design Reviewer Council template.
- The React-facing workflow save endpoint persists full document changes for
  roles, prompt/profile references, contracts, nodes, edges, joins, approval
  gates, subworkflows, test requirements, and editor annotations.
- Users can add agent and sub-agent roles through UI controls.
- Users can add graph nodes and edges through UI controls and through
  keyboard-readable list editors.
- Users can define input/output/data/handoff contracts through UI controls.
- Users can define quorum/join policies through UI controls.
- Users can create or select prompts for each agent through UI controls.
- Users can create or select runtime profiles for each agent through UI
  controls.
- Users can bind prompt/profile references to workflow roles through UI
  controls.
- Users can create required test suites/cases and launch safe evidence from the
  workflow setup flow or linked Agent Tests UI without copying internal ids.
- Publish is blocked when validation or evidence is stale, missing, failed, or
  cross-tenant.
- Published custom workflows appear in runtime/design-review workflow selectors
  when the current principal is authorized.
- A clean-tenant Playwright test proves the full UI setup path from login
  through publish and runtime graph inspection.
- Docs teach the full browser path and API calls remain secondary validation,
  not required configuration steps.

If every item above is true after Specs 069 through 073, the system will have a
complete UI feature for users to configure their own workflows with agents.
