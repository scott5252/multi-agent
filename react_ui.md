# React UI Spec Kit Roadmap

Created: 2026-05-03

This document captures a Spec Kit roadmap for replacing the current
server-rendered admin UI with a modern React.js, TypeScript, and Vite
experience while preserving the existing FastAPI, Auth0/local-principal,
tenant-isolation, audit, redaction, PostgreSQL, runtime, and QA discipline
defined by specs 001 through 019.

Use this as a prompt source. For each proposed spec, run the commands in order:

1. `/speckit.specify`
2. `/speckit.clarify`
3. `/speckit.plan`
4. `/speckit.tasks`
5. `/speckit.analyze`
6. `/speckit.implement`

## Current Solution Context

The existing platform is a Python 3.12 FastAPI control plane with PostgreSQL,
SQLAlchemy 2.x, Alembic, Auth0 JWT validation, deterministic local-principal
test mode, LangChain/LangGraph durable runtime services, audit/debugging,
reliability controls, model gateway services, skill registry services,
prompt/profile services, tenant membership administration, Telegram/channel
administration, usage analytics, and operations dashboards.

### Spec Inventory Reviewed

| Spec | Current solution contribution |
|------|-------------------------------|
| 001 | Platform foundation: FastAPI app, worker entrypoints, async PostgreSQL, tenancy, queues, secrets, artifacts, health, and quality gates. |
| 002 | Auth and access: Auth0 production auth, local-principal dev/test mode, role grants, delegated credentials, and access audit records. |
| 003 | Workflow studio and registry: admin workflow drafts, validation, immutable published bundles, field help, and server-rendered UI. |
| 004 | Durable orchestration runtime: published-bundle execution, checkpoints, leases, handoffs, approvals, side-effect intents, and lineage. |
| 005 | Immutable memory: append-only memory versions, current-head projections, replay, diffing, and content-safe audit records. |
| 006 | User interaction channels: Web UI, Telegram, REST channels, normalized run requests, progress, approval/resume, notifications, and artifacts. |
| 007 | Model and skill routing: versioned model/prompt/skill/tool/outbound/credential policy resolution and provenance. |
| 008 | Production audit/debugging: timelines, traces, replay views, lineage, version bundles, notification state, safe exports, and admin inspection. |
| 009 | Reliability and scale: quotas, fairness, admission, leases, retries, circuit breakers, dead letters, compensation, and operational controls. |
| 010 | Admin shell: shared Jinja shell, navigation registry, tenant scope selection, breadcrumbs, saved filters, common states, and audit. |
| 011 | Model provider gateway: provider connections, safe probes, catalog sync, ModelGateway adapters, health snapshots, and admin views. |
| 012 | Prompt runtime profiles plus V2 gateway hardening: prompt/profile lifecycle, browser views, ModelGateway-only execution, idempotent attempts, and guardrails. |
| 013 | Guided workflow builder: server-rendered builder forms, graph preview, reference readiness, validation panel, publish gate, and revision history. |
| 014 | Skill registry lifecycle: governed package publication, tenant installation, credential readiness, smoke tests, quarantine, upgrade, and audit. |
| 014-v2 | Browser-first skill registry lifecycle: every primary action executable through admin browser UI with redaction-safe screenshot evidence. |
| 015 | Agent and workflow test bench: suites, cases, safe execution modes, result diagnostics, publication gate evidence, and redacted artifacts. |
| 016 | Token usage and cost analytics: normalized ModelGateway usage events, dashboards, rollups, drilldowns, safe exports, and audit. |
| 017 | Telegram configuration console: platform/tenant settings, safe secret references, webhook validation, link tokens, identities, diagnostics, and redaction. |
| 018 | User and tenant membership administration: invitations, principals, role grants, tenant memberships, status changes, access history, and audit. |
| 019 | Operations console: health, dependencies, capacity, provider/channel status, reliability state, latency, throughput, redacted logs, links, and exports. |

### Current Web Admin UI Reviewed

The admin UI is currently server-rendered with Jinja templates under
`src/multi_agent_platform/web_admin/templates`, shared CSS and small JavaScript
under `src/multi_agent_platform/web_admin/static`, and FastAPI routers under
`src/multi_agent_platform/api/routers` plus view-model helpers under
`src/multi_agent_platform/api/ui`.

Important current UI mechanics:

- `src/multi_agent_platform/api/main.py` mounts `/admin/static` and includes
  admin routers for shell, workflows, model skill config, skill registry, agent
  tests, usage, memberships, Telegram, operations, model providers, prompt
  runtime, run inspection, reliability, and channel run UI.
- `web_admin/templates/admin_shell/base.html` supplies the shell frame, sidebar,
  topbar, scope selector, breadcrumbs, flash messages, common states, saved
  filters, and page actions.
- `api/ui/admin_console.py` owns navigation metadata, tenant/platform scope
  resolution, fail-closed policy checks, shell context, saved filter profiles,
  common-state sanitization, and safe flash text.
- `web_admin/static/workflow_studio.css` is the shared style surface for both
  the admin shell and domain pages.
- Domain templates are mostly dense forms and tables. The workflow builder,
  operations console, memberships page, skill registry, provider pages, prompt
  pages, usage dashboards, run inspection pages, and reliability pages all
  extend the same shell but duplicate many filter, table, action, and status
  patterns.
- JavaScript is deliberately small today: field help modals, dirty-form
  warnings, simple fetch actions, EventSource lifecycle close behavior, and
  auto-submit filters.

Constraints the React UI must preserve:

- Production authentication remains Auth0-backed; local-principal mode remains
  explicit for development and tests.
