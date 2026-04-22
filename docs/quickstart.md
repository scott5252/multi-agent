# Platform Foundation Quickstart

## Prerequisites

- Python 3.12
- [uv](https://docs.astral.sh/uv/)
- Docker Compose v2

## Local Setup

1. Install dependencies with `uv sync`.
2. Copy `.env.example` to `.env`.
3. Start PostgreSQL with `docker compose up -d postgres`.
4. Optionally start MinIO for S3-compatible storage validation:
   `docker compose --profile storage up -d minio`.
5. Apply migrations with `uv run alembic upgrade head`.

## Run The Services

Start the API:

```bash
uv run uvicorn multi_agent_platform.api.main:app --reload
```

Start the worker in another shell:

```bash
uv run python -m multi_agent_platform.workers.main
```

## Validate The Foundation

Run the full local quality workflow:

```bash
./scripts/check.sh
```

Capture operational smoke output against a running API:

```bash
./scripts/smoke_foundation.sh
```

## Troubleshooting

- `503 /health/ready`: confirm `.env` is present, PostgreSQL is reachable, and
  `uv run alembic upgrade head` has run successfully.
- Missing artifacts in local mode: verify `FILESYSTEM_STORAGE_ROOT` exists and
  is writable.
- Secret lookup failures in local mode: confirm the configured static secret or
  `MAP_SECRET_*` variable exists for the requested reference.
- Recovery validation: rerun `uv run alembic downgrade -1` followed by
  `uv run alembic upgrade head` before opening a PR.

## Related Docs

- [Foundation Runbook](/Users/scottcornell/src/my-projects/multi-agent/docs/foundation-runbook.md)
- [Architecture](/Users/scottcornell/src/my-projects/multi-agent/docs/architecture.md)
