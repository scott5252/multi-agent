# Remove Mock Data Spec Kit Roadmap

Created: 2026-05-07

This roadmap covers the work needed to remove backend-generated deterministic
fixture/demo data from the React admin surfaces introduced in Specs 026 through
047. The goal is not only to delete obvious hardcoded rows, but to make the
browser display live, authorized data from durable services and PostgreSQL, or
honest empty states when no live data exists.

Use this as a prompt source. For each proposed spec, run the commands in order:

1. `/speckit.specify`
2. `/speckit.clarify`
3. `/speckit.plan`
4. `/speckit.tasks`
5. `/speckit.analyze`
6. `/speckit.implement`

## Executive Summary

Removing the deterministic React data is a high-value, medium-to-high effort
cleanup. The React UI currently fetches backend JSON; it is not browser-only
mocking. However, many backend React projection builders return fixed QA/demo
payloads instead of querying repositories. Removing those builders will make the
UI reflect actual database state, which is what production needs.

The main user-visible impact is that many local pages that currently look
populated will become empty until the database is seeded through real APIs or
repositories. That is the desired truthfulness, but it means QA guides,
Playwright flows, screenshots, and tests must create real setup data first.

## Level Of Effort

Overall estimate: 12 focused specs, roughly 6 to 10 engineering weeks for
one senior engineer, or 3 to 5 weeks for a small parallel team after Spec 048
is complete. The highest-risk pieces are workflow builder mutations,
governance/provider readiness, skill lifecycle, test bench, and channel run
status because they touch authorization, audit, revision, artifact, and
redaction behavior.

| Area | Effort | Impact |
|------|--------|--------|
| Inventory and guardrails | Medium | Prevents future mock regressions and gives a reliable worklist. |
| Sample/pattern route retirement | Low to Medium | Removes harmless demo surface from production navigation; may affect frontend tests. |
| Workflow builder and registry | High | Changes highly visible workflow UI from demo rows to real drafts, revisions, validations, publish gates, and versions. |
| Governance | High | Requires live provider, prompt, profile, routing, policy, and provenance projections without leaking secrets or raw prompts. |
| Skill lifecycle | High | Requires package/install/readiness/diagnostic data to come from skill registry and gateway services. |
| Test bench | High | Requires suite/case/run/artifact/publish-gate UI to use real test-bench repositories. |
| Memberships and access | Medium to High | Replaces safe fake directory/access records with real principal, membership, role, invitation, and audit rows. |
| Channels, Telegram, briefing | High | Replaces QA036 fixed aliases, delivery attempts, identities, run IDs, and preference profiles with real persisted state. |
| Usage analytics | Medium | Switches React usage dashboard from in-code `USAGE_EVENTS` to `llm_usage_events` and export requests. |
| Operations and run debug | Medium to High | Replaces fixture workbench cards/timelines with operations, reliability, audit, runtime, usage, gateway, and channel records. |
| Final decommission gate | Medium | Adds scanners, route assertions, Playwright checks, and documentation proving live-only behavior. |
| Transitional React terminology removal | Low to Medium | Removes migration-era "React" wording from user-facing navigation, breadcrumbs, headings, page titles, and compatibility copy. |

## Expected Product Impact

- Empty states become common in fresh local databases. They must say what live
  data is missing without inventing rows.
- QA data must be seeded by documented setup flows, APIs, repositories, or
  migrations. Test fixture modules may remain under `tests/` and
  `frontend/admin/src/test`, but production route handlers cannot import or
  mirror them.
- Existing screenshots and Playwright assertions that rely on `qa031`,
  `qa032`, `qa033`, `qa034`, `qa035`, or `qa036` labels will need replacement
  with seeded live records.
- Demo-friendly route names such as `/admin/app/patterns` should be removed
  from production navigation or gated behind explicit development/test-only
  settings.
- Some route responses should add provenance metadata so reviewers can confirm
  whether the response came from live repositories, computed system inventory,
  or an honest empty state.
- Migration-era technology labels should disappear from the product UI. Users
  should see "Admin", "Skill tools Diagnostics", and domain page names instead
  of "React Admin", "Skill tools Diagnostics React", or similar implementation
  labels.

## Live Data Policy

Allowed in production code:

- Live database-backed domain data loaded through repositories/services.
- Computed system metadata that is intrinsically not database state, such as
  React asset manifest availability, route inventory, feature flags, and
  scanner-derived migration evidence.
- Empty, loading, denied, unavailable, stale, conflict, and validation states
  derived from real service outcomes.
- Test factories and fixtures under test-only paths.

Not allowed in production React route handlers or projection services:

- Fixed domain rows such as a fake "Daily briefing workflow" when no workflow
  draft/version exists.
- Fixed `qa0xx` IDs, audit references, trace IDs, artifact references, link
  tokens, run IDs, prompt/profile revisions, package versions, usage events, or
  membership records returned as if they are live data.
- In-memory domain collections such as `USAGE_EVENTS` used by production routes.
- Fake mutation success that does not persist durable state or call the domain
  service that owns the mutation.
- Browser code that supplies production revision IDs, audit IDs, principal IDs,
  or idempotency defaults that should come from backend contracts.

## Current Mock/Demo Surface Inventory

This is the initial known inventory. Spec 048 must regenerate it with a scanner.

