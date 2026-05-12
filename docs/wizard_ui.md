# Wizard-Based Onboarding UI Roadmap

Created: 2026-05-11

This document defines the Spec Kit roadmap for adding a generic wizard-based
onboarding process to the React Admin console. The wizard should guide an
authorized user step by step from Console Home to a configured, validated,
published, and launchable workflow without tying the experience to the Design
Reviewer Council or Daily Intelligence Briefing tutorials.

The roadmap was written after reviewing:

- `tutorials/design_reviewer_example.md`
- `tutorials/test_example.md`
- Specs 031 through 073
- `docs/react_ui.md`
- `docs/react_ui2.md`
- `docs/remove_mock_data_specs.md`
- `docs/graphical_ui.md`
- `docs/workflow_setup_specs.md`

It follows the existing prompt-source pattern: each spec below includes prompts
for `/speckit.specify`, `/speckit.plan`, `/speckit.tasks`, and
`/speckit.implement`.

## Source Review Summary

The two tutorials prove that useful setup currently spans many React Admin
workspaces: local login and tenant scope, Console Home navigation, Workflow
Registry, workflow draft creation, roles, contracts, graph topology,
prompt/profile bindings, skill or channel readiness, required Test Bench
evidence, validation, publishing, runtime launch, operations evidence, usage,
and optional domain-specific handoffs.

Specs 031 through 059 establish the React Admin shell, governance, skill
lifecycle, Test Bench, membership, usage, channels, live-data, no-Jinja, and
mock-data guardrails. Specs 060 through 064 add the Design Reviewer scenario,
but that scenario is intentionally not the model for this wizard. Specs 065
through 068 add graph projection and runtime interaction evidence. Specs 069
through 073 add full workflow document editing, role/graph authoring,
prompt/profile binding, test evidence setup, and a builder-level custom
workflow checklist.

The remaining gap is a Console Home-launched onboarding wizard that is generic,
bounded to a non-scrolling 1280 x 800 experience, and composed from existing
backend-owned APIs instead of a new scenario template or a new backend workflow
engine.

## Product Constraints

- The wizard must launch from Console Home through a visible authorized action.
- The wizard must support arbitrary user scenarios, not hard-coded tutorial
  scenarios.
- The wizard must use existing APIs: Console Home, Workflow Registry create and
  builder state, workflow lookups, full document save, validation, publish
  gate, publish, governance prompt/profile, skill lifecycle, channel, Test
  Bench, runtime launch, operations, and graph evidence APIs.
- New backend route families are out of scope unless implementation discovers a
  missing existing API that blocks durable setup. Small additions to existing
  React Admin envelopes are acceptable when they expose already-authorized
  navigation or derived state.
- Every wizard screen must fit inside a standard 1280 x 800 viewport without
  page scrolling or internal content scrolling. If content does not fit, split
  it into another screen or page the collection.
- The wizard may link to advanced editors, but the wizard screens themselves
  must remain fixed-frame, non-scrolling, and usable without editing raw JSON.
- Browser state may guide progress, but authorization, tenant scope,
  validation, evidence freshness, publish readiness, redaction, and runtime
  eligibility must remain backend-owned.
- QA must use visible UI links after initial local login. API or curl checks
  are secondary validation only.

## Proposed Spec Breakdown

| Proposed spec | Name | Depends on | Purpose |
|---------------|------|------------|---------|
| 074 | Console Home Onboarding Wizard Entry And Fixed-Frame Shell | 039, 040, 073 | Add the Console Home entry point, wizard route, fixed-frame layout, step navigation, resume behavior, and 1280 x 800 no-scroll guardrails. |
| 075 | Generic Scenario Intake And Durable Draft Blueprint | 074, 069 | Capture arbitrary scenario intent and create a durable editable workflow draft blueprint using existing create/save APIs. |
| 076 | Stepwise Agents, Contracts, And Graph Configuration | 075, 070 | Guide users through roles, contracts, nodes, edges, joins, approvals, and graph review using bounded wizard screens over existing document editors. |
| 077 | Resource Readiness, Bindings, And Evidence Configuration | 076, 031, 032, 033, 041, 042, 043, 071, 072 | Guide prompt/profile selection or creation, provider/skill/channel readiness, and required evidence setup through existing APIs. |
| 078 | Publish, Launch, And Operational Verification Finish | 077, 046, 057, 067, 068, 073 | Validate, publish, launch, and verify runtime or graph evidence from the wizard completion path without copying IDs or editing URLs. |
| 079 | Non-Scrolling Wizard QA, Docs, And Guardrails | 074-078, 037, 048, 049, 058, 059 | Add end-to-end QA, visual no-scroll checks, accessibility/performance gates, docs, redaction sweeps, and terminology guardrails. |