- Every React feature spec MUST include acceptance criteria and tasks that
  validate both Auth0-backed authentication and `AUTH_MODE=local_principal`,
  including principal bootstrap, tenant/platform scope handling, navigation
  visibility, denied access, and protected actions for the feature's affected
  routes.
- Every route and action must preserve tenant scope and role authorization.
- Denied or unaudited protected actions fail closed.
- UI and API responses must not expose secrets, raw prompts, raw completions,
  raw memory content, private channel messages, raw provider responses, raw
  stack traces, raw package payloads, raw credential values, or cross-tenant
  details.
- PostgreSQL remains the transactional source of truth; object storage remains
  the large-artifact store.
- Existing domain services remain authoritative. React should consume explicit
  JSON contracts rather than duplicate business rules in the browser.
- Each implemented spec must include focused tests, Playwright UI evidence,
  QA docs, PR notes, testing instructions, README or quickstart updates where
  affected, and at least 90 percent relevant coverage.

### Frontend Reference Notes

Official React documentation recommends a framework for new full-stack apps,
but also documents starting with a build tool such as Vite when building a
custom app. Vite officially supports `react-ts` templates and currently
requires Node.js 20.19+ or 22.12+. React and TypeScript documentation confirms
TypeScript supports JSX and React Web typing through React type packages.

References:

- React: https://react.dev/learn/creating-a-react-app
- React from scratch with Vite: https://react.dev/learn/build-a-react-app-from-scratch
- React with TypeScript: https://react.dev/learn/typescript
- Vite guide: https://vite.dev/guide/
- TypeScript React docs: https://www.typescriptlang.org/docs/handbook/react.html

## Recommended Spec Breakdown

The React migration should be incremental. Do not start by rewriting every
admin page. Build a foundation, create a shared shell and design system, add
safe data/form contracts, then migrate domain surfaces in slices that can be
validated independently.

| Proposed spec | Name | Depends on | Purpose |
|---------------|------|------------|---------|
| 020 | React Admin UI Foundation | 001, 002, 010 | Add Vite/React/TypeScript app infrastructure, static serving, dev proxy, auth/session bridge, generated types, tests, and parity guardrails. |
| 021 | Modern Admin Shell And Design System | 020 | Replace the shared shell experience with a modern, accessible React shell and reusable UI components. |
| 022 | React Admin Data Contracts And Form Patterns | 020, 021 | Standardize page envelopes, problem details, safe action results, filters, forms, validation, concurrency, and audit-aware mutations. |
| 023 | Operations, Reliability, And Run Debug Workbench | 022, 008, 009, 019 | Give operators an intuitive triage workspace across health, logs, reliability, run timelines, and replay links. |
| 024 | React Workflow Builder | 022, 003, 013, 015 | Create the modern graph-and-form workflow authoring experience. |
| 025 | Model, Prompt, Profile, And Provider Governance | 022, 007, 011, 012 | Modernize provider setup, prompt/profile management, model routing preview, policy history, and provenance. |
| 026 | React Skill Registry And Installation Lifecycle | 022, 014, 014-v2 | Modernize platform package publication and tenant installation/configuration workflows. |
| 027 | React Agent And Workflow Test Bench | 022, 015 | Modernize suite authoring, safe run launch, results, diagnostics, and publish-gate evidence. |
| 028 | React User And Tenant Membership Administration | 022, 018 | Modernize invitations, user directory, role grants, memberships, status changes, and access history. |
| 029 | React Usage And Cost Analytics | 022, 016 | Modernize usage dashboards, cost summaries, rollups, drilldowns, and exports. |
| 030 | React Channel And Telegram Administration | 022, 006, 017 | Modernize Telegram configuration, channel readiness, identity links, diagnostics, and user run status surfaces. |
| 031 | React Admin Migration Hardening And Jinja Retirement | 020-030 | Validate parity, performance, accessibility, security, docs, feature flags, redirects, and legacy template retirement. |

## Global Prompt Prefix

Prepend or keep in mind for every prompt below:

```text
Use the current multi-agent platform repository context. Preserve the
constitution, specs 001 through 019, existing FastAPI backend services,
PostgreSQL storage model, Auth0 production authentication, local-principal
test mode, tenant isolation, audit fail-closed behavior, redaction rules,
runtime version pinning, secret hygiene, object-storage boundaries, QA docs,
Playwright evidence, and at least 90 percent relevant coverage.

The UI target is a modern React.js + TypeScript + Vite admin experience for
non-technical platform and tenant administrators. React must improve clarity,
guided workflows, responsiveness, accessibility, empty/error/loading states,
safe confirmations, progressive disclosure, and cross-linking. Do not duplicate
security or domain business rules in the browser. Existing domain services and
explicit JSON/API contracts remain authoritative.

Keep each feature independently testable, additive, and reversible. Existing
Jinja admin routes may remain available as fallbacks until the migration parity
spec retires them. Any route that handles protected data must fail closed if
authorization, tenant scoping, or audit persistence cannot be proven.

Every `/speckit.specify` output must make dual-auth-mode validation a
mandatory acceptance criterion: the feature must be testable with Auth0-backed
production-style principals and with `AUTH_MODE=local_principal`. Every
`/speckit.tasks` output must include explicit test tasks for both modes, using
backend route tests for Auth0 claim/principal resolution and browser
Playwright flows for local-principal login unless a safer feature-specific
validation path is documented.
```

## Spec 020 - React Admin UI Foundation

### Specify Prompt

