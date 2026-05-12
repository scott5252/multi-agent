# Multi-Agent Platform User Guide

This guide explains how to set up, secure, configure, operate, and troubleshoot
the Multi-Agent Platform from an empty machine to a working local or
production-like installation. It is written for administrators and operators who
do not write code every day, but it stays precise about the current system so
that setup decisions are repeatable.

This document reflects the repository state reviewed on May 11, 2026. It covers
feature specifications 001 through 079, the Python code under
`src/multi_agent_platform`, and the Admin browser implementation under
`frontend/admin`.

## Before You Begin

You will need:

- A computer with Python 3.12 installed.
- `uv`, which installs Python dependencies and runs project commands.
- Docker Compose v2, used here to run PostgreSQL locally.
- Node.js `>=20.19.0 <26` and npm for the React admin build.
- A terminal window.
- Optional: an Auth0 tenant if you want production-style login.
- Optional: an OpenAI API key or a local OpenAI-compatible model server.
- Optional: a Telegram bot token if you want Telegram access.

The fastest path to a working system is:

1. Install dependencies with `uv sync`.
2. Copy `.env.example` to `.env`.
3. Use `AUTH_MODE=local_principal` for the first local setup.
4. Start PostgreSQL with `docker compose up -d postgres`.
5. Apply database migrations with `uv run alembic upgrade head`.
6. Build the Admin browser assets from `frontend/admin`.
7. Seed at least one tenant row.
8. Start the API server.
9. Open `/admin/app` through the local login screen.
10. Configure model providers, prompts, agent profiles, skill diagnostics,
   workflows, onboarding wizards, briefing preferences, tests, channels, and
   operational monitoring.

The platform is meant to be administered through the browser first. APIs are
available for automation, but most setup steps can be completed through the
Admin console at `/admin/app`. Older browser URLs are handled only as
non-Jinja compatibility redirects or safe responses. After Specs 048 through
059, production Admin routes are also live-data guarded: they must return
authorized durable data, allowed computed system metadata, or truthful empty,
denied, unavailable, or redirect states rather than sample records.

## Current Implementation Notes

Most management areas use PostgreSQL through SQLAlchemy repositories after
migrations run. This includes tenants, role grants, workflow drafts and
published bundles, prompt library records, agent runtime profiles, model
provider definitions, test bench suites and runs, usage analytics, Telegram
configuration and alias records, briefing preference profiles and revisions,
audit/debug records, reliability records, and operations console projections.

Some areas are intentionally lighter in the current code:

- The Admin console is the primary browser entry for the migrated management
  journeys. It is served by FastAPI at `/admin/app` from built Vite assets under
  `src/multi_agent_platform/web_admin/static/react`, and its browser contracts
  are generated from Pydantic schemas. Build or verify those assets before
  browser QA. Server-rendered Jinja pages, the template renderer, legacy
  one-off static files outside `static/react`, and the direct `jinja2`
  dependency have been removed. Old browser links should redirect or alias into
  Admin without rendering templates. User-facing labels now use product terms
  such as "Admin"; "React" is reserved for implementation context and
  developer-only evidence.
- Production Admin JSON routes follow the live-only policy introduced in Specs
  048 through 058. Workflow, governance, skill lifecycle, test bench,
  memberships, channels, usage, operations, and run-debug workspaces should
  project from durable repositories/services or show truthful empty, denied, or
  unavailable states. The old sample patterns page is no longer a production
  destination, and live-data inventory, live-only route gate, and
  transitional-label gate evidence remain reviewer-safe Admin guardrails.
- The `/runtime/runs` API is backed by a process-local runtime service in the
  public API facade. Durable runtime database models, repositories, graph
  execution, and worker code exist, but a run started only through that facade
  should not be treated as persisted across API restarts unless your deployment
  wires it to the DB-backed runtime path. Runs claimed by the orchestration
  worker can load a pinned published workflow bundle, execute graph nodes in
  dependency order, schedule independent role nodes in parallel waves, persist
  run steps and timeline evidence, and resume without duplicating succeeded
  steps.
- The `/runs` Web API channel service still has process-local pieces for some
  user-channel run state and rate windows. Browser access to `/runs` redirects
  or aliases into the Admin run workspace under `/admin/app/channels/runs`.
  Telegram command aliases, link token audits, linked identity records, webhook
  update receipts, and delivery attempts are PostgreSQL-backed, so Telegram
  linking, duplicate update replay, alias routing evidence, and final delivery
  diagnostics survive API restarts after migrations are applied.
- The Admin skill lifecycle workspace projects packages, versions, tenant
  grants, installations, readiness checks, smoke-test evidence, diagnostics,
  binding eligibility, and audit records from persistent skill registry
  repositories. Some legacy direct `/admin/skill-registry` API paths still use
  a process-local `SkillRegistryService` facade, so use `/admin/app/skills` and
  the repository-backed route family for production-like validation.
- The SkillExecutionGateway provides governed read-only Daily Intelligence
  Briefing tool execution for calendar events, Gmail messages, news search,
  weather forecasts, and commute lookup. Local QA and diagnostics use
  deterministic mock fixtures. Approved live probes require non-local
  environment policy, tenant-scoped installation readiness, credential metadata,
  and outbound allow decisions.
- The model provider gateway can call OpenAI and local OpenAI-compatible chat
  completion endpoints. Provider connection records store ordered safe
  credential secret reference ids. Provider probes and runtime gateway attempts
  resolve the first configured reference through the configured secret provider
  at call time, never at save time. OpenAI calls fail closed when a credential
  reference is missing or cannot be resolved. Local OpenAI-compatible providers
  may run without credentials only when the endpoint passes the configured local
  allowlist.
- The workflow builder now supports a complete custom workflow setup path. It
  can save full workflow documents through the React Admin mutation contract,
  edit role/contract/graph/join/approval/subworkflow structure through visible
  controls, bind prompt and runtime profile references per agent, attach
  repository-backed Test Bench evidence, validate and publish with backend-owned
  gates, and hand the published workflow to runtime launch or Design Reviews.
  The browser remains a guided authoring surface; the backend remains the
  source of truth for revision checks, idempotency, validation, publish
  readiness, evidence freshness, authorization, and redaction.
- Console Home now includes an authorized `Set up workflow` action that opens
  the fixed-frame workflow onboarding wizard at
  `/admin/app/workflows/onboarding`. Use it when a tenant admin wants to start
  from arbitrary scenario intent rather than first learning workflow registry
  internals. The wizard creates or resumes durable drafts through existing
  workflow APIs, keeps generated roles/contracts/graph/evidence editable, and
  preserves backend-owned validation, publish readiness, launch eligibility,
  tenant scope, and redaction.

These notes are not warnings to avoid the system. They are the boundaries to
know when moving from local evaluation to a production deployment.

## Spec Coverage Map

The setup and operating guidance in this document is based on these feature
areas:

- Spec 001, platform foundation: FastAPI service, PostgreSQL, migrations,
  health, dependency checks, workers, and baseline commands.
- Spec 002, platform auth and access: Auth0, local principals, tenants, role
  grants, support overrides, and access audit decisions.
- Spec 003, workflow studio registry: workflow lineages, drafts, revisions,
  validation, publishing, immutable bundles, and sharing grants.
- Spec 004, durable orchestration runtime: workflow runs, run steps, leases,
  checkpoints, approvals, handoffs, side effects, lineage, and retention.
- Spec 005, immutable memory: memory scopes, immutable versions, head
  projections, audit records, archive markers, and runtime links.
- Spec 006, user interaction channels: Web UI, Web API, Telegram commands,
  idempotency, approvals, notifications, callbacks, and artifacts.
- Spec 007, model and skill routing: tenant, workflow, agent, and step routing
  precedence; prompts, tools, outbound domains, credentials, and provenance.
- Spec 008, production audit debugging: run search, timeline, replay, lineage,
  version bundles, redacted exports, trace ids, and audit-safe inspection.
- Spec 009, reliability and scale hardening: admission controls, quotas, fair
  scheduling, retries, circuit breakers, compensation, dead letters, and
  artifact throughput.
- Spec 010, admin console shell: shared navigation, scope display, saved
  filters, common states, and route-preserving admin links.
- Spec 011, model provider gateway: provider connections, OpenAI/local
  adapters, safe probes, health, catalog sync, gateway records, and visibility.
- Spec 012, prompt runtime profiles and gateway completion: prompt library,
  profile versions, tenant grants, runtime pins, provider provenance, and
  gateway-ready execution metadata.
- Spec 013, admin workflow builder: guided browser workflow authoring, graph
  preview, reference lookup, validation, publish gate, and bundle detail views.
- Spec 014, skill registry lifecycle and browser-first V2: package manifests,
  validation, publication, tenant grants, installations, credentials, smoke
  tests, and binding eligibility.
- Spec 015, agent workflow test bench: suites, cases, safe execution modes,
  redacted transcripts, contract assertions, token summaries, and publish gates.
- Spec 016, token usage and cost analytics: normalized usage events, pricing
  versions, dashboards, tenant/platform access, and CSV exports.
- Spec 017, Telegram configuration console: tenant Telegram readiness, protected
  commands, link tokens, masked identities, diagnostics, and safe webhook
  validation.
- Spec 018, user and tenant membership administration: only a QA environment
  stub is present in this checkout, so this guide relies on the implemented
  access-control and tenancy code for practical tenant and user setup.
- Spec 019, operations console logs and performance: health, capacity, provider
  and channel status, reliability pressure, redacted logs, bounded filters, and
  CSV operational exports.
- Spec 020, workflow graph execution and parallel sub-agent runtime: pinned
  bundle graph loading, dependency scheduling, parallel scout waves, join
  policies, durable run-step evidence, checkpoint/resume safety, and safe final
  outputs.
- Spec 021, real skill tool execution connectors: SkillExecutionGateway,
  read-only Daily Briefing adapters, tool/outbound/credential policy decisions,
  mock diagnostics, live-probe gating, and redacted request/response summaries.
- Spec 022, Telegram natural-language trigger delivery persistence: tenant
  command aliases, persistent link tokens and identities, webhook idempotency,
  alias-triggered workflow runs, mocked-safe Bot API delivery, and delivery
  attempts.
- Spec 023, user briefing preferences and context: tenant/principal Daily
  Briefing preference profiles, immutable revisions, safe admin summaries,
  import/export, and runtime preference resolution.
- Spec 024, automatic test bench evidence integration in workflow publish
  gates: repository-backed required-test evidence, current draft-revision
  matching, stale/missing/failing blockers, safe publish gate summaries, and
  legacy manual status compatibility without trust.
- Spec 025, live model credential resolution for gateway calls: call-time
  ProviderSecretResolver use in probes and runtime, OpenAI fail-closed
  credential behavior, local no-auth allowlist behavior, and redaction-safe
  diagnostics.
- Spec 026, React admin UI foundation: `/admin/app` mount, built assets served
  under `/admin/static/react`, bootstrap/config/manifest contracts, generated
  TypeScript contracts, and Auth0/local-principal validation.
- Spec 027, modern admin shell and design system: backend-authorized navigation,
  active scope, breadcrumbs, command/search, saved-filter chips, common states,
  responsive layout, and shared React primitives.
- Spec 028, React admin data contracts and form patterns: page envelopes, safe
  problem details, mutation results, filters, pagination, sorting, export
  snapshots, evidence summaries, and a protected patterns sample.
- Spec 029, operations workbench: React operations, reliability, run debug,
  redacted log, and export workspace over existing operations services.
- Spec 030, React workflow builder: guided workflow draft authoring, graph/list
  review, validation, publish evidence, revision history, and redacted JSON
  preview.
- Spec 031, React governance: provider setup and health, credential reference
  diagnostics, prompt/profile governance, routing previews, policy history,
  direct-call guardrails, and run provenance.
- Spec 032, React skill lifecycle: package publication, tenant discovery and
  installation, credentials, smoke/readiness checks, connector diagnostics,
  binding eligibility, quarantine/withdrawal state, and audit evidence.
- Spec 033, React agent and workflow test bench: suite/case authoring, safe run
  launch, progress, diagnostics, artifacts, publish-gate evidence, and audit.
- Spec 034, React membership administration: user directory, invitations,
  principal linking, role grants, status changes, access history, and audit.
- Spec 035, React usage and cost analytics: metric cards, trends, rollups,
  event drilldowns, filters, exports, confidence, partial, and denied states.
- Spec 036, React channel, Telegram, and briefing preferences: readiness,
  Telegram configuration, aliases, link tokens, identity summaries, delivery
  diagnostics, safe run status, and Daily Briefing preferences.
- Spec 037, React admin migration hardening and Jinja retirement: route parity
  matrix, retirement planning, rollback guidance, performance, accessibility,
  redaction, tenant-isolation, and reviewer evidence.
- Spec 038, Jinja surface inventory and deletion plan: inventory of remaining
  templates, legacy static assets, browser routes, direct links, dependencies,
  parity blockers, and deletion evidence.
- Spec 039, no-Jinja React host, auth shell utilities, and local login:
  non-Jinja React host HTML, local-login HTML, shell compatibility, and
  old-link redirects.
- Spec 040, workflow registry full React parity and Jinja removal: workflow
  registry, creation, builder, validation, publish, and revision browser flows
  moved fully to React.
- Spec 041, governance full React parity and Jinja removal: provider, prompt,
  profile, routing, policy, credential diagnostic, and provenance browser
  flows moved fully to React.
- Spec 042, skill registry and tool diagnostics full React parity and Jinja
  removal: skill package, tenant installation, credential readiness, connector
  diagnostics, eligibility, quarantine, and audit browser flows moved fully to
  React.
- Spec 043, test bench full React parity and Jinja removal: suite/case
  authoring, safe run launch, diagnostics, artifacts, publish-gate evidence,
  and audit browser flows moved fully to React.
- Spec 044, operations, reliability, run inspection, and usage full React
  parity: readiness, reliability, run debug, log, export, and cost review
  browser flows moved fully to React.
- Spec 045, channels, memberships, access, Telegram, and briefing full React
  parity: channel readiness, Telegram, briefing preferences, memberships,
  saved filters, identities, delivery diagnostics, and access browser flows
  moved fully to React.
- Spec 046, user-facing run UI React port and Jinja removal: `/runs` and
  `/runs/{run_id}` browser links redirect or alias into the React run workspace
  with start, status, timeline, result, artifact, and approval controls.
- Spec 047, Jinja infrastructure decommission: template renderer wiring,
  server template directory, legacy static assets, and direct `jinja2`
  dependency removed, with readiness evidence available through Admin
  guardrail routes.
- Spec 048, live data inventory and mock guardrails: production Admin route,
  backend projection, frontend source, generated contract, and built asset
  scanner with live-only policy, computed metadata allowlists, route response
  scans, and reviewer-safe guardrail evidence.
- Spec 049, React contract provenance and sample route retirement:
  backend-owned provenance and empty-state metadata, `/admin/app/patterns`
  removed or development-gated outside production, and production frontend
  actions cleared of hardcoded QA revision or idempotency defaults.
- Spec 050, workflow React live data: workflow registry and builder projections
  replaced with live workflow registry, validation, publish-gate, sharing,
  artifact, and test-bench evidence services.
- Spec 051, governance React live data: provider, credential-reference, prompt,
  runtime profile, routing, policy history, gateway diagnostic, and run
  provenance panels backed by durable governance services.
- Spec 052, skill lifecycle React live data: package publication, tenant grant,
  installation, credential readiness, smoke-test, connector diagnostic,
  binding eligibility, quarantine, withdrawal, and audit panels backed by live
  skill registry and gateway evidence.
- Spec 053, test bench React live data: suites, cases, assertions, runs, run
  steps, artifacts, publish-gate evidence, launcher metadata, diagnostics, and
  audit panels backed by durable test bench services.
- Spec 054, membership and access React live data: principal identities,
  invitations, tenant memberships, role grants, access decisions, support
  override state, status actions, history, and audit panels backed by live
  membership/access repositories.
- Spec 055, channels, Telegram, and briefing React live data: channel
  readiness, Telegram config, aliases, link-token audit, linked identities,
  webhook receipts, delivery attempts, channel runs, notifications, and Daily
  Briefing preference summaries backed by durable records.
- Spec 056, usage React live data: usage totals, trends, rollups, drilldowns,
  pricing confidence, attribution, reconciliation, and export requests backed
  by live usage events, pricing versions, and storage metadata.
- Spec 057, operations and run debug React live data: operational health,
  pressure, run-debug timelines, likely causes, reliability recovery, exports,
  provider/channel/skill/usage evidence, and worker/queue state backed by live
  operations and runtime sources.
- Spec 058, live-only UI decommission gate: final production Admin route
  inventory, empty and seeded route probes, built asset scans, obsolete
  deterministic module retirement, seed requirements, fixture boundaries, and
  rollback guidance.
- Spec 059, Admin UI transitional React label removal: user-facing Admin
  labels, breadcrumbs, titles, command/search text, redirects, fallback copy,
  docs, screenshots, and visible-text scanner evidence that reserve "React" for
  implementation or developer-only migration context.
- Spec 060, design review domain foundation: tenant-scoped sessions,
  immutable revisions, review rounds, reviewer assignments, verdicts, quorum
  decisions, manual decisions, handoffs, idempotency, and safe JSON contracts.
- Spec 061, model-backed graph role executor: governed role-node execution
  through ModelGateway when explicit execution mode, pins, credentials, policy,
  tenant scope, redaction, and output-contract validation permit it.
- Spec 062, design review coordinator and iteration loop: one acyclic runtime
  run per review round, four-of-five or three-of-four zero-blocker quorum,
  revision creation, approved handoff, and durable manual decisions.
- Spec 063, Admin design review workspace: `/admin/app/design-reviews` live
  session creation, launch controls, revision/round/verdict/quorum/handoff
  inspection, template state, and manual-resolution actions.
- Spec 064, Design Reviewer Council template and publish gates: explicit
  tenant template install, deterministic and model-safe evidence, current
  draft-revision publish readiness, and QA outcome matrix.
- Spec 065, Agent Communication Graph contracts: safe backend graph JSON for
  workflow drafts and published bundles with node/edge categories, references,
  badges, provenance, layout hints, and accessibility summaries.
- Spec 066, Agent Graph Viewer: read-only workflow draft/version graph canvas,
  equivalent keyboard node and edge lists, selected details, and truthful
  empty/partial/denied states.
