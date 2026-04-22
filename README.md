# Multi-Agent AI Platform

This repository now includes the platform-foundation implementation for a
multi-tenant FastAPI and worker service with PostgreSQL durability boundaries,
tenant-aware queue primitives, provider-based secret and artifact adapters,
operational health endpoints, Alembic migrations, and CI quality gates.

## Foundation Scope

- operational placeholder API: `/health/live`, `/health/ready`, `/version`,
  and `/dependencies`
- worker bootstrap and durable queue repository primitives
- tenant, artifact, secret-reference, queue, and audit persistence models
- secret-provider and artifact-provider abstractions for local, test, and
  production-oriented wiring
- local validation scripts and CI enforcement for Ruff, mypy, pytest, and
  migration checks

## Quickstart

1. Install dependencies with `uv sync`.
2. Copy `.env.example` to `.env`.
3. Start dependencies with `docker compose up -d postgres`.
4. Apply migrations with `uv run alembic upgrade head`.
5. Run the API with
   `uv run uvicorn multi_agent_platform.api.main:app --reload`.
6. Run the worker with `uv run python -m multi_agent_platform.workers.main`.
7. Validate the repo with `./scripts/check.sh`.

## Operations And Review

- [Quickstart](/Users/scottcornell/src/my-projects/multi-agent/docs/quickstart.md)
- [Foundation Runbook](/Users/scottcornell/src/my-projects/multi-agent/docs/foundation-runbook.md)
- [Architecture](/Users/scottcornell/src/my-projects/multi-agent/docs/architecture.md)
- [Constitution](/Users/scottcornell/src/my-projects/multi-agent/.specify/memory/constitution.md)
