# Testing Instructions: Workflow Graph Execution And Parallel Sub-Agent Runtime

## Focused Suite

Run the deterministic Spec 020 suite without coverage when iterating:

```bash
uv run pytest --no-cov \
  tests/unit/runtime/orchestration/test_graph_execution.py \
  tests/unit/runtime/orchestration/test_graph_roles.py \
  tests/unit/runtime/orchestration/test_graph_redaction.py \
  tests/contract/test_workflow_graph_execution_contract.py \
  tests/docs/test_workflow_graph_execution_docs.py \
  tests/integration/runtime/test_workflow_graph_execution.py \
  tests/integration/workers/test_orchestration_worker.py \
  tests/performance/runtime/test_workflow_graph_execution_performance.py
```

Expected: the focused graph suite passes.

## High-Signal Individual Tests

```bash
uv run pytest --no-cov -vv tests/integration/runtime/test_workflow_graph_execution.py::test_daily_briefing_graph_schedules_four_scouts_in_one_wave
uv run pytest --no-cov -vv tests/integration/runtime/test_workflow_graph_execution.py::test_manual_resolution_join_pauses_and_persists_approval
uv run pytest --no-cov -vv tests/integration/runtime/test_workflow_graph_execution.py::test_cross_tenant_bundle_execution_fails_closed
uv run pytest --no-cov -vv tests/integration/runtime/test_workflow_graph_execution.py::test_graph_execution_redacts_sensitive_step_and_timeline_values
uv run pytest --no-cov -vv tests/integration/workers/test_orchestration_worker.py::test_orchestration_worker_executes_claimed_graph_run
```

Expected: each targeted behavior passes independently.

## QA Document And Autopilot Validation

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/020-workflow-graph-execution-parallel-sub-agent-runtime
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/020-workflow-graph-execution-parallel-sub-agent-runtime/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/020-workflow-graph-execution-parallel-sub-agent-runtime/validation.yml --start-processes
```

Expected: QA docs, API health checks, process startup, Playwright smoke, and
configured quality commands pass.

## Full Repository Gates

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected: linting, formatting, type checking, and coverage pass.

## Notes

- Use `.env.qa020` for manual QA and autopilot validation.
- Use the isolated `multi_agent_platform_qa020` database.
- Do not add real provider credentials.
- Do not expect a Spec 020 Alembic revision.
- Browser validation is a smoke path over existing shared admin UI because
  Spec 020 is runtime-first.