- Spec 067, Runtime Agent Communication Graph: operations run inspection graph
  overlaying published topology with run steps, timeline, handoffs, gateway,
  tool, delivery, lineage, artifact, status, and partial evidence.
- Spec 068, durable interaction replay evidence: tenant-scoped safe interaction
  records for delegation, context transfer, result return, joins, approvals,
  handoffs, tool calls, checkpoints, manual resolution, and replay details.
- Spec 069, workflow document authoring contracts and mutation APIs: complete
  workflow document save/load contracts, section summaries, idempotent replay,
  stale conflict recovery, validation finding mapping, and redaction-safe
  mutation evidence.
- Spec 070, React workflow graph and agent role builder: browser controls for
  roles, contracts, graph nodes and edges, join policies, approval gates,
  subworkflow references, and graph layout without raw JSON editing.
- Spec 071, prompt profile creation and per-agent binding UI: per-role prompt
  and runtime profile binding matrix, safe readiness badges, reference key
  generation, and durable save/reload behavior.
- Spec 072, custom workflow test evidence and publish setup: required publish
  evidence setup in the workflow builder, safe case creation, deterministic run
  launch, current/stale/failed evidence distinctions, and Test Bench handoff.
- Spec 073, end-to-end custom workflow setup wizard and runtime launch:
  checklist-driven workflow creation, three-agent starter, evidence setup,
  validation, publish, runtime launch prefill, Design Reviews workflow
  selection, mobile layout checks, and tenant isolation.
- Spec 074, Console Home onboarding wizard entry and fixed-frame shell:
  authorized `Set up workflow` quick action, tenant-scoped onboarding route,
  bounded step rail/body/footer, resume and exit behavior, and 1280 x 800
  no-scroll shell guardrails.
- Spec 075, generic scenario intake and durable draft blueprint:
  scenario-neutral intake, workflow key normalization, durable draft creation,
  editable generic blueprint generation, revision-safe saves, and tutorial
  label guardrails.
- Spec 076, stepwise agents, contracts, and graph configuration: bounded
  agent, contract, graph, join, approval, and review steps with paged
  collections and backend validation summaries.
- Spec 077, resource readiness, bindings, and evidence configuration:
  prompt/profile summaries, provider/skill/channel readiness, required Test
  Bench evidence attachment, deterministic evidence state, and safe freshness
  display.
- Spec 078, publish, launch, and operational verification finish:
  validation, publish blockers, confirmation, published bundle refresh,
  runtime launch links, Design Reviews handoff, operations, and graph evidence
  links.
- Spec 079, non-scrolling wizard QA, docs, and guardrails: QA documents,
  validation manifests, Playwright no-scroll journeys, screenshot evidence,
  redaction sweeps, hard-coded tutorial terminology scans, and final docs.

## 1. Overview

The Multi-Agent Platform is an administrative and runtime system for building,
testing, publishing, running, auditing, and operating AI workflows. A workflow is
a governed definition of work that may reference prompts, agent profiles,
sub-agents, skills, model providers, memory scopes, approval gates, reusable
subworkflows, input and output contracts, and publish-time validation rules.

The system has several major capabilities:

- Tenant-aware authentication and authorization with Auth0 or local principals.
- An Admin console with workflow, access, reliability, operations, model,
  prompt, profile, skill, test bench, usage, channel/Telegram, and briefing
  preference workspaces, plus Design Review Council workspace and graph
  inspection panels.
- Workflow registry and workflow builder pages for creating draft workflows,
  validating graphs and references, reviewing revisions, and publishing
  immutable workflow bundles.
- A Console Home-launched generic workflow onboarding path for tenant admins:
  choose `Set up workflow`, describe an arbitrary scenario, create or resume a
  durable draft, review bounded agents/contracts/graph/resource/evidence steps,
  validate, publish, and open runtime launch or Design Reviews handoff
  surfaces. The older checklist-driven builder path remains available for
  advanced editing.
- Published workflow graph execution for role nodes, sub-agent nodes, joins,
  approvals, terminal nodes, parallel fanout, partial failures, and durable
  checkpoint/resume evidence.
- Design Review Council sessions that persist safe design revisions, review
  rounds, reviewer verdicts, quorum decisions, manual decisions, template
  readiness, and development handoff references.
- Agent Communication Graphs for workflow drafts, published versions, and
  runtime runs, including durable replay evidence when interaction records are
  available.
- Durable orchestration models for workflow runs, steps, worker leases,
  checkpoints, handoffs, approvals, side-effect intents, audit events, and
  retention metadata.
- Immutable memory models for append-only memory scopes, version lineage,
  current head projections, read/write audit records, archive markers, and
  runtime references.
- User interaction channels for Web UI, Web API, Telegram command access, and
  tenant-scoped Telegram aliases such as `Morning briefing`.
- Daily Intelligence Briefing preference profiles that personalize on-demand
  and future scheduled briefing workflows while preserving safe admin views.
- Model and skill routing configuration with tenant, workflow, agent, and step
  precedence.
- Model provider gateway management for OpenAI and local OpenAI-compatible
  providers.
- Prompt library and agent runtime profile management with immutable versions,
  tenant grants, validation, preview, and history.
- Skill registry lifecycle pages for package publication, tenant availability,
  tenant installation, credential readiness, smoke-test evidence, and binding
  eligibility.
- Governed skill tool execution for approved read-only Daily Briefing
  connectors with policy checks, redacted summaries, and diagnostics.
- Agent and workflow test bench for safe mock, mocked-tool, and approved probe
  test runs, including repository-backed required evidence for workflow publish
  gates.
- Production audit/debugging surfaces for run search, timeline, replay, lineage,
  bundle snapshots, export evidence, and redaction-safe investigation.
- Reliability controls for admission, quotas, retries, circuit breakers,
  compensation, dead letters, and operator inspection.
- Operations console for platform-admin and auditor review of readiness,
  capacity, providers, channels, reliability pressure, throughput, redacted logs,
  and CSV exports.
- Token usage and cost analytics for LLM usage events captured through the
  model gateway.
- Live-data guardrails for production Admin routes, including route inventory,
  source and built-asset scans, backend-owned provenance, truthful empty states,
  sample route retirement, live-only gate evidence, and transitional label
  cleanup.

### What A Complete Local Setup Includes

A complete local setup has:

- PostgreSQL running.
- Migrations applied.
- Admin browser dependencies installed and built.
- At least one active tenant.
- One platform administrator principal.
- One tenant administrator principal.
- The API server running.
- Optionally, a worker process running in a second terminal.
- A model provider configured, either local or OpenAI.
- At least one prompt version and one agent runtime profile.
- Optional Daily Intelligence Briefing preference profiles for tenant users.
- At least one workflow draft that validates and publishes.
- A complete workflow setup path that can be verified through the browser
  without raw JSON edits.
- The `Set up workflow` onboarding action visible on Console Home for
  authorized workflow principals.
- Current passing test-bench evidence for any workflow draft that declares
  required suites.
- Optional skill packages and tenant installations.
- Optional Skill Tool Diagnostics showing all Daily Briefing tools ready in
  mock mode.
- Optional test bench suite with passing evidence.
- Optional Telegram configuration, command aliases, identity link, and delivery
  attempts.
- Audit, usage, and operations pages available for troubleshooting.

### Install The Project

From the repository root:

```bash
uv sync
cp .env.example .env
```

For the simplest first setup, edit `.env` and set:

```bash
AUTH_MODE=local_principal
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/multi_agent_platform
```

Start PostgreSQL:

```bash
docker compose up -d postgres
```

Apply migrations:

```bash
uv run alembic upgrade head
```

Build Admin browser assets:

```bash
cd frontend/admin
npm install
npm run build
cd ../..
```

Create starter tenant rows:

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform <<'SQL'
INSERT INTO tenants (
  tenant_id,
  slug,
  display_name,
  status,
  created_at,
  updated_at
)
VALUES
  (
    '11111111-1111-1111-1111-111111111111',
    'acme',
    'Acme',
    'active',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
  ),
  (
    '22222222-2222-2222-2222-222222222222',
    'globex',
    'Globex',
    'active',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
  )
ON CONFLICT (slug) DO NOTHING;
SQL
```

Start the API:

```bash
uv run uvicorn multi_agent_platform.api.main:app --reload
```

If you are validating runtime worker behavior, start a worker in a second
terminal:

```bash
uv run python -m multi_agent_platform.workers.main
```

Open the local login page:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app
```

Useful health pages:

- `http://127.0.0.1:8000/health/live`
- `http://127.0.0.1:8000/health/ready`
- `http://127.0.0.1:8000/dependencies`
- `http://127.0.0.1:8000/version`

### Main Admin Areas

After login, start at `/admin/app`. The Admin console groups the system
by operational area while preserving backend authorization, active scope,
breadcrumbs, search, common states, and generated browser contracts. Older
admin browser paths are compatibility redirects or safe non-Jinja responses.

Build the Admin browser assets whenever frontend code or generated contracts
change:

```bash
cd frontend/admin
npm install
npm run build
cd ../..
```

Important browser pages:

- `/admin/app` - Admin home and authorized workspace shell.
- `/admin/app/operations` - operations, reliability, and run debug workbench.
- `/admin/app/workflows` - workflow registry, guided builder, custom workflow
  setup checklist, graph/role authoring, prompt/profile binding, required
  evidence setup, validation, publish, and launch handoff.
- `/admin/app/workflows/onboarding` - generic workflow onboarding wizard
  launched from Console Home through `Set up workflow`. Use this first when a
  tenant admin wants step-by-step setup from scenario intent to draft,
  evidence, publish, and launch without raw JSON editing.
- `/admin/app/design-reviews` - Design Review Council sessions, reusable
  template readiness, review rounds, manual decisions, quorum evidence, and
  handoff references.
- `/admin/app/governance` - model providers, prompt library, runtime profiles,
  routing previews, policy history, and run provenance.
- `/admin/app/skills` - skill package lifecycle, tenant installations,
  connector diagnostics, and binding eligibility.
- `/admin/app/test-bench` - agent and workflow test bench.
- `/admin/app/memberships` - user and tenant membership administration.
- `/admin/app/usage` - token usage and cost analytics.
- `/admin/app/channels` - channel readiness, Telegram configuration, aliases,
  identities, delivery evidence, safe run status, and Daily Briefing
  preferences.
- `/admin/app/patterns` - not a production sample-data route. If a
  development-only patterns route is retained, it must be explicitly enabled
  and unavailable in production-like validation.
- `/admin` and older `/admin/...` browser links - safe redirects or non-Jinja
  compatibility responses into Admin.
- `/runs` and `/runs/{run_id}` - user-facing run links that open the Admin run
  workspace under `/admin/app/channels/runs`.

### Admin UI Visual Tour

The screenshots below were captured from the running local server on May 8-11,
2026 with Playwright at desktop viewports. The workflow setup screenshots for
Specs 069 through 079 are captured from the focused Playwright QA runs under
`output/playwright/qa069_ui` through `output/playwright/qa079_ui`. The Admin
pages use the `tenant-admin-acme` local principal so tenant-scoped controls and
records are visible. If a Markdown viewer scales a screenshot down, open the
image directly.

Common shell elements appear on nearly every Admin page:

- Left navigation: grouped links for Access, Workflows, Model and Skill Config,
  Prompt Runtime, Run Inspection, and Reliability. The highlighted link is the
  current workspace. These links preserve the active authorization context.
- Breadcrumbs: the path at the top of the page. The first breadcrumb returns to
  Console Home, and the final breadcrumb names the current workspace.
- Page title and product label: confirms the current workspace and that the
  browser is inside the Multi-Agent Admin console.
- Signed-in user: shows the active principal catalog key or display name.
- System health: summarizes backend readiness for the current request.
- Active scope: shows whether the page is platform scoped or tenant scoped.
  Platform administrators may see a scope selector; tenant administrators see
  their assigned tenant.
- Log off: clears the local login cookie and returns to the login flow.
- Status pills: short state labels such as `ready`, `empty`, `unavailable`, or
  `missing`. These describe backend-owned live data, not sample records.
- Action buttons: run mutations, exports, validation, or refresh requests
  through guarded Admin routes. When an area has no live rows, the page keeps
  the action or empty state visible instead of inventing data.

#### Local Login

![Local login screen](docs/assets/user-guide/admin-ui/local-login-wide.png)

- Principal cards list the enabled local QA identities from
  `LOCAL_PRINCIPAL_CATALOG_JSON`.
- Role badges show the catalog roles granted to that local identity.
- The catalog key text is the value stored in the protected local cookie after
  sign-in.
- Each Sign In button posts the chosen principal, a safe redirect target, and a
  local action token to `/auth/local-login`.
- Use `Platform Admin` for platform-wide readiness checks. Use `Acme Tenant
  Admin` or another tenant principal for tenant-scoped setup and operating
  pages.

#### Console Home

![Console home](docs/assets/user-guide/admin-ui/admin-home-wide.png)

- The summary panel reports the active tenant, the number of authorized
  workspaces, the number of notices needing attention, and whether the scope is
  tenant or platform mode.
- Refresh reloads the home envelope from the backend.
- Current notices lists actionable system notices for the active scope. An
  empty notice state means there are no active notices.
- Start here contains quick-action links for common workflows: set up a
  workflow, review workflows, search runs, check routing, review providers,
  manage skills, open test bench, manage access, and review usage.
- Set up workflow opens the generic onboarding wizard. It preserves the active
  tenant scope and is shown only when backend navigation says the principal may
  use workflow registry actions.
- Authorized destinations lists every workspace the principal can open in the
  current scope. Each card states the destination purpose and provides an
  Open button.
- The page intentionally shows only destinations allowed by backend
  authorization.

#### Workflow Onboarding Wizard

Use `Set up workflow` on Console Home when you want a guided, generic setup
path before opening the advanced workflow builder. The wizard is mounted at
`/admin/app/workflows/onboarding`, but reviewers should reach it by clicking
the visible Console Home action after local login.

- Scenario intake captures a neutral workflow name, key, purpose, launch mode,
  expected inputs, expected outputs, coordination style, approval needs,
  optional channel preference, and evidence preference.
- Create durable draft uses the existing workflow draft create action. The
  draft is persisted in the workflow registry and can be reopened in the
  advanced editor.
- Draft, Agents, Contracts, Graph, Resources, Evidence, Publish, and Launch
  steps stay inside a fixed frame with a step rail and footer actions. Large
  collections are summarized or paged instead of requiring vertical scrolling.
- The generated blueprint is generic and editable. It should not mention
  tutorial scenarios as default product behavior.
- Resource readiness, validation, publish readiness, required evidence
  freshness, tenant scope, authorization, and launch eligibility remain
  backend-owned. Browser progress is only a summary.
- Evidence setup attaches required Test Bench suites through the existing
  workflow save action and keeps raw transcripts out of wizard summaries.
- Launch links open authorized Admin workspaces such as user runs, Design
  Reviews, operations, or graph evidence with tenant scope preserved.
- At a 1280 x 800 viewport, the page, wizard body, and footer should remain
  usable without vertical scrolling, clipped controls, overlapping text, or
  hidden buttons.

#### Operations And Run Debug

![Operations and run debug](docs/assets/user-guide/admin-ui/operations-wide.png)

- Workbench summaries show operational readiness cards for tenant evidence,
  system health, Telegram/channel status, reliability state, run activity,
  provider gateway, skill execution, and usage.
- Open details links on cards jump the operator to the deeper source page for
  that signal when one is available.
- Likely causes summarizes detected run or operations failure patterns for the
  active scope.
- Tenant activity shows recent visible run or operational activity for the
  selected tenant and time range.
- Recovery posture reports retries, dead letters, breaker state, and recovery
  evidence that the principal is allowed to see.
- Export evidence requests a redacted operational evidence package.
- Redacted signals lists safe log rows and summaries without raw secrets,
  prompts, completions, messages, connector payloads, or local filesystem
  paths.

#### Runtime Agent Graph

![Runtime agent graph](docs/assets/user-guide/admin-ui/runtime-agent-graph-wide.png)

- The Run Debug section can show a runtime communication graph for the selected
  run when authorized evidence exists.
- Node and edge colors and pills show safe runtime status such as succeeded,
  retry scheduled, paused, queued, or unavailable.
- The selected detail panel shows safe references to run steps, timeline
  events, gateway/tool summaries, handoffs, approvals, artifacts, or partial
  evidence.
- Node list and Edge list mirror the graph for keyboard review and narrow
  layouts.
- Partial or unmapped evidence appears as a graph-level status instead of
  fabricated nodes.

#### Interaction Replay Graph

![Interaction replay graph](docs/assets/user-guide/admin-ui/interaction-replay-graph-wide.png)

- When durable interaction evidence exists, graph edges include ordered replay
  references for delegation, context transfer, result return, joins, approvals,
  handoffs, tool calls, checkpoints, manual resolution, or run completion.
- The detail panel lists safe replay summaries, statuses, classifications,
  timestamps, and authorized reference links.
- Replayed interactions are idempotent across worker retry/resume; the graph
  should not show duplicated replay rows for the same stable interaction key.
- Unmapped replay evidence stays in graph-level partial evidence so operators
  know the replay is incomplete without guessing topology.

#### Workflow Registry And Builder

![Workflow registry and builder](docs/assets/user-guide/admin-ui/workflows-wide.png)

- The registry area lists workflow lineages, drafts, revision status, validation
  state, publish readiness, and sharing evidence when live workflow records
  exist.
- The empty state is truthful: no workflow rows are currently available for
  the captured Acme scope.
- Create draft starts a guided workflow draft flow for the active tenant.
- The active draft area shows full-document authoring, graph, prompt/profile
  reference, required evidence, validation, publish, revision, and launch
  controls once a draft exists.
- Complete workflow saves post the canonical workflow document plus revision,
  idempotency key, safe client context, and change summary to the backend-owned
  save route.
- Duplicate saves replay safely. Same-key different-payload saves return safe
  idempotency validation findings. Stale saves return recovery guidance without
  overwriting the local draft.
- Validation and publish sections use backend-owned evidence, including
  required test-bench gates when configured.
- The page keeps older workflow URLs compatible through redirects into this
  Admin workspace.

#### Workflow Document Save Contract

![Workflow document save contract](output/playwright/qa069_ui/qa069-workflow-setup-smoke.png)

- The workflow builder loads a canonical `WorkflowDraftDocument` and safe
  section summaries from `/admin/app/workflows/drafts/{workflow_draft_id}/detail.json`.
