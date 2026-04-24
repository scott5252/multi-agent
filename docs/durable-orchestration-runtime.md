# Durable Orchestration Runtime

This runbook covers Spec `004`, the durable LangGraph orchestration runtime.
The runtime starts only published workflow bundles, pins an execution bundle per
run, records semantic timeline events, and gives workers a durable claim and
resume surface.

## Start The Runtime

Install dependencies and apply migrations:

```bash
uv sync
uv run alembic upgrade head
```

Run the API:

```bash
uv run uvicorn multi_agent_platform.api.main:app --reload
```

Run a worker:

```bash
uv run python -m multi_agent_platform.workers.main
```

Workers receive a process-scoped `worker_id`, poll runtime work, claim runnable
runs with a two-minute default lease, and release or complete work through the
runtime repository.

## Operator Checks

Use `POST /runtime/runs` to start a published workflow version. Inspect the run
with `GET /runtime/runs/{workflow_run_id}`, review timeline evidence at
`GET /runtime/runs/{workflow_run_id}/timeline`, and cancel active or paused
runs with `POST /runtime/runs/{workflow_run_id}/cancel`.

Runtime inspection is tenant-scoped. Cross-tenant run IDs return not found for
callers outside the owning tenant.

## Recovery Evidence

Durable runtime validation should include:

- checkpoint persistence and stable LangGraph `thread_id`
- resume after crash at claim, checkpoint, and side-effect boundaries
- worker lease expiry and takeover after the configured lease window
- idempotent side-effect retry using stored intent state
- contract-gated handoff rejection before receiver consumption
- approval pause and resume with the same pinned bundle
- parent-child lineage traversal for nested subworkflows
- retention defaults for checkpoint and payload references

## Security Review Notes

Runtime state stores secret references and delegated credential references, not
secret values. Logs, audit payloads, and timeline payloads must remain redacted.
Resume paths must re-check tenant scope, worker claim ownership, tool allowlists,
egress policy, delegated credential availability, and approval authorization.

## Validation

Run the quality gates before review:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Latest local evidence for Spec `004`: 201 tests passed with 91.44 percent
coverage on 2026-04-24.