| Surface | Current deterministic source |
|---------|------------------------------|
| React sample patterns | `src/multi_agent_platform/api/routers/admin_react.py` sample envelope, sample records, sample mutation, and sample export helpers. |
| Workflow builder/registry | `src/multi_agent_platform/admin/workflow_builder.py` fixed draft, lineage, registry, reference, validation, publish, revision, version, sharing, and graph data. |
| Governance | `src/multi_agent_platform/admin/governance.py` fixed providers, prompts, profiles, routing previews, policy history, probes, and provenance. |
| Skill lifecycle | `src/multi_agent_platform/admin/skill_lifecycle.py` fixed package, installation, connector readiness, diagnostics, grants, smoke tests, binding previews, and audit rows. |
| Test bench React | `src/multi_agent_platform/testing/agent_bench/react_test_bench.py` fixed suites, cases, assertions, runs, artifacts, gates, and audit rows. |
| Memberships React | `src/multi_agent_platform/admin/memberships/react_memberships.py` fixed users, invitations, role grants, status actions, access history, and audit timeline. |
| Channels/Telegram/briefing React | `src/multi_agent_platform/admin/channel_telegram_briefing/react_channel_telegram_briefing.py` fixed tenant readiness, Telegram config, aliases, identities, deliveries, run status, link tokens, preference profiles, and mutation results. |
| Usage React | `src/multi_agent_platform/admin/usage/react_usage.py` fixed `USAGE_EVENTS`, export IDs, rollups, drilldowns, and trend points. |
| Operations workbench | `src/multi_agent_platform/operations/workbench.py` deterministic health cards, pressure panels, timelines, run-debug summaries, and exports. |
| Frontend action defaults | Several React components contain `qa0xx` revision/idempotency/default payload values that should instead come from backend action metadata or user input. |
| Migration hardening | Some route/decommission panels are legitimate computed system evidence; Spec 048 must classify which entries are scanner-derived versus fake. |

## Recommended Spec Breakdown

| Proposed spec | Name | Depends on | Purpose |
|---------------|------|------------|---------|
| 048 | Live Data Inventory And Mock Guardrails | 026-047 | Inventory every production React mock/demo data source, define live-only rules, and add scanners/tests that fail on prohibited fixture data. |
| 049 | React Contract Provenance And Sample Route Retirement | 048, 026-028, 039 | Add response provenance/empty-state conventions, remove or dev-gate the sample patterns route, and stop production browser code from carrying QA defaults. |
| 050 | Workflow React Live Data | 048-049, 003, 013, 015, 020, 024, 030, 040 | Replace workflow React builders with live repository/service projections and durable mutations. |
| 051 | Governance React Live Data | 048-049, 007, 011, 012, 025, 031, 041 | Replace governance builders with live provider, prompt, profile, routing, policy, credential, and provenance data. |
| 052 | Skill Lifecycle React Live Data | 048-049, 014, 014-v2, 021, 032, 042 | Replace skill lifecycle builders with live package, installation, readiness, diagnostics, eligibility, and audit data. |
| 053 | Test Bench React Live Data | 048-049, 015, 020, 024, 025, 033, 043 | Replace test-bench builders with live suite, case, assertion, run, artifact, gate, and audit projections. |
| 054 | Membership And Access React Live Data | 048-049, 002, 018, 034, 045 | Replace membership builders with live principal, invitation, membership, role-grant, access-decision, and audit data. |
| 055 | Channels, Telegram, Briefing React Live Data | 048-049, 006, 017, 022, 023, 036, 045, 046 | Replace channel/Telegram/briefing builders with live tenant config, alias, identity, delivery, run, and preference data. |
| 056 | Usage React Live Data | 048-049, 016, 020, 021, 025, 035, 044 | Replace usage React builders with live usage repository summaries, events, pricing, rollups, reconciliation, and exports. |
| 057 | Operations And Run Debug React Live Data | 048-049, 008, 009, 019, 020, 021, 022, 025, 029, 044 | Replace operations workbench fixture cards and run-debug panels with live operations, reliability, audit, runtime, provider, channel, skill, and usage evidence. |
| 058 | Live-Only UI Decommission Gate | 050-057 | Remove obsolete deterministic builders, enforce scanners in CI, update QA/docs, and prove all React routes show live data or honest empty states. |
| 059 | Admin UI Transitional React Label Removal | 049, 058 | Remove implementation-era "React" wording from production UI navigation, breadcrumbs, shell titles, page headings, command/search results, error states, and compatibility copy while preserving internal technical references. |

## Global Prompt Prefix

Prepend or keep in mind for every prompt below:

```text
Use the current multi-agent platform repository context after Specs 026 through
047. The React admin UI is now React-only from a presentation standpoint, but
many React JSON endpoints still return deterministic backend fixture/demo data.
The goal is to make every production React route display live, authorized data
from durable services and PostgreSQL, or an honest empty/denied/unavailable
state when no live data exists.

Preserve the constitution, specs 001 through 047, FastAPI domain services,
PostgreSQL source of truth, Auth0 production authentication,
AUTH_MODE=local_principal browser QA, tenant isolation, audit fail-closed
behavior, redaction rules, runtime version pinning, secret hygiene, object
storage boundaries, generated TypeScript contracts, Playwright evidence, QA
docs, and at least 90 percent relevant coverage.

React must consume backend-owned JSON contracts generated from Pydantic schemas.
Do not move authorization, tenant scoping, validation, credential readiness,
publish readiness, redaction, audit, or mutation decisions into browser-only
logic. Do not replace backend fixture data with frontend fixture data.

Production route handlers and projection services must not return hardcoded
domain entities, fixed qa0xx IDs, fake audit references, fake artifact
references, fake link tokens, fake run IDs, fake usage events, fake workflows,
fake providers, fake prompts, fake skill packages, fake users, or fake delivery
attempts. Test fixtures may remain in test-only directories and QA setup may
seed real databases, but production UI code must not depend on test fixture
modules.

Every spec must prove both Auth0-shaped principal behavior with backend route
tests and local-principal behavior with browser Playwright flows. Every route
must be tested with live seeded data and with an empty database state. Empty
states must be truthful and must not invent rows.

Raw secrets, credential values, provider authorization headers, raw prompts,
raw completions, memory contents, raw run payloads, private channel messages,
raw tool payloads, raw test transcripts, full Telegram identifiers, link
tokens after creation, local filesystem paths, stack traces, and unauthorized
tenant labels must never appear in React UI, redirects, exports, screenshots,
QA artifacts, logs, or docs.
```