```text
Create a feature specification for introducing the React admin UI foundation.
The goal is to add the build, runtime, routing, authentication/session bridge,
static serving, development workflow, generated type contracts, testing
tooling, and migration guardrails needed for future React admin pages. This
spec must not migrate domain pages yet. It must let engineers and reviewers
open a minimal authenticated React admin app from the existing FastAPI service,
verify active principal and tenant/platform scope, confirm navigation shell
metadata can be fetched safely, and fall back to existing Jinja pages until
domain parity exists. Prioritize non-technical administrator safety, no auth
bypass, no tenant leakage, and a small reversible implementation. Acceptance
criteria must require the foundation to work under both Auth0-backed auth and
`AUTH_MODE=local_principal`.
```

### Clarify Prompt

```text
Run clarification for the React admin UI foundation. Focus only on choices
that materially affect architecture or validation: mount path, fallback
strategy, session/CSRF handling, OpenAPI/type generation strategy, package
manager, Node version policy, React routing mode, feature flag rollout, and
whether Vite serves only development assets while FastAPI serves production
build assets. Recommended defaults: mount React at /admin/app initially, keep
existing Jinja routes direct and authorized, use existing auth cookies and
server-issued CSRF/action tokens, generate TypeScript types from backend
schemas/contracts, use Vite SPA mode for v1, serve built assets from FastAPI
under /admin/static/react, and gate domain migrations behind explicit feature
flags.
```

### Plan Prompt

```text
Plan the React admin UI foundation using React.js, TypeScript, Vite, React
Router, strict TypeScript, Vitest, Testing Library, Playwright, and a generated
API/type contract approach selected during research. Include FastAPI routes for
the React app shell, asset manifest serving, auth/session/scope bootstrap JSON,
safe config, and health/version metadata. Include dev proxy behavior, Node.js
version constraints compatible with current Vite requirements, package scripts,
CI quality commands, CSP/static asset concerns, no production auth shortcuts,
and fallback links to existing Jinja routes. Use paths such as frontend/admin
for the React app and src/multi_agent_platform/api/routers for backend bridge
routes unless research finds a better local pattern.
```

### Tasks Prompt

```text
Generate tasks for the React admin UI foundation. Tasks must be file-specific
and dependency ordered. Include setup tasks for package metadata, Vite config,
TypeScript config, lint/test config, React entrypoints, route skeleton,
generated client/type workflow, FastAPI React app route, static asset serving,
auth/session bootstrap endpoint, scope bootstrap endpoint, feature flag config,
fallback links, unit tests, FastAPI route tests for Auth0-backed principal
resolution, Playwright smoke tests for `AUTH_MODE=local_principal`, docs,
README/quickstart updates, QA docs, and PR notes. Mark parallel tasks only
when they touch disjoint frontend/backend/test/docs files.
```

### Analyze Prompt

```text
Analyze the foundation spec, plan, and tasks for gaps. Prioritize findings for
auth/session bypass risk, tenant-scope leakage, missing audit behavior, missing
fallback route behavior, untyped API contracts, unclear Vite production asset
serving, incomplete Node version constraints, missing Playwright evidence,
missing coverage tasks, or task paths that conflict with existing FastAPI and
web_admin structure.
```

### Implement Prompt

```text
Implement only the React admin UI foundation tasks. Do not migrate domain admin
pages. Mark tasks complete as they land. Run frontend typecheck/build/unit
tests, backend ruff/mypy/pytest tests relevant to new routes, and Playwright
smoke validation for the minimal authenticated React shell. Produce QA docs,
UI walkthrough, environment notes, PR notes, and evidence paths. Stop if any
auth, tenant, or audit behavior is ambiguous.
```

## Spec 021 - Modern Admin Shell And Design System

### Specify Prompt

```text
Create a feature specification for a modern React admin shell and design
system. The shell must make the platform understandable to non-technical
platform admins and tenant admins through clear navigation, scope awareness,
breadcrumbs, saved filters, global search or command access where safe,
contextual page actions, notifications, common loading/empty/error/denied
states, and responsive layouts. It must preserve authorization-aware
navigation, tenant/platform scope semantics, audit evidence, and redaction.
The spec should focus on shared UI behavior and reusable components, not
domain-page rewrites.
```

### Clarify Prompt

```text
Run clarification for the modern shell and design system. Focus on navigation
grouping, mobile behavior, global search scope, saved-filter presentation,
theme/accessibility requirements, icon library policy, design token ownership,
and how React shell links coexist with Jinja fallback links. Recommended
defaults: keep the existing Python navigation registry authoritative, expose a
safe navigation JSON contract, use a left navigation plus compact mobile drawer,
show tenant/platform scope persistently, use saved filters as chips and a
management panel, include command/search only for authorized destinations and
safe identifiers, and require WCAG 2.2 AA-oriented behavior.
```

### Plan Prompt

```text
Plan the React admin shell and design system. Use React components with strict
TypeScript, stable design tokens, responsive CSS, accessible dialogs/menus,
keyboard-visible focus, route-aware navigation, shell bootstrap from the
foundation API, and reusable components for buttons, icon buttons, tabs,
forms, filters, tables, status badges, cards, panels, modals, toasts, common
states, saved filters, breadcrumbs, page headers, and scope selector. Research
whether to use a lightweight accessible headless component library or build
small local primitives. Avoid a marketing-style landing page; the first screen
must be the useful admin console.
```

### Tasks Prompt

```text
Generate tasks for the shell and design system. Include tasks for navigation
contract DTOs if missing, React shell layout, responsive navigation, scope
selector, breadcrumbs, page actions, safe messages, common states, saved filter
components, design tokens, icon integration, typography, data density rules,
keyboard navigation, accessibility tests, visual regression screenshots,
component unit tests, Playwright shell flows, docs, QA walkthrough, and PR
notes. Keep domain-specific pages as placeholders or links unless required by
this spec.
```

### Analyze Prompt

