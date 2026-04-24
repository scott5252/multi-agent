# multi-agent Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-04-24

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
- 005-immutable-memory: Planned append-only PostgreSQL-backed memory scopes, immutable version lineage, head projections, runtime-safe reads/writes, retrieval APIs, audit redaction, archival markers, and concurrency tests.
- 004-durable-orchestration-runtime: Planned the LangGraph durable orchestration runtime, PostgreSQL checkpointer, worker leases, handoff contracts, side-effect intents, approval wait states, and crash-resume test strategy.
- 003-workflow-studio-registry: Added Python 3.12 + FastAPI, Pydantic v2, Pydantic Settings, SQLAlchemy

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->

<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan:
`specs/005-immutable-memory/plan.md`
<!-- SPECKIT END -->
