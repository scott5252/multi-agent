# Testing Instructions: Token Usage And Cost Analytics

## Focused Tests

```bash
uv run pytest --no-cov \
  tests/unit/model_providers/test_usage.py \
  tests/unit/usage \
  tests/unit/db/test_usage_models.py \
  tests/unit/db/test_usage_repository.py \
  tests/unit/auth/test_usage_policy.py \
  tests/unit/api/test_usage_schemas.py \
  tests/unit/api/test_usage_ui_models.py \
  tests/contract/test_usage_analytics_contract.py \
  tests/integration/db/test_usage_migration.py \
  tests/integration/model_providers/test_gateway_usage_capture.py \
  tests/integration/api/test_admin_usage_api.py \
  tests/integration/api/test_admin_usage_ui.py \
  tests/docs/test_usage_analytics_docs.py
```

## Full Quality Gate

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

## Manual Browser Validation

Use `specs/016-token-usage-cost-analytics/qa016_ui.md`.

## Manual API Validation

Use `specs/016-token-usage-cost-analytics/qa016.md`.