## Spec 048 - Live Data Inventory And Mock Guardrails

### Specify Prompt

```text
Create a feature specification for Live Data Inventory And Mock Guardrails.
The React admin surfaces from Specs 026 through 047 fetch backend JSON, but many
backend projection builders still return deterministic fixture/demo data. The
goal is to produce a deletion-grade inventory of every production code path
that can return hardcoded domain rows, fixed qa0xx IDs, fake audit references,
fake artifact references, fake link tokens, fake usage events, fake run IDs,
or fake mutation success. The feature must define live-only policy, classify
which computed system metadata is allowed, and add guardrails that prevent new
mock data from being exposed by production React routes.
```

### Clarify Prompt

```text
Run clarification for the live data inventory. Focus on what counts as mock
data versus legitimate computed system metadata, whether dev-only sample routes
may remain behind explicit settings, how to treat QA seed data in dedicated QA
databases, whether fixture markers like qa031 are prohibited in production
responses, and which scanners must be CI-blocking. Recommended defaults: allow
test-only fixtures under tests and frontend/admin/src/test, allow computed
system metadata only when derived from code/config/scanners, block hardcoded
domain entities in production routes, and require every React route to pass
both live-data and empty-state checks.
```

### Plan Prompt

```text
Plan the live data inventory and guardrail feature. Add a scanner that maps
production React route handlers, projection builders, frontend components,
generated contracts, and built assets back to fixture markers. Classify each
finding by severity, route, owner spec, durable data source, and replacement
spec. Add route tests that call every /admin/app JSON endpoint with a fresh
database and verify responses do not contain prohibited fixture markers unless
the route is explicitly classified as computed system metadata. Add docs and
CI checks that keep production code from importing test fixture modules.
```

### Tasks Prompt

```text
Generate tasks for Live Data Inventory And Mock Guardrails. Include scanner
implementation, inventory schema, fixture marker taxonomy, production route
enumeration, frontend source scan, built asset scan, response scan, allowlist
for computed system metadata, CI integration, route tests for platform and
tenant principals, empty database checks, seeded database checks, docs,
QA guide, reviewer guide, and migration dashboard evidence. Do not remove
the deterministic builders yet except for scanner false positives.
```

### Analyze Prompt

```text
Analyze the live data inventory for missed production routes, overbroad
allowlists, false positives in test directories, false negatives in generated
assets, missing endpoint response scans, missing tenant/cross-tenant cases,
missing empty-state cases, and replacement specs that are too large or lack
clear durable data sources.
```

### Implement Prompt

```text
Implement the inventory and guardrails only. Run the scanner, backend route
tests, frontend tests, generated contract checks, docs validation, and a local
database response scan. Produce the inventory artifact and update the migration
dashboard with mock-data removal readiness. Stop before replacing major
domain builders.
```

## Spec 049 - React Contract Provenance And Sample Route Retirement

### Specify Prompt

```text
Create a feature specification for React Contract Provenance And Sample Route
Retirement. The goal is to establish shared response provenance, empty-state,
and live-data conventions for React contracts, remove or development-gate the
sample patterns route, and stop production frontend components from supplying
QA revision/idempotency defaults. Production React pages must either display
live repository-backed data, computed system metadata, or a truthful empty
state that names the missing live setup without inventing records.
```

### Clarify Prompt

```text
Run clarification for contract provenance and sample route retirement. Focus
on whether provenance is a shared envelope field or per-page metadata, whether
/admin/app/patterns is removed, hidden, or dev-only, how empty states describe
missing live data, whether action idempotency defaults are backend-supplied or
user-generated, and how generated TypeScript contracts change. Recommended
defaults: hide sample pages in production, keep component tests with test-only
fixtures, add backend-owned provenance/empty-state metadata where useful, and
make frontend defaults derive from backend action metadata or generated client
state rather than hardcoded qa strings.
```

### Plan Prompt

```text
Plan the contract provenance and sample route retirement feature. Update shared
admin schemas, frontend state components, action metadata, generated contracts,
tests, and documentation. Remove the sample patterns page from production
navigation or gate it behind an explicit development-only setting. Add route
tests proving production cannot reach sample data unless the setting is enabled.
Add Playwright validation for empty-state presentation and no fixture markers.
```

### Tasks Prompt

```text
Generate tasks for contract provenance and sample route retirement. Include
schema changes, TypeScript regeneration, frontend state component updates,
route navigation changes, sample route gating/removal, production route tests,
dev-only route tests if retained, fixture marker scanner updates, frontend
tests, Playwright empty-state screenshots, docs updates, QA guide, and PR notes.
```

### Analyze Prompt

```text
Analyze contract provenance and sample route retirement for inconsistent
envelope fields, broken generated TypeScript, stale frontend tests, sample
route leakage in navigation/search/saved filters, production access to sample
mutations, and empty states that imply demo records exist.
```

### Implement Prompt

