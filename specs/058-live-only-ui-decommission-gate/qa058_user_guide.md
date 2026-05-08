# QA058 User Guide: Spec 058 - Live-Only UI Decommission Gate

## Detailed Overview

QA058 is the final live-only gate before the remaining user-facing terminology
cleanup. Its job is to prove the admin browser UI no longer relies on backend
deterministic demo rows for production route responses. The page can still show
computed migration metadata, empty states, denied states, unavailable states,
and one transitional bootstrap marker assigned to Spec 059.

The gate is intentionally strict. A production route that returns a fake
workflow, fake provider, fake prompt, fake package, fake audit reference, fake
artifact reference, fake run ID, fake usage event, fake delivery attempt, or
test fixture import must be blocking. Test fixtures and QA seed records remain
allowed only in documented test, QA, validation, or historical-spec locations.

## Who Should Use This Guide

- Manual QA reviewers validating the migration dashboard.
- Engineers confirming source and built-asset scanner behavior.
- Reviewers checking that tenant isolation and redaction are still intact.
- Release reviewers verifying that the remaining mapped marker belongs to Spec 059.
- Operators who need to understand why a fresh database may show empty states.

## Manual QA Prerequisites

1. Work from the repository root.
2. Use a local PostgreSQL container.
3. Use `.env.qa058`.
4. Do not use production credentials.
5. Do not make real provider, Telegram, connector, or outbound calls.
6. Keep screenshots under `output/playwright/qa058_ui`.
7. Keep temporary notes under `/tmp/qa058-*`.
8. Confirm the database name is `multi_agent_platform_qa058`.

## Step-by-Step Manual QA

### Step 1: Prepare Environment

```bash
cp specs/058-live-only-ui-decommission-gate/.env.qa058 .env
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa058 && createdb -U postgres multi_agent_platform_qa058'
uv run alembic upgrade head
```

Expected: the QA058 database is clean.

Expected: migrations complete without errors.

### Step 2: Seed Live Data

```bash
uv run python scripts/qa/seed_live_only_gate_qa058.py
```

Expected: output includes `Seeded QA058 live-only gate records`.

Expected: output includes `external_calls=0`.

### Step 3: Start The Server

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected: `http://127.0.0.1:8000/health/live` returns a healthy response.

### Step 4: Sign In

Open:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/migration
```

Expected: local login options are visible.

Choose `platform-admin`.

Expected: the browser redirects to `/admin/app/migration`.

### Step 5: Review The Gate

Find the panel named `Live-data guardrails`.

Expected: the panel eyebrow says `Live-only gate`.

Expected: blocking count is zero.

Expected: route targets are visible.

Expected: `qa058-live-only-source-scan` is visible.

Expected: the next step mentions Spec 059 for the transitional bootstrap marker.

### Step 6: Capture Evidence

Save a screenshot or run Playwright:

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/058-live-only-ui-decommission-gate/validation.yml --start-processes
```

Expected: screenshot path is `output/playwright/qa058_ui/qa058-live-data-ui-api-smoke.png`.

### Step 7: Verify Backend Evidence

```bash
uv run python scripts/qa/verify_live_only_gate_qa058.py
```

Expected: `blocking_findings=0`.

Expected: `missed_static_routes=0`.

Expected: `built_asset_blockers=0`.

Expected: `.data/qa058-artifacts/live-only-gate-report.json` exists.

### Step 8: Verify Tenant Isolation

```bash
status=$(curl --silent --output /tmp/qa058-user-cross-tenant.json --write-out '%{http_code}' \
  -H 'X-Local-Principal: tenant-admin-acme' \
  'http://127.0.0.1:8000/admin/app/migration/live-data-inventory.json?tenant_id=22222222-2222-2222-2222-222222222222')
printf '%s\n' "$status"
```

Expected: status is `403`.

Expected: the response file does not include `Globex`.

## Expected Results

- The migration dashboard loads for an authorized local principal.
- The live-only gate panel appears.
- Source scan evidence reports zero blocking findings.
- Route inventory reports zero missed static admin JSON routes.
- Built asset scan reports zero blocking findings.
- Test-only markers remain counted but are not production blockers.
- The remaining mapped marker is assigned to Spec 059.
- Cross-tenant requests fail closed.
- Screenshots contain no raw secrets or private data.
- QA artifacts use repository-relative paths.

## Evidence To Capture

- `/tmp/qa058-seed.log`
- `/tmp/qa058-verifier.log`
- `/tmp/qa058-live-data-source.json`
- `/tmp/qa058-live-data-projected.json`
- `/tmp/qa058-cross-tenant.json`
- `.data/qa058-artifacts/live-only-gate-report.json`
- `output/playwright/qa058_ui/qa058-live-data-ui-api-smoke.png`
- `.data/curl_test_runs/qa058-after-spec`

## Security And Redaction Checks

Confirm these strings are absent from browser text, JSON responses, logs, docs,
screenshots, and reports:

- raw prompt
- raw completion
- private message
- raw run payload
- raw tool payload
- raw test transcript
- provider authorization
- credential value
- `/Users/`
- stack trace
- unauthorized tenant label

Expected: none of these strings appear in QA058 evidence.

## Tenant Isolation Checks

Use `tenant-admin-acme` only with the Acme tenant ID:

```bash
curl --fail --silent -H 'X-Local-Principal: tenant-admin-acme' \
  'http://127.0.0.1:8000/admin/app/migration/live-data-inventory.json?tenant_id=11111111-1111-1111-1111-111111111111'
```

Expected: request succeeds.

Use `tenant-admin-acme` with the Globex tenant ID:

```bash
status=$(curl --silent --output /tmp/qa058-tenant-negative.json --write-out '%{http_code}' \
  -H 'X-Local-Principal: tenant-admin-acme' \
  'http://127.0.0.1:8000/admin/app/migration/live-data-inventory.json?tenant_id=22222222-2222-2222-2222-222222222222')
printf '%s\n' "$status"
```

Expected: request returns `403`.

Expected: response does not include `Globex`.

## Automated Commands

Run:

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/058-live-only-ui-decommission-gate
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/remove-mock-data-roadmap/058-live-only-ui-decommission-gate/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/058-live-only-ui-decommission-gate/validation.yml --start-processes
uv run python scripts/qa/verify_live_only_gate_qa058.py
uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa058-after-spec
```

Expected: every command exits successfully.

## Troubleshooting

- If login does not show local principals, recopy `.env.qa058`.
- If the database has old rows, rerun the QA058 reset command.
- If the source scan reports a blocker, inspect the `source_path` in the report.
- If route targets are missing, update route target inventory and tests.
- If built assets are stale, rebuild the frontend.
- If the screenshot is missing, inspect `/tmp/qa058-api.log`.
- If a tenant denial leaks a tenant label, stop and fix route authorization.
- If curl regression fails, inspect the first failed command in `.data/curl_test_runs/qa058-after-spec`.

## Related Files

- `specs/058-live-only-ui-decommission-gate/qa058.md`
- `specs/058-live-only-ui-decommission-gate/qa058_ui.md`
- `specs/058-live-only-ui-decommission-gate/.env.qa058`
- `specs/_autopilot/remove-mock-data-roadmap/058-live-only-ui-decommission-gate/validation.yml`
- `scripts/qa/seed_live_only_gate_qa058.py`
- `scripts/qa/verify_live_only_gate_qa058.py`
- `src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py`
- `frontend/admin/src/components/migrationHardening/LiveDataInventoryPanel.tsx`
