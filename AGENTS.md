# multi-agent Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-04-26

## Active Technologies
- Python 3.12 + FastAPI security dependencies, Auth0 JWT validation, Pydantic
  Settings, SQLAlchemy 2.x, Alembic, PostgreSQL auth metadata, pytest,
  pytest-asyncio, httpx, Ruff, mypy, uv (002-platform-auth-access)
- Python 3.12 + FastAPI, Pydantic v2, Pydantic Settings, SQLAlchemy (003-workflow-studio-registry)
- PostgreSQL for workflow lineages, active drafts, immutable draft revisions, published bundle metadata (003-workflow-studio-registry)
- Python 3.12 + FastAPI, Pydantic v2, SQLAlchemy 2.x, Alembic, PostgreSQL 16+, psycopg 3, LangChain 1.2.15, LangGraph 1.1.9, langgraph-checkpoint-postgres 3.0.5, pytest, pytest-asyncio, httpx, Ruff, mypy, uv (004-durable-orchestration-runtime)
- PostgreSQL for workflow runs, run steps, worker leases, LangGraph checkpoints, handoff envelopes, side-effect intents, approvals, parent-child lineage, audit events, and retention metadata (004-durable-orchestration-runtime)
- Python 3.12 + FastAPI, Pydantic v2, Pydantic Settings, SQLAlchemy 2.x, Alembic, PostgreSQL 16+, psycopg 3, LangChain 1.2.15, LangGraph 1.1.9, langgraph-checkpoint-postgres 3.0.5, pytest, pytest-asyncio, httpx, Ruff, mypy, uv (005-immutable-memory)
- PostgreSQL for memory scopes, immutable memory versions, head projections, read/write audit records, archival markers, links to runtime execution bundles, workflow runs, run steps, and parent-child lineage (005-immutable-memory)
- Python 3.12 + FastAPI, Starlette `StreamingResponse` for SSE, Pydantic v2,
  SQLAlchemy 2.x, Alembic, PostgreSQL 16+, psycopg 3, Auth0 JWT validation,
  httpx, pytest, pytest-asyncio, Ruff, mypy, uv (006-user-interaction-channels)
- PostgreSQL for channel sessions, Telegram identity links, normalized
  requests, idempotency records, notification subscriptions and delivery
  attempts, API callbacks, timeline projections, and interaction audit records
  (006-user-interaction-channels)
- Python 3.12 + FastAPI, Pydantic v2, Pydantic Settings, SQLAlchemy 2.x,
  Alembic, PostgreSQL 16+, psycopg 3, Auth0 JWT validation,
  LangChain 1.2.15, LangGraph 1.1.9, langgraph-checkpoint-postgres 3.0.5,
  pytest, pytest-asyncio, httpx, Ruff, mypy, uv (007-model-skill-routing)
- PostgreSQL for model provider catalog entries, versioned model routing,
  prompt references, skill bindings, tool policies, outbound policies,
  secret-reference metadata, credential requirements, active pointers, runtime
  pins, policy decisions, migrations, and configuration audit records
  (007-model-skill-routing)
- Python 3.12 + FastAPI, Pydantic v2, Pydantic Settings, SQLAlchemy 2.x,
  Alembic, PostgreSQL 16+, psycopg 3, Auth0 JWT validation,
  LangChain 1.2.15, LangGraph 1.1.9, langgraph-checkpoint-postgres 3.0.5,
  pytest, pytest-asyncio, httpx, Ruff, mypy, uv
  (008-production-audit-debugging)
- PostgreSQL for append-only audit events, run timeline events, runtime trace
  records, capture gaps, lineage projections, version-bundle references,
  notification delivery projections, secret-access audit metadata, inspection
  access audits, export metadata, redaction/classification records, and replay
  snapshots (008-production-audit-debugging)
- Python 3.12 + FastAPI, Starlette response handling, Pydantic v2,
  Pydantic Settings, SQLAlchemy 2.x async ORM, Alembic, PostgreSQL 16+,
  psycopg 3, Auth0 JWT validation, LangChain 1.2.15, LangGraph 1.1.9,
  langgraph-checkpoint-postgres 3.0.5, prometheus-client, pytest,
  pytest-asyncio, httpx, Ruff, mypy, uv (009-reliability-scale-hardening)
- PostgreSQL for reliability policies, worker leases, queue state, quota
  counters, fairness windows, retry schedules, circuit breaker state,
  compensation requests, dead-letter records, operational snapshots, audit
  events, artifact metadata, and object-storage artifact references
  (009-reliability-scale-hardening)

- Python 3.12 + FastAPI, Pydantic Settings, LangChain, LangGraph, SQLAlchemy 2.x, Alembic, psycopg 3, pytest, pytest-asyncio, httpx, Ruff, mypy, uv (001-platform-foundation)

## Project Structure

```text
src/multi_agent_platform/
tests/
alembic/
```

## Commands

- `uv sync`
- `uv run alembic upgrade head`
- `uv run uvicorn multi_agent_platform.api.main:app --reload`
- `uv run python -m multi_agent_platform.workers.main`
- `uv run ruff check .`
- `uv run ruff format --check .`
- `uv run mypy src`
- `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90`

## Code Style

Python 3.12: Follow standard conventions with type annotations on public
boundaries, FastAPI dependency injection for service wiring, and SQLAlchemy 2.x
async patterns for PostgreSQL access.

## Recent Changes
- 009-reliability-scale-hardening: Planned reliability and scale hardening with
  tenant-aware admission and backpressure, worker autoscaling signals, lease
  tuning, DB pooling, partitioning, retry budgets, circuit breakers,
  compensation orchestration, dead-letter handling, operational dashboards,
  tenant fairness controls, artifact-throughput limits, failure-mode research,
  and resume-after-failure validation under load.
- 008-production-audit-debugging: Planned production observability and audit
  debugging with structured logs, trace IDs, metrics, append-only audit tables,
  admin timeline/search/replay APIs, lineage and version-bundle views,
  redaction/classification, exports, and completeness testing.
- 007-model-skill-routing: Planned versioned model routing and skill/tool
  configuration, deterministic precedence resolution, run and first-use
  pinning, rollback, outbound and credential policy enforcement, audit
  provenance, and admin preview/history views.
- 006-user-interaction-channels: Planned FastAPI channel adapters for Web UI,
  Telegram webhooks, and REST APIs with normalized requests, shared run status,
  SSE/polling, callbacks, approval/resume flows, notifications, and artifact
  access.
- 005-immutable-memory: Planned append-only PostgreSQL-backed memory scopes,
  immutable version lineage, head projections, runtime-safe reads/writes,
  retrieval APIs, audit redaction, archival markers, and concurrency tests.

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->

<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan:
`specs/009-reliability-scale-hardening/plan.md`
<!-- SPECKIT END -->
