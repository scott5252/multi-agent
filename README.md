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
- model provider gateway management under `/admin/model-providers` for
  platform-admin OpenAI/local OpenAI-compatible provider configuration, safe
  probes, health review, catalog sync evidence, and gateway-governed runtime
  invocation metadata

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
10. Validate the repo with `./scripts/check.sh`.

## Admin Console Shell

Open `/admin` to use the shared server-rendered admin console. Platform scope
omits `tenant_id`; tenant scope uses a validated `tenant_id=<uuid>` query
parameter on shell links and forms. The shell shows the active scope on every
wrapped page so administrators can identify whether they are acting at the
platform level or inside a tenant.

Navigation groups organize existing pages without replacing their routes:
Workflows, Model And Skill Config, Run Inspection, Reliability, and Access.
The main destinations remain `/admin/workflows/ui`, `/admin/config/ui`,
`/admin/config/ui/history`, `/admin/runs`, `/admin/reliability/ui/`,
`/admin/reliability/ui/breakers`, and
`/admin/reliability/ui/dead-letters`, plus `/admin/model-providers`.

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

Platform administrators configure model providers at `/admin/model-providers`.
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

Catalog sync makes only active, healthy, tenant-visible, gateway-governed model
entries selectable. Runtime workers and test bench executions use
`ModelGateway` so latency, normalized errors, usage availability, retry/breaker
signals, and safe audit summaries are captured consistently.

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
- [Durable Orchestration Runtime](/Users/scottcornell/src/my-projects/multi-agent/docs/durable-orchestration-runtime.md)
- [Immutable Memory](/Users/scottcornell/src/my-projects/multi-agent/docs/immutable-memory.md)
- [Production Audit Debugging](/Users/scottcornell/src/my-projects/multi-agent/docs/production-audit-debugging.md)
- [Reliability Scale Hardening](/Users/scottcornell/src/my-projects/multi-agent/docs/reliability-scale-hardening.md)
- [Admin Console Shell](/Users/scottcornell/src/my-projects/multi-agent/docs/admin-console-shell.md)
- [Foundation Runbook](/Users/scottcornell/src/my-projects/multi-agent/docs/foundation-runbook.md)
- [Architecture](/Users/scottcornell/src/my-projects/multi-agent/docs/architecture.md)
- [Constitution](/Users/scottcornell/src/my-projects/multi-agent/.specify/memory/constitution.md)
