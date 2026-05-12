# Spec 079 - Non-Scrolling Wizard QA, Docs, And Guardrails: Tasks

Roadmap source: `docs/wizard_ui.md`

## Deterministic Targets

- Feature directory: `specs/079-non-scrolling-wizard-qa-docs-and-guardrails`
- Git branch: `codex/079-non-scrolling-wizard-qa-docs-and-guardrails`
- QA id: `qa079`
- QA database: `multi_agent_platform_qa079`


## Autonomy Rules

- Continue directly to the next spec after validation passes.
- Keep local QA deterministic with local-principal auth and mocked provider/model/tool paths unless a spec explicitly allows otherwise.
- Preserve tenant isolation, redaction, auditability, backend-owned validation and publish readiness, generated TypeScript contract integrity, truthful live-data UI states, and browser-first QA.
- Do not expose raw secrets, credentials, provider payloads, prompts outside authorized edit forms, completions, memory contents, private messages, raw tool payloads, raw test transcripts, stack traces, local filesystem paths, or unauthorized tenant labels.

## Tasks Prompt

Generate implementation tasks for Non-Scrolling Wizard QA, Docs, And
Guardrails. Include tasks for QA079 guide, UI walkthrough, user guide, QA
environment, validation manifest, Playwright no-scroll helper, Playwright clean
tenant happy path, resume path, blocked validation path, stale evidence path,
denied scope path, two arbitrary-scenario paths, screenshot review, accessible
name and keyboard checks, performance budget checks, redaction scans, hardcoded
tutorial label scans, live-data/mock-data scans, docs validation, curl coverage
decision, multi-agent-curl-test decision or run, and PR review notes.

## Required Post-Spec Validation Contract

After implementation, the active spec must pass QA document validation, `run_spec_qa.py`, Playwright UI validation when browser behavior exists, focused backend/frontend quality gates, and curl coverage review for new or changed APIs before the next spec starts. Update the spec status files and queue status before continuing. Do not stage, commit, push, or create pull requests unless the user explicitly asks.

## Global Prompt Prefix

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

## Roadmap Context

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

## Roadmap Completion Notes

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
