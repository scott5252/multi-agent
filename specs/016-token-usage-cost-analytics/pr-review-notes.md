# PR Review Notes: Token Usage And Cost Analytics

## Scope

- Adds normalized usage analytics storage, repository, pricing, export, and
  capture services.
- Extends ModelGateway usage metadata and records safe usage events through an
  optional recorder wired by the application container.
- Adds `/admin/usage` server-rendered dashboard plus JSON summary, event, and
  export APIs.
- Adds authorization surfaces and local-principal usage permissions.
- Adds QA016 docs, README, quickstart, contract, and focused tests.

## Security Review Points

- Verify usage records and CSV exports contain safe identifiers, token counts,
  cost estimates, latency, status, and version references only.
- Verify no raw prompts, completions, secrets, memory content, provider
  credentials, Authorization headers, or unauthorized run content are stored.
- Verify tenant admins cannot query or export another tenant's rows.
- Verify platform-wide visibility remains platform-admin-only.

## Data Review Points

- Migration is additive and creates `llm_usage_events`, `llm_usage_rollups`,
  `llm_pricing_versions`, `usage_export_requests`, and
  `usage_reconciliation_records`.
- Query-time rollups are used for MVP; the rollup table is reserved for future
  materialization.
- Pricing estimates use internal versioned pricing metadata.

## Validation Evidence

Run:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Focused QA:

```bash
uv run pytest --no-cov tests/unit/usage tests/integration/api/test_admin_usage_api.py tests/integration/api/test_admin_usage_ui.py
```
