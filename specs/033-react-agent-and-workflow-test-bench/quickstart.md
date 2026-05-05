# Quickstart: React Agent And Workflow Test Bench

## Goal

Validate the additive React test bench route for suite authoring, case authoring, safe run launch, run diagnostics, artifact metadata, publish-gate evidence, and redaction-safe browser evidence.

## Local Setup

```bash
cp specs/033-react-agent-and-workflow-test-bench/.env.qa033 .env
uv sync
cd frontend/admin
npm install
npm run build
cd ../..
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa033 && createdb -U postgres multi_agent_platform_qa033'
uv run alembic upgrade head
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa033 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
mkdir -p .data/qa033-artifacts output/playwright/qa033_ui
```

## Run The App

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
uv run python -m multi_agent_platform.workers.main
```

Open:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/test-bench
```

Use `tenant-admin-acme` for tenant suite/run flows and `platform-admin` for platform-visible evidence.

## Focused Validation

```bash
uv run pytest --no-cov \
  tests/unit/api/test_admin_test_bench_schema.py \
  tests/unit/admin/test_test_bench_react_service.py \
  tests/performance/test_bench/test_react_test_bench_queries.py \
  tests/contract/test_admin_react_contract.py \
  tests/integration/test_admin_react_routes.py
```

```bash
cd frontend/admin
npm run typecheck
npm run test
npm run build
cd ../..
```

```bash
uv run python scripts/frontend/generate_admin_react_types.py --check
```

## Full QA

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/033-react-agent-and-workflow-test-bench
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui-roadmap/033-react-agent-and-workflow-test-bench/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/033-react-agent-and-workflow-test-bench/validation.yml --start-processes
```

## Redaction Scan

```bash
rg -n "qa033-secret-value|raw prompt|raw completion|resolved credential|authorization header|provider token|private message|connector request|connector response|raw tool output|raw transcript|stack trace|/Users/|Globex" /tmp/qa033-* output/playwright/qa033_ui || true
```

Expected result: no unreviewed matches.
