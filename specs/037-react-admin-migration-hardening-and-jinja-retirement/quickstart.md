# Quickstart: React Admin Migration Hardening And Jinja Retirement

## Local QA Setup

```bash
test ! -f .env || test -f .env.autopilot-backup || cp .env .env.autopilot-backup
cp specs/037-react-admin-migration-hardening-and-jinja-retirement/.env.qa037 .env
uv sync
cd frontend/admin && npm install && npm run build && cd ../..
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa037 && createdb -U postgres multi_agent_platform_qa037'
uv run alembic upgrade head
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa037 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
mkdir -p .data/qa037-artifacts output/playwright/qa037_ui
```

## Start Processes

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

```bash
uv run python -m multi_agent_platform.workers.main
```

## Browser Routes

- `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app`
- `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/migration`
- `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/migration?tenant_id=11111111-1111-1111-1111-111111111111`

## Focused Checks

```bash
uv run python scripts/frontend/generate_admin_react_types.py --check
uv run pytest --no-cov tests/unit/api/test_admin_migration_hardening_react_schema.py tests/unit/admin/test_migration_hardening_service.py tests/performance/migration_hardening/test_react_migration_hardening_queries.py tests/contract/test_admin_react_contract.py tests/integration/test_admin_react_routes.py
cd frontend/admin && npm run typecheck && npm run test && npm run build && cd ../..
```

## Full QA

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/037-react-admin-migration-hardening-and-jinja-retirement
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui-roadmap/037-react-admin-migration-hardening-and-jinja-retirement/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/037-react-admin-migration-hardening-and-jinja-retirement/validation.yml --start-processes
```

## Acceptance Notes

- Verify `/admin/app` renders migration hardening evidence.
- Verify platform admin sees full parity matrix.
- Verify tenant-admin Acme does not receive unauthorized Globex-only route evidence.
- Verify rollback plan is visible and does not contain private paths or production values.
- Verify redaction and tenant isolation sweeps report zero unsafe matches.