When these specs are complete, a user should be able to:

1. Sign in and land on Console Home.
2. Choose a `Set up workflow` action.
3. Describe any scenario they need.
4. Create or resume a durable workflow draft.
5. Configure agents, contracts, graph, prompts, profiles, tools, channels, and
   evidence step by step.
6. Validate and publish through backend-owned gates.
7. Launch or select the published workflow through authorized UI links.
8. Inspect safe runtime and graph evidence.

## Global Prompt Prefix

Prepend or keep in mind for every prompt below:

```text
Use the current multi-agent platform repository after Specs 001 through 073.
React Admin is the primary browser UI. Workflow Registry, full workflow
document saves, role and graph authoring, prompt/profile binding, Test Bench
evidence setup, validation, publish gates, runtime launch, operations, and
graph evidence foundations already exist.

The goal is a generic wizard-based onboarding process launched from Console
Home. It must guide authorized users step by step to configure the system for
any scenario they need. Do not hard-code Design Reviewer Council, Daily
Intelligence Briefing, or any other tutorial scenario as the product path.

Use existing backend APIs and generated TypeScript contracts wherever possible:
Console Home, Workflow Registry create/builder/lookups/save/validate/publish,
governance prompt/profile/provider readiness, skill lifecycle/readiness, channel
configuration, Test Bench suite/case/run/evidence, runtime launch, operations,
and graph projection APIs. Do not add a new backend route family unless an
existing API is proven insufficient for a durable backend-owned decision.

Every wizard screen must fit within a 1280 x 800 viewport without scrolling.
The page, shell content area, wizard body, and fixed footer must not require
vertical scrolling at that resolution. If information or controls do not fit,
split them into more wizard screens or use bounded pagination. Text, controls,
tables, and graph previews must not overlap.

Preserve FastAPI domain services, PostgreSQL source of truth, Auth0 production
authentication, AUTH_MODE=local_principal QA, tenant isolation, audit
fail-closed behavior, redaction rules, runtime version pinning, secret hygiene,
object storage boundaries, generated TypeScript contracts, Playwright evidence,
QA docs, and at least 90 percent relevant coverage.

React must consume backend-owned JSON contracts generated from Pydantic schemas.
Do not move authorization, tenant scoping, workflow validation, prompt/profile
validation, credential readiness, publish readiness, redaction, or audit
decisions into browser-only logic. Raw secrets, credential values, provider
authorization headers, raw completions, memory contents, raw run payloads,
private channel messages, raw external tool payloads, raw test transcripts,
local filesystem paths, stack traces, and unauthorized tenant labels must never
appear in React UI, redirects, exports, screenshots, QA artifacts, logs, or
docs.

All navigation in QA guides must use visible UI links, nav items, buttons,
menus, tabs, row actions, and in-page links after the initial local login entry
point. Do not tell users to configure onboarding by editing the browser URL.
```

## Spec 074 - Console Home Onboarding Wizard Entry And Fixed-Frame Shell

### Specify Prompt

```text
Create a feature specification for Console Home Onboarding Wizard Entry And
Fixed-Frame Shell. Authorized users need a visible Console Home action that
launches a generic onboarding wizard for setting up a workflow-driven system.
The wizard must not be buried inside an already-open workflow draft, and it
must not require users to know Workflow Registry internals before starting.

The feature must add an authorized Console Home entry point, a React Admin
wizard route, a fixed-frame shell with step navigation, resume or exit behavior,
safe draft selection when a draft already exists, and clear save/progress
states. It must use the existing Console Home envelope, Admin shell, Workflow
Registry, workflow create, workflow builder, and workflow lookup APIs. Every
wizard screen must fit in 1280 x 800 without page or panel scrolling.
```

### Plan Prompt