- Saving a draft persists roles, prompt/profile references, skill references,
  contracts, nodes, edges, join policies, approval gates, subworkflow
  references, required test requirements, and editor annotations in one
  revisioned document.
- Backend validation maps malformed documents to safe section and field-path
  findings so reviewers can return directly to metadata, roles, graph,
  references, tests, or publish readiness.
- The JSON inspector remains read-only and redacted. It must not expose raw
  prompts, completions, credential values, provider payloads, tool payloads,
  memory contents, private channel content, stack traces, or local filesystem
  paths.

#### Workflow Graph And Role Builder

![Workflow graph and role builder](output/playwright/qa070_ui/qa070-workflow-graph-role-desktop.png)

- Role cards let authorized admins edit role keys, names, kind, purpose,
  responsibilities, contracts, prompt/profile references, skill bindings, and
  graph node references through form controls.
- Contract cards define workflow input, output, data, handoff, artifact,
  memory, tool-access, approval-decision, failure, and compatibility contracts
  without editing raw JSON.
- Graph topology controls edit the entry node, nodes, edges, edge contracts,
  branch conditions, retry metadata, and node layout positions.
- Join controls support `all_success`, `quorum`, `first_success`, and
  `manual_resolution` strategies with required branches, quorum count,
  timeout, failure behavior, and merge contract metadata.
- Approval controls capture approver scope, optional role code, decision
  contract, resume behavior, timeout, visibility, and reviewer instructions.
- The canvas is visual, and node/edge/join lists provide keyboard-readable
  equivalents for accessibility and mobile review.

#### Prompt And Runtime Profile Binding

![Prompt/profile binding](output/playwright/qa071_ui/qa071-prompt-profile-binding-desktop.png)

- The Per-Agent Bindings area summarizes prompt and runtime profile readiness
  for every role in the workflow document.
- The binding matrix shows ready, missing, incomplete, or blocked state without
  rendering raw prompt template content.
- Role binding controls can generate safe prompt reference keys and runtime
  profile reference keys, then save those references back into the workflow
  document.
- Graph summaries and role fields show safe binding readiness and reference
  keys only. Credential values, provider headers, prompt bodies, completions,
  private messages, raw tool payloads, memory contents, and unauthorized tenant
  labels must not appear.
- Mixed readiness is allowed while authoring. Validation and publish readiness
  decide whether unresolved prompt/profile references block release.

#### Required Publish Evidence Setup

![Required publish evidence setup](output/playwright/qa072_ui/qa072-workflow-test-evidence-desktop.png)

- The Required publish evidence section helps attach authorized Test Bench
  suites to the workflow draft and current revision.
- Create suite, Attach suite, Add safe case, Launch deterministic run, and
  Clear run result actions write through backend-owned Test Bench and workflow
  save routes.
- Evidence cards distinguish current passing evidence from stale, missing,
  failed, queued, running, or blocked evidence. The browser must not claim stale
  or failed evidence is current.
- Publish readiness and validation findings link back to evidence setup when a
  required suite is missing, stale, or failing.
- The workflow document stores safe requirement references and summaries. It
  does not store protected run payloads, prompt bodies, provider headers,
  credentials, tool payloads, private channel messages, stack traces, or local
  filesystem paths.

#### End-To-End Custom Workflow Setup

![End-to-end workflow setup](output/playwright/qa073_ui/qa073-workflow-setup-desktop.png)

- The Custom workflow launch checklist appears near the top of the builder and
  groups the setup path into Metadata, Agents, Prompts And Profiles, Graph,
  Contracts, Evidence, Validation, Publish, and Launch.
- Apply three-agent starter creates a realistic coordinator, research agent,
  and synthesis agent with prompt/profile references, contracts, role nodes,
  a join node, edges, and a join policy.
- The checklist summarizes progress for reviewers, but backend validation,
  repository-backed Test Bench evidence, and publish readiness remain the
  release source of truth.
- After publish, Open runtime launch sends the workflow id to the run
  workspace. The run page preselects the workflow but does not start a run until
  the user submits Start Run.
- Select in Design Reviews opens the Design Reviews workspace with the
  published workflow available for authorized session creation.
- Mobile views should stack checklist cards, evidence cards, controls, and
  long ids without overlap.

#### Workflow Agent Graph

![Workflow agent graph](docs/assets/user-guide/admin-ui/workflow-agent-graph-wide.png)

- Draft and published workflow detail pages include a read-only Agent
  Communication Graph when backend graph data is available.
- The graph shows coordinator agents, sub-agents, tools, joins, approval gates,
  handoffs, terminals, and directional communication edges.
- The selected node or edge detail panel shows safe category, status, badges,
  references, and related links without raw prompts, completions, credentials,
  provider payloads, memory contents, or raw tool payloads.
- Node list and Edge list provide the same information as the canvas for
  keyboard and mobile review.
- Empty, partial, denied, and stale graph states are rendered directly from
  backend-owned graph contracts.

#### Design Reviews

![Design reviews workspace](docs/assets/user-guide/admin-ui/design-reviews-wide.png)

- The Design Reviews workspace shows live tenant sessions, current review
  status, manual-decision count, approved handoff count, and template readiness.
- Create request starts a durable design review session from a safe request
  summary, quorum policy, and optional authorized published workflow bundle.
- Workflow selectors can be prefilled from a published workflow handoff. The
  selected workflow must still be visible to the active principal and tenant.
- Sessions lists only live tenant-scoped records. Empty states do not invent
  reviewer rows, quorum decisions, or handoffs.
- Selected session details expose safe revisions, rounds, reviewer verdict
  summaries, quorum decisions, manual decisions, and handoff references.
- Launch and manual-resolution actions write through coordinator APIs with
  idempotency keys and safe rationale.

#### Governance

![Governance workspace](docs/assets/user-guide/admin-ui/governance-wide.png)

- The governance summary covers provider connections, prompt versions, runtime
  profiles, routing policy, gateway diagnostics, policy history, and run
  provenance.
- The empty state means the current scope has no live governance records yet.
- Section buttons for Setup, Providers, Prompts, Profiles, Routing, and
  Provenance switch the operator between governance panels and display each
  panel status.
- Readiness summary counts visible provider connections, prompt lineages, and
  runtime profiles.
- Setup and health lists configured model provider connections and safe
  provider health status.
- Versions and safe previews show prompt lineage/version information and
  redacted preview state when records exist.
- Runtime configuration shows profile resolution evidence and active profile
  version state.
- Read-only policy preview shows routing and policy history without allowing
  unsafe direct provider calls.
- Safe changes and Run evidence show policy history and run provenance when
  live records are present.

#### Skill Lifecycle

![Skill lifecycle workspace](docs/assets/user-guide/admin-ui/skills-wide.png)

- The skill lifecycle summary covers package publication, tenant grants,
  installations, credential readiness, smoke tests, connector diagnostics,
  binding eligibility, and audit evidence.
- Section buttons such as Discover, Installations, Diagnostics, Binding, and
  Audit switch between lifecycle panels and report live status.
- The empty state confirms no governed skill lifecycle rows are visible for the
  captured scope.
- Lifecycle readiness explains whether available, granted, installed, ready,
  quarantined, or diagnostic skill records exist.
- Granted tenant skills and installation panels list package versions and
  tenant install readiness when records exist.
- Reference readiness, queued readiness, and connector readiness explain
  credential-reference and smoke-test state without exposing credential values.
- Preview binding computes whether a skill can be bound to a workflow.
- Run diagnostic launches a governed, redaction-safe connector diagnostic.

#### Agent Tests

![Agent tests workspace](docs/assets/user-guide/admin-ui/test-bench-wide.png)

- The test bench header describes guided suite authoring, safe run launch,
  diagnostics, artifacts, publish gates, and governance evidence.
- The empty state shows that no suite, run, or gate rows are available for the
  captured Acme scope.
- Release confidence cards summarize suites, running test runs, runs needing
  review, and required publish gates.
- Audit timeline shows test-bench lifecycle events when records exist.
- When suites are present, this workspace is where operators create cases,
  launch safe mock or approved probe runs, inspect diagnostics, and confirm
  current publish-gate evidence.

#### Membership Administration

![Membership administration](docs/assets/user-guide/admin-ui/memberships-wide.png)

- The section navigation switches between Overview, Directory, Invitations,
  Role grants, Status, Access history, Support overrides, and Audit.
- Summary cards show current platform user count, invitation count, role grant
  count, access-history count, support override count, and audit event count.
- Users lists visible principals and tenant memberships. Details buttons open
  a user's membership and access context when available.
- Invite users sends a tenant invitation with a selected role. The replay-safe
  checkbox controls whether repeated submissions reuse the same invitation
  request.
- Link identity connects an external or local identity to a principal, with a
  confirmation checkbox for conflict recovery.
- Assign roles grants a selected role to a selected principal.
- Access-changing actions lists grant, suspend, restore, or similar actions
  that have changed access state.
- Recent decisions records authorization decisions and the route or permission
  involved.
- Temporary access evidence shows support override state.
- Membership timeline lists membership and access audit events for the tenant.

#### Usage Analytics

![Usage analytics](docs/assets/user-guide/admin-ui/usage-wide.png)

- Filters constrain the view by group, tenant, provider, and model. Tenant
  administrators are locked to their tenant.
- Export CSV requests a redacted usage export for the selected filters.
- Usage states explain empty, tenant-constrained, denied, partial, or
  unavailable conditions.
- Summary cards report total tokens, estimated cost, usage events, average
  latency, unavailable usage, and pricing confidence.
- Daily usage shows the selected time series with confirmed tokens, estimated
  tokens, cost, and latency.
- Rollups group usage by the selected dimension, such as day, provider, model,
  workflow, agent, prompt, execution mode, principal, gateway operation, or
  governed tool.
- Safe events lists individual redacted usage events when available.
- Create export records an audited CSV export request and links to export
  detail when generated.

#### Channels, Telegram, And Briefing Preferences

![Channels and briefing workspace](docs/assets/user-guide/admin-ui/channels-wide.png)

- The readiness header shows how many scoped channel summaries are ready and
  when the panel was refreshed.
- Refresh reloads channel, Telegram, run, notification, and briefing preference
  evidence.
- Readiness cards summarize Telegram enablement, webhook availability,
  reference readiness, linked identity count, alias count, and delivery
  attempts.
- States shows empty or unavailable channel conditions for the active scope.
- Telegram Configuration shows redacted bot/reference state and saves safe
  configuration changes.
- Webhook Validation shows the latest persisted validation evidence and the
  Validate button triggers a mock-safe validation path.
- Aliases lists natural-language command aliases and Create Alias adds one for
  the tenant.
- Identity Links lists linked Telegram identities and Create Code starts a safe
  one-time link-code flow.
- Delivery Diagnostics summarizes delivery attempts and receipt status without
  exposing raw private messages.
- Admin Summaries contains redacted briefing preference summaries plus Import
  and Export controls for safe preference artifacts.

#### User-Facing Run Workspace

![Run workspace](docs/assets/user-guide/admin-ui/channel-runs-wide.png)

- The run workspace keeps `/runs` and `/runs/{run_id}` browser links inside the
  Admin shell while preserving the user-facing run flow.
- The status pill reports whether the run page is ready, loading, or in an
  action state.
- New run opens a blank run-start state.
- Workflow selects the safe workflow reference to run.
- Links from a published workflow can prefill the Workflow field through a safe
  `workflow_id` query value, but a run does not start until Start Run is
  submitted.
- Request summary is the only free-text request content shown in the browser.
  It should remain a safe summary rather than a private message or raw payload.
- Start Run submits the workflow reference and request summary to the retained
  run API.
- The action-state area reports whether a start request has been submitted,
  accepted, denied, or failed.

### Quality Checks

Use the project checks when changing code or validating an installation:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

For React admin changes also run:

```bash
uv run python scripts/frontend/generate_admin_react_types.py --check
cd frontend/admin
npm run typecheck
npm run test
npm run build
cd ../..
```

For production Admin route, live-data, or visible-copy changes, add focused
guardrail validation:

```bash
uv run pytest tests/unit/admin/test_live_data_inventory_scanner.py \
  tests/integration/api/test_admin_live_data_inventory_routes.py \
  tests/unit/admin/test_transitional_label_scanner.py \
  tests/integration/api/test_admin_transitional_label_routes.py
uv run python scripts/qa/verify_live_only_gate_qa058.py
uv run python scripts/qa/verify_transitional_labels_qa059.py
```

The repository also provides:

```bash
./scripts/check.sh
```

## 2. Security

The platform supports two authentication modes:

- `AUTH_MODE=auth0` for production-style JWT authentication.
- `AUTH_MODE=local_principal` for local development, browser QA, and demos.

Production refuses to start with `AUTH_MODE=local_principal`. If `APP_ENV` is
`production`, Auth0 settings must be complete and secret values must be supplied
through safe references where required.

### Roles

The principal roles used by the platform are:

- `tenant_user` - can use tenant-scoped user surfaces where allowed.
- `tenant_admin` - can administer tenant-scoped resources for one tenant.
- `platform_admin` - can administer platform-wide resources and cross-tenant
  surfaces.
- Auditor-style access is supported in policy for operational inspection
  surfaces, especially the operations console.

Permissions are checked against protected route surfaces. Role grants are stored
in the database and evaluated with tenant scope, platform scope, and support
override rules.

Important: the authorization service checks required permission codes before it
checks the required role for protected routes. In local-principal mode, those
permission codes come from `LOCAL_PRINCIPAL_CATALOG_JSON`. In Auth0 mode, those
permission codes come from validated token claims, while platform role grants
come from the platform database.

### Tenant Scope

A tenant is a customer or isolated business unit. Most records are either
platform scoped or tenant scoped. Tenant-scoped admin pages and APIs usually
accept `tenant_id=<uuid>` or infer the tenant from the signed-in principal.

Platform admins can review platform-scoped resources. Cross-tenant access is
guarded, and support-style override records are required for sensitive
cross-tenant work. Tenant admins should see only their own tenant data.

### Running With Local Principals

Local principals are the easiest and safest first setup mode. They are not
password accounts. They are named test identities defined in
`LOCAL_PRINCIPAL_CATALOG_JSON` and activated through the `X-Local-Principal`
header or the browser login cookie.

Example local catalog:

```bash
export AUTH_MODE=local_principal
export LOCAL_PRINCIPAL_HEADER=X-Local-Principal
export LOCAL_PRINCIPAL_CATALOG_JSON='{
  "platform-admin": {
    "catalog_key": "platform-admin",
    "display_name": "Platform Admin",
    "role_codes": ["platform_admin"],
    "permission_codes": [
      "platform:admin",
      "tenant:read",
      "tenant:admin",
      "admin:role-grants:write",
      "admin:support-overrides:write",
      "admin:support-overrides:approve",
      "skill-registry:publish",
      "skill-registry:quarantine",
      "skill-registry:audit",
      "skill-execution:read",
      "agent-tests:manage",
      "agent-tests:run",
      "agent-tests:read",
      "agent-tests:gate",
      "usage:read",
      "usage:export",
      "telegram-config:read",
      "telegram-config:write",
      "telegram-config:tokens",
      "telegram-config:diagnostics",
      "briefing-preferences:read",
      "briefing-preferences:write",
      "briefing-preferences:export",
      "briefing-preferences:resolve",
      "operations:read",
      "operations:logs",
      "operations:export"
    ]
  },
  "tenant-admin-acme": {
    "catalog_key": "tenant-admin-acme",
    "display_name": "Acme Tenant Admin",
    "tenant_id": "11111111-1111-1111-1111-111111111111",
    "org_id": "org-acme",
    "role_codes": ["tenant_user", "tenant_admin"],
    "permission_codes": [
      "tenant:read",
      "tenant:admin",
      "skill-registry:install",
      "skill-registry:bind",
      "skill-registry:audit",
      "skill-execution:read",
      "agent-tests:manage",
      "agent-tests:run",
      "agent-tests:read",
      "agent-tests:gate",
      "usage:read",
      "usage:export",
      "telegram-config:read",
      "telegram-config:write",
      "telegram-config:tokens",
      "telegram-config:diagnostics",
      "briefing-preferences:read",
      "briefing-preferences:write",
      "briefing-preferences:export",
      "briefing-preferences:resolve"
    ]
  },
  "auditor": {
    "catalog_key": "auditor",
    "display_name": "Operations Auditor",
    "role_codes": [],
    "permission_codes": ["operations:read", "operations:logs", "operations:export"]
  }
}'
```

