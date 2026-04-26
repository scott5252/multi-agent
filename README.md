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
- [Foundation Runbook](/Users/scottcornell/src/my-projects/multi-agent/docs/foundation-runbook.md)
- [Architecture](/Users/scottcornell/src/my-projects/multi-agent/docs/architecture.md)
- [Constitution](/Users/scottcornell/src/my-projects/multi-agent/.specify/memory/constitution.md)