```text
Analyze shell/design artifacts for missing non-technical usability outcomes,
navigation authorization drift, inaccessible controls, one-off styling that
will not scale to domain pages, mobile layout gaps, missing safe-state
coverage, duplicate business logic, and absent Playwright evidence across
platform and tenant scopes.
```

### Implement Prompt

```text
Implement the React shell and design system tasks. Keep the existing Jinja
admin shell available. Verify platform admin and tenant admin navigation,
scope switching, saved filter rendering, denied state rendering, keyboard-only
navigation, mobile viewport behavior, and visual polish. Run frontend tests,
backend contract tests for navigation/scope endpoints, Playwright screenshots,
and required QA/documentation validation.
```

## Spec 022 - React Admin Data Contracts And Form Patterns

### Specify Prompt

```text
Create a feature specification for shared React admin data contracts and form
patterns. Non-technical admins need consistent filtering, table browsing,
details panels, wizards, validation messages, optimistic/stale conflict
recovery, safe confirmations, export flows, audit-aware mutation feedback, and
loading/empty/error states across every future React admin page. The feature
must define reusable browser-facing contracts without moving domain rules out
of backend services.
```

### Clarify Prompt

```text
Run clarification for shared data/form patterns. Focus on the standard page
envelope, error/problem format, mutation result format, CSRF/action token
strategy, stale revision token behavior, filter persistence, export status,
pagination/sorting, polling versus SSE, and how unsafe fields are redacted
before reaching React. Recommended defaults: use a safe AdminPageEnvelope,
RFC-style problem details with safe reason categories, backend-issued action
tokens where needed, existing revision tokens for optimistic concurrency,
server-owned allowed filter criteria, cursor or bounded page pagination, and
no raw unsafe payloads in JSON responses.
```

### Plan Prompt

```text
Plan shared admin data contracts and form patterns. Add backend schemas and
helpers for page envelopes, safe problem details, action results, filter
profiles, pagination, sorting, export snapshots, stale conflict details,
field-level validation, confirmation requirements, and audit reference ids.
Add frontend hooks/components for query loading, mutation submission,
validation mapping, form dirty-state protection, stale conflict recovery,
filter chips, table state, export progress, and safe toasts. Integrate with
existing admin shell sanitization and service-layer authorization. Include
unit, integration, contract, and Playwright validation.
```

### Tasks Prompt

```text
Generate tasks for shared data contracts and form patterns. Include backend
schema/helper tasks, frontend client/hook/component tasks, generated type
tasks, field validation tests, tenant-scope denial tests, stale conflict tests,
redaction tests, saved filter tests, export result tests, Playwright examples
using at least one harmless sample page, docs, QA guide, and PR notes. Ensure
each task names exact files and separates backend/frontend/test/docs work.
```

### Analyze Prompt

```text
Analyze data/form artifacts for unowned contracts, duplicate validation logic,
missing tenant-scope enforcement, unsafe raw payload exposure, vague error
states, missing stale conflict recovery, missing audit evidence, incomplete
filter persistence, and absent examples for future domain specs to follow.
```

### Implement Prompt

```text
Implement the shared data contracts and form patterns. Do not migrate major
domain pages except for a minimal sample if tasks require it. Verify contracts
through generated TypeScript, backend tests, frontend unit tests, redaction
tests, stale conflict tests, and Playwright sample flows. Update developer docs
so later specs know how to create React admin pages.
```

## Spec 023 - Operations, Reliability, And Run Debug Workbench

### Specify Prompt

```text
Create a feature specification for a React operations, reliability, and run
debug workbench. Platform operators need one intuitive workspace to understand
health, dependencies, capacity, queue pressure, database pool pressure, model
provider health, Telegram/channel status, reliability breaker state, retries,
dead letters, latency, throughput, error rate, redacted logs, run timelines,
lineage, replay links, and safe exports. Tenant admins may see only explicitly
authorized tenant-scoped views. The experience must guide non-technical admins
from symptom to likely cause without raw data exposure.
```

### Clarify Prompt

```text
Run clarification for the operations workbench. Focus on platform-only versus
tenant-limited scope, default time range, refresh behavior, chart/table density,
log filtering, cross-links to run/reliability/provider/usage pages, export
workflow, and how degraded dependencies appear. Recommended defaults:
platform-admin and auditor full access, tenant admin limited only where
existing policies allow, default last 60 minutes, manual refresh plus safe
short polling for health panels, filters matching Spec 019, and degraded cards
instead of hidden sections.
```

### Plan Prompt

```text
Plan the React operations workbench on top of existing operations, audit,
reliability, model provider, Telegram, usage, and run inspection services.
Create safe JSON endpoints or adapt existing ones for dashboard summary,
dependency panels, capacity, latency/throughput rollups, redacted log search,
run timeline summaries, reliability controls, dead letters, export requests,
and authorized cross-links. Plan React dashboards with compact cards, trend
visuals, filter drawer, log table, timeline drawer, and recovery guidance.
Include performance targets for large log result sets, redaction tests,
authorization tests, and Playwright evidence.
```

### Tasks Prompt

```text
Generate tasks for the operations workbench. Include endpoint/view-model
contracts, React route/page components, health cards, charts or trend panels,
filter state, log table, run timeline drawer, reliability/dead-letter panels,
export flow, authorized links, degraded/empty/denied states, platform and
tenant-scope tests, performance tests, redaction tests, Playwright screenshots,
docs, QA guide, and PR notes.
```

### Analyze Prompt

```text
Analyze operations workbench artifacts for missing Spec 019 filter coverage,
unsafe logs or stack traces, tenant leakage, export audit gaps, lack of
performance constraints, hidden degraded states, missing links back to existing
debug pages, and untested platform-admin/auditor/tenant-admin differences.
```

