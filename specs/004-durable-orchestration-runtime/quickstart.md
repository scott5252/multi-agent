# Quickstart: Durable Orchestration Runtime

**Feature**: Durable Orchestration Runtime  
**Date**: 2026-04-24

This quickstart describes the validation flow expected after implementation.

## 1. Install Dependencies

```bash
uv sync
```

The implementation must update dependency bounds to include:

```text
langchain>=1.2.15
langgraph>=1.1.9
langgraph-checkpoint-postgres>=3.0.5
```

## 2. Prepare PostgreSQL

```bash
uv run alembic upgrade head
```

Confirm the durable runtime migration creates platform runtime tables and the
LangGraph Postgres checkpointer setup is available before workers start.

## 3. Start The API

```bash
uv run uvicorn multi_agent_platform.api.main:app --reload
```

## 4. Start A Runtime Worker

In a second terminal:

```bash
uv run python -m multi_agent_platform.workers.main
```

The worker must log its `worker_id`, claim polling interval, and orchestration
runtime readiness.

## 5. Start A Published Workflow Run

Use a published workflow version id from the workflow registry:

```bash
curl -sS -X POST http://127.0.0.1:8000/runtime/runs \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: acme" \
  -d '{
    "published_workflow_version_id": "00000000-0000-0000-0000-000000000004",
    "idempotency_key": "demo-durable-run-001",
    "input": {"prompt": "Run the durable orchestration demo"}
  }'
```

Expected result:

- HTTP 202
- `workflow_run_id`
- `run_bundle_id`
- `bundle_digest`
- initial status `pending` or `runnable`

## 6. Inspect Run Status

```bash
curl -sS http://127.0.0.1:8000/runtime/runs/{workflow_run_id} \
  -H "X-Tenant-ID: acme"
```

Verify the response includes:

- pinned bundle digest
- current status
- current checkpoint id when execution has progressed
- pause reason or terminal reason when applicable

## 7. Validate Crash And Resume

Run the focused recovery tests:

```bash
uv run pytest tests/integration/runtime/test_orchestration_crash_resume.py -q
```

Required evidence:

- crash after checkpoint resumes from latest checkpoint
- crash after side-effect success does not repeat the side effect
- expired worker lease is claimed by a different worker after configured expiry
- stale queued work cannot mutate terminal runs

## 8. Validate Approval Pause And Resume

Run a workflow that reaches an approval gate, then inspect pending gates:

```bash
curl -sS http://127.0.0.1:8000/runtime/runs/{workflow_run_id}/approval-gates \
  -H "X-Tenant-ID: acme"
```

Approve the gate:

```bash
curl -sS -X POST \
  http://127.0.0.1:8000/runtime/runs/{workflow_run_id}/approval-gates/{approval_gate_id}/decisions \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: acme" \
  -d '{"decision": "approve", "decision_payload": {"approved": true}}'
```

Expected result:

- decision accepted
- resume work queued
- run continues with the same `bundle_digest` and checkpoint thread

## 9. Validate Handoff Contract Failure

Run the contract validation tests:

```bash
uv run pytest tests/unit/runtime/orchestration/test_contracts.py \
  tests/contract/test_runtime_orchestration_contract.py -q
```

Required evidence:

- invalid handoff payload is not consumed
- handoff envelope records validation errors
- default failure route fails the affected run path

## 10. Validate Nested Subworkflow Lineage

```bash
curl -sS http://127.0.0.1:8000/runtime/runs/{workflow_run_id}/lineage \
  -H "X-Tenant-ID: acme"
```

Expected result:

- parent and child run nodes
- parent-child edge with parent step id
- child bundle digest
- child status visible from parent and child inspection paths

## 11. Run Quality Gates

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

PR evidence must include the coverage summary, crash/resume logs, worker lease
takeover evidence, approval pause/resume evidence, contract failure evidence,
and README/operator documentation updates.