```text
Implement contract provenance and sample route retirement. Regenerate contracts,
run backend tests, frontend typecheck/tests/build, scanner checks, and
Playwright empty-state validation. Confirm /admin/app/patterns no longer shows
production sample data unless explicitly dev-gated.
```

## Spec 050 - Workflow React Live Data

### Specify Prompt

```text
Create a feature specification for Workflow React Live Data. Replace the
deterministic workflow React builders with live projections from the workflow
registry, validation, publish-gate, sharing, artifact, and test-bench evidence
services. The React workflow registry and builder must list real workflow
lineages, drafts, revisions, validation results, published bundles, graph
documents, references, publish readiness, required evidence, and sharing state.
When the database has no workflows, the UI must show truthful empty states and
creation actions. Save, validate, publish, restore, and copy actions must call
the durable workflow services and persist or reject state through existing
revision/audit/idempotency behavior.
```

### Clarify Prompt

```text
Run clarification for workflow live data. Focus on list/create/detail route
shape, whether the builder opens the latest draft or requires a draft ID, how
to paginate/search/sort real workflows, how graph preview is generated from
stored documents, how required test-bench evidence is queried, how stale
revision conflicts are represented, and which QA workflows are seeded. Default
to reusing existing workflow registry repositories/services, not inventing new
tables.
```

### Plan Prompt

```text
Plan Workflow React Live Data. Replace src/multi_agent_platform/admin/workflow_builder.py
deterministic builders with service-backed projection functions. Wire
admin_react.py endpoints to WorkflowRegistryRepository, AdminService,
ArtifactRepository, AgentTestBenchService publish-gate evidence, and existing
validation/publish services. Update frontend to handle real pagination,
empty states, route parameters, stale conflicts, and backend-owned actions.
Include database seed helpers for QA, route tests, repository tests, contract
tests, frontend tests, Playwright create/edit/validate/publish flows, and
scanner assertions that old qa030 fixed IDs are absent from production
responses.
```

### Tasks Prompt

```text
Generate tasks for Workflow React Live Data. Include projection service
design, workflow list query, draft detail query, version detail query, graph
preview from stored documents, reference catalog from live prompts/profiles/
skills/providers where available, validation action persistence, publish action
persistence, required evidence query, sharing projection, empty-state UI,
seeded QA data setup, Auth0-shaped route tests, local-principal Playwright
flows, redaction checks, scanner updates, docs, QA guide, and PR notes.
```

### Analyze Prompt

```text
Analyze Workflow React Live Data for any route still using DEFAULT_DRAFT_ID,
DEFAULT_LINEAGE_ID, qa030 revisions, fake audit references, fake publish
evidence, fake graph nodes, fake version details, or non-persistent mutation
results. Check tenant scoping, platform scope, empty database behavior, stale
revision behavior, publish gate accuracy, redaction of workflow documents, and
bounded query performance.
```

### Implement Prompt

```text
Implement Workflow React Live Data. Seed QA workflows through real APIs or
repositories, migrate routes to live projections, update frontend empty states,
remove obsolete deterministic workflow builders, regenerate contracts, and run
backend tests, frontend typecheck/tests/build, scanner checks, Spec QA, and
Playwright workflow validation.
```

## Spec 051 - Governance React Live Data

### Specify Prompt

```text
Create a feature specification for Governance React Live Data. Replace
deterministic governance builders with live data from model provider,
credential-reference, prompt library, runtime profile, model-skill routing,
policy history, gateway diagnostics, and run provenance services. The UI must
show real provider connections, health snapshots, credential readiness,
prompt lineages/drafts/versions/render tests, profile drafts/versions, routing
history/previews, policy records, and run provenance. Empty states must be
truthful when no providers, prompts, profiles, or runs exist.
```

### Clarify Prompt

```text
Run clarification for governance live data. Focus on safe prompt summary versus
raw prompt content, provider health freshness, credential reference display,
which probes are live versus explicitly disabled in local QA, routing preview
inputs, profile resolution scope, and provenance lookup behavior. Default to
using existing provider, prompt, profile, model-skill config, gateway, and
audit repositories; no raw prompt/completion/secret data may reach React.
```

### Plan Prompt

```text
Plan Governance React Live Data. Replace src/multi_agent_platform/admin/governance.py
fixed data with live projection services. Wire admin_react.py governance
endpoints to ModelProviderRepository, PromptRepository, AgentProfileRepository,
ModelSkillConfigRepository, ProviderSecretResolver diagnostics, gateway health
records, usage/provenance records, and audit services. Preserve platform-only
probe/credential actions and tenant-scoped read behavior. Add QA seed flows,
empty-state tests, route tests, frontend tests, Playwright validation, redaction
scans, and scanner assertions that qa031 fixed data is absent from production
responses.
```

### Tasks Prompt

```text
Generate tasks for Governance React Live Data. Include provider list/detail
projection, health snapshot projection, credential reference readiness,
prompt list/history/preview using safe fixtures stored with prompt records,
profile list/history/resolution, routing preview backed by policy services,
policy history, run provenance, platform/tenant authorization, mutation
persistence, empty states, QA seeding, route tests, repository tests, frontend
tests, Playwright flows, redaction scans, docs, QA guide, and PR notes.
```

### Analyze Prompt

```text
Analyze Governance React Live Data for fixed qa031 providers, prompt revisions,
profile revisions, fake probe results, fake credential fingerprints, fake
routing previews, fake policy history, fake provenance, raw prompt leakage,
secret leakage, tenant leakage, and non-persistent mutations.
```

### Implement Prompt

