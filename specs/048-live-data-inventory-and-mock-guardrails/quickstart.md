# Quickstart: Live Data Inventory And Mock Guardrails

## 1. Prepare QA Environment

```bash
test ! -f .env || cp .env .env.autopilot-backup
cp specs/048-live-data-inventory-and-mock-guardrails/.env.qa048 .env
uv sync
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa048 && createdb -U postgres multi_agent_platform_qa048'
uv run alembic upgrade head
```

Expected: QA database `multi_agent_platform_qa048` is available with local-principal auth and filesystem artifacts under `.data/qa048-artifacts`.

## 2. Run Focused Scanner And Route Tests

```bash
uv run pytest --no-cov \
  tests/unit/admin/test_live_data_inventory_scanner.py \
  tests/integration/api/test_admin_live_data_inventory_routes.py \
  tests/contract/test_admin_live_data_inventory_contract.py -q
```

Expected: scanner taxonomy, route authorization, Auth0-shaped principal behavior, local-principal behavior, and contract shape pass without unsafe strings.

## 3. Check Generated Contracts

```bash
uv run python scripts/frontend/generate_admin_react_types.py --check
```

Expected: generated TypeScript contracts are current.

## 4. Check Frontend Migration Evidence

```bash
cd frontend/admin
npm test -- --run src/components/migrationHardening src/App.test.tsx
npm run typecheck
npm run build
cd ../..
```

Expected: migration hardening UI renders live-data inventory evidence and the production bundle does not include new unallowlisted fixture markers.

## 5. Run Quality Gates

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected: all quality gates pass.

## 6. Run Spec Validation

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/048-live-data-inventory-and-mock-guardrails
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/remove-mock-data-roadmap/048-live-data-inventory-and-mock-guardrails/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/048-live-data-inventory-and-mock-guardrails/validation.yml --start-processes
```

Expected: QA docs, API/database/quality validation, and Playwright UI validation pass and produce evidence under `.data/qa048-artifacts` and `output/playwright/qa048_ui`.

## 7. Run Post-Spec Curl Test

```bash
uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa048-after-spec
```

Expected: full curl walkthrough passes against the dedicated `multi_agent_curl_test` database.
