# Quickstart: Jinja Surface Inventory And Deletion Plan

## Setup

```bash
uv sync
cp specs/038-jinja-surface-inventory-and-deletion-plan/.env.qa038 .env
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa038 && createdb -U postgres multi_agent_platform_qa038'
uv run alembic upgrade head
```

## Generate Contracts

```bash
uv run python scripts/frontend/generate_admin_react_types.py
```

## Run Focused Backend Checks

```bash
uv run pytest tests/unit/admin/test_jinja_inventory_scanner.py \
  tests/unit/api/test_admin_migration_hardening_react_schema.py \
  tests/contract/test_admin_migration_jinja_inventory_contract.py \
  tests/integration/api/test_admin_react_migration_inventory_routes.py
```

## Run Focused Frontend Checks

```bash
cd frontend/admin
npm test -- --run src/components/migrationHardening/JinjaInventoryPanel.test.tsx \
  src/components/migrationHardening/MigrationHardeningPage.test.tsx
```

## Manual Browser Review

1. Start the API with `AUTH_MODE=local_principal`.
2. Open `/auth/local-login`.
3. Sign in as platform admin and open `/admin/app/migration`.
4. Confirm "Jinja surface inventory" shows template, route, static asset, direct-link, blocked, and safe-to-delete counts.
5. Confirm all paths are repo-relative and no raw secrets, local filesystem absolute paths, stack traces, raw prompts, raw run payloads, or unauthorized tenant labels appear.
6. Switch to tenant-admin Acme and verify tenant-safe inventory projection does not expose platform-only unauthorized data.

## Full Validation

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/038-jinja-surface-inventory-and-deletion-plan
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui2-roadmap/038-jinja-surface-inventory-and-deletion-plan/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui2-roadmap/038-jinja-surface-inventory-and-deletion-plan/validation.yml --start-processes
```