```text
Implement Governance React Live Data. Replace deterministic builders, seed live
QA providers/prompts/profiles/routing records, keep live probes disabled unless
explicitly approved by settings, regenerate contracts, and run backend tests,
frontend typecheck/tests/build, scanner checks, redaction sweeps, Spec QA, and
Playwright governance validation.
```

## Spec 052 - Skill Lifecycle React Live Data

### Specify Prompt

```text
Create a feature specification for Skill Lifecycle React Live Data. Replace
deterministic skill lifecycle builders with live projections from skill package,
version, tenant grant, installation, credential, readiness, smoke-test,
quarantine, audit, governed connector, and SkillExecutionGateway services.
React must display only real packages, versions, installations, credential
reference readiness, smoke-test evidence, binding eligibility, connector
diagnostics, quarantine decisions, withdrawal state, and audit records.
```

### Clarify Prompt

```text
Run clarification for skill lifecycle live data. Focus on package publication
candidate persistence, manifest summary storage, tenant grant source, install
and credential mutation behavior, readiness/smoke-test execution modes,
binding eligibility context choices, connector diagnostics, quarantine actions,
and empty states. Default to existing skill registry services and repositories,
with no raw manifest payloads, credentials, or connector payloads in React.
```

### Plan Prompt

```text
Plan Skill Lifecycle React Live Data. Replace src/multi_agent_platform/admin/skill_lifecycle.py
fixed data with service-backed projections over SkillRegistryRepository,
SkillRegistryService, readiness/smoke runners, artifact store, quarantine
service, SkillExecutionGateway diagnostics, and audit records. Add durable
candidate/grant/install/credential/readiness/diagnostic/eligibility mutations.
Add QA seed data, route tests, repository tests, frontend tests, Playwright
flows, scanner assertions for qa032 removal, and redaction checks.
```

### Tasks Prompt

```text
Generate tasks for Skill Lifecycle React Live Data. Include live package list,
package version detail, candidate workspace, tenant grant projection, discovery
projection, installation projection, credential options, smoke-test history,
connector readiness, diagnostics, binding eligibility, audit timeline, mutation
persistence, empty states, QA seeding, Auth0-shaped tests, local-principal
Playwright tests, scanner updates, docs, QA guide, and PR notes.
```

### Analyze Prompt

```text
Analyze Skill Lifecycle React Live Data for qa032 package/install IDs, fake
credential fingerprints, fake connector evidence, fake smoke-test results, fake
audit records, fake binding previews, raw manifest leakage, secret leakage,
cross-tenant grants, and non-persistent mutations.
```

### Implement Prompt

```text
Implement Skill Lifecycle React Live Data. Seed live skill packages and
installations, migrate projections and actions to existing services, remove
obsolete deterministic builders, regenerate contracts, and run backend tests,
frontend typecheck/tests/build, scanner checks, redaction sweeps, Spec QA, and
Playwright skill lifecycle validation.
```

## Spec 053 - Test Bench React Live Data

### Specify Prompt

```text
Create a feature specification for Test Bench React Live Data. Replace the
deterministic test-bench React projection with live data from agent test suite,
case, assertion, run, run step, artifact, publication requirement, publish-gate,
and audit repositories/services. React must display real suites, cases,
assertions, run launcher metadata, runs, progress, diagnostics, artifacts,
publish-gate evidence, and audit records. Empty states must be truthful when no
suites or runs exist.
```

### Clarify Prompt

```text
Run clarification for test bench live data. Focus on suite/case authoring,
safe execution modes, target workflow/profile references, launch idempotency,
progress polling, artifact access grants, publish-gate freshness, trace
redaction, and QA seed runs. Default to AgentTestBenchService and
AgentTestRepository as the source of truth.
```

### Plan Prompt

```text
Plan Test Bench React Live Data. Replace
src/multi_agent_platform/testing/agent_bench/react_test_bench.py fixed data
with live projections over AgentTestRepository, AgentTestBenchService,
ArtifactRepository/storage, workflow publish-gate service, usage summaries,
and audit records. Add durable suite/case/run/gate refresh mutations, empty
states, QA seed helpers, route tests, repository tests, frontend tests,
Playwright flows, scanner assertions for qa033/qa043 removal, and redaction
checks for raw transcripts and fixtures.
```

### Tasks Prompt

```text
Generate tasks for Test Bench React Live Data. Include live dashboard metrics,
suite list/detail, case list/detail, assertion summaries, run list/detail,
progress projection, trace/artifact projection, publish gate evidence,
audit timeline, mutation persistence, empty states, QA seeding, route tests,
frontend tests, Playwright flows, scanner updates, docs, QA guide, and PR notes.
```

### Analyze Prompt

```text
Analyze Test Bench React Live Data for qa033/qa043 suite IDs, fake runs, fake
artifacts, fake gates, fake audit records, raw transcripts, unsafe fixture
payloads, cross-tenant target access, non-persistent authoring mutations, and
publish-gate evidence that is not repository-backed.
```

### Implement Prompt

```text
Implement Test Bench React Live Data. Seed live suites/cases/runs/artifacts
through existing services, migrate React routes to live projections, remove
obsolete deterministic test-bench builders, regenerate contracts, and run
backend tests, frontend typecheck/tests/build, scanner checks, redaction sweeps,
Spec QA, and Playwright test-bench validation.
```

## Spec 054 - Membership And Access React Live Data

### Specify Prompt

```text
Create a feature specification for Membership And Access React Live Data.
Replace deterministic membership React builders with live projections from
principal identity, invitation, tenant membership, role grant, access decision,
support override, and membership audit repositories/services. React must show
real users, masked identity details, invitations, memberships, role grants,
status actions, access history, and audit records for the authorized scope.
Empty states must be truthful when the tenant has no users or grants.
```