### Implement Prompt

```text
Implement the operations workbench tasks. Keep existing server-rendered
operations, reliability, and run inspection routes available until migration
hardening. Run backend tests, frontend tests, performance-focused tests for
bounded log results, Playwright platform/auditor flows, redaction checks, and
QA document validation.
```

## Spec 024 - React Workflow Builder

### Specify Prompt

```text
Create a feature specification for the React Workflow Builder. Platform and
tenant admins must be able to create, edit, validate, review, and publish
workflow drafts through guided forms and an interactive graph-oriented view
without editing raw JSON. The UI must cover metadata, roles, sub-agent roles,
prompt/profile references, model routing readiness, skill installation
requirements, contracts, nodes, edges, join policies, approval gates, reusable
subworkflows, required test suites, validation findings, draft revisions, and
publish gate decisions. It must be intuitive for non-technical admins while
preserving exact backend validation and immutable publishing.
```

### Clarify Prompt

```text
Run clarification for the React Workflow Builder. Focus on graph editing
authority, advanced JSON inspector visibility, draft autosave versus explicit
save, validation refresh timing, publish gate flow, large workflow size,
field-help style, and whether JavaScript is now required for primary authoring.
Recommended defaults: semantic saves remain explicit backend submissions,
graph layout annotations are non-authoritative, advanced JSON is read-only and
collapsed, validation can refresh on demand and after saves, publish gate is a
guided review, support 100-node workflows, and React is required for the new
builder while old Jinja editor remains fallback during migration.
```

### Plan Prompt

```text
Plan the React Workflow Builder using existing workflow registry services,
schemas, editor metadata, graph preview, validation, reference readiness,
publish gate, revision history, prompt/profile/model/skill/test bench
integrations, and audit helpers. Research a proven React graph library for the
interactive graph while keeping backend document validation authoritative.
Plan JSON contracts for editor bootstrap, lookups, document patches or full
document saves, validation results, publish readiness, revisions, and safe
field help. Include accessibility, keyboard graph navigation alternatives,
large workflow performance, stale revision recovery, tenant isolation, and
Playwright reviewer flows.
```

### Tasks Prompt

```text
Generate tasks for the React Workflow Builder. Include backend editor contract
tasks, React route/page tasks, graph canvas, section forms, reference pickers,
validation panel, publish gate, revision history, field help, dirty-state and
stale-conflict recovery, read-only JSON inspector, tests for each user story,
graph accessibility tests, tenant isolation/redaction tests, Playwright
workflow create/edit/validate/publish flows, docs, QA walkthrough, README or
quickstart updates, and PR notes.
```

### Analyze Prompt

```text
Analyze workflow builder artifacts for mismatches with Specs 003 and 013,
missing publish blockers, graph state becoming authoritative without backend
validation, unsafe prompt/profile/provider/skill details, stale revision gaps,
missing required test-suite evidence, inaccessible graph-only workflows,
large-workflow performance gaps, and missing Playwright screenshots.
```

### Implement Prompt

```text
Implement the React Workflow Builder tasks. Preserve existing workflow storage,
services, published bundle model, and Jinja fallback route. Verify create,
edit, validation, publish gate, stale conflict, revision review, tenant scope,
and redaction flows. Run backend, frontend, graph/component, Playwright, and
QA-doc validation commands.
```

## Spec 025 - Model, Prompt, Profile, And Provider Governance

### Specify Prompt

```text
Create a feature specification for React-based model, prompt, profile, and
provider governance. Non-technical admins need a coherent experience for
configuring model providers, testing safe connections, reviewing provider
health, managing prompt versions, previewing safe prompt renders, configuring
agent runtime profiles, previewing model/skill routing decisions, reviewing
policy history, and understanding run provenance. The UI must hide raw
secrets, raw prompts where unsafe, raw completions, provider tokens, and
unauthorized tenant data while preserving all existing backend controls.
```

### Clarify Prompt

```text
Run clarification for model/prompt/profile/provider governance. Focus on how
to group the domains, what the default admin journey is, safe prompt preview
limits, provider probe refresh behavior, routing preview inputs, history
filtering, tenant visibility, and direct SDK guardrail evidence. Recommended
defaults: organize around Setup, Prompts, Profiles, Routing, Providers, and
Provenance; provider mutations are platform-admin only; tenant admins see only
authorized catalog/profile/prompt grants; safe previews use existing fixture
safety; probes are explicit actions; routing previews are read-only policy
evaluations.
```

### Plan Prompt

```text
Plan React governance pages on top of Specs 007, 011, and 012. Reuse existing
model provider services, prompt services, profile services, model-skill config
resolver, gateway provenance, audit/redaction helpers, and local-principal test
mode. Define contracts for provider lists/detail/forms/tests/catalog, prompt
library lists/detail/edit/preview/history, profile lists/detail/edit/resolve,
routing preview, configuration history, and run provenance. Plan guided forms,
safe diff/history views, health/status badges, inline explanations, and
authorization-aware links.
```

### Tasks Prompt

```text
Generate tasks for model/prompt/profile/provider governance. Include backend
contract tasks where React needs safer or richer JSON, React routes/pages,
provider forms and tests, prompt editor and safe preview, profile editor and
resolver, model/skill routing preview, history/provenance tables, tenant
visibility states, redaction tests, provider secret safety tests, direct-call
guardrail evidence surfaces, Playwright flows, docs, QA guide, and PR notes.
```

### Analyze Prompt

```text
Analyze governance artifacts for unsafe secret or prompt exposure, missing
platform-admin mutation enforcement, tenant catalog leakage, provider probe
audit gaps, drift from ModelGateway-only execution requirements, missing
history/provenance coverage, and missing non-technical recovery guidance for
failed routing or health checks.
```

