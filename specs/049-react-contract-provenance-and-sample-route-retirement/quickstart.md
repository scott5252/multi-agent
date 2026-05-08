# Quickstart: React Contract Provenance And Sample Route Retirement

## Setup

```bash
uv sync
cp specs/049-react-contract-provenance-and-sample-route-retirement/.env.qa049 .env
docker compose up -d postgres
uv run alembic upgrade head
```

## Focused Backend Validation

```bash
uv run pytest --no-cov \
  tests/unit/api/test_admin_react_schema.py \
  tests/contract/test_admin_react_contract.py \
  tests/integration/test_admin_react_routes.py \
  tests/unit/admin/test_live_data_inventory_scanner.py \
  -q
```

Expected:

- Shared provenance and empty-state schemas validate safe text.
- `/admin/app/patterns` and related sample JSON/action/export routes cannot return production sample data.
- Admin bootstrap/navigation/search omit sample patterns.
- Scanner checks do not report new unallowlisted production fixture defaults.

## Frontend Validation

```bash
uv run python scripts/frontend/generate_admin_react_types.py --check
cd frontend/admin
npm test -- --run src/App.test.tsx src/bootstrapContract.test.ts src/components src/hooks
npm run typecheck
npm run build
```

Expected:

- Generated contracts are up to date.
- Production React routing no longer imports or renders `PatternsPage`.
- Shared component tests still use test-only pattern fixtures.
- Built assets do not include retired sample route code or fixed QA action defaults introduced by this spec.

## Full Spec Validation

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh \
  specs/049-react-contract-provenance-and-sample-route-retirement

uv run python scripts/qa/run_spec_qa.py \
  specs/_autopilot/remove-mock-data-roadmap/049-react-contract-provenance-and-sample-route-retirement/validation.yml

uv run python scripts/qa/run_playwright_ui.py \
  specs/_autopilot/remove-mock-data-roadmap/049-react-contract-provenance-and-sample-route-retirement/validation.yml \
  --start-processes

uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py \
  --output-dir .data/curl_test_runs/qa049-after-spec
```

## Manual Review

1. Open `/auth/local-login?redirect_to=/admin/app/migration`.
2. Sign in as `platform-admin`.
3. Confirm the migration page shows live-data inventory/provenance evidence.
4. Confirm `/admin/app/patterns` is not available as a production sample data route.
5. Confirm screenshots and route responses contain no raw secrets, local paths, stack traces, or unauthorized tenant labels.