```text
Plan Console Home Onboarding Wizard Entry And Fixed-Frame Shell. Review
ConsoleHomePage, AdminShell, App route dispatch, shell navigation, Console Home
backend envelope construction, WorkflowBuilderPage, WorkflowCreatePage,
WorkflowSetupWizardPanel, workflow registry/create/builder/lookups client
helpers, and current CSS layout constraints.

Design a Console Home quick action such as Set up workflow that opens a new
React wizard route or mode while preserving tenant scope. Decide whether the
route is a dedicated `/admin/app/workflows/onboarding` path or an existing
workflow route with a safe wizard query mode. Reuse existing APIs for create,
resume, draft selection, builder state, and lookups. Define a fixed-frame
layout with a compact step rail, one bounded content panel, and fixed footer
actions. Add no-scroll acceptance checks at 1280 x 800 and recovery states for
loading, denied, dependency unavailable, no tenant scope, draft not found, and
stale draft.
```

### Tasks Prompt

```text
Generate implementation tasks for Console Home Onboarding Wizard Entry And
Fixed-Frame Shell. Include tasks to inspect current home and workflow routing,
add the authorized Console Home quick action, add or wire the React wizard
route, build the fixed-frame wizard shell component, preserve tenant query
scope, load existing workflow registry/create/builder/lookups state through
existing API helpers, support start/resume/exit actions, add no-scroll CSS at
1280 x 800, add state handling for denied/loading/empty/stale cases, add unit
tests for route selection and step shell behavior, add backend envelope tests
for the home action, and add Playwright checks that the wizard route has no
vertical scroll at 1280 x 800.
```

### Implement Prompt

```text
Implement Console Home Onboarding Wizard Entry And Fixed-Frame Shell. Add the
Console Home launch action and React wizard shell while reusing existing
workflow APIs for all durable data. Keep the route scope-aware, authorized, and
recoverable, with no raw IDs exposed beyond safe route query hints already used
by Admin.

Run focused frontend tests, backend Console Home envelope tests, route tests,
typecheck, build, generated contract freshness checks if contracts changed,
Playwright 1280 x 800 no-scroll validation, accessibility checks for step
navigation, and redaction checks for screenshots and route text.
```

## Spec 075 - Generic Scenario Intake And Durable Draft Blueprint

### Specify Prompt

```text
Create a feature specification for Generic Scenario Intake And Durable Draft
Blueprint. The wizard must let users describe any workflow scenario in neutral
terms, then create a durable editable workflow draft from that input without
using scenario-specific templates or raw JSON.

The intake must capture workflow name, key suggestion, purpose, trigger or
launch mode, expected inputs, desired outputs, optional channels, rough agent
count, coordination pattern, approval needs, and evidence preference. The
resulting blueprint must be a valid draft document transformation persisted
through existing workflow create and full document save APIs. All generated
roles, contracts, nodes, edges, joins, and annotations must remain editable in
later wizard steps and advanced editors.
```

### Plan Prompt

```text
Plan Generic Scenario Intake And Durable Draft Blueprint. Review workflow
create payloads, full document save contracts from Spec 069, workflow document
editor helpers, current three-agent starter logic, validation summaries,
workflow key normalization, and draft revision token behavior.

Design bounded intake screens that fit 1280 x 800 without scrolling. Avoid a
large form on one page; split intake into compact screens for identity,
trigger/input, output, agent shape, and coordination. Define deterministic
client-side blueprint helpers only for editable document scaffolding; backend
save and validation remain authoritative. Ensure the blueprint is generic:
field labels and default values may be neutral, but they must not mention or
encode Design Reviewer Council, Daily Intelligence Briefing, or any tutorial
scenario. Persist the draft after creation and after blueprint application
using existing APIs with revision tokens and idempotency keys.
```

### Tasks Prompt

```text
Generate implementation tasks for Generic Scenario Intake And Durable Draft
Blueprint. Include tasks for intake state modeling, key/display-name helpers,
bounded screen components, generic blueprint generation, draft creation through
existing create APIs, full document save through existing save APIs, validation
refresh, stale save recovery, idempotency keys, tests for arbitrary scenario
inputs, tests that tutorial scenario strings are not hard-coded into defaults,
tests for duplicate keys and invalid names, no-scroll layout checks, and QA
docs for starting from a clean tenant.
```

### Implement Prompt

