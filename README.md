# Multi-Agent AI Platform

This repository now includes the platform foundation plus a production-style
authentication and authorization layer for the multi-tenant FastAPI and worker
service. The platform supports Auth0 JWT validation in production,
deterministic local principals in `local`/`test`/`ci`, tenant-aware protected
routes, platform-admin role grants, support-override approvals, delegated
credential linkage, durable access-decision audit records, operational health
endpoints, Alembic migrations, and CI quality gates.

## Current Scope

- operational placeholder API: `/health/live`, `/health/ready`, `/version`,
  and `/dependencies`
- worker bootstrap and durable queue repository primitives
- auth and admin-access API surfaces: `/auth/me`,
  `/auth/tenant-context/{tenant_id}`, `/admin/role-grants`, and
  `/admin/support-overrides`
- tenant, artifact, secret-reference, queue, audit, principal-identity,
  role-grant, support-override, delegated-credential, and access-decision
  persistence models
- secret-provider and artifact-provider abstractions for local, test, and
  production-oriented wiring
- local validation scripts and CI enforcement for Ruff, mypy, pytest, and
  migration and contract checks

## Quickstart

1. Install dependencies with `uv sync`.
2. Copy `.env.example` to `.env`.
3. Choose `AUTH_MODE=local_principal` for local/testing or `AUTH_MODE=auth0`
   for production-style validation.
4. Start dependencies with `docker compose up -d postgres`.
5. Apply migrations with `uv run alembic upgrade head`.
6. Run the API with
   `uv run uvicorn multi_agent_platform.api.main:app --reload`.
7. Run the worker with `uv run python -m multi_agent_platform.workers.main`.
8. Validate the repo with `./scripts/check.sh`.

## Operations And Review

- [Quickstart](/Users/scottcornell/src/my-projects/multi-agent/docs/quickstart.md)
- [Foundation Runbook](/Users/scottcornell/src/my-projects/multi-agent/docs/foundation-runbook.md)
- [Architecture](/Users/scottcornell/src/my-projects/multi-agent/docs/architecture.md)
- [Constitution](/Users/scottcornell/src/my-projects/multi-agent/.specify/memory/constitution.md)
