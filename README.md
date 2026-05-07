# Multi-Agent AI Platform

This repository now includes the platform foundation, the auth and access
layer, the full Spec `003` workflow-studio registry flow, the Spec `004`
durable orchestration runtime, the Spec `005` immutable versioned memory
subsystem, and Spec `006` user interaction channels. Admins and users can
author workflow drafts, publish immutable version bundles, start pinned durable
runs, inspect runtime timeline evidence, create append-only memory versions,
and interact with workflow runs through Web UI, Telegram, and Web API channels.

## Current Scope

- operational API: `/health/live`, `/health/ready`, `/version`, `/dependencies`
- auth and admin-access APIs: `/auth/me`, `/auth/tenant-context/{tenant_id}`,
  `/admin/role-grants`, `/admin/support-overrides`
- workflow-registry APIs under `/admin/workflows`
- embedded workflow registry UI under `/admin/workflows/ui`
- durable runtime APIs under `/runtime/runs`
- immutable memory APIs under `/memory`
- user interaction channel APIs under `/runs`
- Web UI run list/detail pages under `/runs`
- Telegram webhook commands under `/channels/telegram/webhook/{secret}`
- Telegram tenant command aliases under `/admin/telegram` for natural-language
  triggers such as `Morning briefing`
- browser-friendly local QA login under `/auth/local-login`
- durable lineage, draft, revision, validation-result, published-version, and
  sharing-grant persistence
- per-run execution bundle pinning, worker leases, timeline events, approval
  gates, handoff envelopes, side-effect intents, lineage, and retention models
- append-only memory scopes, versions, current heads, replay, diff, audit, and
  runtime source links
- filesystem or provider-backed artifact storage for compiled workflow bundles
- production audit debugging for admin run search, timelines, replay, lineage,
  version bundles, notification state, secret-access metadata, and redacted
  exports
- reliability scale hardening for admission controls, tenant quotas, fair
  scheduling, retries, circuit breakers, compensation, dead letters, artifact
  throughput, and operator inspection APIs under `/admin/reliability`
- shared admin console shell under `/admin` with platform and tenant scope
  display, authorization-aware navigation, common states, safe messages,
  breadcrumbs, saved filters, and route-preserving links to workflow,
  model-skill, run inspection, and reliability pages
- model provider gateway management under `/admin/app/governance/providers` for
  platform-admin OpenAI/local OpenAI-compatible provider configuration, safe
  probes, health review, catalog sync evidence, and gateway-governed runtime
  invocation metadata
- prompt library and agent runtime profile management under
  `/admin/app/governance/prompts` and `/admin/app/governance/profiles` with
  immutable prompt/profile versions, safe fixture previews, tenant grants,
  workflow validation hooks, model-skill prompt reference digests, runtime
  provenance pins, audit-safe summaries, and reviewer QA evidence
- guided admin workflow builder under `/admin/workflows/ui` with create,
  editor, graph preview, reference lookup, validation, revision history,
  publish gate, and published bundle pin/provenance views
- governed skill registry under `/admin/app/skills/packages` and
  `/admin/app/skills/installations` for declarative package
  publication, tenant installation, credential readiness, smoke-test evidence,
  binding eligibility, upgrades, quarantine, and safe audit summaries
- governed skill tool execution diagnostics under
  `/admin/app/skills/diagnostics` for Daily Briefing calendar, Gmail, news,
  weather, and commute mock adapters with policy decisions and redacted
  summaries. Legacy skill registry and diagnostics browser URLs redirect to
  the React skill workspace.
- user and tenant membership administration under `/admin/memberships` and
  `/admin/memberships/api` for platform-admin user management, tenant-admin
  self-service, idempotent invitations, Auth0 subject linking, role grants,
  principal suspension/reactivation, tenant membership status, access history,
  and redaction-safe audit evidence
- React agent and workflow test bench under `/admin/app/test-bench` plus
  JSON APIs under `/admin/agent-tests` for tenant-scoped suites,
  fixture-backed cases, safe mock or mocked-provider runs, redacted
  diagnostics, blocked side-effect evidence, and publish gate readiness
  checks. Legacy `/admin/agent-tests/ui...` browser URLs redirect safely to
  the React workspace.
- operations console under `/admin/operations` and `/admin/operations/api` for
  platform-admin and auditor review of health, dependency readiness, capacity,
  provider and channel status, reliability pressure, throughput, redacted
  operational logs, bounded filtering, and CSV export evidence
