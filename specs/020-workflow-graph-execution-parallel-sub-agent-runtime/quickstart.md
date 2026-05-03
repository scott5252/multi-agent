# Quickstart: Workflow Graph Execution And Parallel Sub-Agent Runtime

## Goal

Validate that a worker can execute a published workflow graph, fan out the
Daily Intelligence Briefing scout branches in parallel, evaluate joins, resume
without duplicating completed nodes, and persist safe final output evidence.

## Local Setup

```bash
uv sync
cp specs/020-workflow-graph-execution-parallel-sub-agent-runtime/.env.qa020 .env
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa020 && createdb -U postgres multi_agent_platform_qa020'
uv run alembic upgrade head
```

Expected: dependencies install, PostgreSQL starts, the QA020 database is reset,
and migrations complete.

## Run Focused Tests

```bash
uv run pytest \
  tests/unit/runtime/orchestration/test_graph_execution.py \
  tests/unit/runtime/orchestration/test_graph_roles.py \
  tests/unit/runtime/orchestration/test_graph_redaction.py \
  tests/integration/runtime/test_workflow_graph_execution.py \
  tests/integration/workers/test_orchestration_worker.py
```

Expected: graph planning, join policy evaluation, deterministic role execution,
resume behavior, tenant isolation, and worker integration tests pass.

## Manual Runtime Smoke

1. Start the API:

   ```bash
   uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
   ```

2. Start the worker in another terminal:

   ```bash
   uv run python -m multi_agent_platform.workers.main
   ```

3. Use the QA020 guide to seed a published Daily Intelligence Briefing bundle
   and a runnable workflow run.

Expected: the worker claims the run, records graph execution timeline events,
creates run steps for orchestrator, four scouts, join, focus, synthesis, and
terminal nodes, then marks the run succeeded with safe final output.

## API Checks

```bash
curl --fail --silent http://127.0.0.1:8000/health/live
curl --fail --silent http://127.0.0.1:8000/health/ready
curl --fail --silent http://127.0.0.1:8000/version
curl --fail --silent http://127.0.0.1:8000/dependencies
```

Expected: every command exits successfully.

## Quality Gates

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected: all quality gates pass.