### Implement Prompt

```text
Implement the governance tasks. Preserve backend services and existing Jinja
fallbacks. Verify platform provider creation/test/sync, prompt draft/save/
publish/preview, profile configuration, routing preview, history, provenance,
tenant scope, redaction, and denied states. Run backend, frontend, Playwright,
coverage, and QA-doc validation.
```

## Spec 026 - React Skill Registry And Installation Lifecycle

### Specify Prompt

```text
Create a feature specification for a React Skill Registry and Installation
Lifecycle. Platform admins must be able to publish skill packages through a
guided browser flow, and tenant admins must be able to discover, install,
configure, test, and preview binding eligibility for granted skills. The UI
must cover package creation, manifest paste/upload, candidate validation,
immutable publication, tenant grants, tenant discovery, tenant installation,
credential reference configuration, smoke-test/readiness evidence, binding
eligibility preview, stale conflict recovery, quarantine/withdrawal states,
audit timeline, and redaction-safe evidence.
```

### Clarify Prompt

```text
Run clarification for the React skill registry lifecycle. Focus on wizard
steps, manifest paste versus upload behavior, publish readiness gating,
credential reference picker behavior, smoke-test refresh, binding context
selection, stale revision handling, and how much safe manifest detail is shown.
Recommended defaults: use guided wizards for platform publication and tenant
installation, upload takes precedence over paste when both are present, raw
manifest text is never echoed after submit, credential references are selected
from authorized options only, smoke tests are explicit queued actions, and
stale conflicts provide reload-latest and retry guidance.
```

### Plan Prompt

```text
Plan the React Skill Registry using existing Spec 014 and 014-v2 services,
schemas, templates as behavior references, validation runner, smoke runner,
readiness, eligibility, audit, object storage, redaction, and tenant isolation.
Define React JSON contracts for package list/create/detail, manifest candidate,
validation findings, publish, version detail, grants, available versions,
installations, credentials, smoke tests, eligibility preview, conflicts, and
audit timeline. Include browser-first QA, no curl/API primary path, and
redaction-safe screenshots.
```

### Tasks Prompt

```text
Generate tasks for the React skill registry lifecycle. Include backend
contract adapters, React routes/pages/wizards, manifest input/upload, validation
findings, publish gate, grant form, available versions, installation detail,
credential picker, smoke test panel, eligibility preview, stale conflict UI,
audit timeline, tenant isolation tests, redaction tests, Playwright browser
lifecycle flows, docs, QA walkthrough, README updates, and PR notes.
```

### Analyze Prompt

```text
Analyze skill registry artifacts for any return to curl/API as the primary QA
path, raw manifest or credential exposure, cross-tenant discovery leakage,
missing immutable publication gates, stale revision gaps, unsafe smoke evidence,
quarantine/withdrawal confusion, missing binding eligibility policy reasons,
and incomplete browser screenshot evidence.
```

### Implement Prompt

```text
Implement the React skill registry lifecycle tasks. Preserve existing skill
registry domain services and JSON APIs for automation. Verify platform package
publication, tenant grants, tenant discovery, installation, credential
configuration, smoke-test/readiness, eligibility preview, stale conflict,
quarantine/withdrawal, denied/not-found, and redaction flows through
Playwright. Run backend/frontend tests and QA-doc validation.
```

## Spec 027 - React Agent And Workflow Test Bench

### Specify Prompt

```text
Create a feature specification for a React Agent and Workflow Test Bench.
Platform and tenant admins must be able to define reusable test suites and
cases, select safe execution modes, launch tests against prompts, profiles,
workflow drafts, subworkflows, or published workflows, inspect results,
understand pass/fail diagnostics, review redacted traces and artifacts, and
see publish-gate evidence. The UI must make testing understandable for
non-technical admins without exposing raw prompts, completions, secrets, tools,
or unauthorized tenant data.
```

### Clarify Prompt

```text
Run clarification for the React test bench. Focus on suite/case authoring
complexity, default safe execution mode, evaluator prompt visibility, run
progress updates, assertion editing, artifact access, and publish-gate links.
Recommended defaults: guided suite and case forms, mock model/mock tools as the
default local mode, real dependency probes only when policy allows, redacted
transcripts only, polling or SSE for run progress based on existing channel
patterns, and direct links from workflow publish gates.
```

### Plan Prompt

```text
Plan the React test bench using existing Spec 015 services, schemas, result
components, publish-gate integration, artifact metadata, ModelGateway test
mode metadata, redaction helpers, and audit. Define contracts for suite list,
suite detail, suite form, case form, run launch, run list, run detail, step
trace, assertions, result summary, gate status, artifacts, and safe evidence.
Include frontend components for forms, assertion builder, run launcher,
progress/status, diagnostics, and publish-gate panels.
```

### Tasks Prompt

```text
Generate tasks for the React test bench. Include backend contract adapters,
React route/page tasks, suite/case forms, assertion builder, target selector,
safe execution mode selector, run launcher, run progress/result views, trace
step components, artifact links, publish-gate evidence, tenant isolation tests,
redaction tests, Playwright suite/case/run flows, docs, QA guide, and PR notes.
```

### Analyze Prompt

```text
Analyze test bench artifacts for unsafe transcript/artifact exposure, missing
safe-mode enforcement, unclear pass/fail thresholds, missing publish-gate
coverage, tenant leakage, run progress gaps, duplicate evaluator logic in
React, and missing browser evidence for both passing and failing test runs.
```

### Implement Prompt

