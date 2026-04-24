# Multi-Agent AI Platform

This repository now includes the platform foundation, the auth and access
layer, the full Spec `003` workflow-studio registry flow, and the Spec `004`
durable orchestration runtime. Admins can author workflow drafts, publish
immutable version bundles, start pinned durable runs, inspect runtime timeline
evidence, and operate background workers that resume interrupted work.

## Current Scope

- operational API: `/health/live`, `/health/ready`, `/version`, `/dependencies`
- auth and admin-access APIs: `/auth/me`, `/auth/tenant-context/{tenant_id}`,
  `/admin/role-grants`, `/admin/support-overrides`
- workflow-registry APIs under `/admin/workflows`
- embedded workflow registry UI under `/admin/workflows/ui`
- durable runtime APIs under `/runtime/runs`
- browser-friendly local QA login under `/auth/local-login`
- durable lineage, draft, revision, validation-result, published-version, and
  sharing-grant persistence
- per-run execution bundle pinning, worker leases, timeline events, approval
  gates, handoff envelopes, side-effect intents, lineage, and retention models
- filesystem or provider-backed artifact storage for compiled workflow bundles

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
9. Validate the repo with `./scripts/check.sh`.

## Latest Validation Evidence

Latest full validation run: `2026-04-24`

- command: `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90`
- result: `201 passed`
- coverage: `91.44%`
- durable runtime gates also passed: `uv run ruff check .`,
  `uv run ruff format --check .`, and `uv run mypy src`

## Operations And Review

- [Quickstart](/Users/scottcornell/src/my-projects/multi-agent/docs/quickstart.md)
- [Admin Workflow Studio](/Users/scottcornell/src/my-projects/multi-agent/docs/admin-workflow-studio.md)
- [Durable Orchestration Runtime](/Users/scottcornell/src/my-projects/multi-agent/docs/durable-orchestration-runtime.md)
- [Foundation Runbook](/Users/scottcornell/src/my-projects/multi-agent/docs/foundation-runbook.md)
- [Architecture](/Users/scottcornell/src/my-projects/multi-agent/docs/architecture.md)
- [Constitution](/Users/scottcornell/src/my-projects/multi-agent/.specify/memory/constitution.md)
