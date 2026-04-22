# Quickstart: Platform Foundation

## Purpose

Bootstrap the platform foundation locally, validate the operational placeholder
endpoints, run the worker shell, and execute the required quality gates.

## Prerequisites

- Python 3.12
- [uv](https://docs.astral.sh/uv/)
- Docker Compose v2

## 1. Install dependencies

```bash
uv sync
```

## 2. Prepare environment configuration

```bash
cp .env.example .env
```

Required environment groups:

- application settings
- PostgreSQL connection settings
- secret-provider selection
- artifact-provider selection
- observability toggles

## 3. Start infrastructure dependencies

Default infrastructure:

```bash
docker compose up -d postgres
```

Optional local S3-compatible artifact storage:

```bash
docker compose --profile storage up -d minio
```

Optional observability helpers:

```bash
docker compose --profile observability up -d
```

## 4. Apply database migrations

```bash
uv run alembic upgrade head
```

Local and test rollback validation:

```bash
uv run alembic downgrade -1
uv run alembic upgrade head
```

## 5. Start the API

```bash
uv run uvicorn multi_agent_platform.api.main:app --reload
```

## 6. Start the worker

In another shell:

```bash
uv run python -m multi_agent_platform.workers.main
```

## 7. Validate operational endpoints

```bash
curl http://127.0.0.1:8000/health/live
curl http://127.0.0.1:8000/health/ready
curl http://127.0.0.1:8000/version
curl http://127.0.0.1:8000/dependencies
```

Readiness is expected to fail until:

- configuration is valid
- PostgreSQL is reachable
- required migrations are current
- required worker dependencies are healthy

## 8. Run quality gates

Lint:

```bash
uv run ruff check .
uv run ruff format --check .
```

Type check:

```bash
uv run mypy src
```

Tests with coverage:

```bash
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

## 9. Shut everything down

```bash
docker compose down
```

If storage or observability profiles were enabled, the same command will stop
them as well.