For browser use, open:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app
```

Choose a catalog key such as `platform-admin` or `tenant-admin-acme`. The login
sets the configured local principal cookie, which defaults to
`map_local_principal`. For API calls, send `X-Local-Principal:
tenant-admin-acme` or another configured key.

Troubleshooting local login:

- If login shows no users, `LOCAL_PRINCIPAL_CATALOG_JSON` is missing or invalid.
- If a tenant admin cannot see tenant pages, confirm the catalog entry includes a
  `tenant_id` matching an active row in the `tenants` table.
- If the server refuses to start, check that `APP_ENV` is not `production`.
- If a custom local principal header is used, it must start with `X-`.

### Running With Auth0

Auth0 mode validates bearer JWTs through Auth0 JWKS metadata. The platform
requires the Auth0 domain, issuer, and audience settings in `.env`.

Minimum Auth0 `.env` settings:

```bash
APP_ENV=production
AUTH_MODE=auth0
AUTH0_DOMAIN=your-tenant.us.auth0.com
AUTH0_ISSUER=https://your-tenant.us.auth0.com/
AUTH0_AUDIENCE=https://multi-agent-platform.example.com
AUTH0_ALGORITHMS=RS256
AUTH0_REQUIRED_ORG_CLAIM=true
```

Recommended Auth0 setup:

1. Create an Auth0 API for the platform.
2. Set the API Identifier to the same value used in `AUTH0_AUDIENCE`.
3. Make sure issued access tokens use RS256.
4. Configure applications that will access the platform to request that
   audience.
5. Include organization or tenant information in the token when
   `AUTH0_REQUIRED_ORG_CLAIM=true`.
6. Define permissions in Auth0 for the admin surfaces your users need.
7. Create users in Auth0 and assign them to the correct organization or roles.
8. Have each user sign in or call `/auth/me` once so the platform can upsert the
   principal identity.
9. Add database role grants for those principal identities.

The platform normalizes JWT claims into a principal. Auth0 proves who the user
is, token permissions prove which protected actions the token may request, and
platform role grants determine the user's platform or tenant role. This means a
user can exist in Auth0 but still be denied by the platform until both the token
permissions and the database role grants match the route being used.

### Adding Tenants

Create tenants before assigning tenant admins or creating tenant-scoped
resources. Tenant ids are UUIDs. Use clear slugs and display names because these
appear in admin views and audit context.

Example tenant insert:

```sql
INSERT INTO tenants (
  tenant_id,
  slug,
  display_name,
  status,
  created_at,
  updated_at
)
VALUES (
  '33333333-3333-3333-3333-333333333333',
  'northwind',
  'Northwind Traders',
  'active',
  CURRENT_TIMESTAMP,
  CURRENT_TIMESTAMP
)
ON CONFLICT (slug) DO NOTHING;
```

For local testing, add a local principal entry with that tenant id. For Auth0,
create or assign the user in Auth0, then create a platform role grant for the
principal identity that corresponds to that Auth0 subject.

### Adding Users In Local Principal Mode

Add users by adding entries to `LOCAL_PRINCIPAL_CATALOG_JSON`.

For a tenant admin, include:

- `catalog_key` - what the user chooses at local login.
- `display_name` - what admin pages display.
- `tenant_id` - tenant UUID.
- `org_id` - organization label used by auth context.
- `role_codes` - include `tenant_user` and `tenant_admin`.
- `permission_codes` - include the permissions needed for the target admin
  surfaces.
- `enabled` - omit it or set `true`.

Restart the API after changing `.env`. If the user is already logged in with a
different local cookie, visit `/auth/local-login` again and choose the new
principal.

### Adding Users In Auth0 Mode

For Auth0:

1. Create the user in Auth0.
2. Assign the user to the correct Auth0 organization or application access.
3. Make sure the access token contains the configured audience and issuer.
4. Have the user access `/auth/me` or any protected platform page.
5. Locate the new row in `principal_identities`.
6. Create a `role_grants` row for platform or tenant scope.
7. Test the user on `/admin` and a tenant-scoped page.

Bootstrap tip: many teams first run local-principal mode to create tenants and
understand role grants, then switch to Auth0. In a new production environment,
you can bootstrap the first platform admin by inserting the principal identity
and role grant directly through a controlled database migration or one-time DBA
procedure.

### Role Grant Checklist

When a user is denied access:

1. Confirm the user is authenticated: `/auth/me`.
2. Confirm the tenant exists and is active.
3. Confirm the role grant is active.
4. Confirm the role grant scope matches the page, platform for global pages and
   tenant for tenant pages.
5. Confirm the route policy allows the user's role or permission.
6. Confirm cross-tenant platform-admin work has the required support override
   when the policy requires it.
7. Check the response `x-trace-id`, then inspect audit and operations views.

## 3. LLM Setup

LLM setup has four parts:

1. Configure secret handling.
2. Configure model providers.
3. Create prompts and agent runtime profiles.
4. Attach those prompts, profiles, providers, and skills to workflows.

### Secret Handling

The settings support three secret provider modes:

- `SECRET_PROVIDER=static` with values in `STATIC_SECRETS_JSON`.
- `SECRET_PROVIDER=env` with environment variables named from the requested
  reference and prefixed by `ENV_SECRET_PREFIX`.
- `SECRET_PROVIDER=secret_manager` with references starting with
  `SECRET_MANAGER_PREFIX`.

For local evaluation, `static` or `env` is usually enough. For production, use
environment or secret-manager references instead of raw tokens in `.env`,
provider records, prompt text, workflow definitions, or skill manifests.

Example env-style secret for records that are resolved by the current built-in
environment secret provider:

```bash
SECRET_PROVIDER=env
ENV_SECRET_PREFIX=MAP_SECRET_
MAP_SECRET_OPENAI_API_KEY=sk-your-key
```

Then use `OPENAI_API_KEY` as the external reference in records that call the
secret provider. Current code builds the environment variable name from the exact
reference it receives by uppercasing it, replacing `/` and `-` with `_`, and
prepending `MAP_SECRET_`. Separate settings such as
`TELEGRAM_PROVIDER_TOKEN_REF` and `CHANNEL_CALLBACK_SIGNING_SECRET_REF` require
safe labels like `env:` or `secret-manager/` in production for readiness
validation, so deployments that also resolve those labels should provide a
resolver or convention that maps the label to the real secret value.

Model provider records must store only safe credential secret reference ids.
Provider probes and runtime gateway calls select the first configured reference
in stored order and resolve it immediately before the adapter call. Blank,
duplicate, or raw-secret-looking entries such as direct `sk-` keys, bearer
tokens, passwords, and pasted API keys are rejected by provider validation.

### OpenAI Provider Setup

OpenAI provider readiness, credential references, health, and probe evidence
are reviewed in `/admin/app/governance`. Sign in as a platform admin and keep
provider records configured with safe secret references. Older
`/admin/model-providers` browser links should redirect into the React
governance workspace or expose only safe JSON/API behavior.

Recommended fields:

- Display name: `OpenAI Production`.
- Provider type: `openai`.
- Base URL: leave blank for the default OpenAI chat completions URL unless your
  deployment uses an OpenAI-compatible proxy.
- Models: add the model ids you allow, for example `gpt-4.1` or the approved
  model id for your organization.
- Timeout policy: set connection, read, and total timeouts appropriate to your
  SLO.
- Visibility: use `platform_default` for a shared provider or
  `tenant_allowlist` for selected tenants.
- Credential references: add the safe secret reference that your deployment uses
  for the OpenAI API key. With the built-in environment secret provider, a
  resolvable reference usually looks like `OPENAI_API_KEY` paired with
  `MAP_SECRET_OPENAI_API_KEY`; if your deployment uses `env:` labels, verify
  that your resolver maps the label before live calls.
- Active: enable only after the connection is reviewed.

OpenAI provider probes and runtime calls require a resolvable credential
reference. If the first configured reference is missing, empty, or cannot be
resolved by the configured secret provider, the probe or gateway attempt fails
before any provider call with the safe category `secret_reference_invalid`.
Diagnostics show the provider, model, connection id, trace id, and reference id;
they do not show authorization headers, prompt bodies, completion bodies, or the
raw credential value.

### Local Model Setup

Local providers use OpenAI-compatible chat completions. This works with services
that expose `/v1/chat/completions`, such as a local model gateway or a compatible
server in front of Ollama.

Default local URL safety settings allow:

- Schemes: `http`, `https`.
- Hosts: `127.0.0.1`, `localhost`.
- Ports: `8000`, `8080`, `11434`.
- CIDR ranges: `127.0.0.0/8`.

Example local provider:

- Display name: `Local Ollama Compatible`.
- Provider type: `local_openai_compatible`.
- Base URL: `http://127.0.0.1:11434`.
- Models: add the exposed model ids, for example `llama3.1` or your local
  server's advertised model name.
- Credential references: leave blank if the local endpoint does not require a
  bearer token.
- Visibility: allow the tenant that will use the provider.
- Active: enabled.

If your local model server runs on a different host or port, update the
`MODEL_PROVIDER_LOCAL_ALLOWED_*` settings before saving the connection. The
platform intentionally rejects local URLs with userinfo, secret-like query
parameters, disallowed ports, or disallowed networks.

For an Ollama-style local setup, install and start the local model server, pull
the model you want to use, and confirm the OpenAI-compatible endpoint responds
before adding it to the platform:

```bash
ollama pull llama3.1
curl http://127.0.0.1:11434/v1/models
```

If the curl command fails, fix the local model server before changing platform
settings. If the curl command works but the platform rejects the provider URL,
check `MODEL_PROVIDER_LOCAL_ALLOWED_HOSTS`, `MODEL_PROVIDER_LOCAL_ALLOWED_PORTS`,
and `MODEL_PROVIDER_LOCAL_ALLOWED_CIDRS`.

Local OpenAI-compatible providers may omit credentials only when the base URL
passes the local endpoint allowlist. If a credential reference is configured,
the gateway resolves it at call time and passes it only to the adapter request
for that physical attempt.

### Model Routing

Model routing decides which provider/model a workflow step should use.
Resolution precedence is:

1. Step override.
2. Agent override.
3. Workflow override.
4. Tenant default.

Set a tenant default first so every workflow has a fallback. Then add workflow,
agent, or step overrides only where a different model is clearly needed. The
governance workspace at `/admin/app/governance` exposes preview, history,
rollback, and provenance views so you can verify the final resolved model before
publishing or running. Older model-skill configuration browser links should
redirect into React or return safe non-Jinja responses.

### Prompt Library

Prompt review, safe preview, save feedback, and history live in
`/admin/app/governance`. Older prompt-runtime browser links should redirect
into React or return safe non-Jinja responses.

Recommended workflow:

1. Create a prompt lineage with a clear name and purpose.
2. Save a draft with the template text.
3. Define template variables.
4. Run safe fixture previews to confirm variables render correctly.
5. Validate the prompt.
6. Publish an immutable prompt version.
7. Grant the version to the tenants that may use it.
8. Retire old versions only after workflows no longer require them.

Do not put raw secrets, credentials, customer private data, or unsupported
memory content in prompt text. Prompt versions become immutable once published,
so fixing a prompt means publishing a new version, not editing the old one.

### Agents And Sub-Agents

Agent runtime profile review, safe edits, resolution previews, and history live
in `/admin/app/governance`. Older profile browser links should redirect into
React or return safe non-Jinja responses. A profile
describes the behavior and runtime expectations for one agent or sub-agent.

Important profile fields include:

- `agent_key` - stable identifier used by workflow definitions.
- `agent_kind` - `agent` or `sub_agent`.
- Purpose - what the agent is allowed and expected to do.
- Prompt references - immutable prompt versions the profile uses.
- Model routing hints - preferred provider/model behavior.
- Memory scope policy - what memory the agent may read or write.
- Skill requirements - skills the agent may call.
- Tool policy expectations - allowed tools and side-effect limits.
- Output contract expectations - shape of the response.
- Test suite requirements - required test evidence before use.

Recommended setup:

1. Create a profile for the main workflow agent.
2. Create separate profiles for specialized sub-agents, such as research,
   summarization, review, routing, or tool-use roles.
3. Attach prompt versions to each profile.
4. Validate each profile.
5. Activate immutable profile versions.
6. Grant versions to the tenants that may use them.
7. Use the profile resolution page to confirm the platform selects the intended
   profile for a tenant/workflow/agent key.

Use sub-agents when a workflow has a bounded, specialized task that benefits
from separate prompts, models, skills, or test requirements. Avoid making every
step a sub-agent; each additional profile increases routing, testing, and
operational complexity.

### Daily Briefing Preferences

Daily Intelligence Briefing preferences live in `/admin/app/channels`.
Preferences store one active profile per tenant/principal, with immutable
revisions and a current head projection for fast runtime lookup. API endpoints
remain available for automation; old browser links should redirect into React
or return safe non-Jinja responses.

Useful API endpoints are:

- `/admin/briefing-preferences/api/profile`
- `/admin/briefing-preferences/api/summaries`
- `/admin/briefing-preferences/api/export`
- `/admin/briefing-preferences/api/import`
- `/admin/briefing-preferences/api/resolve`

User-editable fields include:

- Location label and IANA timezone.
- News topics.
- VIP sender hints.
- Workday start and end time in `HH:MM`.
- Commute mode.
- Default calendar and email account references.
- Output style.
- Optional scheduled briefing toggle and scheduled time.

Calendar and email fields must be references such as
`delegated:calendar:primary`, `delegated:gmail:primary`, or another approved
secret/delegated reference. Do not enter OAuth tokens, API keys, passwords, raw
account identifiers, or customer-private credential values. Admin summaries show
readiness, counts, masked/fingerprinted values, revision metadata, and
timestamps rather than raw VIP senders or full account references.

When Telegram or another channel starts a Daily Intelligence Briefing run, the
runtime resolver can attach the latest preference revision and content digest to
the run input. Updates affect future runs only; already-started runs keep the
preference context pinned at creation time.

### Workflow Setup From Start To Finish

Use Console Home `Set up workflow` for the generic onboarding path, especially
from a clean tenant or when the user wants to describe an arbitrary scenario
before seeing advanced workflow controls. The action opens
`/admin/app/workflows/onboarding` with the active tenant scope preserved. The
wizard captures scenario intent, creates or resumes a durable draft, pages
agents/contracts/graph/resource summaries inside a 1280 x 800 fixed frame,
attaches required evidence when available, validates, publishes, and links to
runtime, Design Reviews, operations, or graph evidence surfaces through visible
Admin links.

Use `/admin/app/workflows` for the full builder and advanced guided browser
flow. Older workflow browser links should redirect into this workspace or
return safe non-Jinja responses. A tenant admin can complete the custom
workflow setup journey from these pages without raw JSON editing.

1. Start from Console Home and select `Set up workflow`, or open Workflows when
   you already know which draft to edit.
2. Enter a neutral workflow scenario, review the suggested workflow key, and
   create or resume the durable draft.
3. Open the new draft from the create result or use the Advanced editor link
   when you need the full builder.
4. Review the Custom workflow launch checklist near the top of the builder.
5. Fill in metadata such as name, description, owner, tenant visibility, and
   intended business use.
6. Apply the three-agent starter when you want a complete baseline. It creates
   coordinator, research, and synthesis roles plus starter contracts, role
   nodes, a join node, edges, prompt/profile references, and a join policy.
7. Adjust role cards through visible controls for role key, name, kind,
   purpose, responsibilities, contracts, prompt/profile references, skill
   bindings, and graph node references.
8. Define input, output, approval-decision, handoff, artifact, memory,
   tool-access, or data contracts so the workflow has clear boundaries.
9. Edit graph topology with entry node, node, edge, edge-contract, branch,
   retry, and layout controls.
10. Configure approval gates for human review points.
11. Configure join policies for parallel work, such as `all_success`, `quorum`,
    `first_success`, or `manual_resolution`.
12. Add subworkflow references only to authorized published workflow versions.
13. Use the Per-Agent Bindings area to attach prompt and runtime profile
    references to each role. Safe reference keys and readiness badges are shown;
    raw prompt bodies and credential values are not.
14. Attach model routing overrides only where they are necessary.
15. Attach skill installations and tool policies needed by each step.
16. Use Required publish evidence to create or attach a Test Bench suite, add a
    safe deterministic case, and launch a deterministic run for the current
    draft revision.
17. Save the draft. The save route stores the complete workflow document with a
    revision token and idempotency key.
18. Validate the draft and review backend-owned findings.
19. Resolve reference errors, missing skill versions, missing prompt/profile
    grants, invalid edges, missing evidence, stale evidence, and contract
    problems through the linked sections.
20. Review the publish gate page or the publish section in the builder.
21. Prepare and confirm publish only when validation and current required
    evidence are ready.
22. Inspect the immutable published bundle detail page and Agent Communication
    Graph.
23. Open runtime launch from the workflow handoff. The workflow field is
    prefilled, but a run starts only after the operator submits Start Run.
24. Open Design Reviews from the workflow handoff if the published workflow
    should be used as a review workflow selection.
25. Start a run through the Web UI, Web API, or Telegram after channel setup.

Workflow validation is intentionally strict. It checks graph structure,
reference visibility, exact skill versions, secret-like text markers, approval
scope, join strategies, and publish gate evidence. Required test evidence is
loaded from the Agent Test Bench repository for the same tenant, workflow draft,
and current draft revision. The browser checklist can summarize progress, but it
does not override backend validation or publish readiness. Legacy
`latest_result_status` fields remain parseable compatibility metadata, but they
should not be treated as release evidence unless repository-backed current
passing test runs also exist. Skill references should use specific immutable
versions rather than floating labels such as `latest`, `main`, or `dev`.

The workflow document save route is revisioned and idempotent. An exact replay
of a save returns an idempotent replay result without creating another
revision. Reusing an idempotency key for a different document returns a safe
validation error. A stale save returns safe reload guidance and leaves the
current document intact.

When a published workflow run is claimed by the durable worker, the graph
executor loads the pinned bundle document and runs graph nodes in dependency
order. Independent role nodes can run in the same parallel wave. The Daily
Intelligence Briefing flagship graph starts with an orchestrator, fans out to
four scout sub-agents, joins their safe summaries, runs a focus recommender, and
then runs synthesis to produce the final briefing. Join policies include
`all_success`, `quorum`, `first_success`, and `manual_resolution`; manual
resolution pauses the run with durable approval and timeline evidence.

### Design Review Council Setup

Use `/admin/app/design-reviews` for the Design Reviewer Council scenario. The
workspace is live-data backed and depends on the design-review domain APIs,
workflow registry, runtime coordinator, test bench, and publish gates.

Typical setup:

1. Sign in as a tenant admin or platform admin acting in explicit tenant scope.
2. Open `/admin/app/design-reviews?tenant_id=<tenant-id>`.
3. If the council template is not installed, run the Install council template
   action. The action creates or reuses the tenant's canonical workflow draft,
   attaches required Test Bench evidence, and reports publish readiness.
4. Open `/admin/app/workflows` to inspect the created draft, Agent
   Communication Graph, validation findings, and publish gate.
5. Publish only after the current draft revision has passing required evidence.
6. Return to `/admin/app/design-reviews` and create a session from a safe
   request summary, quorum policy, and optional published workflow bundle.
7. Launch a coordinator round when a workflow bundle is available.
8. Inspect round history, reviewer verdict summaries, quorum decisions,
   revisions, and handoff state.
9. If the session pauses for manual resolution, choose revise,
   approve-by-exception, retry, or cancel with safe rationale.

The coordinator keeps the runtime graph acyclic. One workflow run is one review
round against one immutable design revision. Passing quorum requires
`four_of_five_no_blockers` or `three_of_four_no_blockers` with zero blocking
issues. Non-passing complete evidence can create a new immutable revision.
Incomplete, contradictory, unsafe, exhausted, or policy-conflicted evidence
pauses for manual resolution.

Useful API patterns:

```bash
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  "http://127.0.0.1:8000/admin/design-reviews/sessions?tenant_id=<tenant-id>"

curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  "http://127.0.0.1:8000/admin/design-reviews/sessions/<session-id>/coordinator?tenant_id=<tenant-id>"

curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  "http://127.0.0.1:8000/admin/workflows/drafts/<workflow-draft-id>/agent-graph?tenant_id=<tenant-id>"
```

Design Review records and graph contracts store safe summaries, digests,
artifact references, usage/provenance summaries, and policy references. They
must not store or render raw prompts, raw completions, provider responses,
credentials, private channel payloads, memory contents, unauthorized payloads,
stack traces, or raw tool outputs.