```text
Implement Generic Scenario Intake And Durable Draft Blueprint. Add the neutral
intake screens and blueprint helper, create or resume durable workflow drafts
through existing APIs, and persist the generated editable document through the
full document save route.

Run focused helper and component tests, workflow create/save tests, stale
revision tests, arbitrary-scenario tests, typecheck, build, generated contract
checks when applicable, Playwright no-scroll checks for every intake screen,
and redaction scans for scenario text in logs, screenshots, and QA artifacts.
```

## Spec 076 - Stepwise Agents, Contracts, And Graph Configuration

### Specify Prompt

```text
Create a feature specification for Stepwise Agents, Contracts, And Graph
Configuration. After the generic intake creates a draft blueprint, users need
wizard screens that let them refine agents, input/output contracts, data
contracts, graph nodes, graph edges, joins, approvals, and graph review without
leaving the bounded onboarding flow.

The feature must reuse the existing workflow document editor helpers,
generated contracts, workflow lookups, full document save route, graph
projection, and validation summaries. Each screen must be small enough for
1280 x 800 with no scrolling. Large role, contract, or edge collections must be
handled through paging or one-item detail screens instead of scrollable lists.
```

### Plan Prompt

```text
Plan Stepwise Agents, Contracts, And Graph Configuration. Review
WorkflowRoleEditor, WorkflowContractEditor, WorkflowTopologyEditor,
WorkflowJoinApprovalEditor, AgentGraphPanel, workflowDocumentEditor helpers,
graph validation findings, and Spec 070 role/graph behavior.

Design a sequence of bounded wizard screens for agents, contracts, graph
topology, joins/approvals, and review. Reuse existing editor logic rather than
forking validation rules. Define save points, dirty-state handling, duplicate
key handling, missing reference recovery, keyboard navigation, compact graph
preview behavior, and section-level validation feedback that links back to the
current wizard screen. Preserve an escape hatch to open advanced editors, but
do not make advanced editors required for the wizard happy path.
```

### Tasks Prompt

```text
Generate implementation tasks for Stepwise Agents, Contracts, And Graph
Configuration. Include tasks for extracting reusable bounded editor primitives
from existing workflow editors, adding role paging/detail screens, adding
contract paging/detail screens, adding graph node and edge screens, adding
join/approval screens, adding compact graph review, wiring saves through the
existing full document save API, refreshing backend validation, mapping
validation findings to wizard steps, adding tests for duplicate/missing role,
contract, node, edge, join, and approval references, adding keyboard and
accessibility tests, adding Playwright no-scroll checks for each screen, and
adding screenshots that prove no text overlap at 1280 x 800.
```

### Implement Prompt

```text
Implement Stepwise Agents, Contracts, And Graph Configuration. Reuse the
existing workflow document editor behavior in bounded wizard screens, persist
all edits through the existing save route, and show backend validation feedback
without browser-only publish or validation decisions.

Run focused editor helper tests, workflow wizard component tests, graph
projection tests, validation mapping tests, frontend typecheck, frontend build,
Playwright 1280 x 800 no-scroll journeys, accessibility checks, and redaction
checks for graph and contract summaries.
```

## Spec 077 - Resource Readiness, Bindings, And Evidence Configuration

### Specify Prompt

```text
Create a feature specification for Resource Readiness, Bindings, And Evidence
Configuration. A generic scenario may need prompts, runtime profiles, model
provider readiness, skill/tool readiness, channel readiness, and required Test
Bench evidence. The wizard must guide users through those decisions using
existing APIs while keeping every screen bounded and scenario-neutral.

The feature must support selecting or creating prompt/profile bindings for
each role, reviewing provider readiness without raw credentials, selecting
eligible skill/tool references, optionally preparing channel or trigger
configuration, creating required Test Bench suite/case evidence, launching
deterministic safe evidence, and showing backend-owned freshness/readiness.
```

### Plan Prompt