### Clarify Prompt

```text
Run clarification for membership/access live data. Focus on platform versus
tenant admin authority, subject/email masking, local-principal bootstrap rows,
role assignment guardrails, next-request grant refresh, invitation replay,
status transitions, access-decision history, audit retention, and QA seed
principals. Default to MembershipService, MembershipRepository,
AccessControlRepository, and AuditRepository as sources of truth.
```

### Plan Prompt

```text
Plan Membership And Access React Live Data. Replace
src/multi_agent_platform/admin/memberships/react_memberships.py fixed data with
service-backed projections and durable mutations. Wire admin_react.py
membership endpoints to MembershipService/Repository, AccessControlRepository,
AuditService, and safe redaction helpers. Add seeded QA principals, route
tests, repository tests, frontend tests, Playwright flows, scanner assertions
for qa034 removal, and cross-tenant denial checks.
```

### Tasks Prompt

```text
Generate tasks for Membership And Access React Live Data. Include live
directory query, invitation list/query, role grant list/query, tenant
membership list/query, access history, audit timeline, invitation mutation,
principal link mutation, role grant/revoke mutation, status mutations,
empty states, QA seeding, route tests, frontend tests, Playwright flows,
redaction scans, scanner updates, docs, QA guide, and PR notes.
```

### Analyze Prompt

```text
Analyze Membership And Access React Live Data for qa034 user IDs, fake
invitations, fake grants, fake access decisions, fake audit records, raw
external subjects, raw emails where masking is required, cross-tenant leakage,
platform-role escalation by tenant admins, and non-persistent mutations.
```

### Implement Prompt

```text
Implement Membership And Access React Live Data. Seed live principal and
membership rows, migrate projections/actions to membership/access services,
remove obsolete deterministic membership builders, regenerate contracts, and
run backend tests, frontend typecheck/tests/build, scanner checks, redaction
sweeps, Spec QA, and Playwright membership validation.
```

## Spec 055 - Channels, Telegram, Briefing React Live Data

### Specify Prompt

```text
Create a feature specification for Channels, Telegram, Briefing React Live
Data. Replace deterministic channel/Telegram/briefing builders with live
projections from Telegram tenant config, command alias, link-token audit,
linked identity, delivery attempt, webhook receipt, channel run, notification,
briefing preference profile/revision/import/export, and audit services. React
must show real channel readiness, real Telegram configuration state, real
aliases, real identity links, real delivery diagnostics, real run status links,
and real Daily Intelligence Briefing preference summaries.
```

### Clarify Prompt

```text
Run clarification for channel/Telegram/briefing live data. Focus on tenant user
access, platform versus tenant admin actions, token visibility, link-token
one-time display, alias enable/disable/delete persistence, webhook validation
evidence, delivery attempt bounds, run status access checks, briefing preference
privacy, import/export artifact references, and QA seed data. Default to the
existing Telegram config, briefing preference, channel run, notification, and
audit services.
```

### Plan Prompt

```text
Plan Channels, Telegram, Briefing React Live Data. Replace
src/multi_agent_platform/admin/channel_telegram_briefing/react_channel_telegram_briefing.py
fixed data with live projections and durable mutations. Wire admin_react.py
channel endpoints to TelegramConfigRepository/Service, BriefingPreferenceService,
channel run APIs/services, notification/delivery repositories, AuditService,
and redaction helpers. Add QA seeded config/aliases/preferences/runs, route
tests, frontend tests, Playwright flows, scanner assertions for qa036 removal,
and redaction checks for tokens, private messages, preferences, and Telegram
identifiers.
```

### Tasks Prompt

```text
Generate tasks for Channels, Telegram, Briefing React Live Data. Include live
readiness projection, Telegram config projection, alias list/action projection,
identity link projection, link-token mutation, webhook validation mutation,
delivery diagnostic query, run status query, briefing preference list/detail,
preference save/import/export mutations, empty states, QA seeding, route tests,
frontend tests, Playwright flows, scanner updates, docs, QA guide, and PR notes.
```

### Analyze Prompt

```text
Analyze Channels, Telegram, Briefing React Live Data for qa036 run IDs, fake
aliases, fake identities, fake delivery attempts, fake token audit records,
fake preference profiles, fake artifact references, token leakage, private
message leakage, full Telegram ID leakage, cross-tenant scope leakage, and
non-persistent mutations.
```

### Implement Prompt

```text
Implement Channels, Telegram, Briefing React Live Data. Seed live Telegram
config, aliases, identities, delivery attempts, runs, and preference profiles
through existing services, migrate React projections/actions to live services,
remove obsolete deterministic channel builders, regenerate contracts, and run
backend tests, frontend typecheck/tests/build, scanner checks, redaction sweeps,
Spec QA, and Playwright channel validation.
```

## Spec 056 - Usage React Live Data

### Specify Prompt

```text
Create a feature specification for Usage React Live Data. Replace the in-code
React usage fixture events with live data from llm_usage_events, pricing
versions, usage rollups, usage export requests, reconciliation records, runtime
run/step attribution, provider gateway attempts, skill execution summaries, and
workflow/prompt/profile metadata. React must show real totals, trend points,
rollups, drilldowns, confidence states, cost estimates, attribution, and export
requests. Empty states must be truthful when no usage has been recorded.
```

### Clarify Prompt