### Skills

Skills represent approved tools or MCP references that agents may use. The
governed lifecycle is handled through `/admin/app/skills`. Older skill registry
and skill execution browser links should redirect into this workspace or return
safe non-Jinja responses.

Skill package setup:

1. Sign in as a platform admin.
2. Create a skill package slug and description.
3. Paste or upload a manifest candidate.
4. Validate the manifest.
5. Fix schema, credential, permission, action-category, network, or docs
   classification errors.
6. Publish an immutable package version.
7. Grant that version to allowed tenants.

Tenant installation setup:

1. Sign in as the tenant admin or platform admin acting in tenant scope.
2. Open available skill versions.
3. Install the approved version.
4. Configure credential references, never raw credentials.
5. Run smoke tests.
6. Review readiness evidence.
7. Preview binding eligibility.
8. Attach the installation to agent profiles or workflow steps.

Skill manifests must avoid raw secrets. They should list approved tool or MCP
references, action categories, network requirements, credential requirements,
runtime permissions, compatibility information, safe documentation, artifact
digests, maintainers, and support metadata.

Supported action category vocabulary includes read, write, notify, admin,
search, summarize, and calendar. Unsupported action categories, unsupported
runtime permissions, secret-looking values, unknown integration refs, and unsafe
documentation classification fail validation.

Publishing and installing a skill does not automatically let every model call
use it. The tenant installation must be ready, the workflow or agent profile
must reference the skill, and model-skill routing or tool policy must allow the
tool action for that tenant and scope. Use the binding eligibility preview
before publishing a workflow so the first runtime attempt does not fail because
the tool is unavailable.

Current-state reminder: complete skill package and tenant installation flows in
one API session unless your deployment has replaced the in-memory service with a
persistent registry service.

### Skill Tool Execution

Runtime nodes should call approved tools through the SkillExecutionGateway, not
by importing adapters directly. The gateway accepts a typed request with tenant,
actor, workflow run, role node, skill package version, tool name, execution
mode, and output contract metadata. It checks installation/version eligibility,
model-skill tool policy, outbound allowlist policy, side-effect policy,
credential metadata, and credential tenant ownership before adapter invocation.

The first built-in read-only tools are for the Daily Intelligence Briefing:

- `google_calendar.events.read`
- `gmail.messages.read`
- `news.search`
- `weather.forecast.read`
- `commute.lookup`

Open `/admin/app/skills` and use the connector diagnostics/readiness sections
to run safe mock diagnostics. The page should show all five tool families, mode
`mock`, readiness, redacted credential status, allowed domains, latest safe
summaries, and policy decisions. The automation API endpoints are
`/admin/skill-execution/api/diagnostics` and
`/admin/skill-execution/api/diagnostics/run`.

Local QA does not call Google, Gmail, news, weather, traffic, or maps services.
Approved live probes are staging-style checks and require non-local environment
policy, tenant-scoped skill installation readiness, delegated credential or
secret-reference metadata, and outbound allow decisions. Write-capable or
side-effecting tool requests are blocked by default unless a future explicit
policy allows the exact operation.

## 4. Test Bench

The agent and workflow test bench lives at `/admin/app/test-bench`. It lets
administrators create safe, tenant-scoped test suites for prompts, agent
profiles, workflow drafts, published subworkflows, and published workflows.
Older test-bench browser links should redirect into Admin or return safe
non-Jinja responses.

The test bench workspace is live-data backed. Empty tenants should show
truthful empty states, and seeded tenants should show only repository-backed
suites, cases, assertions, runs, steps, artifacts, publish-gate evidence, and
audit summaries. Test fixtures may remain in test-only paths, but production
Admin routes must not import or render them as domain data.

Supported target types:

- `prompt_version`
- `agent_profile_version`
- `workflow_draft`
- `published_subworkflow`
- `published_workflow`

Supported safe execution modes:

- `mock_model` - uses deterministic model output for repeatable tests.
- `mock_tools` - allows model-like execution while mocking tools and blocking
  real side effects.
- `real_model_side_effects_disabled` - allows a real-model-style path while
  blocking side effects.
- `approved_real_probe` - requires an approved probe reference and fails closed
  without one.

### Creating A Test Suite

You can create and run suites directly in `/admin/app/test-bench`, or from a
workflow draft's Required publish evidence section when the suite is for that
draft.

1. Open `/admin/app/test-bench`, or open the workflow builder and scroll to
   Required publish evidence.
2. Create a new suite.
3. Choose the tenant.
4. Choose the target type and target id.
5. For workflow publish evidence, target the workflow draft and current draft
   revision.
6. Add safe fixture summaries.
7. Add one or more test cases, or use Add safe case from the workflow evidence
   panel for deterministic evidence.
8. Define expected contract shapes.
9. Add deterministic assertions or evaluator settings.
10. Choose the model/tool mode.
11. Set a pass threshold.
12. Save the suite.
13. Run the suite, or use Launch deterministic run from the workflow evidence
    panel.

Results include pass/fail status, step traces, provider/model metadata,
prompt/profile and skill references, token usage summary, latency, contract
validation, assertion diagnostics, blocked side effects, redacted transcript
summary, and artifact metadata. The test bench avoids raw secrets, prompt
bodies, full private transcripts, and unauthorized tenant data.

### Publish Gate Use

Publish gates can require current passing test evidence before a workflow,
prompt profile, or related target is published. Workflow publish gates read
required-suite evidence from the Agent Test Bench repository; admins should not
copy status values into workflow JSON to satisfy the gate. For workflow drafts,
current evidence means the same tenant, the same workflow draft id, the same
current draft revision id, a matching target type, and a passing run.

If a publish gate blocks, open the test bench run detail and confirm:

- The suite target matches the current candidate.
- The latest run is current, not stale, queued, running, failed, blocked, or
  tied to an older revision.
- The run passed the configured threshold.
- Fixture summaries are valid and safe.
- Contract assertions match the current workflow or profile output.
- Any approved real probe includes a valid approved probe reference.
- The publish gate's required-test summary shows the expected required,
  passing, missing, failing, and stale counts.

In the workflow publish gate UI, this appears as the required-test or Required
Test Evidence summary. A blocked summary should disable publish confirmation
and provide safe remediation text.

Publication performs a fresh evidence lookup after validation so a workflow
cannot publish with stale validation JSON. Cross-tenant suite references fail
closed and must not reveal the other tenant's suite name, run id, fixtures,
transcripts, prompts, secrets, or artifacts.

### Test Bench Troubleshooting

If a run does not start, check authentication, tenant scope, and whether the
target id exists. If a run fails immediately, check the selected safe mode and
whether a real probe was attempted without approval. If assertions fail, compare
the expected contract to the current prompt/profile/workflow output contract.

If a tenant admin sees no suites, confirm the suite tenant matches the user's
tenant. If a platform admin sees cross-tenant information unexpectedly missing,
check support override requirements and the active scope shown in the admin
shell.

## 5. Audit And Debugging

Effective troubleshooting starts with the trace id. The platform adds
`x-trace-id` to responses. When a user reports a failure, ask for the time, the
tenant, the page or command, and the trace id if available.

### First Checks

1. Confirm the API is running with `/health/live`.
2. Confirm dependencies with `/health/ready` and `/dependencies`.
3. Confirm the user can authenticate with `/auth/me`.
4. Confirm the active tenant id.
5. Confirm the relevant resource exists.
6. Confirm role grants and support overrides.
7. Check `/admin/app/operations` for platform readiness and redacted logs.
8. Check `/admin/app/operations` for workflow run timelines and replay
   evidence, or `/admin/app/channels/runs` for user-facing run state.
9. Check `/admin/app/usage` if the issue is model invocation or cost related.
10. Check `/admin/app/channels` if the issue came from Telegram.

### Operations Console

The operations console at `/admin/app/operations` is intended for platform
admins and auditors. It summarizes health, dependency readiness, capacity,
provider and channel status, reliability pressure, throughput, redacted logs,
and exportable evidence. Older operations, reliability, and run-inspection
browser links should redirect into React or return safe non-Jinja responses.

Use log filters for:

- Trace id.
- Tenant id.
- Run id.
- Component.
- Severity.
- Status.
- Dependency.
- Start and end time.
- Limit.

The operations console reads redacted operational records from audit timeline,
runtime traces, gateway attempts, and related projections. It does not expose
raw log files, secrets, raw prompts, raw completions, raw memory content, or
provider credentials.

### Run Inspection

Use `/admin/app/operations` for React run-debug summaries. The debug surfaces
support run search, timeline, replay, lineage, bundle snapshots, notification
state, secret-access metadata, and redacted exports. Older `/admin/runs`
browser links should redirect into React; the listed API patterns remain
automation/debug endpoints.

Useful API patterns:

```bash
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  "http://127.0.0.1:8000/admin/runs/debug-search?tenant_id=<tenant-id>&status=failed"

curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  "http://127.0.0.1:8000/admin/runs/<workflow-run-id>/timeline?tenant_id=<tenant-id>"

curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  "http://127.0.0.1:8000/admin/runs/<workflow-run-id>/replay?tenant_id=<tenant-id>"

curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  "http://127.0.0.1:8000/admin/runs/<workflow-run-id>/agent-graph?tenant_id=<tenant-id>"
```

When reviewing a run, look for:

- The published workflow bundle id.
- The execution bundle pin.
- The graph load event and graph schema/version.
- Step status transitions.
- Parallel execution wave markers.
- Role kind, agent key, sub-agent key, and node key metadata.
- Approval gate status.
- Join policy decisions and partial failure summaries.
- Side-effect intent status.
- Handoff envelopes.
- Checkpoint references and resume markers.
- Worker lease acquisition and renewal.
- Retry and breaker summaries.
- Model gateway attempts.
- Skill tool execution summaries.
- Runtime Agent Communication Graph node and edge statuses.
- Durable interaction replay references on graph edges and graph-level partial
  replay evidence.
- Usage event ids.
- Export events.
- Redaction markers.

### Reliability Debugging

Use `/admin/app/operations` when work is queued, delayed, or failing
repeatedly. The reliability layer tracks admission controls, tenant
quotas, queue state, worker leases, retry budgets, circuit breakers,
compensation requests, dead letters, operational snapshots, and artifact
throughput.

Common checks:

- If work is not admitted, check submitted and active work limits.
- If one tenant is starved, check tenant fairness and quota windows.
- If retries stop, check retry budget and max attempts.
- If calls are blocked, check circuit breaker state and cooldown.
- If artifacts are delayed, check tenant and global artifact concurrency.
- If a worker appears stuck, compare lease expiry and renewal settings.

### Model Provider Debugging

If provider setup fails:

- Confirm the provider is active.
- Confirm the tenant can see the provider.
- Confirm the model id is listed in the connection catalog.
- Confirm OpenAI providers have at least one safe credential reference.
- Confirm the first configured credential reference resolves through the
  configured secret provider.
- Confirm local provider base URL uses an allowed scheme, host, port, and CIDR.
- Confirm OpenAI custom base URLs use HTTPS.
- Confirm no URL userinfo or secret-like query parameters are present.
- Confirm timeout settings are within configured min and max values.
- Confirm failures show safe categories such as `secret_reference_invalid`
  without raw headers, prompt bodies, completion bodies, or credential values.

If token usage does not appear, check whether the call went through
`ModelGateway.record_gateway_result` and whether a tenant id was present. Usage
events without a tenant id are skipped by design.

### Workflow Debugging

If workflow validation fails:

- Check that all node keys are unique.
- Check that every edge references existing nodes.
- Check that the graph has the required start and terminal structure.
- Check input and output contracts.
- Check prompt and profile version references.
- Check that subworkflow references are visible to the tenant.
- Check that skill references use exact immutable versions.
- Remove `latest`, `main`, or `dev` from skill version references.
- Remove secret-like values from workflow definitions.
- Confirm approval gates use supported scopes.
- Confirm join policies use supported strategies.
- Confirm required test suites have current same-tenant passing repository
  evidence for the current draft revision.

If publish is blocked, open the publish gate page and review missing test,
validation, reference, skill, prompt, profile, or provider readiness evidence.
Manual `latest_result_status` values in older workflow documents may still be
visible, but they are not enough by themselves; rerun the required suite against
the current draft revision and validate again.

### Skill Tool Debugging

Use `/admin/app/skills` when Daily Briefing tools do not appear ready or a role
node reports a tool denial. Check:

- The requested tool name is one of the installed and supported tools.
- The tenant has the skill installation and exact version required by the
  workflow/profile.
- Tool policy allows the operation.
- Outbound policy allows the provider domain.
- Credential metadata exists and belongs to the same tenant.
- Execution mode is allowed for the environment.
- The request is read-only or explicitly allowed by policy.
- Summaries contain redaction markers rather than raw provider payloads.

### Briefing Preference Debugging

Use `/admin/app/channels` when a Daily Intelligence Briefing is missing personal
context. Check:

- The profile exists for the linked tenant/principal.
- Timezone is a valid IANA value.
- Workday and scheduled times use `HH:MM`.
- Calendar and email fields are safe references, not raw credentials.
- Admin summaries mask VIP senders and account references.
- The runtime resolver returns a revision id and content digest for future run
  input pinning.
- Cross-tenant reads fail closed and do not reveal whether another tenant's raw
  profile exists.

### Auth Debugging

Common auth failures:

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| API will not start in production | `AUTH_MODE=local_principal` | Set `AUTH_MODE=auth0` and configure Auth0 settings. |
| Auth0 user receives 401 | Missing or invalid bearer token | Confirm audience, issuer, signature, and token expiry. |
| Auth0 user receives 403 | No platform role grant | Add active role grant for platform or tenant scope. |
| Tenant admin sees empty pages | Tenant id mismatch | Confirm catalog, token claim, or role grant tenant id. |
| Local login has no entries | Empty local catalog | Set valid `LOCAL_PRINCIPAL_CATALOG_JSON`. |
| Cross-tenant access denied | Missing support override | Create or activate the required support override. |

### Channel Debugging

For Web API and Web UI run channels:

- Use idempotency keys for duplicate-prone actions.
- Check `/runs/{run_id}/status`.
- Check `/runs/{run_id}/timeline`.
- Remember that current channel run state is process-local.
- Restarting the API can clear process-local Web UI/API run state. Telegram
  alias records, link token audits, linked identities, update receipts, and
  delivery attempts are persisted after migrations run.

For Telegram:

- Confirm tenant Telegram config is enabled.
- Confirm `TELEGRAM_WEBHOOK_SECRET` matches the webhook path.
- Confirm provider readiness in `/admin/app/channels`.
- Confirm the alias is enabled, tenant scoped, and normalized as expected.
- Confirm protected aliases require an active linked identity.
- Confirm link token has not expired.
- Confirm the Telegram identity is linked to the right tenant principal.
- Confirm the user uses protected commands only after `/link`.
- Confirm duplicate webhook updates replay from the update receipt instead of
  creating a second run.
- Confirm final delivery attempts show safe destination fingerprints, retry
  status, and provider correlation references.
- Use local webhook validation only as a local diagnostic, not as proof that
  Telegram accepted a real public webhook.

## 6. Token Usage And Cost Analytics

Usage analytics live at `/admin/app/usage`; older usage browser links should
redirect into React or return safe non-Jinja responses.
The platform records normalized LLM usage when model calls pass through the
model gateway usage capture path.

Tracked fields include:

- Tenant.
- Principal.
- Provider.
- Model.
- Workflow.
- Workflow run.
- Run step.
- Agent.
- Sub-agent.
- Prompt version.
- Agent profile version.
- Execution mode.
- Input token count.
- Output token count.
- Cached token count.
- Reasoning token count.
- Billable units.
- Latency.
- Usage status.
- Pricing version.
- Estimated cost.
- Trace id.
- Idempotency key.

Platform admins can view and export all tenant usage. Tenant admins can view
and export their own tenant only. Exports are CSV files generated from safe
normalized columns and stored through the configured storage provider.

### Understanding Cost

Cost is estimated by applying the pricing version for the provider/model to the
captured token counts. The repository has default pricing behavior when no
explicit pricing version exists, with separate rates for input, output, cached,
and reasoning tokens. Treat costs as estimated unless the event status indicates
confirmed provider usage.

If a call does not include provider token usage, the platform can still record a
safe event with estimated or unavailable usage status. Use provider/model,
workflow, agent, and prompt filters to find the largest contributors.

### Ways To Save Tokens

Practical savings usually come from:

- Shorter system prompts.
- Smaller prompt templates.
- Removing repeated background context.
- Using prompt variables carefully.
- Routing simple steps to smaller or local models.
- Keeping expensive models only for steps that need them.
- Splitting long workflows so only necessary steps see large context.
- Using memory reads narrowly.
- Summarizing artifacts before sending them to a model.
- Avoiding unnecessary sub-agent fanout.
- Using cached prompts or stable prompt prefixes where the provider supports
  caching.
- Testing changes in the test bench before running large real-model workloads.

Use `/admin/app/usage` after each workflow change. Compare cost by workflow,
provider, model, agent, sub-agent, prompt version, and execution mode. If cost
jumps after a prompt or workflow edit, inspect that version's input contract and
prompt rendering path.

### Usage Troubleshooting

If usage events are missing:

1. Confirm the model call used the model gateway path.
2. Confirm a tenant id was present.
3. Confirm the provider returned usage metadata or the gateway had enough
   information to estimate.
4. Confirm the time filter includes the event.
5. Confirm the active admin principal has access to the tenant.
6. Check `/admin/app/operations` for gateway attempt records.

If estimated costs look wrong:

1. Check provider and model filters.
2. Check whether the event used default pricing.
3. Check input, output, cached, and reasoning token counts separately.
4. Check whether retries produced multiple physical attempts.
5. Check if a workflow or agent was accidentally routed to a more expensive
   model.

## 7. Integration

The platform integrates with users and systems through Web UI, Web API,
Telegram webhooks, callbacks, artifacts, and model/tool providers.

### Web UI

Users can start and inspect workflow runs through `/runs`, which opens the
React run workspace under `/admin/app/channels/runs`. Admins use `/admin/app`
and its domain workspaces. Older browser links are compatibility redirects or
safe non-Jinja responses. The browser UI is the best first integration for
operations teams because it exposes scope, validation messages, readiness
checks, audit links, and safe diagnostics.

### Web API

The Web API channel under `/runs` supports starting runs, reading status,
reading timeline events, reading results, handling approvals, canceling runs,
subscribing to notifications, registering callbacks, and granting artifact
URLs.