```text
Implement the React test bench tasks. Preserve existing safe execution
services and Jinja fallback pages. Verify suite creation, case creation, safe
run launch, progress, passing/failing diagnostics, artifact access, publish
gate evidence, redaction, and denied states. Run all relevant backend,
frontend, Playwright, coverage, and QA-doc validation.
```

## Spec 028 - React User And Tenant Membership Administration

### Specify Prompt

```text
Create a feature specification for React User and Tenant Membership
Administration. Platform admins need a clear user directory, invitation flow,
principal linking/provisioning, platform role assignment, tenant role
assignment, suspension/reactivation, grant revocation, membership status
management, and access history across tenants. Tenant admins need a safer
tenant-scoped view for inviting users, assigning permitted roles, revoking
memberships, and viewing user status for their tenant only. The UI must avoid
raw identifiers as the primary experience and must preserve safe email
handling, idempotent invites, next-request role effect, tenant isolation, and
audit records.
```

### Clarify Prompt

```text
Run clarification for membership administration. Focus on default directory
columns, search/filter behavior, invite idempotency presentation, role grant
wizard design, confirmation requirements for destructive actions, access
history depth, and masked email/subject display. Recommended defaults: show
human-friendly display names with masked emails and safe subject suffixes,
provide guided invite and role grant dialogs, require confirmation for suspend/
remove/revoke, show next-request effect copy, and keep full raw IDs in
copyable detail panels only when safe and authorized.
```

### Plan Prompt

```text
Plan React membership administration using Spec 018 services, repositories,
schemas, admin router behavior, access decision audit, membership audit,
Auth0/local-principal behavior, and redaction helpers. Define contracts for
snapshot list, principal detail, invitation create/status, role grant create/
revoke, principal suspend/reactivate, membership status changes, access
history, audit timeline, allowed roles, and scope options. Plan React directory
tables, filters, role summary cards, action dialogs, safe confirmations, and
tenant-scoped denied/not-found states.
```

### Tasks Prompt

```text
Generate tasks for React membership administration. Include backend contract
adapters if needed, React routes/pages, user directory, invite dialog, role
grant dialog, status action dialogs, membership table, access history, audit
timeline, filters, masked identity components, tenant isolation tests,
idempotent invite tests, local-principal grant refresh tests, Playwright
platform and tenant flows, docs, QA guide, and PR notes.
```

### Analyze Prompt

```text
Analyze membership artifacts for password handling mistakes, raw email/subject
exposure, cross-tenant leakage, missing role boundary enforcement, missing
next-request role effect, absent audit coverage, unsafe destructive actions,
and non-technical usability gaps caused by raw IDs or unclear role labels.
```

### Implement Prompt

```text
Implement the React membership administration tasks. Preserve existing
membership services and Jinja fallback route. Verify platform and tenant admin
flows, invitation idempotency, role grant boundaries, suspend/reactivate,
revoke/remove, access history, audit timeline, masked displays, denied states,
and Playwright screenshot evidence. Run backend/frontend tests and QA-doc
validation.
```

## Spec 029 - React Usage And Cost Analytics

### Specify Prompt

```text
Create a feature specification for React Usage and Cost Analytics. Platform
admins and tenant admins need modern dashboards to understand token usage,
model cost estimates, confirmed versus estimated usage, latency, unavailable
usage, provider/model/workflow/agent/prompt rollups, event drilldowns, and
audited CSV exports. The UI must be understandable for non-technical admins,
must respect platform versus tenant visibility, and must never expose raw
prompts, completions, secrets, memory content, provider credentials, or
unauthorized run content.
```

### Clarify Prompt

```text
Run clarification for usage analytics. Focus on default date range, grouping
defaults, chart types, drilldown depth, export status behavior, cost precision,
estimated versus confirmed labels, tenant admin visibility, and empty state
guidance. Recommended defaults: default last 7 days, daily group first,
summary cards plus trend chart plus rollup table plus event drilldown, clear
estimated/confirmed badges, export current safe filter snapshot, and tenant
admins see only their tenant scope.
```

### Plan Prompt

```text
Plan React usage analytics using Spec 016 usage services, pricing metadata,
safe exports, audit records, existing dashboard APIs, and admin shell scope.
Define or adapt contracts for dashboard summary, time-series rollups, group
rollups, event drilldown, filter metadata, export creation, export detail, and
denied states. Plan React charts, metric cards, filters, group selector,
drilldown table, export flow, latency/cost formatting, and performance limits
for bounded result sets.
```

### Tasks Prompt

```text
Generate tasks for React usage analytics. Include backend contract adapters,
React routes/pages, metric cards, charts, filter drawer, group selector,
rollup table, event drilldown, export flow and detail page, cost formatting,
tenant-scope authorization tests, redaction tests, performance tests,
Playwright platform/tenant/export flows, docs, QA guide, and PR notes.
```

### Analyze Prompt

```text
Analyze usage analytics artifacts for unsafe attribution exposure, tenant
leakage, missing export audit behavior, unbounded queries, unclear estimated
cost labels, missing empty/denied states, missing rollup groups from Spec 016,
and incomplete Playwright coverage for exports and drilldowns.
```

### Implement Prompt

```text
Implement the React usage analytics tasks. Preserve existing usage capture and
export services. Verify summary, trend, rollup, drilldown, filters, export
creation/detail, tenant scope, denied attempts, redaction, and performance
limits. Run backend/frontend tests, Playwright flows, and QA-doc validation.
```

## Spec 030 - React Channel And Telegram Administration

### Specify Prompt

```text
Create a feature specification for React Channel and Telegram Administration.
Platform admins and authorized tenant admins need an intuitive UI for channel
readiness, Telegram tenant enablement, safe secret-reference configuration,
webhook validation, linked Telegram identities, one-time link tokens,
protected command readiness, delivery diagnostics, webhook diagnostics, and
user-facing run status surfaces where applicable. The UI must not display real
bot tokens, webhook secrets, private messages, raw prompts, run results, or
unauthorized tenant data.
```

