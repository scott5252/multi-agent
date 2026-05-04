# Quickstart: Live Model Credential Resolution For Gateway Calls

## Environment Setup

Run from the repository root.

```bash
test ! -f .env || test -f .env.autopilot-backup || cp .env .env.autopilot-backup
cp specs/025-live-model-credential-resolution-for-gateway-calls/.env.qa025 .env
uv sync
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa025 && createdb -U postgres multi_agent_platform_qa025'
uv run alembic upgrade head
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa025 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
```

## Start Services

Terminal A:

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Terminal B:

```bash
uv run python -m multi_agent_platform.workers.main
```

## Browser Flow

Open:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/model-providers
```

Choose `platform-admin`.

Create or edit an OpenAI provider connection:

- Provider type: `openai`
- Display name: `QA025 OpenAI`
- Models: `gpt-test`
- Credential secret references: `qa025/openai-placeholder`
- Active: enabled

Run the provider test.

Expected:

- The test records either success from the mocked adapter path or a safe normalized provider failure from the local test harness.
- The page never displays the fake raw credential value from `.env.qa025`.
- The credential field shows only `qa025/openai-placeholder`.

Create a local OpenAI-compatible provider connection:

- Provider type: `local_openai_compatible`
- Base URL: `http://localhost:11434`
- Models: `local-test`
- Credential secret references: leave empty
- Active: enabled

Expected:

- Validation allows the no-auth local provider because the endpoint is allowlisted.
- Credential resolution does not require a reference for this local no-auth case.

## Focused Tests

```bash
uv run pytest --no-cov \
  tests/unit/model_providers/test_secret_references.py \
  tests/unit/model_providers/test_probes.py \
  tests/unit/model_providers/test_gateway.py \
  tests/unit/model_providers/test_adapters.py \
  tests/unit/model_providers/test_validation.py \
  tests/unit/api/test_model_provider_schemas.py \
  tests/unit/bootstrap/test_container_model_gateway_factories.py \
  tests/integration/model_providers/test_gateway_attempt_evidence.py \
  tests/integration/runtime/test_gateway_operation_recovery.py
```

## QA Validation Scripts

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/025-live-model-credential-resolution-for-gateway-calls/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/025-live-model-credential-resolution-for-gateway-calls/validation.yml --start-processes
```

## Full Quality Gates

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

## Redaction Checks

Search for fake raw credential values after tests, excluding the QA env file and
test fixture source where the values are intentionally defined:

```bash
rg "qa025-(openai|local)-secret-value" \
  README.md docs src .data output /tmp/qa025-api.log /tmp/qa025-worker.log
```

Expected:

- No raw secret value appears in application docs, persisted evidence, screenshots, logs, or artifacts.
- `.env.qa025` and targeted test fixtures may contain fake values when explicitly asserting redaction behavior.