Use idempotency keys for start, approval, cancel, and callback-related actions.
External systems should store the returned `run_id` and the response trace id.

### Telegram

Telegram support has two parts:

- Runtime webhook: `/channels/telegram/webhook/{secret}`.
- Admin configuration console: `/admin/app/channels`; older Telegram browser
  links should redirect into React or return safe non-Jinja responses.

Supported runtime commands include:

- `/start`
- `/link <token>`
- `/run <workflow_id> [text]`
- `/status <run_id>`
- `/approve <run_id> <prompt_id>`
- `/reject <run_id> <prompt_id>`
- `/resume <run_id> <prompt_id>`
- `/cancel <run_id>`
- `/result <run_id>`
- `/artifacts <run_id>`
- `/subscribe <run_id>`
- `/watch`
- `/unwatch`

The recommended flow is to create a one-time link token from the platform, send
`/link TOKEN` through Telegram, then use protected commands. Link tokens expire
based on `TELEGRAM_LINK_TOKEN_TTL_SECONDS`.

Tenants can also configure natural-language aliases in `/admin/app/channels`. An
alias is a tenant-scoped exact match after trimming, case folding, and whitespace
normalization. For example, `Morning briefing` and `/briefing` can both point to
a published Daily Intelligence Briefing workflow version. Protected aliases
require an active linked Telegram identity before they start a run.

When a linked user sends an enabled alias, the webhook checks tenant Telegram
readiness, provider readiness, linked identity status, alias policy, and update
idempotency. Duplicate Telegram updates replay the stored safe response instead
of creating duplicate runs. When an alias-triggered run reaches a final state,
the Telegram delivery boundary formats either the final result or a concise
partial-failure note and sends it back to the originating chat. Delivery
attempts store safe destination fingerprints, provider correlation references,
retry metadata, trace ids, and redacted status only.

### Briefing Preferences

The Daily Intelligence Briefing preference resolver can be used by Telegram,
Web API, or future scheduler triggers. It resolves the latest profile by
tenant/principal, returns private runtime context plus safe metadata, and emits
audit evidence for resolved, missing, and denied outcomes. Missing profiles
should produce a typed setup-needed result rather than letting an orchestrator
guess location, timezone, accounts, or output style.

### Callbacks And Webhooks To Other Systems

External systems can register callbacks for workflow run events through the Web
API channel. Configure `CHANNEL_CALLBACK_SIGNING_SECRET_REF` so callback
payloads can be signed and verified by the receiving system. Keep callback URLs
tenant-scoped, record idempotency keys, and design receivers to handle duplicate
delivery safely.

The channel layer records notification subscriptions and delivery attempts in
the intended data model. In the current default channel service, some runtime
channel state is process-local, so production integrations should verify the
deployment uses persistent channel storage for callback and notification
durability.

### Artifacts

Artifacts are exposed through short-lived authenticated URLs rather than direct
storage paths. Configure filesystem storage for local development or S3 storage
for production. Set artifact URL TTLs low enough to reduce leakage risk but high
enough for users to download reports.

### Model And Tool Providers

Model providers are configured through the gateway. Skills and tools are
configured through the governed skill registry and model-skill configuration.
Outbound domains, credential requirements, and allowed tools should be
deny-by-default and granted only to the tenants and workflows that require them.
Model credentials resolve through safe secret references at probe and runtime
call time. Tool calls go through SkillExecutionGateway policy checks and return
contract-shaped safe outputs.

## 8. Environment Variables

All of the following variables can be added to `.env`. The application reads
`.env` through Pydantic Settings and ignores unknown extra values. Use quoted
JSON for dictionary-style settings such as `LOCAL_PRINCIPAL_CATALOG_JSON` and
`STATIC_SECRETS_JSON`.

### Core Application

#### `APP_ENV`

Controls the environment profile and must be one of `local`, `test`, `ci`, or
`production`. In production, the settings validator refuses
`AUTH_MODE=local_principal`, which prevents accidentally running a browser QA
identity mode in a real environment. Example: use `APP_ENV=local` on a laptop
and `APP_ENV=production` in a hosted deployment.

#### `APP_NAME`

Sets the human-readable application name used by operational metadata and
service identity. Most installations can keep the default
`multi-agent-platform`, but a hosted company instance might set
`APP_NAME=acme-agent-platform`. Use a stable value because logs and dashboards
may group records by app name.

#### `APP_VERSION`

Sets the application version reported by operational endpoints and metadata.
Local development can leave this at `0.1.0`, while release pipelines can stamp
it with a release number such as `2026.05.03.1`. Pair this with `COMMIT_SHA` and
`BUILD_TIME` when investigating which build produced a behavior.

#### `API_HOST`

Sets the host address the API should bind to when used by a launcher that reads
settings. For local development, `127.0.0.1` is safest because it is reachable
only from the same machine. For container or network deployments, use the host
binding required by your process manager, commonly `0.0.0.0`.

#### `API_PORT`

Sets the API port for launchers that read settings. The common local value is
`8000`, matching examples such as `http://127.0.0.1:8000/admin`. If another
service already uses the port, choose an unused port and update any browser,
callback, or Telegram webhook URLs.

#### `LOG_LEVEL`

Controls application logging verbosity. Use `INFO` for normal operation,
`DEBUG` for local investigation, and avoid very verbose logs in production
unless you are actively diagnosing an incident. Logs should still be treated as
sensitive operational data even though platform audit and operations views
redact secrets and private content.

### Authentication And Authorization

#### `AUTH_MODE`

Selects `auth0` or `local_principal`. Use `local_principal` only for local
development, demos, and browser QA; production startup rejects it. Use `auth0`
when real users authenticate through Auth0 bearer tokens.

#### `AUTH0_DOMAIN`

Sets the Auth0 domain used to build the JWKS URL. Example:
`AUTH0_DOMAIN=your-tenant.us.auth0.com` causes the platform to read keys from
`https://your-tenant.us.auth0.com/.well-known/jwks.json` by default. This value
is required when `AUTH_MODE=auth0`.

#### `AUTH0_ISSUER`

Sets the expected token issuer. It usually looks like
`https://your-tenant.us.auth0.com/` and must match the `iss` claim in issued
tokens exactly. A missing slash or wrong custom domain is a common cause of
otherwise valid tokens being rejected.

#### `AUTH0_AUDIENCE`

Sets the expected API audience for Auth0 access tokens. This should match the
Identifier configured for the Auth0 API, such as
`https://multi-agent-platform.example.com`. If users authenticate successfully
but API calls return 401, confirm the client requested this audience.

#### `AUTH0_ALGORITHMS`

Lists accepted JWT signing algorithms. The default is `RS256`, which is the
normal Auth0 production choice. Do not broaden this list unless your identity
team explicitly requires it and has reviewed the security impact.

#### `AUTH0_REQUIRED_ORG_CLAIM`

Controls whether Auth0 tokens must contain organization context. The default is
`true`, which is appropriate for tenant-aware deployments because it helps map
users to organization and tenant scope. Set it to `false` only for a controlled
environment where tenant scope is supplied another way.

#### `AUTH0_JWKS_PATH`

Sets the path appended to `AUTH0_DOMAIN` for public signing keys. The default is
`/.well-known/jwks.json`, which is Auth0's standard JWKS endpoint. Change it
only if an identity gateway or custom domain exposes JWKS at a different path.

#### `LOCAL_PRINCIPAL_HEADER`

Sets the request header used for local-principal API calls. The default is
`X-Local-Principal`, and custom values must start with `X-` or the settings
validator rejects startup. Example: `X-Local-Principal: tenant-admin-acme`
authenticates as the catalog entry with that key.

#### `LOCAL_PRINCIPAL_COOKIE_NAME`

Sets the browser cookie name used by `/auth/local-login`. The default is
`map_local_principal`, and it stores the selected local catalog key for browser
QA. Change it only if another local app conflicts with the cookie name.

#### `LOCAL_PRINCIPAL_CATALOG_JSON`

Defines the local users available in local-principal mode. Each entry includes a
catalog key, display name, optional tenant id, optional org id, role codes,
permission codes, and enabled flag. Example entries are `platform-admin` for
global setup and `tenant-admin-acme` for tenant-scoped administration.

### Database

#### `DATABASE_URL`

Sets the SQLAlchemy database URL used by the application. Local PostgreSQL
usually uses
`postgresql+psycopg://postgres:postgres@localhost:5432/multi_agent_platform`.
The default SQLite URL can help quick experiments, but PostgreSQL is the target
database for the platform features and migrations.

#### `DATABASE_ECHO`

Controls whether SQLAlchemy echoes SQL statements. Keep this `false` for normal
use because SQL logs can be noisy and may reveal operational details. Set it to
`true` briefly during local debugging when you need to see generated SQL.

### Secrets

#### `SECRET_PROVIDER`

Selects how secret references are resolved and must be `static`, `env`, or
`secret_manager`. Use `static` only for local demo values, `env` when secrets
are provided as environment variables, and `secret_manager` when your
deployment integrates a managed secret store. Production records should contain
secret references, not raw credentials.

#### `STATIC_SECRETS_JSON`

Provides a JSON dictionary of named secrets when `SECRET_PROVIDER=static`.
Example: `{"OPENAI_API_KEY":"sk-test"}` can support a local-only demo, but this
puts the value directly in environment configuration. Do not use static raw
secrets for production provider tokens, Telegram tokens, callback signing
secrets, or customer credentials.

#### `ENV_SECRET_PREFIX`

Sets the prefix used by the environment secret resolver. The default
`MAP_SECRET_` means a provider-resolved reference such as `OPENAI_API_KEY`
resolves from `MAP_SECRET_OPENAI_API_KEY`. The current resolver uses the exact
reference string it receives; it does not strip an `env:` label automatically.
This lets operators inject real secret values through deployment tooling as long
as references and environment variable names follow the same convention.

#### `SECRET_MANAGER_PREFIX`

Sets the prefix expected for secret-manager references. The default is
`secret-manager/`, which makes references such as
`secret-manager/prod/openai/api-key` recognizable as managed secrets. In
production, Telegram and callback signing secret references must start with
`env:` or `secret-manager/` when provided.

### Storage

#### `STORAGE_PROVIDER`

Selects `filesystem` or `s3` artifact storage. Use `filesystem` for local
development because it stores artifacts under a local directory. Use `s3` or an
S3-compatible service for production when artifacts must survive process
restarts and be shared across workers.

#### `FILESYSTEM_STORAGE_ROOT`

Sets the local directory used for filesystem artifact storage. The default is
`.data/artifacts`, and the settings helper creates the directory when needed.
For local QA, this path keeps generated reports and exports inside the project
workspace.

#### `S3_BUCKET`

Sets the bucket name used when `STORAGE_PROVIDER=s3`. Example:
`S3_BUCKET=acme-agent-platform-artifacts` stores exports and generated evidence
in a dedicated bucket. Configure bucket policies so only the platform runtime
and approved operators can access objects.

#### `S3_ENDPOINT_URL`

Sets an optional S3-compatible endpoint URL. Leave it empty for AWS S3, or set
it for MinIO and other compatible storage services. The compose file includes a
MinIO service under the storage profile, which is useful for local production
rehearsals.

#### `S3_REGION`

Sets the S3 region used by the storage client. The default is `us-east-1`, which
is acceptable for local MinIO and many examples. Match the real AWS bucket
region in production to avoid signing or redirect issues.

### Observability

#### `METRICS_ENABLED`

Enables or disables metrics instrumentation. Keep it `true` when running
operations and reliability dashboards because metrics help identify pressure,
latency, and throughput issues. Set it `false` only for constrained local tests
where metrics setup causes noise.

#### `TRACING_ENABLED`

Controls tracing support. The default is `false`, but production deployments may
turn it on when connected to a trace collector. Even without external tracing,
the platform still propagates and reports `x-trace-id` for support workflows.

### Worker And Runtime

#### `WORKER_POLL_INTERVAL_SECONDS`

Sets the polling interval for the general worker loop. The default `0.1` favors
responsive local tests. Increase it when you need to reduce database polling
pressure in low-volume environments.

#### `WORKER_LEASE_SECONDS`

Sets the general worker lease duration. The default `60` seconds is enough for
many short tasks while still allowing recovery if a worker stops. Longer tasks
may need a longer lease paired with reliable renewal behavior.

#### `RUNTIME_WORKER_POLL_INTERVAL_SECONDS`

Sets the polling interval for runtime orchestration workers. The default `0.1`
keeps tests and demos responsive. For production, tune it with queue volume,
database capacity, and acceptable run-start latency in mind.

#### `RUNTIME_WORKER_LEASE_SECONDS`

Sets the lease duration for runtime orchestration work. The default `120`
seconds gives longer-running workflow steps more room than the general worker
lease. If workers duplicate work or leave stale claims, compare this setting
with step duration and renewal behavior.

#### `RUNTIME_CHECKPOINT_RETENTION_DAYS`

Controls how long runtime checkpoints are retained. The default is `90` days,
which supports incident review and resume-after-failure validation for recent
runs. Reduce it only after confirming audit, compliance, and replay needs.

#### `RUNTIME_PAYLOAD_REF_RETENTION_DAYS`

Controls retention for payload references used by runtime execution. The
default is `90` days, aligned with checkpoint retention. If artifacts or payload
references expire too soon, replay and debugging may lose useful context.

#### `RUNTIME_CHECKPOINTER_DATABASE_URL`

Sets an optional separate database URL for the LangGraph checkpointer. Leave it
empty to use the main database path where supported by your deployment. Use a
separate database only when operations require independent scaling, retention,
or access boundaries for checkpoint data.

### Reliability And Scale

#### `RELIABILITY_MAX_SUBMITTED_WORK`

Limits how much submitted work can be admitted. The default `1000` protects the
system from unbounded queues during spikes. Lower it for small local
environments and raise it only after checking database and worker capacity.

#### `RELIABILITY_MAX_ACTIVE_WORK`

Limits active in-progress work. The default `250` helps prevent workers and
providers from being overwhelmed. If valid work is queued but not starting,
check this limit alongside tenant quotas and provider circuit breakers.

#### `RELIABILITY_RETRY_BUDGET_PER_WINDOW`

Sets the retry budget available in a reliability window. The default `500`
allows retry recovery without letting repeated failures dominate capacity. If
many transient failures occur, review root causes before simply raising the
budget.

#### `RELIABILITY_MAX_RETRY_ATTEMPTS`

Sets the maximum retry attempts for eligible failed work. The default `3` is a
reasonable balance between recovery and cost control. For expensive LLM steps,
raising this value can materially increase token usage and provider spend.

#### `RELIABILITY_LEASE_EXPIRY_SECONDS`

Sets when reliability leases are considered expired. The default `120` seconds
must be greater than `RELIABILITY_LEASE_RENEWAL_SECONDS`, or settings validation
fails. If work is reclaimed too aggressively, increase expiry after reviewing
worker heartbeat behavior.

#### `RELIABILITY_LEASE_RENEWAL_SECONDS`

Sets how often leases should be renewed before expiry. The default `30` seconds
gives a healthy margin under the default expiry. Keep this lower than expiry so
workers can prove they still own active work.

#### `RELIABILITY_BREAKER_FAILURE_THRESHOLD`

Sets how many failures trip a circuit breaker. The default `5` prevents repeated
calls to a failing provider or dependency. If a provider is flaky, inspect
gateway attempts and normalized errors before changing this threshold.

#### `RELIABILITY_BREAKER_COOLDOWN_SECONDS`

Sets how long a tripped breaker cools down before retrying. The default `60`
seconds gives dependencies time to recover. Longer cooldowns reduce repeated
failure cost but may delay recovery after a short outage.

#### `RELIABILITY_ARTIFACT_TENANT_CONCURRENCY`

Limits concurrent artifact work per tenant. The default `10` prevents one
tenant from consuming all artifact throughput. This value cannot exceed
`RELIABILITY_ARTIFACT_GLOBAL_CONCURRENCY`.

#### `RELIABILITY_ARTIFACT_GLOBAL_CONCURRENCY`

Limits total artifact concurrency across the platform. The default `100`
protects storage and export systems from overload. If exports are slow across
all tenants, review this limit, storage provider latency, and object-store
health.

#### `RELIABILITY_DB_POOL_WAIT_P95_MS_THRESHOLD`

Sets the p95 database pool wait threshold used by reliability inspection. The
default `250` milliseconds is a warning line for database pressure. If the
operations console shows high pool waits, add capacity or reduce polling and
concurrency before increasing workload.

#### `RELIABILITY_ADMIN_CONNECTION_RESERVE_FRACTION`

Reserves a fraction of database connection capacity for admin operations. The
default `0.2` keeps inspection and recovery pages usable during load. Lowering
it can make incidents harder to investigate because admin requests may compete
with runtime work.

### Model Provider Gateway

#### `MODEL_PROVIDER_LOCAL_ALLOWED_SCHEMES`

Lists URL schemes allowed for local OpenAI-compatible providers. Defaults are
`http` and `https`, which support local development and secured internal
gateways. Do not allow unusual schemes because provider URLs are operator
controlled and must not become a path to local file or metadata access.

#### `MODEL_PROVIDER_LOCAL_ALLOWED_HOSTS`

Lists hostnames allowed for local provider URLs. Defaults are `127.0.0.1` and
`localhost`, which are safe for laptop model servers. Add internal hostnames
only after reviewing network boundaries and tenant access expectations.

#### `MODEL_PROVIDER_LOCAL_ALLOWED_PORTS`

Lists ports allowed for local provider URLs. Defaults are `8000`, `8080`, and
`11434`, covering common OpenAI-compatible local servers and Ollama-style
setups. If your server listens elsewhere, add only that specific port.

#### `MODEL_PROVIDER_LOCAL_ALLOWED_CIDRS`

Lists allowed network ranges for local provider URLs. The default
`127.0.0.0/8` keeps local providers on loopback. Expanding this to private
networks should be treated as a production security decision.

#### `MODEL_PROVIDER_PROBE_TIMEOUT_SECONDS`

Sets the timeout for provider probe requests. The default `30.0` seconds is
long enough for slow local models while still bounded. If probes time out,
confirm the model server is healthy before raising this value.

#### `MODEL_PROVIDER_GATEWAY_MIN_TIMEOUT_SECONDS`

Sets the minimum timeout allowed for gateway invocation policies. The default
`0.1` seconds prevents invalid near-zero timeout settings. Very low timeouts can
cause false failures, especially for local models that need warmup time.