```text
Plan Resource Readiness, Bindings, And Evidence Configuration. Review
GovernancePage prompt/profile/provider APIs, WorkflowPromptProfileBinder,
SkillLifecyclePage readiness and binding eligibility APIs, channel readiness
and alias APIs, TestBenchPage suite/case/run APIs, WorkflowTestEvidencePanel,
publish gate evidence summaries, and Specs 031-033, 041-043, 071, and 072.

Design bounded wizard screens for prompts/profiles, provider readiness,
optional skills/tools, optional channels/triggers, and required evidence.
Every screen must fit 1280 x 800 without scroll; use per-role paging and
summary badges rather than large stacked panels. Use existing API actions for
prompt/profile save or selection, skill readiness, channel readiness, suite and
case creation, deterministic evidence launch, and evidence refresh. Raw
secrets, prompt previews outside authorized editors, connector payloads, and
test transcripts must not appear in wizard summaries or QA artifacts.
```

### Tasks Prompt

```text
Generate implementation tasks for Resource Readiness, Bindings, And Evidence
Configuration. Include tasks for per-role prompt/profile binding screens,
provider readiness summaries, skill eligibility summaries, optional channel
setup summaries, Test Bench suite/case/evidence setup, deterministic run launch
from the wizard, evidence freshness refresh, blocked-state recovery, frontend
tests for each resource type, backend route smoke tests for existing API usage,
tenant isolation tests, redaction tests for credentials/prompts/transcripts and
tool payloads, generated type checks, no-scroll Playwright checks, and docs for
safe deterministic setup.
```

### Implement Prompt

```text
Implement Resource Readiness, Bindings, And Evidence Configuration. Compose
the existing governance, skill lifecycle, channel, and Test Bench APIs into
bounded wizard screens. Keep readiness and evidence status backend-owned, and
ensure every prompt/profile, skill, channel, and evidence choice remains
editable in the existing detailed workspaces.

Run focused frontend tests, existing API smoke tests, generated contract
freshness checks, typecheck, build, deterministic evidence tests, tenant
isolation tests, redaction sweeps, Playwright no-scroll and no-overlap checks,
and QA document validation.
```

## Spec 078 - Publish, Launch, And Operational Verification Finish

### Specify Prompt

```text
Create a feature specification for Publish, Launch, And Operational
Verification Finish. After wizard configuration, users need a final path to
validate, publish, launch, and inspect safe runtime evidence without copying
IDs, editing browser URLs, or switching to direct API calls.

The feature must use existing workflow validation, publish gate, publish,
runtime launch, Design Reviews selection when applicable, operations run
inspection, runtime graph, and interaction replay graph APIs. The finish flow
must stay generic: Design Reviews, Telegram, or other channel handoffs appear
only when authorized and relevant to the configured workflow, not as mandatory
scenario-specific steps.
```

### Plan Prompt

```text
Plan Publish, Launch, And Operational Verification Finish. Review
WorkflowValidationPanel, WorkflowPublishPanel, user run workspace, Design
Reviews workflow selector, channel run status pages, operations workbench,
runtime graph and replay graph panels, publish readiness contracts, and Spec
073 launch handoffs.

Design bounded final wizard screens for validation, publish blockers,
confirmation, published bundle summary, launch target selection, deterministic
launch, and evidence inspection. Use existing backend-owned publish readiness
and runtime validation. Preserve tenant scope in handoff links. Show only safe
identifiers and summaries. Provide recovery links back to wizard steps when
validation or publish is blocked. Verify every finish screen fits 1280 x 800
without scrolling.
```

### Tasks Prompt

```text
Generate implementation tasks for Publish, Launch, And Operational
Verification Finish. Include tasks for validation summary screen, publish gate
screen, publish confirmation, published bundle refresh, generic launch target
selection, runtime launch prefill, optional Design Reviews/channel handoff only
when applicable, operations run evidence links, runtime graph and replay graph
inspection links, recovery links to wizard steps, frontend tests, backend route
smoke tests for existing validation/publish/launch APIs, Playwright happy-path
and blocked-path journeys, tenant isolation tests, redaction tests, and QA docs.
```

### Implement Prompt

```text
Implement Publish, Launch, And Operational Verification Finish. Wire the wizard
completion path to existing validation, publish, runtime, operations, and graph
evidence surfaces. Keep launch targets generic and authorization-aware, and
label unavailable or blocked states truthfully.

Run focused workflow validation and publish tests, runtime launch tests,
operations/graph handoff tests, frontend typecheck, build, generated contract
checks when applicable, Playwright 1280 x 800 no-scroll journeys for success
and blocker recovery, redaction sweeps, tenant isolation tests, and QA docs
validation.
```