### Clarify Prompt

```text
Run clarification for channel and Telegram administration. Focus on whether
user-facing run status is in scope for this migration slice, how link tokens
are displayed, webhook validation refresh behavior, diagnostics retention,
protected command readiness, and tenant-admin permissions. Recommended
defaults: include admin Telegram configuration plus links to existing user run
status pages, show one-time link token result only at creation with safe
expiration guidance, use explicit webhook validation actions, and keep tenant
admins limited to their tenant settings and identities.
```

### Plan Prompt

```text
Plan React channel and Telegram administration using Specs 006 and 017,
existing Telegram config services, channel services, link-token behavior,
webhook diagnostics, notification delivery records, secret providers,
reliability retry/breaker summaries, local fake-secret readiness, and audit/
redaction helpers. Define contracts for readiness, tenant enablement,
configuration forms, webhook validation, linked identities, link tokens,
diagnostics, protected command readiness, and safe run status links.
```

### Tasks Prompt

```text
Generate tasks for React channel and Telegram administration. Include backend
contract adapters, React routes/pages, readiness cards, tenant enablement
forms, secret-reference picker, webhook validation panel, linked identities
table, link token create/revoke flow, diagnostics panels, protected command
readiness, tenant isolation tests, redaction tests, Playwright platform/tenant
flows, docs, QA guide, and PR notes.
```

### Analyze Prompt

```text
Analyze channel/Telegram artifacts for real token or secret exposure, private
message leakage, cross-tenant identity leakage, missing webhook validation
audit, unsafe link token display, unclear protected command readiness, and
missing denied/empty/degraded states.
```

### Implement Prompt

```text
Implement the React channel and Telegram administration tasks. Preserve
existing channel services and Jinja fallback routes. Verify readiness,
configuration, webhook validation, link token creation/revocation, identity
inspection, diagnostics, tenant isolation, redaction, and Playwright evidence.
Run backend/frontend tests and QA-doc validation.
```

## Spec 031 - React Admin Migration Hardening And Jinja Retirement

### Specify Prompt

```text
Create a feature specification for React Admin Migration Hardening and Jinja
Retirement. After the React domain specs reach parity, the platform needs a
safe final migration that verifies every admin destination has an authorized
React path, preserves direct links or redirects, retires duplicated legacy UI
only where parity is proven, documents rollback behavior, validates
performance and accessibility, and updates reviewer/operator guidance. The
feature must be cautious, auditable, and reversible.
```

### Clarify Prompt

```text
Run clarification for migration hardening. Focus on which Jinja routes can be
retired versus kept as fallback, redirect semantics, route aliases, feature
flag defaults, visual regression scope, browser support, performance budgets,
accessibility threshold, and rollback procedure. Recommended defaults: keep
read-only fallback routes until two releases of React parity, redirect primary
navigation to React, preserve old direct routes with deprecation notices where
safe, require WCAG-oriented automated and manual checks, and document rollback
by feature flag plus asset version.
```

### Plan Prompt

```text
Plan React admin migration hardening. Build a parity matrix for all admin
routes from Specs 003, 006, 007, 008, 009, 010, 011, 012, 013, 014/014-v2,
015, 016, 017, 018, and 019. Plan route redirects or aliases, feature flags,
legacy template deprecation, CSS/static cleanup, generated contract checks,
accessibility audit, performance budgets, Playwright end-to-end suite,
redaction sweep, tenant isolation sweep, docs, reviewer guides, and rollback
runbook. Do not delete legacy routes unless the spec's criteria are met.
```

### Tasks Prompt

```text
Generate tasks for migration hardening and Jinja retirement. Include route
inventory, parity matrix, navigation switch, redirect/alias handlers,
feature-flag defaults, legacy route notices, screenshot/visual regression
suite, accessibility tests, performance tests, bundle analysis, redaction
sweep, tenant isolation sweep, docs and runbook updates, QA guides for all
major admin journeys, PR notes, and cleanup tasks for only proven-obsolete
templates/static files.
```

### Analyze Prompt

```text
Analyze migration hardening artifacts for premature deletion, missing route
parity, broken direct links, lost authorization checks, missing audit events,
unbounded frontend bundles, accessibility regressions, visual regressions,
missing rollback steps, incomplete docs, and any admin journey still depending
on raw Jinja behavior without a React equivalent.
```

### Implement Prompt

```text
Implement migration hardening cautiously. Preserve rollback until validation
passes. Execute route parity tests, full Playwright admin journey suite,
visual screenshots, accessibility checks, performance/bundle checks, backend
quality gates, frontend quality gates, redaction and tenant isolation sweeps,
QA-doc validation, docs updates, and PR notes. Delete or disable legacy UI only
for routes that meet the approved retirement criteria.
```

## Execution Notes

- Create one Spec Kit feature at a time. Do not run all specs in parallel.
- After each implementation, run its generated QA guide and Playwright UI
  walkthrough before starting the next spec.
- Keep the React UI additive until Spec 031 proves parity.
- Treat dual-auth-mode coverage as mandatory for every implementation spec:
  each feature must prove Auth0-backed principal behavior and
  `AUTH_MODE=local_principal` behavior for its React routes and protected
  actions.
- Prefer backend-owned JSON contracts and generated TypeScript types over
  hand-maintained browser models.
- Prefer explicit user journeys and guided actions over exposing raw IDs,
  JSON, and domain jargon as the primary interface.
- Treat security, tenant isolation, audit, and redaction uncertainty as a stop
  condition, not a styling issue.