- Spec Kit Autopilot via `/speckit.autopilot` for file-backed Codex runs that
  execute preflight, specify, clarify-auto, plan, tasks, analyze-auto,
  implement, and API/browser validation from `specs/_autopilot/*`
- workflow graph execution in the runtime worker for published bundle graphs,
  including deterministic role/sub-agent nodes, parallel ready-wave fan-out,
  join policies, resume-safe persisted steps, tenant-compatible bundle loading,
  and redaction-safe graph evidence
- React admin foundation, modern shell, shared data/form patterns,
  operations workbench, workflow builder, governance workspace, skill
  lifecycle workspace, test bench workspace, membership administration, and
  usage analytics under
  `/admin/app`, backed by FastAPI bootstrap, config, manifest, authorized
  command search, generated page envelopes, reusable filter/table/form
  contracts, safe mutation feedback, workbench health/run/reliability
  summaries, workflow draft/reference/graph/validation/publish contracts,
  model/provider/prompt/profile/routing/provenance governance contracts,
  skill package publication/discovery/installation/credential/readiness/
  binding/diagnostic/audit contracts, test suite/case/run/gate contracts,
  membership invitation/principal/role/status/history/audit contracts, usage
  summary/trend/rollup/drilldown/export contracts, export and evidence artifact
  references, shared design tokens, common states, React routes, and safe
  compatibility redirects for older browser URLs

## Quickstart

1. Run `uv sync`.
2. Copy `.env.example` to `.env`.
3. Set `AUTH_MODE=local_principal`.
4. Run `docker compose up -d postgres`.
5. Run `uv run alembic upgrade head`.
6. Run `uv run uvicorn multi_agent_platform.api.main:app --reload`.
7. Run `uv run python -m multi_agent_platform.workers.main` in a second shell
   when validating runtime execution.
8. Open
   [http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/workflows/ui](http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/workflows/ui).
