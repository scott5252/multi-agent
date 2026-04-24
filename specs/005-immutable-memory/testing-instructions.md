# Testing Instructions: Immutable Versioned Memory

## Automated Checks

Run the focused memory suite:

```bash
uv run pytest --no-cov tests/unit/memory tests/unit/db/test_memory_models.py \
  tests/contract/test_memory_contract.py tests/integration/db/test_memory_migration.py \
  tests/integration/runtime/test_runtime_memory_flows.py \
  tests/integration/api/test_memory_api.py tests/performance/memory/test_memory_latency.py -q
```

Run quality gates:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

## Manual QA

Use
[qa005.md](/Users/scottcornell/src/my-projects/multi-agent/specs/005-immutable-memory/qa005.md),
[.env.qa005](/Users/scottcornell/src/my-projects/multi-agent/specs/005-immutable-memory/.env.qa005),
and
[qa005_collection.json](/Users/scottcornell/src/my-projects/multi-agent/specs/005-immutable-memory/qa005_collection.json).

Validate:

- initial write creates version sequence `1`
- successor write links to the prior head
- stale writes return `409 stale_expected_head`
- current-head reads return `has_memory: true` for populated scopes and
  `has_memory: false` for missing scopes
- history lists versions newest-first
- replay returns the exact target snapshot
- diff reports additions, removals, and changes
- audit responses contain ids, hashes, action/outcome, and redacted summaries,
  but no raw memory content
- cross-tenant reads fail closed
- runtime writes persist run, step, bundle, digest, and lineage ids