#### `MODEL_PROVIDER_GATEWAY_MAX_TIMEOUT_SECONDS`

Sets the maximum timeout allowed for gateway invocation policies. The default
`300.0` seconds caps long-running model calls. If a workflow needs longer than
this, consider splitting the step or using an asynchronous pattern rather than
allowing very long blocking model calls.

### Telegram And Channels

#### `TELEGRAM_WEBHOOK_SECRET`

Sets the secret path segment for Telegram webhook requests. If this is
`local-secret`, the webhook URL is
`/channels/telegram/webhook/local-secret`. Treat it as sensitive because anyone
who knows the URL can attempt to submit webhook-shaped requests.

#### `TELEGRAM_PROVIDER_TOKEN_REF`

Stores the secret reference for the Telegram bot token. In production, this must
start with `env:` or `secret-manager/` when provided. Example:
`TELEGRAM_PROVIDER_TOKEN_REF=env:TELEGRAM_BOT_TOKEN` is treated as a safe
production label by Telegram readiness checks; if your deployment resolves that
token inside the platform for webhook registration or final-result delivery,
make sure the resolver maps the label to the real secret value. Runtime and
diagnostic records should store only the safe reference, fingerprints, provider
correlation ids, and status categories.

#### `TELEGRAM_LINK_TOKEN_TTL_SECONDS`

Controls how long one-time Telegram link tokens remain valid. The default and
maximum are `600` seconds, or 10 minutes. Short-lived tokens reduce the risk of
someone linking the wrong Telegram account after a token is shared.

#### `CHANNEL_CALLBACK_SIGNING_SECRET_REF`

Stores the secret reference used to sign callback payloads to external systems.
In production, this must use `env:` or `secret-manager/` when provided. Example:
use `env:CALLBACK_SIGNING_KEY` as the safe label and configure the receiving
system to verify the signature before trusting a callback. If callback signing
is resolved through the built-in environment provider, ensure your deployment
maps that label to the actual environment secret.

#### `CHANNEL_ARTIFACT_URL_TTL_SECONDS`

Sets the default lifetime for generated artifact URLs. The default is `900`
seconds, or 15 minutes, which is usually enough for a user to download a report.
This value cannot exceed `CHANNEL_ARTIFACT_URL_MAX_TTL_SECONDS`.

#### `CHANNEL_ARTIFACT_URL_MAX_TTL_SECONDS`

Sets the maximum allowed artifact URL lifetime. The default and maximum
configured by validation constraints is `3600` seconds, or one hour. Keep this
bounded so exported artifacts and run outputs are not exposed longer than
necessary.

#### `CHANNEL_SSE_HEARTBEAT_SECONDS`

Sets the heartbeat interval for server-sent event streams. The default `15`
seconds keeps browser and proxy connections alive during quiet periods. If
proxies close idle connections, lower this value within the allowed range.

#### `CHANNEL_RATE_LIMIT_PER_MINUTE`

Sets the per-minute channel rate limit. The default `120` protects channel APIs
from accidental loops while allowing normal use. If Telegram or webhook
integrations generate bursts, tune this alongside idempotency and retry
behavior.

### React Admin

#### `REACT_ADMIN_ENABLED`

Enables the React admin entry at `/admin/app`. It defaults to `true`. Set it to
`false` only for explicit asset-host troubleshooting. The supported browser
interface is React; old links are handled by redirects or safe compatibility
responses and do not restore server-rendered Jinja pages.

#### `REACT_ADMIN_ASSET_BASE_PATH`

Controls where FastAPI serves built React assets. The default is
`/admin/static/react`, which points to files produced by `npm run build` under
`frontend/admin`.

#### `REACT_ADMIN_MANIFEST_PATH`

Optionally points to a specific Vite manifest file. Leave it unset for normal
local development so the application uses the bundled static React directory.

#### `REACT_ADMIN_DOMAIN_ROUTES_JSON`

Optional JSON map for domain route enablement experiments. Use it only with the
internal route-safety evidence, because route ownership must remain
backend-authorized and tenant-safe.

### Build Metadata

#### `COMMIT_SHA`

Records the source commit for the running build. The default `dev` is fine
locally, but CI/CD should stamp the real commit SHA. This is one of the first
values to check when comparing behavior across environments.

#### `BUILD_TIME`

Records when the build artifact was created. The default
`1970-01-01T00:00:00+00:00` is a placeholder for development. Set an ISO 8601
timestamp in release pipelines so operations can confirm whether a deployment
contains the expected build.

## Appendix

### Appendix A: Architecture

```mermaid
flowchart TD
    Users["Users and Administrators"] --> Browser["Browser UI"]
    External["External Systems"] --> WebAPI["Web API Channel"]
    Telegram["Telegram"] --> TelegramWebhook["Telegram Webhook"]

    Browser --> FastAPI["FastAPI Application"]
    WebAPI --> FastAPI
    TelegramWebhook --> FastAPI

    FastAPI --> Auth["Auth Service\nAuth0 or Local Principal"]
    FastAPI --> Admin["Admin Console Shell"]
    FastAPI --> WorkflowRegistry["Workflow Registry\nDrafts, Revisions, Published Bundles"]
    FastAPI --> PromptProfiles["Prompt Library\nAgent Runtime Profiles"]
    FastAPI --> ModelConfig["Model and Skill Routing"]
    FastAPI --> SkillRegistry["Skill Registry\nPackages and Installations"]
    FastAPI --> SkillExecution["Skill Execution Gateway\nRead-Only Connectors"]
    FastAPI --> RuntimeAPI["Runtime and Channel Run APIs"]
    FastAPI --> TestBench["Agent Workflow Test Bench"]
    FastAPI --> Usage["Usage and Cost Analytics"]
    FastAPI --> Ops["Operations, Audit, Reliability"]
    FastAPI --> Memory["Immutable Memory"]
    FastAPI --> BriefingPrefs["Briefing Preferences\nProfiles and Revisions"]

    RuntimeAPI --> Worker["Worker Process"]
    Worker --> GraphExecutor["Published Bundle\nGraph Executor"]
    GraphExecutor --> LangGraph["LangGraph Runtime\nCheckpoints"]
    GraphExecutor --> SkillExecution
    Worker --> ModelGateway["Model Gateway"]
    TestBench --> ModelGateway
    ModelGateway --> SecretResolver["Provider Secret Resolver"]
    ModelGateway --> OpenAI["OpenAI Provider"]
    ModelGateway --> LocalModel["Local OpenAI-Compatible Provider"]
    SecretResolver --> Secrets["Secret Provider\nstatic, env, or manager"]

    FastAPI --> DB["PostgreSQL"]
    Worker --> DB
    LangGraph --> DB
    Usage --> DB
    Ops --> DB
    Memory --> DB
    BriefingPrefs --> DB

    FastAPI --> Storage["Artifact Storage\nFilesystem or S3"]
    Worker --> Storage

    Auth --> DB
    WorkflowRegistry --> DB
    PromptProfiles --> DB
    ModelConfig --> DB
    TestBench --> DB
    Usage --> DB
    Ops --> DB
```

Component responsibilities:

- FastAPI hosts browser pages, JSON APIs, channel endpoints, and health checks.
- Auth service normalizes Auth0 JWTs or local-principal selections into platform
  principals.
- Admin console shell provides scoped navigation, saved filters, common error
  states, and authorization-aware links.
- Workflow registry stores drafts, revisions, validation results, published
  bundles, sharing grants, and safe communication graph projections.
- Design Review stores council sessions, immutable revisions, review rounds,
  verdicts, quorum decisions, manual decisions, template evidence, and
  development handoff references.
- Runtime and workers coordinate workflow execution, leases, approvals,
  graph scheduling, parallel sub-agent waves, joins, handoffs, side effects,
  checkpoints, run timelines, runtime communication graphs, and durable
  interaction replay evidence.
- Model gateway centralizes provider invocation, normalized errors, latency,
  retry/breaker metadata, usage capture, and call-time credential resolution.
- Prompt and profile management governs immutable prompt versions and agent or
  sub-agent runtime profiles.
- Skill registry governs tool availability, package publication, tenant
  installation, credentials, smoke tests, and binding eligibility.
- Skill execution gateway runs approved read-only connectors through policy,
  credential metadata, outbound checks, and redacted summaries.
- Test bench provides safe evidence before prompts, agents, sub-agents, or
  workflows are published or used, and workflow publish gates query that
  repository-backed evidence directly.
- Briefing preferences store tenant/principal Daily Briefing context with
  immutable revisions and safe runtime resolution.
- Operations, audit, usage, and reliability surfaces support troubleshooting,
  compliance, and cost control.

### Appendix B: AI Sequence Diagrams

#### Web Message To Workflow Result

```mermaid
sequenceDiagram
    participant User
    participant Web as Web UI or Web API
    participant Auth as Auth Service
    participant Runtime as Runtime Service
    participant Worker
    participant Graph as Graph Executor
    participant Registry as Workflow Registry
    participant Gateway as Model Gateway
    participant Secrets as Provider Secret Resolver
    participant LLM as OpenAI or Local Model
    participant Usage as Usage Analytics
    participant Audit as Audit and Timeline

    User->>Web: Start workflow run
    Web->>Auth: Authenticate principal and tenant scope
    Auth-->>Web: Principal, roles, tenant context
    Web->>Runtime: Create run with idempotency key
    Runtime->>Registry: Load published workflow bundle
    Registry-->>Runtime: Immutable bundle and references
    Runtime->>Audit: Record run accepted event
    Runtime-->>User: Return run id and trace id
    Worker->>Runtime: Claim eligible run or step
    Worker->>Graph: Load pinned bundle graph
    Graph->>Registry: Resolve prompt, profile, model, skill, and test pins
    Graph->>Graph: Schedule ready nodes and joins
    Graph->>Gateway: Invoke selected provider/model for a role node
    Gateway->>Secrets: Resolve first safe credential reference
    Secrets-->>Gateway: Call-time credential or safe failure
    Gateway->>LLM: Chat completion request
    LLM-->>Gateway: Completion and usage metadata
    Gateway->>Usage: Record token and cost event
    Gateway-->>Graph: Normalized model result
    Graph->>Runtime: Store step result, checkpoint, handoff, timeline event
    Runtime->>Audit: Record status, side-effect, approval, and trace evidence
    User->>Web: Poll status, timeline, or result
    Web->>Runtime: Read run state
    Runtime-->>Web: Redacted status and result
    Web-->>User: Show result and audit-safe details
```

#### Telegram Message To Workflow Result

```mermaid
sequenceDiagram
    participant Person as Telegram User
    participant Telegram
    participant Webhook as Platform Telegram Webhook
    participant Channel as Channel Service
    participant Auth as Linked Identity
    participant Prefs as Briefing Preferences
    participant Runtime as Runtime Service
    participant Worker
    participant Gateway as Model Gateway
    participant Delivery as Bot API Delivery
    participant Admin as Telegram Admin Console

    Person->>Telegram: /link one-time-token
    Telegram->>Webhook: Webhook update
    Webhook->>Channel: Validate webhook secret and token
    Channel->>Auth: Link Telegram identity to platform principal
    Channel-->>Person: Link confirmed
    Admin->>Channel: Save Morning briefing alias to published workflow version
    Person->>Telegram: Morning briefing
    Telegram->>Webhook: Webhook update
    Webhook->>Channel: Normalize text and replay idempotency receipt if duplicate
    Channel->>Auth: Resolve linked identity and tenant
    Channel->>Prefs: Resolve latest tenant/principal preference revision
    Prefs-->>Channel: Runtime context or safe missing-profile result
    Channel->>Runtime: Start alias run with Telegram and preference metadata
    Runtime-->>Channel: Run id
    Channel-->>Person: Run accepted with run id
    Worker->>Runtime: Claim run
    Worker->>Gateway: Invoke configured model
    Gateway-->>Worker: Result
    Worker->>Runtime: Complete run
    Runtime-->>Channel: Final result or partial-failure summary
    Channel->>Delivery: Send safe final text to originating chat
    Delivery-->>Telegram: sendMessage through Bot API boundary
    Channel->>Admin: Persist delivery attempt, fingerprints, diagnostics
    Admin->>Channel: Review aliases, readiness, identities, receipts, delivery attempts
```

#### Human Approval Gate

```mermaid
sequenceDiagram
    participant Worker
    participant Runtime
    participant UserChannel as Web UI, API, or Telegram
    participant Approver
    participant Audit

    Worker->>Runtime: Step reaches approval gate
    Runtime->>Audit: Record waiting-for-input event
    Runtime-->>UserChannel: Expose approval prompt and run status
    UserChannel-->>Approver: Notify authorized approver
    Approver->>UserChannel: Approve, reject, or resume
    UserChannel->>Runtime: Submit decision with principal context
    Runtime->>Audit: Record decision and trace id
    Runtime-->>Worker: Resume or stop workflow branch
```

### Appendix C: Database ERD Diagrams

The diagrams below group the data model by function. They intentionally show the
operator-facing relationships rather than every column in every table.

#### Tenancy, Auth, And Admin Access

```mermaid
erDiagram
    TENANTS ||--o{ PRINCIPAL_IDENTITIES : scopes
    TENANTS ||--o{ ROLE_GRANTS : grants
    TENANTS ||--o{ SUPPORT_OVERRIDES : permits
    PRINCIPAL_IDENTITIES ||--o{ ROLE_GRANTS : receives
    PRINCIPAL_IDENTITIES ||--o{ SUPPORT_OVERRIDES : requests
    PRINCIPAL_IDENTITIES ||--o{ ADMIN_SAVED_FILTERS : owns
    TENANTS ||--o{ ADMIN_SAVED_FILTERS : scopes

    TENANTS {
        uuid tenant_id PK
        string slug
        string display_name
        string status
        timestamp created_at
        timestamp updated_at
    }
    PRINCIPAL_IDENTITIES {
        uuid principal_identity_id PK
        string auth_provider
        string external_subject
        string email
        uuid tenant_id FK
        timestamp created_at
        timestamp updated_at
    }
    ROLE_GRANTS {
        uuid role_grant_id PK
        uuid principal_identity_id FK
        string scope_type
        uuid tenant_id FK
        string role_code
        string status
        timestamp effective_at
    }
    SUPPORT_OVERRIDES {
        uuid support_override_id PK
        uuid principal_identity_id FK
        uuid tenant_id FK
        string reason
        string status
        timestamp expires_at
    }
    ADMIN_SAVED_FILTERS {
        uuid saved_filter_id PK
        uuid principal_identity_id FK
        uuid tenant_id FK
        string admin_area
        string filter_key
        json criteria
    }
```

#### Workflow, Runtime, And Memory

```mermaid
erDiagram
    TENANTS ||--o{ WORKFLOW_LINEAGES : owns
    WORKFLOW_LINEAGES ||--o{ WORKFLOW_DRAFTS : has
    WORKFLOW_DRAFTS ||--o{ WORKFLOW_DRAFT_REVISIONS : versions
    WORKFLOW_DRAFTS ||--o{ WORKFLOW_VALIDATION_RESULTS : validates
    WORKFLOW_LINEAGES ||--o{ WORKFLOW_VERSION_BUNDLES : publishes
    WORKFLOW_VERSION_BUNDLES ||--o{ WORKFLOW_SHARING_GRANTS : grants
    WORKFLOW_VERSION_BUNDLES ||--o{ RUNTIME_WORKFLOW_RUNS : pins
    WORKFLOW_VERSION_BUNDLES ||--o{ DESIGN_REVIEW_SESSIONS : selected_for
    RUNTIME_WORKFLOW_RUNS ||--o{ RUNTIME_RUN_STEPS : contains
    RUNTIME_WORKFLOW_RUNS ||--o{ RUNTIME_TIMELINE_EVENTS : records
    RUNTIME_WORKFLOW_RUNS ||--o{ RUNTIME_INTERACTION_EVIDENCE : replays
    RUNTIME_RUN_STEPS ||--o{ WORKER_LEASES : claimed_by
    RUNTIME_RUN_STEPS ||--o{ SIDE_EFFECT_INTENTS : requests
    RUNTIME_WORKFLOW_RUNS ||--o{ APPROVALS : waits_for
    RUNTIME_WORKFLOW_RUNS ||--o{ HANDOFF_ENVELOPES : hands_off
    TENANTS ||--o{ DESIGN_REVIEW_SESSIONS : owns
    DESIGN_REVIEW_SESSIONS ||--o{ DESIGN_REVISIONS : versions
    DESIGN_REVIEW_SESSIONS ||--o{ DESIGN_REVIEW_ROUNDS : reviews
    DESIGN_REVIEW_ROUNDS ||--o{ DESIGN_REVIEWER_ASSIGNMENTS : assigns
    DESIGN_REVIEW_ROUNDS ||--o{ DESIGN_REVIEWER_VERDICTS : records
    DESIGN_REVIEW_ROUNDS ||--o{ DESIGN_QUORUM_DECISIONS : decides
    DESIGN_REVIEW_SESSIONS ||--o{ DESIGN_MANUAL_DECISIONS : resolves
    DESIGN_REVIEW_SESSIONS ||--o{ DESIGN_DEVELOPMENT_HANDOFFS : hands_off
    TENANTS ||--o{ MEMORY_SCOPES : owns
    MEMORY_SCOPES ||--o{ MEMORY_VERSIONS : versions
    MEMORY_SCOPES ||--|| MEMORY_HEADS : projects
    MEMORY_VERSIONS ||--o{ MEMORY_AUDIT_RECORDS : audited_by

    WORKFLOW_LINEAGES {
        uuid workflow_lineage_id PK
        uuid tenant_id FK
        string name
        string status
    }
    WORKFLOW_DRAFTS {
        uuid workflow_draft_id PK
        uuid workflow_lineage_id FK
        uuid tenant_id FK
        string status
        int revision
    }
    WORKFLOW_VERSION_BUNDLES {
        uuid workflow_version_bundle_id PK
        uuid workflow_lineage_id FK
        string version
        string bundle_digest
        string status
    }
    RUNTIME_WORKFLOW_RUNS {
        uuid workflow_run_id PK
        uuid tenant_id FK
        uuid workflow_version_bundle_id FK
        string status
        string idempotency_key
    }
    RUNTIME_RUN_STEPS {
        uuid run_step_id PK
        uuid workflow_run_id FK
        string step_key
        string status
    }
    RUNTIME_INTERACTION_EVIDENCE {
        uuid interaction_evidence_id PK
        uuid workflow_run_id FK
        string source_node_key
        string target_node_key
        string interaction_kind
        int sequence
        string status
        string payload_digest
    }
    DESIGN_REVIEW_SESSIONS {
        uuid design_review_session_id PK
        uuid tenant_id FK
        uuid workflow_version_bundle_id FK
        string status
        string quorum_policy_key
        int active_revision_number
    }
    DESIGN_REVISIONS {
        uuid design_revision_id PK
        uuid design_review_session_id FK
        int revision_number
        string payload_digest
    }
    DESIGN_REVIEW_ROUNDS {
        uuid design_review_round_id PK
        uuid design_review_session_id FK
        uuid workflow_run_id FK
        int round_number
        string status
    }
    DESIGN_REVIEWER_VERDICTS {
        uuid design_reviewer_verdict_id PK
        uuid design_review_round_id FK
        string reviewer_key
        string verdict
        int blocking_issue_count
    }
    DESIGN_QUORUM_DECISIONS {
        uuid design_quorum_decision_id PK
        uuid design_review_round_id FK
        string status
        string next_action
    }
    MEMORY_SCOPES {
        uuid memory_scope_id PK
        uuid tenant_id FK
        string scope_key
        string status
    }
    MEMORY_VERSIONS {
        uuid memory_version_id PK
        uuid memory_scope_id FK
        int version_number
        string content_digest
        timestamp created_at
    }
```