9. Open [http://127.0.0.1:8000/runs](http://127.0.0.1:8000/runs) to start
   and inspect runs through the Web UI channel.
10. Validate a guided workflow draft at
    `/admin/workflows/drafts/{workflow_draft_id}/editor`, then review
    `/admin/workflows/drafts/{workflow_draft_id}/publish-gate/ui`.
11. Review skill packages at `/admin/app/skills/packages` and tenant
    installations at `/admin/app/skills/installations`.
12. Review skill tool diagnostics at `/admin/app/skills/diagnostics`.
13. Review agent and workflow test suites at `/admin/app/test-bench`, then run
    safe mock or mocked-provider checks before publication.
14. Review React membership administration at `/admin/app/memberships` as
    `platform-admin` and as `tenant-admin-acme`; old membership browser links
    redirect to React.
15. Review React usage analytics at `/admin/app/usage` as `platform-admin` and
    as `tenant-admin-acme`; old usage browser links redirect to React.
16. Review platform operational status at `/admin/operations` as
    `platform-admin` or `auditor`.
17. Dry-run the Spec Kit Autopilot example with
    `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/example/validation.yml --dry-run`.
18. Validate workflow graph execution with
    `uv run pytest --no-cov tests/integration/runtime/test_workflow_graph_execution.py`.
19. Validate Telegram alias delivery with
    `uv run pytest --no-cov tests/contract/test_telegram_alias_delivery_contract.py tests/integration/api/test_telegram_webhook.py`.
20. Validate the repo with `./scripts/check.sh`.

### React Admin Foundation, Shell, Patterns, Workbench, Builder, Governance, Skills, Test Bench, Membership, And Usage

The React admin shell is available at
[http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app](http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app)
when `AUTH_MODE=local_principal` is enabled. Build assets before manual browser
review:

```bash
cd frontend/admin
npm install
npm run build
cd ../..
uv run uvicorn multi_agent_platform.api.main:app --reload
```

The shell uses backend-authorized bootstrap metadata from
`/admin/app/bootstrap.json` and safe command-search metadata from
`/admin/app/search.json`. React renders shared shell chrome, active scope,
breadcrumbs, page actions, saved-filter presentation, notifications, common
  states, and local design tokens from the backend contract. Browser admin
  pages are React-only; old domain links are preserved through backend-owned
  redirects or safe compatibility responses.

The reusable data/form pattern page is available at
[http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/patterns](http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/patterns).
It reads an authorized `AdminPageEnvelope` from `/admin/app/patterns.json` and
demonstrates backend-owned table records, allowed filters, sorting, field
validation, confirmation prompts, stale revision recovery, idempotency replay
feedback, safe toast metadata, and export snapshots that expose artifact
reference IDs instead of local paths or raw payloads. The page is intentionally
harmless and exists so later React admin routes can reuse the same generated
contracts instead of copying domain rules into the browser.

The React operations workbench is available at
[http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/operations](http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/operations).
It reads `/admin/app/operations.json` and renders backend-owned health,
dependency pressure, likely-cause, run debug, graph branch, gateway attempt,
tool call, channel delivery, reliability recovery, log, and export summaries.
Platform administrators and auditors see platform summaries; tenant
administrators see tenant-scoped summaries with platform-only provider and
pressure details hidden. Exports return `artifact-ref-qa029-*` references and
audit references instead of raw files or operational payloads.

The React workflow builder is available at
[http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/workflows](http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/workflows).
It reads `/admin/app/workflows/builder.json` and
`/admin/app/workflows/lookups.json`, then renders backend-owned draft
metadata, reference options, graph preview, validation findings, publish
readiness, required evidence, revisions, and redacted JSON preview summaries.
Save, validation, stale revision, and publish decisions post back to protected
workflow builder actions. Old workflow browser links redirect to
`/admin/app/workflows`.

The React governance workspace is available at
[http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/governance](http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/governance).
It reads `/admin/app/governance/bootstrap.json` plus provider, prompt, profile,
routing, history, and provenance contracts, then renders backend-owned provider
health, credential-reference diagnostics, explicit platform-admin probes, safe
prompt previews, runtime profile resolution, read-only routing decisions,
policy history, and run provenance. Provider mutations and credential-reference
changes are platform-admin only; tenant administrators receive authorized
readiness and provenance summaries without raw credentials, provider payloads,
prompts, completions, or cross-tenant labels.

The React skill lifecycle workspace is available at
[http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/skills](http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/skills).
It reads `/admin/app/skills/bootstrap.json` plus discovery, installation,
diagnostic, eligibility, and audit contracts, then renders backend-owned
package publication, manifest upload precedence, validation findings,
platform-only tenant grants, immutable publication, quarantine/withdrawal
evidence, tenant discovery, installation, credential references, queued
smoke-test/readiness actions, connector readiness, SkillExecutionGateway
diagnostics, binding eligibility, and lifecycle audit records. Legacy skill
registry and skill execution diagnostic browser routes redirect to React.

The React agent and workflow test bench is available at
[http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/test-bench](http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/test-bench).
It reads `/admin/app/test-bench/bootstrap.json` plus suite, run, gate,
artifact, and audit contracts, then renders backend-owned suite authoring,
target revision binding, safe execution mode choices, run progress, assertion
diagnostics, trace summaries, artifact references, required publish-gate
evidence, and governance audit records. Test runs are deterministic in local
QA, default to mocked model/tool execution, and expose only safe summaries,
audit references, and artifact metadata to React.

The React usage and cost analytics workspace is available at
[http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/usage](http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/usage).
It reads `/admin/app/usage/bootstrap.json`, `/admin/app/usage/events.json`,
and `/admin/app/usage/exports/*` contracts, then renders backend-owned token
usage, estimated cost, confidence coverage, latency, unavailable usage, trend
buckets, provider/model/workflow/agent/sub-agent/prompt/execution-mode/
principal rollups, graph node attribution, gateway operation attribution,
physical attempt attribution, governed tool attribution, bounded event
drilldowns, and audited export summaries. Platform administrators can review
authorized cross-tenant usage; tenant administrators see only their active
tenant. Old usage browser links redirect to `/admin/app/usage`.

Focused shell validation:

```bash
uv run pytest --no-cov \
  tests/unit/api/test_admin_react_schema.py \
  tests/contract/test_admin_react_contract.py \
  tests/integration/test_admin_react_routes.py
cd frontend/admin && npm run typecheck && npm run test && npm run build
cd ../..
uv run python scripts/frontend/generate_admin_react_types.py --check
```

Focused data/form pattern validation:

```bash
uv run pytest --no-cov \
  tests/unit/api/test_admin_patterns_schema.py \
  tests/unit/api/test_admin_react_schema.py \
  tests/contract/test_admin_react_contract.py \
  tests/integration/test_admin_react_routes.py
cd frontend/admin && npm run typecheck && npm run test && npm run build
cd ../..
uv run python scripts/frontend/generate_admin_react_types.py --check
```

Focused operations workbench validation:

```bash
uv run pytest --no-cov \
  tests/unit/api/test_admin_workbench_schema.py \
  tests/unit/operations/test_workbench_service.py \
  tests/contract/test_admin_react_contract.py \
  tests/integration/test_admin_react_routes.py \
  tests/performance/operations/test_workbench_queries.py
cd frontend/admin && npm run typecheck && npm run test && npm run build
cd ../..
uv run python scripts/frontend/generate_admin_react_types.py --check
```

Focused workflow builder validation:

```bash
uv run pytest --no-cov \
  tests/unit/api/test_admin_workflow_builder_schema.py \
  tests/unit/admin/test_workflow_builder_service.py \
  tests/contract/test_admin_react_contract.py \
  tests/integration/test_admin_react_routes.py \
  tests/performance/workflows/test_workflow_builder_queries.py
cd frontend/admin && npm run typecheck && npm run test && npm run build
cd ../..
uv run python scripts/frontend/generate_admin_react_types.py --check
```

Focused governance validation:

```bash
uv run pytest --no-cov \
  tests/unit/api/test_admin_governance_schema.py \
  tests/unit/admin/test_governance_service.py \
  tests/contract/test_admin_react_contract.py \
  tests/integration/test_admin_react_routes.py \
  tests/performance/governance/test_governance_queries.py
cd frontend/admin && npm run typecheck && npm run test && npm run build
cd ../..
uv run python scripts/frontend/generate_admin_react_types.py --check
```

Focused skill lifecycle validation:

```bash
uv run pytest --no-cov \
  tests/unit/api/test_admin_skill_lifecycle_schema.py \
  tests/unit/admin/test_skill_lifecycle_service.py \
  tests/contract/test_admin_react_contract.py \
  tests/integration/test_admin_react_routes.py \
  tests/performance/skills/test_skill_lifecycle_queries.py
cd frontend/admin && npm run typecheck && npm run test && npm run build
cd ../..
uv run python scripts/frontend/generate_admin_react_types.py --check
```

Focused test bench validation:

```bash
uv run pytest --no-cov \
  tests/unit/api/test_admin_test_bench_schema.py \
  tests/unit/admin/test_test_bench_react_service.py \
  tests/contract/test_admin_react_contract.py \
  tests/integration/test_admin_react_routes.py \
  tests/performance/test_bench/test_react_test_bench_queries.py
cd frontend/admin && npm run typecheck && npm run test && npm run build
cd ../..
uv run python scripts/frontend/generate_admin_react_types.py --check
```

Focused usage analytics validation:

```bash
uv run pytest --no-cov \
  tests/unit/api/test_admin_usage_react_schema.py \
  tests/unit/admin/usage/test_react_usage_service.py \
  tests/performance/usage/test_react_usage_queries.py \
  tests/contract/test_admin_react_contract.py \
  tests/integration/test_admin_react_routes.py
cd frontend/admin && npm run typecheck && npm run test && npm run build
cd ../..
uv run python scripts/frontend/generate_admin_react_types.py --check
```

## Admin Console Shell

Open `/admin` to use the shared React admin console. Platform scope
omits `tenant_id`; tenant scope uses a validated `tenant_id=<uuid>` query
parameter on shell links and forms. The shell shows the active scope on every
wrapped page so administrators can identify whether they are acting at the
platform level or inside a tenant.

Navigation groups organize existing pages and React workspaces:
Workflows, Governance, Run Inspection, Reliability, and Access. The main
destinations include `/admin/app/workflows`, `/admin/app/governance`,
`/admin/runs`, `/admin/reliability/ui/`,
`/admin/reliability/ui/breakers`, and
`/admin/reliability/ui/dead-letters`.

Common states distinguish empty lists, filtered-empty lists, denied access,
not-found resources, unavailable dependencies, validation failures, partial
data, and unexpected errors. Safe messages, breadcrumbs, and saved-filter
summaries are sanitized so raw secrets, credentials, prompt text, memory
content, run payloads, stack traces, and cross-tenant labels are not rendered.

Saved filters are available only on useful filterable pages and are persisted
server-side by principal, admin area, filter key, and platform or tenant scope.
Restoration revalidates criteria and scope before redirecting to the target
page.

## Production Audit Debugging

Administrators and auditors can inspect tenant-scoped run evidence without
database access:

```bash
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  "http://127.0.0.1:8000/admin/runs/{workflow_run_id}/timeline?tenant_id={tenant_id}"

curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  "http://127.0.0.1:8000/admin/runs/debug-search?tenant_id={tenant_id}&status=failed"

curl -X POST -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  "http://127.0.0.1:8000/admin/runs/{workflow_run_id}/exports" \
  -d '{"tenant_id":"{tenant_id}","recipient_scope":"tenant_auditor","reason":"incident review"}'
```

Evidence is append-only and redacted by default. Timelines, traces, replay
views, lineage, version bundles, notifications, secret access, exports, logs,
and metrics never expose raw secrets, credentials, unauthorized prompt text, or
unauthorized memory content.

## User Interaction Channels

The channel layer supports Web UI, Telegram, and Web API access to the same run
model. Accepted starts return one canonical `run_id`, and all channels use the
same lifecycle states: `queued`, `running`, `waiting-for-input`, `completed`,
`failed`, and `canceled`.

- Web API: `POST /runs`, `/runs/{run_id}/status`,
  `/runs/{run_id}/timeline`, `/runs/{run_id}/events`,
  `/runs/{run_id}/result`, approvals, cancel, subscriptions, callbacks, and
  artifact URL grants.
- Web UI: `/runs` and `/runs/{run_id}` for run start, status, timeline, result,
  artifact, notification, and support trace visibility.
- Telegram: `/link`, `/run`, `/status`, `/approve`, `/reject`, `/resume`,
  `/cancel`, `/result`, `/artifacts`, and `/subscribe` after one-time platform
  identity linking.
- Telegram command aliases: tenant admins configure normalized natural-language
  triggers such as `Morning briefing` in `/admin/telegram`; linked Telegram
  users can send the alias to start the pinned published workflow and receive
  the safe result through the configured Bot API client.

Duplicate-prone actions require idempotency keys. The initiating user is
automatically subscribed to terminal notifications, additional authorized users
can subscribe per run, and artifacts are exposed through short-lived
platform-authenticated download URLs rather than direct bytes.

## Model Routing And Skill Configuration

Administrators can define one tenant default model plus workflow, agent, and
step overrides. Resolution precedence is step, agent, workflow, then tenant
default. Prompt references use step, agent, and workflow precedence only.

Skills, allowed tool policies, outbound domain policies, secret references,
and credential requirements deny by default and record safe provenance. Admin
APIs under `/admin/config/*` and minimal admin web views expose preview,
history, rollback, and run provenance for reviewer verification.

## Model Provider Gateway

Platform administrators configure model providers at
`/admin/app/governance/providers`. Old `/admin/model-providers` browser URLs
redirect to the React governance workspace.
Supported providers are OpenAI and local OpenAI-compatible chat completions
endpoints. Connections capture display name, provider type, safe base URL,
model ids, timeout policy, tenant visibility, active state, health state, last
test evidence, and credential secret reference ids.

Tenant-scoped users can read only visible provider rows and catalog entries.
They cannot create, edit, activate, deactivate, test, or sync provider
connections unless they also have platform administrator authority.

Safe provider tests use non-customer probes and persist only outcome, latency,
tested model, normalized reason, and safe diagnostics. Local provider URLs must
match the configured scheme, host, port, and CIDR allowlist. Raw API keys,
provider tokens, Authorization headers, prompts, completions, URL userinfo,
secret query parameters, and raw provider responses are not stored.

Provider probes and `ModelGateway` runtime calls resolve credentials through
the configured secret provider only at call time. OpenAI calls require a
resolvable safe reference and fail closed with `secret_reference_invalid` when
the reference is missing or invalid. Local OpenAI-compatible providers may run
without credentials only for allowlisted local endpoints. QA025 reviewer
evidence lives in
`specs/025-live-model-credential-resolution-for-gateway-calls/qa025.md`,
`specs/025-live-model-credential-resolution-for-gateway-calls/qa025_ui.md`,
and
`specs/025-live-model-credential-resolution-for-gateway-calls/qa025_user_guide.md`.

Catalog sync makes only active, healthy, tenant-visible, gateway-governed model
entries selectable. Runtime workers and test bench executions use
`ModelGateway` so latency, normalized errors, usage availability, retry/breaker
signals, and safe audit summaries are captured consistently.

## Agent And Workflow Test Bench

Administrators configure tenant-scoped test suites in React at
`/admin/app/test-bench` or through JSON APIs under `/admin/agent-tests`.
Legacy `/admin/agent-tests/ui...` browser URLs are compatibility redirects
that preserve tenant scope and safe route ids. Suites target prompt versions,
agent runtime profile versions, workflow drafts, published subworkflows, or
published workflows. Cases store safe fixture summaries, expected contract
shapes, deterministic assertions, optional evaluator settings, model/tool
modes, and pass thresholds.

Runs support `mock_model`, `mock_tools`, `real_model_side_effects_disabled`,
and `approved_real_probe` safe modes. QA and automated tests use deterministic
mock or mocked-provider paths; unapproved real probes fail closed. Result pages
show pass/fail status, step traces, provider/model metadata, prompt/profile and
skill references, token usage, latency, contract validation, assertion
diagnostics, blocked side effects, redacted transcript summaries, and artifact
metadata without raw secrets or prompt bodies.

Publish gate checks can require selected suites to have current passing
evidence for the candidate target version. Tenant isolation prevents Globex
admins from reading Acme suites, runs, fixtures, transcripts, target names, or
artifact references. QA015 reviewer evidence lives in
`specs/015-agent-workflow-test-bench/qa015.md`,
`specs/015-agent-workflow-test-bench/qa015_ui.md`, and
`specs/015-agent-workflow-test-bench/qa015_user_guide.md`.

Workflow publish gates now re-check required suite readiness against persisted
Agent Test Bench runs instead of trusting manual workflow document result
fields. A required suite must have same-tenant, same-target, current-revision,
passing evidence before validation, gate evaluation, or final publication can
succeed. Missing, failing, stale, wrong-target, platform-scope, and
cross-tenant evidence fail closed with safe summaries and without exposing raw
fixtures, transcripts, secrets, or denied tenant details. QA024 reviewer
evidence lives in
`specs/024-automatic-test-bench-evidence-integration-workflow-publish-gates/qa024.md`,
`specs/024-automatic-test-bench-evidence-integration-workflow-publish-gates/qa024_ui.md`,
and
`specs/024-automatic-test-bench-evidence-integration-workflow-publish-gates/qa024_user_guide.md`.

## Token Usage And Cost Analytics

Administrators review normalized model usage at `/admin/usage` or through JSON
APIs under `/admin/usage/api`. ModelGateway-backed invocations create safe
usage events with tenant, principal, workflow, run step, agent, sub-agent,
provider, model, prompt version, execution mode, token counts, billable units,
latency, pricing version, estimated cost, and estimated or confirmed status
when those values are available.

Platform admins can view and export all tenant usage. Tenant admins can view
and export only their tenant. Exports create CSV reports from safe normalized
columns and store artifact metadata through the configured storage provider.
Usage records, dashboards, exports, and audit-safe summaries exclude raw
prompts, completions, secrets, memory content, provider credentials, and
unauthorized run content.

QA016 reviewer evidence lives in
`specs/016-token-usage-cost-analytics/qa016.md`,
`specs/016-token-usage-cost-analytics/qa016_ui.md`, and
`specs/016-token-usage-cost-analytics/qa016_user_guide.md`.

The React usage workspace is available at `/admin/app/usage` with dashboard,
event drilldown, export creation, and export detail contracts under
`/admin/app/usage/*`. It keeps the same safe usage analytics behaviors while
adding generated TypeScript contracts, summary cards, trend buckets, all
supported rollup dimensions, gateway and physical-attempt attribution,
governed tool attribution, bounded event rows, audited export evidence, and
browser-first platform versus tenant review. QA035 reviewer evidence lives in
`specs/035-react-usage-and-cost-analytics/qa035.md`,
`specs/035-react-usage-and-cost-analytics/qa035_ui.md`, and
`specs/035-react-usage-and-cost-analytics/qa035_user_guide.md`.

## Telegram Configuration Console

Administrators review Telegram channel readiness at `/admin/telegram` or
through JSON APIs under `/admin/telegram/api`. The console shows global
provider readiness, tenant Telegram enablement, protected command readiness,
one-time link-token controls, masked linked Telegram identities, and safe
webhook and delivery diagnostics.

Platform admins can inspect platform readiness and authorized tenant scopes.
Tenant admins can inspect and mutate only their tenant. Local QA uses fake
secret references and simulated webhook validation; it does not call Telegram
or require a real bot token. Bot tokens, webhook secrets, private Telegram
messages, raw prompts, workflow run results, and unauthorized tenant data are
excluded from records, diagnostics, UI, and screenshot evidence.

QA017 reviewer evidence lives in
`specs/017-telegram-configuration-console/qa017.md`,
`specs/017-telegram-configuration-console/qa017_ui.md`, and
`specs/017-telegram-configuration-console/qa017_user_guide.md`.

## Membership Administration

Administrators review user and tenant membership state at
`/admin/memberships` or through JSON APIs under `/admin/memberships/api`.
Platform admins can list users across tenants, create idempotent invitations,
link Auth0-backed principal identities, create or revoke platform and tenant
role grants, suspend or reactivate principals, and inspect safe access history.

Tenant admins can invite users to their own tenant, assign permitted
`tenant_user` and `tenant_admin` roles, update tenant membership status, and
view tenant-local user status. Cross-tenant operations and platform-role
assignment attempts fail closed and write safe audit records.

The platform stores principal metadata, invitation records, tenant membership
state, role grants, access-decision history, and membership audit summaries. It
does not store passwords. UI, API summaries, flash messages, screenshots, and
audit metadata use masked emails, hashes, safe subject labels, role codes,
status values, and trace ids.

QA018 reviewer evidence lives in
`specs/018-user-tenant-membership-administration/qa018.md`,
`specs/018-user-tenant-membership-administration/qa018_ui.md`, and
`specs/018-user-tenant-membership-administration/qa018_user_guide.md`.

The React membership workspace is available at `/admin/app/memberships` with
bootstrap and mutation contracts under `/admin/app/memberships/*`. It keeps the
same safe membership behaviors while adding generated TypeScript contracts,
browser-first invitation, principal linking, role grant, revocation, status,
access-history, and audit panels. QA034 reviewer evidence lives in
`specs/034-react-user-and-tenant-membership-administration/qa034.md`,
`specs/034-react-user-and-tenant-membership-administration/qa034_ui.md`, and
`specs/034-react-user-and-tenant-membership-administration/qa034_user_guide.md`.

## Operations Console

Platform admins and auditors review platform operational status at
`/admin/operations` or through JSON APIs under `/admin/operations/api`. The
console aggregates persisted safe metadata for system health, dependency
readiness, worker capacity, queue pressure, database pool pressure,
object-storage status, model-provider health, Telegram/channel readiness,
reliability breaker state, retry and dead-letter state, request latency, run
lifecycle throughput, model latency, token throughput, error rate, and
operational logs.

Operational logs can be filtered by trace id, tenant id, run id, component,
severity, status, dependency, and time range. Platform admins and auditors with
explicit operations export permission can create CSV export artifacts through
the configured storage provider. Tenant admins are denied in v1, even if a
local QA principal accidentally includes operations permission codes.

The Operations Console does not read raw log files. UI, JSON APIs, CSV exports,
screenshots, and audit-safe summaries exclude raw prompts, model responses,
channel messages, secrets, credentials, memory content, raw payloads, stack
traces, and unauthorized tenant data. QA019 reviewer evidence lives in
`specs/019-operations-console-logs-performance/qa019.md`,
`specs/019-operations-console-logs-performance/qa019_ui.md`, and
`specs/019-operations-console-logs-performance/qa019_user_guide.md`.

## Reliability Scale Hardening

Operators can inspect and tune reliability state through
`/admin/reliability/dashboard`, `/admin/reliability/policies`,
`/admin/reliability/admission-decisions`, `/admin/reliability/breakers`,
`/admin/reliability/retries`, `/admin/reliability/compensations`, and
`/admin/reliability/dead-letters`.

Admission decisions return explicit accepted, queued, delayed, throttled,
rejected, or retry-eligible outcomes. Tenant quotas cover submitted work,
active work, recovery work, retries, compensation, artifact I/O, and operational
actions. Fair scheduling uses weighted shares and burst debt so compliant
tenants retain capacity during another tenant's burst. Breaker events,
recovery outcomes, compensation requests, dead-letter actions, denied attempts,
and control changes are audit-visible.

Safe tuning rules reject settings that disable quotas, fairness, recovery
safety, or containment unless an authorized override is recorded. Unknown or
non-repeatable side effects route to operator intervention, compensation is
requested at most once automatically per affected intent and hook, and large
failure evidence remains in object storage with PostgreSQL metadata only.

## Briefing Preferences

Tenant admins review and save Daily Intelligence Briefing preference profiles
at `/admin/briefing-preferences` or through JSON APIs under
`/admin/briefing-preferences/api`. Profiles capture location, timezone, news
topics, VIP sender hints, workday hours, commute mode, safe calendar/email
account references, output style, and optional scheduled briefing time.

Every profile update appends an immutable revision and moves a current head
projection. Runtime resolution looks up preferences by tenant id and principal
id, returning the pinned revision id and content digest for Daily Intelligence
Briefing run inputs. Telegram `Morning briefing` alias handling can attach this
context when a linked user has saved a profile.

Admin summaries show safe readiness evidence only: counts, masked sender hints,
reference labels, revision metadata, timestamps, and trace ids. Raw credentials,
raw account references, raw VIP sender values, and cross-tenant profile data are
excluded from admin summaries and audit metadata.

QA023 reviewer evidence lives in
`specs/023-user-briefing-preferences-and-context/qa023.md`,
`specs/023-user-briefing-preferences-and-context/qa023_ui.md`, and
`specs/023-user-briefing-preferences-and-context/qa023_user_guide.md`.

The React channel, Telegram, and briefing preference workspace is available at
`/admin/app/channels`. It combines channel readiness, Telegram tenant
configuration, safe secret-reference labels, webhook validation, natural
language aliases such as `Morning briefing`, protected alias readiness, masked
linked identities, one-time link-code handling, delivery diagnostics, safe run
status links, and Daily Intelligence Briefing preference profile management.

Tenant administrators stay scoped to their active tenant for Telegram settings,
aliases, link tokens, identities, diagnostics, and safe preference summaries.
Tenant users can manage their own briefing profile and safe run status links
without receiving tenant-wide alias administration. The workspace never renders
real bot tokens, webhook secrets, full Telegram identifiers, private messages,
raw preference values in admin summaries, raw prompts, run results, or raw tool
payloads. QA036 reviewer evidence lives in
`specs/036-react-channel-telegram-and-briefing-preferences/qa036.md`,
`specs/036-react-channel-telegram-and-briefing-preferences/qa036_ui.md`, and
`specs/036-react-channel-telegram-and-briefing-preferences/qa036_user_guide.md`.

The React admin migration hardening dashboard is available at
`/admin/app/migration`. After Spec 047 it summarizes React-only browser UI
decommission evidence, route compatibility redirects, rollback-by-redeploy
guidance, performance budgets, accessibility coverage, redaction sweeps, and
tenant isolation checks. QA037 and QA047 reviewer evidence lives in
`specs/037-react-admin-migration-hardening-and-jinja-retirement/qa037.md`,
`specs/037-react-admin-migration-hardening-and-jinja-retirement/qa037_ui.md`,
and
`specs/037-react-admin-migration-hardening-and-jinja-retirement/qa037_user_guide.md`.

## Latest Validation Evidence

Latest full validation run: `2026-04-24`

- command: `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90`
- result: `201 passed`
- coverage: `91.44%`
- durable runtime gates also passed: `uv run ruff check .`,
  `uv run ruff format --check .`, and `uv run mypy src`

## Operations And Review

- [Quickstart](/Users/scottcornell/src/my-projects/multi-agent/docs/quickstart.md)
- [User Interaction Channels](/Users/scottcornell/src/my-projects/multi-agent/docs/user-interaction-channels.md)
- [Admin Workflow Studio](/Users/scottcornell/src/my-projects/multi-agent/docs/admin-workflow-studio.md)
- [Guided Admin Workflow Builder](/Users/scottcornell/src/my-projects/multi-agent/docs/admin-workflow-builder.md)
- [Guided Admin Workflow Builder Testing](/Users/scottcornell/src/my-projects/multi-agent/docs/admin-workflow-builder-testing.md)
- [Durable Orchestration Runtime](/Users/scottcornell/src/my-projects/multi-agent/docs/durable-orchestration-runtime.md)
- [Immutable Memory](/Users/scottcornell/src/my-projects/multi-agent/docs/immutable-memory.md)
- [Production Audit Debugging](/Users/scottcornell/src/my-projects/multi-agent/docs/production-audit-debugging.md)
- [Reliability Scale Hardening](/Users/scottcornell/src/my-projects/multi-agent/docs/reliability-scale-hardening.md)
- [Admin Console Shell](/Users/scottcornell/src/my-projects/multi-agent/docs/admin-console-shell.md)
- [Prompt Runtime Profiles](/Users/scottcornell/src/my-projects/multi-agent/docs/prompt-runtime-profiles.md)
- [Prompt Runtime Profiles Testing](/Users/scottcornell/src/my-projects/multi-agent/docs/prompt-runtime-profiles-testing.md)
- Spec 012 V2 `ModelGateway` runtime hardening evidence is included in
  [Prompt Runtime Profiles Testing](/Users/scottcornell/src/my-projects/multi-agent/docs/prompt-runtime-profiles-testing.md)
  and the PR notes.
- [Foundation Runbook](/Users/scottcornell/src/my-projects/multi-agent/docs/foundation-runbook.md)
- [Architecture](/Users/scottcornell/src/my-projects/multi-agent/docs/architecture.md)
- [Constitution](/Users/scottcornell/src/my-projects/multi-agent/.specify/memory/constitution.md)
