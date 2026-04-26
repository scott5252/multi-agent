# Testing Instructions: Production Audit And Debugging

## Successful And Failed Runs

Create one completed run and one failed run. Confirm timeline lookup returns
ordered lifecycle events, safe failure reason, failed stage, recommended
investigation category, trace id, and replay checkpoints.

## Runtime Decisions

Fixture or execute handoffs, contract validations, memory writes, tool usage,
model selection, notification delivery, and secret-reference access. Confirm
every decision links to a same-tenant timeline event and exposes only safe
summaries.

## Governance

Validate bundle visibility, lineage boundary nodes, notification state,
secret-access metadata, authorization failures, redaction, and export creation.

## README Guidance

Review `README.md`, `docs/quickstart.md`, and
`docs/production-audit-debugging.md` for administrator instructions.

## Quality Gates

Run:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Current gate status is updated during implementation validation.

## Latest Validation

- `uv run ruff check .`: passed
- `uv run ruff format --check .`: passed
- `uv run mypy src`: passed
- `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90`: 373 passed, coverage 90.43%
