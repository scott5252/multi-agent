# multi-agent Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-04-22

## Active Technologies

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

- 001-platform-foundation: Added the platform foundation plan, operational
  placeholder API contract, modular service layout, PostgreSQL-backed durability
  boundaries, and CI quality-gate expectations.

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
