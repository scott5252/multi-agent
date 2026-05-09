# Spec 071 - Prompt Profile Creation And Per-Agent Binding UI: Plan

Roadmap source: `docs/workflow_setup_specs.md`
React UI2 context source: `docs/react_ui2.md`

## Deterministic Targets

- Feature directory: `specs/071-prompt-profile-creation-and-per-agent-binding-ui`
- Git branch: `codex/071-prompt-profile-creation-and-per-agent-binding-ui`
- QA id: `qa071`
- QA database: `multi_agent_platform_qa071`
- Post-spec curl-test database: `multi_agent_curl_test`
- Curl regression source: `curl_testing.md`

## Workflow Setup Autonomy Rules

- Continue directly to the next spec after validation passes.
- Do not commit, stage, push, or create pull requests.
- Keep all local QA deterministic with local-principal auth and mocked provider/model/tool paths unless a spec explicitly allows otherwise.
- Preserve tenant isolation, redaction, auditability, backend-owned validation and publish readiness, generated TypeScript contract integrity, keyboard-readable graph equivalents, and truthful live-data UI states.
- Use visible UI navigation in QA and Playwright after login; do not require hand-edited browser URLs to configure custom workflows.
- Do not expose raw secrets, credentials, provider payloads, prompts outside authorized edit forms, completions, memory contents, private messages, raw tool payloads, raw test transcripts, stack traces, or unauthorized tenant labels.

## Plan Prompt

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

## Required Post-Spec Validation Contract

After implementation, the active spec must pass QA document validation, `run_spec_qa.py`, Playwright UI validation, frontend quality gates, curl_testing.md coverage review/update, and the `multi-agent-curl-test` runner before the next spec starts. If the spec adds or changes an API, update `curl_testing.md` in the same spec and fix the implementation or curl commands until the multi-agent curl regression passes. Every spec must have at least one Playwright flow; Specs 070 through 073 must strengthen the generated smoke flow into journeys that exercise the new browser workflow setup controls, desktop/mobile screenshots, reload persistence, accessibility alternatives, and no-overlap checks. Do not pause between completed specs and do not create git commits. After Spec 073 passes, run the final whole-roadmap stability gate from the `speckit-workflow-setup-autopilot` skill before reporting completion.

## Global Prompt Prefix

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

## Workflow Setup Roadmap Context

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
