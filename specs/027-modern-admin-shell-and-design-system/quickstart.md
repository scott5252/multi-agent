# Quickstart: Modern Admin Shell And Design System

## Setup

```bash
test ! -f .env || test -f .env.autopilot-backup || cp .env .env.autopilot-backup
cp specs/027-modern-admin-shell-and-design-system/.env.qa027 .env
uv sync
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa027 && createdb -U postgres multi_agent_platform_qa027'
uv run alembic upgrade head
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa027 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
mkdir -p .data/qa027-artifacts output/playwright/qa027_ui
```

## Build React Assets

```bash
cd frontend/admin
npm install
npm run build
cd ../..
```

## Start Services

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Optional worker:

```bash
uv run python -m multi_agent_platform.workers.main
```

## Browser Smoke

Open:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app
```

Sign in as `tenant-admin-acme`.

Expected:

- The React admin shell shows active tenant scope.
- Desktop navigation is grouped and readable.
- Breadcrumbs and safe page actions are visible.
- The shell links to existing Jinja admin destinations.
- No raw secrets, prompts, completions, memory contents, private channel text,
  provider payloads, tool payloads, or stack traces are rendered.

## Focused Validation

```bash
uv run pytest --no-cov \
  tests/unit/api/test_admin_react_schema.py \
  tests/contract/test_admin_react_contract.py \
  tests/integration/test_admin_react_routes.py
cd frontend/admin
npm run typecheck
npm run test
npm run build
cd ../..
uv run python scripts/frontend/generate_admin_react_types.py --check
```

## Mandatory Validation

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/027-modern-admin-shell-and-design-system
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui-roadmap/027-modern-admin-shell-and-design-system/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/027-modern-admin-shell-and-design-system/validation.yml --start-processes
```
