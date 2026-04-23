# Multi-Agent AI Platform

This repository now includes the platform foundation, the auth and access
layer, and the full Spec `003` workflow-studio registry flow. Admins can now
author workflow drafts, validate them, publish immutable version bundles,
inspect version detail, and share platform-scoped published assets to selected
tenants.

## Current Scope

- operational API: `/health/live`, `/health/ready`, `/version`, `/dependencies`
- auth and admin-access APIs: `/auth/me`, `/auth/tenant-context/{tenant_id}`,
  `/admin/role-grants`, `/admin/support-overrides`
- workflow-registry APIs under `/admin/workflows`
- embedded workflow registry UI under `/admin/workflows/ui`
- browser-friendly local QA login under `/auth/local-login`
- durable lineage, draft, revision, validation-result, published-version, and
  sharing-grant persistence
- filesystem or provider-backed artifact storage for compiled workflow bundles

## Quickstart

1. Run `uv sync`.
2. Copy `.env.example` to `.env`.
3. Set `AUTH_MODE=local_principal`.
4. Run `docker compose up -d postgres`.
5. Run `uv run alembic upgrade head`.
6. Run `uv run uvicorn multi_agent_platform.api.main:app --reload`.
7. Open
   [http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/workflows/ui](http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/workflows/ui).
8. Validate the repo with `./scripts/check.sh`.

## Latest Validation Evidence

Latest full validation run: `2026-04-23`

- command: `./scripts/check.sh`
- result: `153 passed`
- coverage: `90.53%`
- measured workflow-registry timings:
  list `7.36 ms`, draft detail `7.23 ms`, save `10.50 ms`, validate `8.90 ms`,
  publish `13.76 ms`, version detail `6.01 ms`

## Operations And Review

- [Quickstart](/Users/scottcornell/src/my-projects/multi-agent/docs/quickstart.md)
- [Admin Workflow Studio](/Users/scottcornell/src/my-projects/multi-agent/docs/admin-workflow-studio.md)
- [Foundation Runbook](/Users/scottcornell/src/my-projects/multi-agent/docs/foundation-runbook.md)
- [Architecture](/Users/scottcornell/src/my-projects/multi-agent/docs/architecture.md)
- [Constitution](/Users/scottcornell/src/my-projects/multi-agent/.specify/memory/constitution.md)
