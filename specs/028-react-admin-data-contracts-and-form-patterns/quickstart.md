# Quickstart: React Admin Data Contracts And Form Patterns

## Purpose

Use this quickstart to validate the shared React admin page envelope, form
patterns, table/filter/export helpers, and harmless sample patterns page.

## Setup

```bash
cp specs/028-react-admin-data-contracts-and-form-patterns/.env.qa028 .env
uv sync
cd frontend/admin
npm install
npm run build
cd ../..
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa028 && createdb -U postgres multi_agent_platform_qa028'
uv run alembic upgrade head
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa028 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
```

## Run The App

```bash
uv run uvicorn multi_agent_platform.api.main:app --reload
```

```bash
uv run python -m multi_agent_platform.workers.main
```

Open:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/patterns
```

Sign in as `tenant-admin-acme`.

## Focused Backend Validation

```bash
uv run pytest --no-cov \
  tests/unit/api/test_admin_patterns_schema.py \
  tests/contract/test_admin_react_contract.py \
  tests/integration/test_admin_react_routes.py
```

## Focused Frontend Validation

```bash
cd frontend/admin
npm run typecheck
npm run test
npm run build
cd ../..
uv run python scripts/frontend/generate_admin_react_types.py --check
```

## Manual Checks

- Open `/admin/app/patterns`.
- Confirm the page title includes `Forms`.
- Confirm the active scope is `Acme`.
- Confirm sample records render in a bounded table.
- Apply an allowed filter and confirm a safe filter chip appears.
- Submit the sample form with a blank required field and confirm field validation maps to the form.
- Submit the sample form with a stale revision token and confirm recovery guidance appears.
- Submit the sample form with confirmation enabled and confirm a safe confirmation state appears.
- Request the sample export and confirm an export snapshot appears without a local filesystem path.
- Confirm no raw secrets, prompts, completions, memory, provider payloads, tool payloads, stack traces, or Globex labels appear.

## Full QA Commands

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/028-react-admin-data-contracts-and-form-patterns
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui-roadmap/028-react-admin-data-contracts-and-form-patterns/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/028-react-admin-data-contracts-and-form-patterns/validation.yml --start-processes
```
