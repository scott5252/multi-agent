# Reliability Scale Hardening Testing

Run focused reliability checks:

```bash
uv run pytest tests/unit/reliability tests/unit/storage/test_throughput.py
```

Run contract and API checks:

```bash
uv run pytest tests/contract/test_reliability_controls_contract.py
uv run pytest tests/integration/api/test_reliability_controls_api.py
```

Run quality gates:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Acceptance evidence should include load handling, worker interruption recovery,
duplicate suppression, retry stop conditions, breaker transitions, compensation
outcomes, quotas, fairness, authorization failures, audit records, partial
inspection data, and README checks.

## Latest Local Results

- `uv run ruff check .`: PASS
- `uv run ruff format --check .`: PASS
- `uv run mypy src`: PASS
- Focused reliability smoke suite: PASS, 44 passed
- Full coverage command: PASS, 430 passed, coverage 90.18 percent

Note: the full test run emits one SQLAlchemy warning from metadata sorting due
to existing mutually dependent workflow draft tables.