#### Models, Prompts, Profiles, And Usage

```mermaid
erDiagram
    TENANTS ||--o{ MODEL_PROVIDER_CONNECTIONS : visibility
    MODEL_PROVIDER_CONNECTIONS ||--o{ MODEL_DEFINITIONS : exposes
    MODEL_PROVIDER_CONNECTIONS ||--o{ PROVIDER_HEALTH_SNAPSHOTS : checked_by
    MODEL_PROVIDER_CONNECTIONS ||--o{ GATEWAY_INVOCATION_RECORDS : invokes
    PROMPT_LINEAGES ||--o{ PROMPT_DRAFTS : drafts
    PROMPT_LINEAGES ||--o{ PROMPT_VERSIONS : publishes
    PROMPT_VERSIONS ||--o{ PROMPT_TENANT_GRANTS : grants
    AGENT_RUNTIME_PROFILES ||--o{ AGENT_PROFILE_VERSIONS : versions
    AGENT_PROFILE_VERSIONS ||--o{ AGENT_PROFILE_TENANT_GRANTS : grants
    MODEL_DEFINITIONS ||--o{ USAGE_EVENTS : priced_as
    PROMPT_VERSIONS ||--o{ USAGE_EVENTS : used_by
    AGENT_PROFILE_VERSIONS ||--o{ USAGE_EVENTS : used_by
    TENANTS ||--o{ USAGE_EVENTS : owns
    USAGE_EVENTS ||--o{ USAGE_EXPORTS : exported_in

    MODEL_PROVIDER_CONNECTIONS {
        uuid provider_connection_id PK
        string provider_type
        string display_name
        string base_url
        json credential_secret_reference_ids
        string visibility
        string health_state
        bool active
    }
    MODEL_DEFINITIONS {
        uuid model_definition_id PK
        uuid provider_connection_id FK
        string model_id
        string status
    }
    PROMPT_LINEAGES {
        uuid prompt_lineage_id PK
        string prompt_key
        string status
    }
    PROMPT_VERSIONS {
        uuid prompt_version_id PK
        uuid prompt_lineage_id FK
        string version_label
        string template_digest
        string status
    }
    AGENT_RUNTIME_PROFILES {
        uuid agent_runtime_profile_id PK
        string agent_key
        string agent_kind
        string status
    }
    AGENT_PROFILE_VERSIONS {
        uuid agent_profile_version_id PK
        uuid agent_runtime_profile_id FK
        string version_label
        string status
    }
    USAGE_EVENTS {
        uuid usage_event_id PK
        uuid tenant_id FK
        string provider
        string model
        int input_tokens
        int output_tokens
        decimal estimated_cost
    }
```

#### Skills, Test Bench, And Channels

```mermaid
erDiagram
    SKILL_PACKAGES ||--o{ SKILL_PACKAGE_VERSIONS : publishes
    SKILL_PACKAGE_VERSIONS ||--o{ SKILL_TENANT_GRANTS : grants
    SKILL_PACKAGE_VERSIONS ||--o{ SKILL_INSTALLATIONS : installed_as
    TENANTS ||--o{ SKILL_INSTALLATIONS : owns
    SKILL_INSTALLATIONS ||--o{ SKILL_CREDENTIAL_READINESS : checks
    SKILL_INSTALLATIONS ||--o{ SKILL_SMOKE_TEST_EVIDENCE : proves
    SKILL_INSTALLATIONS ||--o{ SKILL_BINDING_ELIGIBILITY : previews
    TENANTS ||--o{ AGENT_TEST_SUITES : owns
    AGENT_TEST_SUITES ||--o{ AGENT_TEST_CASES : contains
    AGENT_TEST_SUITES ||--o{ AGENT_TEST_RUNS : executes
    AGENT_TEST_RUNS ||--o{ AGENT_TEST_RUN_STEPS : records
    TENANTS ||--o{ TELEGRAM_TENANT_CONFIGS : configures
    TELEGRAM_TENANT_CONFIGS ||--o{ TELEGRAM_COMMAND_ALIASES : routes
    TELEGRAM_TENANT_CONFIGS ||--o{ TELEGRAM_LINK_TOKEN_AUDITS : issues
    TELEGRAM_TENANT_CONFIGS ||--o{ TELEGRAM_IDENTITY_LINKS : links
    TELEGRAM_TENANT_CONFIGS ||--o{ TELEGRAM_UPDATE_RECEIPTS : deduplicates
    TELEGRAM_TENANT_CONFIGS ||--o{ TELEGRAM_DELIVERY_ATTEMPTS : sends
    TENANTS ||--o{ BRIEFING_PREFERENCE_PROFILES : owns
    BRIEFING_PREFERENCE_PROFILES ||--o{ BRIEFING_PREFERENCE_REVISIONS : versions
    BRIEFING_PREFERENCE_PROFILES ||--o{ BRIEFING_PREFERENCE_AUDIT_EVENTS : audited_by
    TENANTS ||--o{ CHANNEL_SESSIONS : owns
    CHANNEL_SESSIONS ||--o{ NOTIFICATION_SUBSCRIPTIONS : subscribes

    SKILL_PACKAGES {
        uuid skill_package_id PK
        string slug
        string description
        string status
    }
    SKILL_PACKAGE_VERSIONS {
        uuid skill_package_version_id PK
        uuid skill_package_id FK
        string semantic_version
        string manifest_digest
        string status
    }
    SKILL_INSTALLATIONS {
        uuid skill_installation_id PK
        uuid tenant_id FK
        uuid skill_package_version_id FK
        string status
        string readiness_state
    }
    AGENT_TEST_SUITES {
        uuid suite_id PK
        uuid tenant_id FK
        string target_type
        string target_id
        string status
    }
    AGENT_TEST_RUNS {
        uuid run_id PK
        uuid suite_id FK
        string safe_mode
        string status
        decimal pass_rate
    }
    TELEGRAM_TENANT_CONFIGS {
        uuid telegram_config_id PK
        uuid tenant_id FK
        bool enabled
        string readiness_state
    }
    TELEGRAM_COMMAND_ALIASES {
        uuid alias_id PK
        uuid tenant_id FK
        string alias_text
        string normalized_alias_key
        uuid workflow_version_bundle_id
        bool protected
        bool enabled
    }
    TELEGRAM_IDENTITY_LINKS {
        uuid identity_id PK
        uuid tenant_id FK
        string telegram_user_hash
        string principal_ref
        string status
    }
    TELEGRAM_UPDATE_RECEIPTS {
        uuid receipt_id PK
        uuid tenant_id FK
        string update_id
        string response_fingerprint
        string status
    }
    TELEGRAM_DELIVERY_ATTEMPTS {
        uuid delivery_attempt_id PK
        uuid tenant_id FK
        uuid workflow_run_id FK
        string destination_fingerprint
        string delivery_status
        int attempt_number
    }
    BRIEFING_PREFERENCE_PROFILES {
        uuid profile_id PK
        uuid tenant_id FK
        string principal_ref
        uuid current_revision_id FK
        string readiness_state
    }
    BRIEFING_PREFERENCE_REVISIONS {
        uuid revision_id PK
        uuid profile_id FK
        int revision_sequence
        string content_digest
        timestamp created_at
    }
```

#### Audit, Reliability, And Operations

```mermaid
erDiagram
    TENANTS ||--o{ AUDIT_EVENTS : scopes
    AUDIT_EVENTS ||--o{ RUN_TIMELINE_EVENTS : references
    RUNTIME_WORKFLOW_RUNS ||--o{ RUNTIME_TRACE_RECORDS : traces
    RUNTIME_WORKFLOW_RUNS ||--o{ GATEWAY_ATTEMPT_SUMMARIES : calls
    TENANTS ||--o{ RELIABILITY_QUOTA_COUNTERS : limits
    TENANTS ||--o{ RELIABILITY_QUEUE_STATE : queues
    RELIABILITY_QUEUE_STATE ||--o{ RELIABILITY_RETRY_SCHEDULES : retries
    RELIABILITY_QUEUE_STATE ||--o{ RELIABILITY_DEAD_LETTERS : fails_to
    RELIABILITY_QUEUE_STATE ||--o{ RELIABILITY_COMPENSATION_REQUESTS : compensates
    RELIABILITY_CIRCUIT_BREAKERS ||--o{ GATEWAY_ATTEMPT_SUMMARIES : protects
    AUDIT_EVENTS ||--o{ OPERATIONS_LOG_EXPORTS : exported_by

    AUDIT_EVENTS {
        uuid audit_event_id PK
        uuid tenant_id FK
        string event_type
        string actor_ref
        string trace_id
        timestamp created_at
    }
    RUNTIME_TRACE_RECORDS {
        uuid trace_record_id PK
        uuid workflow_run_id FK
        string trace_id
        string component
        string status
    }
    GATEWAY_ATTEMPT_SUMMARIES {
        uuid gateway_attempt_id PK
        uuid workflow_run_id FK
        string provider
        string model
        string normalized_status
        int latency_ms
    }
    RELIABILITY_QUEUE_STATE {
        uuid queue_state_id PK
        uuid tenant_id FK
        string work_type
        string status
        timestamp next_attempt_at
    }
    RELIABILITY_CIRCUIT_BREAKERS {
        uuid circuit_breaker_id PK
        string dependency
        string state
        timestamp cooldown_until
    }
    OPERATIONS_LOG_EXPORTS {
        uuid export_id PK
        string requested_by
        string filter_digest
        string artifact_ref
        timestamp created_at
    }
```

### Appendix D: Real-World Example - Telegram Setup

This example sets up Telegram for the Acme tenant in a local or staging
environment. Replace sample values with your real domain, tenant id, and secret
references.

#### Goal

An Acme user should be able to:

1. Open Telegram.
2. Link their Telegram account to their platform identity.
3. Start a published workflow from a tenant alias such as `Morning briefing`.
4. Check status.
5. Approve a waiting workflow step.
6. Receive the final result in the same Telegram chat.

#### Step 1: Create A Telegram Bot

Use Telegram BotFather to create a bot. BotFather returns a bot token. Store
that token in your secret system instead of putting it directly in a workflow,
prompt, or provider record.

For local environment-secret testing:

```bash
SECRET_PROVIDER=env
ENV_SECRET_PREFIX=MAP_SECRET_
TELEGRAM_PROVIDER_TOKEN_REF=env:TELEGRAM_BOT_TOKEN
MAP_SECRET_TELEGRAM_BOT_TOKEN=<telegram-bot-token-from-botfather>
TELEGRAM_WEBHOOK_SECRET=acme-local-webhook-secret
```

The Telegram admin readiness check treats `env:TELEGRAM_BOT_TOKEN` as a safe
reference label. Current Telegram configuration code records and validates the
reference label; production webhook registration still needs a secure operator
or deployment job that can read the actual bot token from your secret store.

For production, use a managed secret reference such as:

```bash
SECRET_PROVIDER=secret_manager
TELEGRAM_PROVIDER_TOKEN_REF=secret-manager/prod/telegram/bot-token
TELEGRAM_WEBHOOK_SECRET=<long-random-secret-path-segment>
```

#### Step 2: Confirm The Tenant Exists

Confirm Acme exists in `tenants`:

```sql
SELECT tenant_id, slug, display_name, status
FROM tenants
WHERE slug = 'acme';
```

For this guide, Acme uses:

```text
11111111-1111-1111-1111-111111111111
```

#### Step 3: Start The Platform

Apply migrations and run the API:

```bash
docker compose up -d postgres
uv run alembic upgrade head
cd frontend/admin && npm install && npm run build && cd ../..
uv run uvicorn multi_agent_platform.api.main:app --reload
```

If you are executing workflows with a worker:

```bash
uv run python -m multi_agent_platform.workers.main
```

#### Step 4: Open Telegram Admin Console

Sign in as a platform admin:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/channels
```

Open:

```text
http://127.0.0.1:8000/admin/app/channels?tenant_id=11111111-1111-1111-1111-111111111111
```

Review provider readiness. The console should show whether the global provider
token reference and webhook secret are configured. Local webhook validation is a
diagnostic only; it does not prove Telegram has accepted a public webhook.

#### Step 5: Enable Tenant Telegram Configuration And Alias

In `/admin/app/channels`, enable Telegram for Acme. Configure command
availability according to your policy. Protected commands such as `/run`,
`/status`, `/result`, and approvals should require a linked identity. Protected
aliases should also require a linked identity.

If using the API, use the `/admin/telegram/api/config` endpoint with platform or
tenant admin credentials. Keep tenant id explicit so you do not accidentally
configure the wrong tenant.

Create an alias for the published briefing workflow:

- Alias text: `Morning briefing`.
- Optional command alias: `/briefing`.
- Workflow version: the published workflow version/bundle id to run.
- Protected: enabled.
- Enabled: enabled.

The admin page shows alias management. The automation API endpoint is
`/admin/telegram/api/aliases`. Alias matching is exact after trimming,
whitespace normalization, and case folding, so `morning   briefing` routes like
`Morning briefing`, but fuzzy intent matching is not part of this flow.

#### Step 6: Configure The Public Webhook

For a real Telegram bot, Telegram must reach your public HTTPS URL:

```text
https://your-domain.example.com/channels/telegram/webhook/<TELEGRAM_WEBHOOK_SECRET>
```

Register that URL with Telegram using the bot token. Do this from a secure
operator machine or deployment job. Do not paste the bot token into admin notes,
workflow descriptions, prompts, or tickets.

If you test locally, use a secure tunnel only for temporary QA. Remember that the
webhook secret is part of the URL and should be long, random, and replaced after
exposure.

#### Step 7: Create A Link Token

From `/admin/app/channels`, create a one-time link token for the Acme user. Give
the token only to the intended user. The default link token lifetime is 10
minutes.

The user sends this in Telegram:

```text
/link TOKEN_FROM_PLATFORM
```

After success, the platform stores a masked/safe identity summary and audit
record in PostgreSQL. The raw token is shown only when issued; refreshed admin
views should show only a fingerprint. The admin console should show the linked
identity without exposing raw private Telegram message contents.

#### Step 8: Save Briefing Preferences

For Daily Intelligence Briefing, open `/admin/app/channels` as the Acme user and
save a profile before testing the alias. At minimum, configure:

- Location and timezone.
- News topics and VIP sender hints.
- Workday hours and commute mode.
- Calendar and email account references.
- Output style.

The runtime resolver attaches the latest preference revision to future briefing
runs. Admin summaries should show masked values and counts rather than raw VIP
senders or full account references.

#### Step 9: Run A Telegram Alias

The user can now send either configured alias:

```text
Morning briefing
```

or:

```text
/briefing
```

The platform replies with a run id after it checks the webhook secret, update
idempotency, tenant Telegram readiness, alias status, linked identity, and
preference resolver context. The user can check:

```text
/status RUN_ID
```

If the workflow waits for approval:

```text
/approve RUN_ID PROMPT_ID
```

After completion:

```text
/result RUN_ID
/artifacts RUN_ID
```

For alias-triggered runs, the platform also attempts to deliver the final
briefing or a concise partial-failure note to the originating chat through the
Telegram Bot API boundary. Local QA uses a mocked Bot API client but still
persists safe delivery-attempt evidence.

#### Step 10: Troubleshoot Telegram

If `/link` fails:

- Confirm the token has not expired.
- Confirm the token was generated for the correct tenant and principal.
- Confirm the token has not already been consumed or revoked.
- Confirm the webhook secret in the URL matches `TELEGRAM_WEBHOOK_SECRET`.

If an alias such as `Morning briefing` fails:

- Confirm the user linked first.
- Confirm the tenant Telegram config is enabled.
- Confirm the alias is enabled, protected as intended, and points to a valid
  published workflow version visible to the tenant.
- Confirm the user's platform identity has permission to start that workflow.
- Confirm the briefing preference profile exists if the workflow requires it.
- Confirm current channel rate limits are not blocking requests.
- Confirm duplicate Telegram update ids replay the prior response rather than
  creating new runs.

If the bot does not receive messages:

- Confirm Telegram has the correct public HTTPS webhook URL.
- Confirm firewalls or tunnels allow Telegram to reach the API.
- Confirm the API server is running and can reach its database.
- Confirm the webhook path includes the current secret.
- Check `/admin/app/channels` diagnostics and `/admin/app/operations` logs with
  the trace id if available.

If results or artifacts are missing:

- Confirm the run completed.
- Confirm a Telegram delivery attempt exists for alias-triggered final output.
- Confirm artifact storage is configured and writable.
- Confirm artifact URL TTL has not expired.
- Confirm the requesting Telegram identity belongs to the same tenant and is
  authorized for the run.

#### Step 11: Operate Safely

Rotate the Telegram bot token if it is exposed. Rotate the webhook secret if a
public URL leaks. Review linked identities regularly and revoke stale links from
the Telegram admin console. Disable aliases that should no longer start
workflows, and review delivery attempts for repeated retrying or failed states.

For production, pair Telegram setup with Auth0 identities, tenant role grants,
callback signing secrets, artifact TTL limits, briefing preference governance,
audit exports, and operations console monitoring. Telegram should be treated as
another channel into the same tenant-scoped workflow system, not as a separate
trust boundary.