```text
Run clarification for usage live data. Focus on whether to compute rollups on
read or require persisted rollup rows, how to handle missing pricing, how to
attribute workflow/run/step/prompt/profile/tool data, export status semantics,
platform versus tenant scope, date range defaults, and QA seed events. Default
to UsageRepository and UsageAnalyticsService as sources of truth.
```

### Plan Prompt

```text
Plan Usage React Live Data. Replace
src/multi_agent_platform/admin/usage/react_usage.py fixed USAGE_EVENTS and
export IDs with React-specific projections backed by UsageRepository and
UsageAnalyticsService. Reuse existing /admin/usage API behavior where possible
or consolidate duplicate logic. Add live export creation/detail, empty states,
QA usage-event seeding, route tests, repository tests, frontend tests,
Playwright flows, scanner assertions for qa035 fixed event removal, and
performance tests for bounded date ranges.
```

### Tasks Prompt

```text
Generate tasks for Usage React Live Data. Include live dashboard summary,
trend calculation, rollup projection, event drilldown, filter metadata, export
creation/detail, pricing confidence, attribution badges, empty states, QA
seeding, route tests, frontend tests, Playwright flows, performance tests,
scanner updates, docs, QA guide, and PR notes.
```

### Analyze Prompt

```text
Analyze Usage React Live Data for remaining USAGE_EVENTS, fixed export IDs,
fake provider/model names, fake workflow/prompt/profile labels, fabricated
costs, unbounded queries, tenant leakage, missing pricing behavior, and export
details not backed by usage_export_requests.
```

### Implement Prompt

```text
Implement Usage React Live Data. Seed live usage events and pricing rows,
migrate React usage routes to UsageAnalyticsService, remove obsolete fixed
usage fixtures, regenerate contracts, and run backend tests, frontend
typecheck/tests/build, scanner checks, performance tests, Spec QA, and
Playwright usage validation.
```

## Spec 057 - Operations And Run Debug React Live Data

### Specify Prompt

```text
Create a feature specification for Operations And Run Debug React Live Data.
Replace deterministic operations workbench and run-debug projection data with
live evidence from operations logs, audit debugging records, reliability
policies/counters/breakers/dead letters, runtime orchestration runs/timeline,
provider health/attempts, Telegram/channel delivery records, skill execution
diagnostics, usage analytics, worker/queue state, and export metadata. React
must show real health, pressure, timeline, likely causes, run debug, export,
and remediation data, or honest empty states.
```

### Clarify Prompt

```text
Run clarification for operations/run-debug live data. Focus on platform/admin
access, auditor access, tenant visibility, bounded time ranges, live versus
snapshot health, run ID direct links, audit-debug data redaction, export
storage metadata, likely-cause derivation, and QA seed logs/runs. Default to
OperationsConsoleService, reliability repositories, runtime repositories,
audit debugging services, and existing export providers as sources of truth.
```

### Plan Prompt

```text
Plan Operations And Run Debug React Live Data. Replace
src/multi_agent_platform/operations/workbench.py deterministic cards/panels/
timeline/run-debug/export data with service-backed projections. Reuse
OperationsConsoleService, AuditDebuggingService, reliability repositories,
runtime orchestration repository, provider/gateway repositories, Telegram/
channel repositories, skill execution diagnostics, usage service, and storage
provider. Add empty states, QA seeded logs/runs, route tests, performance
tests, frontend tests, Playwright flows, scanner assertions for fixed workbench
data removal, and redaction checks.
```

### Tasks Prompt

```text
Generate tasks for Operations And Run Debug React Live Data. Include live
summary cards, dependency health, reliability panels, queue/dead-letter data,
timeline query, run debug projection, likely-cause summaries, related evidence
links, export creation/detail, empty states, QA seeding, Auth0-shaped tests,
local-principal Playwright tests, performance tests, scanner updates, docs,
QA guide, and PR notes.
```

### Analyze Prompt

```text
Analyze Operations And Run Debug React Live Data for fixed timelines, fake run
debug rows, fake health cards, fake gateway attempts, fake delivery evidence,
fake skill diagnostics, fake exports, unbounded queries, platform-only data
leakage to tenant admins, raw stack traces, raw payloads, and unsafe filesystem
paths.
```

### Implement Prompt

```text
Implement Operations And Run Debug React Live Data. Seed live operations,
reliability, runtime, provider, channel, skill, and usage records through
existing services or QA factories, migrate workbench projections to live
services, remove obsolete deterministic workbench data, regenerate contracts,
and run backend tests, frontend typecheck/tests/build, scanner checks,
performance tests, redaction sweeps, Spec QA, and Playwright operations
validation.
```

## Spec 058 - Live-Only UI Decommission Gate

### Specify Prompt

```text
Create a feature specification for Live-Only UI Decommission Gate. After Specs
050 through 057 replace deterministic domain builders with live projections,
the final feature must remove obsolete mock/demo modules and enforce CI gates
that prove production React routes never return backend-generated fixture data.
The system must document live seed requirements, empty-state behavior, allowed
computed metadata, test fixture boundaries, and rollback guidance.
```

### Clarify Prompt

```text
Run clarification for the live-only decommission gate. Focus on final scanner
scope, whether qa0xx strings are fully banned outside tests/docs, how built
assets are scanned, how route response scans authenticate, what seed data is
required for QA, how empty database routes are validated, and which old modules
are deleted versus retained for tests. Default to CI-blocking scanners for
production code and production route responses, with test directories and docs
handled by explicit policy.
```

### Plan Prompt

```text
Plan Live-Only UI Decommission Gate. Delete or retire obsolete deterministic
projection modules, update imports, update docs and QA guides, add CI scanner
jobs, route response scans for fresh and seeded databases, Playwright
live-versus-empty evidence, generated contract checks, and a migration dashboard
summary that classifies every React route as live data, computed system
metadata, or empty state. Ensure no production route depends on test fixtures.
```