## Spec 079 - Non-Scrolling Wizard QA, Docs, And Guardrails

### Specify Prompt

```text
Create a feature specification for Non-Scrolling Wizard QA, Docs, And
Guardrails. The wizard must ship with evidence that every onboarding screen is
generic, fits a 1280 x 800 viewport without scrolling, uses existing APIs, and
preserves live-data, redaction, accessibility, performance, and terminology
guardrails.

The feature must add browser-first docs and automated checks that cover a clean
tenant happy path, resume path, blocked validation path, stale evidence path,
denied scope path, and at least two arbitrary workflow scenarios that are not
the tutorial scenarios. It must prevent regressions that reintroduce hard-coded
tutorial labels, raw secrets, raw prompts outside authorized editors, raw test
transcripts, scroll-dependent wizard screens, or fake/demo setup data.
```

### Plan Prompt

```text
Plan Non-Scrolling Wizard QA, Docs, And Guardrails. Review existing QA docs for
Specs 026-073, Playwright runners, run_spec_qa manifests, live-data guardrails,
transitional label gates, frontend visual tests, accessibility checks, docs
validation, curl_testing.md coverage policy, and tutorial guidance.

Design a QA strategy that proves the wizard works without relying on the two
tutorial scenarios. Add Playwright utilities that fail when the document,
Admin shell main region, or wizard frame has vertical scroll at 1280 x 800.
Add text-overlap and screenshot checks for the fixed-frame screens. Add docs
that teach the generic wizard flow while keeping API calls secondary. Update
guardrails so hard-coded tutorial scenario labels, fake setup data, and
scroll-dependent wizard layouts are caught before merge.
```

### Tasks Prompt

```text
Generate implementation tasks for Non-Scrolling Wizard QA, Docs, And
Guardrails. Include tasks for QA079 guide, UI walkthrough, user guide, QA
environment, validation manifest, Playwright no-scroll helper, Playwright clean
tenant happy path, resume path, blocked validation path, stale evidence path,
denied scope path, two arbitrary-scenario paths, screenshot review, accessible
name and keyboard checks, performance budget checks, redaction scans, hardcoded
tutorial label scans, live-data/mock-data scans, docs validation, curl coverage
decision, multi-agent-curl-test decision or run, and PR review notes.
```

### Implement Prompt

```text
Implement Non-Scrolling Wizard QA, Docs, And Guardrails. Add the QA docs,
validation manifests, Playwright utilities, scenario-neutral browser journeys,
redaction scans, live-data guardrails, terminology checks, and review notes
needed to prove the wizard is generic and usable at 1280 x 800 without
scrolling.

Run QA document validation, Playwright desktop 1280 x 800 no-scroll journeys,
accessibility checks, performance checks, frontend tests, typecheck, build,
generated contract checks when applicable, Ruff, mypy, redaction scans,
hard-coded tutorial label scans, live-data/mock-data guardrails, Spec QA, and
multi-agent-curl-test if any API behavior changed.
```

## Completion Review Checklist

Before considering this roadmap complete, verify all of the following:

- Console Home contains an authorized setup action that launches the wizard.
- The wizard can start from a clean tenant or resume an existing draft.
- The wizard accepts arbitrary scenario descriptions without hard-coded
  tutorial defaults.
- Durable workflow drafts are created and saved through existing workflow APIs.
- Users can configure agents, contracts, graph nodes, graph edges, joins, and
  approvals without raw JSON.
- Users can select or create prompt/profile bindings through existing
  governance APIs.
- Users can review provider, skill, and channel readiness through existing APIs.
- Users can create required Test Bench evidence and refresh publish readiness
  without copying internal IDs.
- Publish remains blocked on backend-owned missing, stale, failed, denied, or
  cross-tenant evidence.
- Launch targets are generic, authorized, and shown only when relevant.
- Runtime and graph evidence open through visible UI links.
- Every wizard screen passes a 1280 x 800 no-scroll Playwright assertion.
- Screenshots show no text overlap, clipped controls, hidden footer actions, or
  scroll-dependent content.
- No raw secrets, credentials, private payloads, raw completions, raw test
  transcripts, local paths, stack traces, or unauthorized tenant labels appear
  in UI, screenshots, docs, logs, or exports.
- QA docs teach the browser path first and keep API/curl checks secondary.