### Tasks Prompt

```text
Generate tasks for Live-Only UI Decommission Gate. Include final inventory
diff, module deletion, import cleanup, scanner hardening, built asset scanning,
route response scanning, fresh DB empty-state validation, seeded DB live-data
validation, frontend test cleanup, Playwright evidence, docs updates, QA seed
guide, redaction sweep, performance spot checks, PR notes, and rollback notes.
```

### Analyze Prompt

```text
Analyze the live-only decommission gate for any remaining production imports
of deterministic builders, qa0xx marker leakage in route responses, frontend
hardcoded revision/action defaults, stale generated contracts, tests relying on
production mocks, docs that tell reviewers to expect demo rows, and missing
empty-state or seeded-data evidence.
```

### Implement Prompt

```text
Implement Live-Only UI Decommission Gate. Remove obsolete deterministic
builders, finalize scanner/CI checks, update docs and QA guides, regenerate
contracts, run backend tests, frontend typecheck/tests/build, scanner checks,
route response scans, Spec QA, and Playwright validation. The final report must
state that production React routes display live repository-backed data,
computed system metadata, or truthful empty states only.
```

## Spec 059 - Admin UI Transitional React Label Removal

### Specify Prompt

```text
Create a feature specification for Admin UI Transitional React Label Removal.
After the browser UI migration and live-data decommission are complete, the
production admin interface must stop exposing implementation-era "React"
wording to users. The system must remove "React" from visible navigation,
breadcrumbs, shell titles, page headings, document titles, command/search
labels, redirect/fallback copy, empty/error states, QA-visible screenshots, and
route labels unless the page is an explicitly developer-only migration evidence
view. Examples: `/admin/app` must show "Admin" rather than "React Admin", and
navigation labels such as "Skill tools Diagnostics React" must become
"Skill tools Diagnostics".
```

### Clarify Prompt

```text
Run clarification for Admin UI Transitional React Label Removal. Focus on which
surfaces count as user-facing UI, whether the migration evidence page remains
available to platform admins, whether "React" may remain in internal code
identifiers, generated contract names, package names, build error messages,
developer docs, historical spec names, and test fixture names, how old browser
redirect copy should be worded, and whether docs/QA guides should call the
product "Admin" while using "React" only as implementation context. Default to
removing "React" from all production visible text and preserving it only where a
technical reader needs the implementation detail.
```

### Plan Prompt

```text
Plan Admin UI Transitional React Label Removal. Inventory all visible "React"
strings returned by backend bootstrap/navigation/breadcrumb contracts and
rendered by frontend shell/domain components. Update shell metadata, fallback
HTML, route titles, breadcrumbs, navigation destinations, command search,
saved-filter labels, legacy redirect copy, migration/decommission panels,
frontend empty/error states, screenshots, docs, and QA assertions. Add a
route-level visible-text scanner that opens authenticated production admin
routes and fails when banned transitional "React" labels appear outside an
allowlist for developer-only migration evidence and internal build artifacts.
```

### Tasks Prompt

```text
Generate tasks for Admin UI Transitional React Label Removal. Include backend
bootstrap/navigation label cleanup, breadcrumb/title cleanup, frontend shell and
domain component copy cleanup, fallback HTML copy cleanup, compatibility
redirect text cleanup, command/search result label cleanup, migration evidence
allowlist decisions, generated contract regeneration if schemas change,
frontend test updates, backend route tests, visible-text scanner additions,
Playwright screenshots for `/admin/app` and representative domain pages,
documentation/QA guide updates, and PR notes.
```

### Analyze Prompt

```text
Analyze Admin UI Transitional React Label Removal for remaining visible "React"
labels in navigation, breadcrumbs, headings, page titles, document titles,
buttons, links, toasts, problem details, redirect pages, command search,
saved-filter chips, migration/decommission panels, screenshots, and exports.
Confirm the scanner does not fail on legitimate internal code identifiers,
package names, generated TypeScript contract names, historical spec titles,
developer documentation, or built vendor bundles. Verify `/admin/app` presents
as "Admin" and skill diagnostics navigation no longer appends "React".
```

### Implement Prompt

```text
Implement Admin UI Transitional React Label Removal. Replace production
user-facing "React Admin" and similar migration-era labels with stable product
language such as "Admin", remove appended "React" suffixes from navigation and
domain labels, update backend contracts and frontend components, regenerate
contracts if needed, update tests/docs/QA evidence, add authenticated
visible-text scanner coverage, and run backend route tests, frontend
typecheck/tests/build, scanner checks, Spec QA, and Playwright validation. The
final report must list any intentionally retained "React" references and prove
they are internal or developer-only.
```

## Rollout Notes

- Do Spec 048 first. It should produce the authoritative worklist and prevent
  accidental expansion of mock data while later specs are in flight.
- Specs 050 through 057 can be split across independent workstreams after Spec
  049 lands, but each should own a disjoint production builder/module surface.
- Do not delete test fixture files simply because they contain `qa0xx` markers.
  The target is production UI routes and production projection services.
- Expect QA databases to need richer setup scripts. The UI should become more
  honest, not less testable.
- Each domain spec must validate both an empty live database and a seeded live
  database. This is the key behavior change from the old deterministic demo
  builders.
- Do Spec 059 after the route inventory and decommission work has stabilized.
  It is intentionally about product terminology, not banning React as an
  implementation framework inside code, packages, contracts, or historical
  specs.
