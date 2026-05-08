# QA056 UI: Usage React Live Data

## Goal

Guide a reviewer through browser evidence for qa056.

Expected: the React usage workspace loads live backend records.

Expected: the browser shows seeded Acme usage rows only after the QA seed
command persists them.

Expected: the reviewer can click `Export CSV` and see a completed safe artifact
reference.

Expected: the post-UI verifier proves a new completed export row exists in the
qa056 database after the browser action.

Expected: the browser never displays raw prompts, raw completions,
authorization headers, memory payloads, credential values, local file paths,
storage file URIs, stack traces, or unauthorized tenant usage rows.

What is happening: the page is using `/admin/app/usage/bootstrap.json`,
`/admin/app/usage/events.json`, and `/admin/app/usage/exports` rather than fixed
production helper rows.

Why this matters: qa056 is only done if browser-visible usage analytics are
backed by the same database rows the API and verifier inspect.

## How To Use This Guide

Use this walkthrough with `qa056.md`.

Save screenshots under `output/playwright/qa056_ui`.

Save reviewer notes under `/tmp/qa056-ui-reviewer-notes.txt`.

Save browser console notes under `/tmp/qa056-ui-console-notes.txt`.

Save post-action API notes under `/tmp/qa056-ui-post-api-notes.txt`.

Save verifier output under `/tmp/qa056-ui-verifier-output.txt`.

Expected: screenshot filenames include qa056.

Expected: notes mention the local principal and tenant being reviewed.

Expected: API notes identify the export by `usage-export:UUID` only.

Expected: reviewer notes avoid copying unsafe payload content.

What is happening: automated Playwright follows the same flow as this manual
walkthrough.

Why this matters: manual evidence and automated evidence should match.

## Environment Setup

Copy the QA environment.

```bash
cp specs/056-usage-react-live-data/.env.qa056 .env
```

Expected: `.env` now contains `APP_NAME=multi-agent-platform-qa056`.

Install dependencies.

```bash
uv sync
```

Expected: dependencies are available.

Start PostgreSQL.

```bash
docker compose up -d postgres
```

Expected: the local PostgreSQL service is running.

Reset the qa056 database.

```bash
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa056 && createdb -U postgres multi_agent_platform_qa056'
```

Expected: only the qa056 database is recreated.

Run migrations.

```bash
uv run alembic upgrade head
```

Expected: migrations complete successfully.

Seed tenants.

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa056 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
```

Expected: Acme and Globex exist.

Seed usage records.

```bash
uv run python scripts/qa/seed_usage_qa056.py
```

Expected: the command prints `Seeded QA056 usage live records`.

Create output directories.

```bash
mkdir -p output/playwright/qa056_ui .data/qa056-artifacts
```

Expected: screenshot and artifact directories exist.

Start the app.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected: `http://127.0.0.1:8000/health/live` returns healthy.

Start the worker in another terminal for full evidence.

```bash
uv run python -m multi_agent_platform.workers.main
```

Expected: the worker starts in local QA mode.

## Browser Walkthrough

1. Open the local login page.

URL: `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/usage?tenant_id=11111111-1111-1111-1111-111111111111`

Action: choose `tenant-admin-acme`.

Expected: the browser redirects to the Usage workspace.

What is happening: the local principal cookie scopes the browser session to the
Acme tenant admin.

Why this matters: the usage page must honor the same tenant scope as the API
route tests.

2. Review the page header.

URL: `http://127.0.0.1:8000/admin/app/usage?tenant_id=11111111-1111-1111-1111-111111111111`

Action: look for the usage header and timestamp.

Expected: the page title is `Usage and Cost Analytics`.

Expected: the header shows `Acme` and `Last 30 days`.

What is happening: the React page loaded `/admin/app/usage/bootstrap.json` and
rendered the backend-owned dashboard contract.

Why this matters: a missing title or wrong tenant label usually means the page
is not reading the live usage route.

3. Review summary cards.

Action: inspect Total tokens, Estimated cost, Usage events, Average latency,
Unavailable usage, and Confidence coverage cards.

Expected: Total tokens shows `1,860`.

Expected: Usage events shows `2`.

Expected: Estimated cost is derived from persisted pricing and shows a small
USD value.

Expected: Confidence coverage separates confirmed and estimated values.

What is happening: the backend computed summary cards from `llm_usage_events`
and pricing metadata.

Why this matters: deterministic fixed totals would not prove live usage
capture.

4. Review the filter bar.

Action: inspect group selector, tenant chip, provider chip, and model chip.

Expected: Tenant shows Acme or the active tenant scope.

Expected: Provider and Model chips reflect the seeded events or `All`.

Expected: group options include Provider, Model, Workflow, Agent, Prompt,
Gateway Operation, Physical Attempt, and Governed Tool where authorized.

What is happening: options are built from visible live usage events.

Why this matters: filter metadata must not be a static list copied from QA035.

5. Review rollups.

Action: use the group selector to choose Provider.

Expected: rows include `openai` and `local-compatible`.

Expected: tokens and event counts match the seeded data.

Expected: confidence labels include confirmed or reconciliation-pending states.

What is happening: the browser requests a refreshed dashboard with
`group_by=provider`.

Why this matters: rollups must be computed from current visible events.

6. Open a drilldown.

Action: click a rollup row `View` button.

Expected: the Safe events table refreshes.

Expected: safe rows show Acme, provider, model, workflow label, token count,
latency, and audit reference.

Expected: at least one row shows `Usage export metadata lookup`.

What is happening: the browser calls `/admin/app/usage/events.json` for the
selected rollup key.

Why this matters: drilldowns must be bounded and redaction-safe while still
showing useful attribution.

7. Review missing pricing state.

Action: inspect the state panels and event cost column.

Expected: a missing pricing or reconciliation-pending state is visible.

Expected: the partial local event shows missing pricing truthfully.

What is happening: one seeded row intentionally lacks pricing metadata.

Why this matters: the UI must not fabricate costs when evidence is absent.

8. Create a usage export.

Action: click `Export CSV` in the header.

Expected: the Export panel status becomes `completed`.

Expected: Rows shows `2`.

Expected: Artifact starts with `usage-export:`.

Expected: Checksum starts with `sha256:`.

What is happening: the browser posts to `/admin/app/usage/exports` and the
backend stores a CSV artifact through the configured storage provider.

Why this matters: this is the required write-through action for qa056.

9. Capture a screenshot.

Action: save a screenshot as `output/playwright/qa056_ui/qa056-live-data-ui-api-smoke.png`.

Expected: the screenshot includes the header, summary cards, rollup table,
drilldown table, and export panel.

What is happening: the screenshot documents the browser-visible live state.

Why this matters: the screenshot is the human-reviewable UI artifact.

10. Verify persistence after the browser action.

```bash
uv run python scripts/qa/verify_usage_qa056.py | tee /tmp/qa056-ui-verifier-output.txt
```

Expected: the verifier prints `Verified QA056 usage live-data persistence`.

Expected: the verifier prints `browser_export_reference=usage-export:`.

What is happening: the verifier reads `usage_export_requests` after the browser
click.

Why this matters: the UI action must have persisted backend evidence.

11. Switch to Globex.

URL: `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/usage?tenant_id=22222222-2222-2222-2222-222222222222`

Action: choose `tenant-admin-globex`.

Expected: the page shows `No usage events`.

Expected: it does not show Acme workflow labels, Acme traces, or Acme export
references.

What is happening: the shell changes to the Globex tenant scope.

Why this matters: empty tenant state proves isolation and prevents fixture-like
fallback data.

12. Review redaction in the browser.

Action: search visible page text for unsafe words.

Expected: the page does not show `raw prompt`.

Expected: the page does not show `raw completion`.

Expected: the page does not show `authorization header`.

Expected: the page does not show `credential value`.

Expected: the page does not show `file:`.

What is happening: the backend exposes safe summaries and artifact references.

Why this matters: usage analytics must be useful without leaking sensitive
model, credential, or storage details.

## Required Automated Evidence

Run focused frontend usage tests.

```bash
npm run --prefix frontend/admin test -- --run Usage
```

Expected: all usage component tests pass.

Run frontend typecheck.

```bash
npm run --prefix frontend/admin typecheck
```

Expected: TypeScript typecheck passes.

Run generated contract check.

```bash
uv run python scripts/frontend/generate_admin_react_types.py --check
```

Expected: generated React admin API types are current.

Run focused backend tests.

```bash
uv run pytest --no-cov tests/unit/admin/usage/test_react_usage_service.py tests/unit/api/test_admin_usage_react_schema.py tests/unit/db/test_usage_repository.py tests/performance/usage/test_react_usage_queries.py tests/integration/test_admin_react_routes.py tests/unit/admin/test_live_data_inventory_scanner.py -k 'usage or react_admin_usage or live_data_inventory' -q
```

Expected: focused backend tests pass.

Run project quality checks.

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected: project quality checks pass.

Run automated Playwright validation.

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/056-usage-react-live-data/validation.yml --start-processes
```

Expected: Playwright signs in, loads usage analytics, clicks export, verifies a
safe export reference, and saves a screenshot.

## UI Evidence Checklist

- Screenshot file: `output/playwright/qa056_ui/qa056-live-data-ui-api-smoke.png`
- Reviewer notes: `/tmp/qa056-ui-reviewer-notes.txt`
- Console notes: `/tmp/qa056-ui-console-notes.txt`
- Post-action API notes: `/tmp/qa056-ui-post-api-notes.txt`
- Verifier output: `/tmp/qa056-ui-verifier-output.txt`
- Principal used for seeded action: `tenant-admin-acme`
- Tenant ID used for seeded action: `11111111-1111-1111-1111-111111111111`
- Principal used for empty tenant check: `tenant-admin-globex`
- Tenant ID used for empty tenant check: `22222222-2222-2222-2222-222222222222`
- Export evidence format: `usage-export:UUID`

Expected: every evidence file uses qa056 naming.

Expected: no evidence file copies raw prompts, completions, secrets, file URIs,
or local filesystem paths.

## Acceptance Notes Template

Use this template in `/tmp/qa056-ui-acceptance-notes.txt`.

```text
QA056 UI acceptance notes
Reviewer:
Date:
Browser:
Principal used:
Seed command passed:
Usage page loaded:
Summary token total:
Rollup inspected:
Drilldown inspected:
Export button clicked:
Export artifact reference:
Screenshot path:
Verifier output path:
Redaction issues:
Tenant isolation result:
Decision:
```

Expected: the artifact reference is safe and starts with `usage-export:`.

Expected: the decision records pass, fail, or blocked with a safe reason.

## Troubleshooting

If the page stays on loading, check the API process logs.

```bash
curl --fail --silent http://127.0.0.1:8000/health/live
```

Expected: health returns success.

If the page shows no Acme usage, rerun the seed script.

```bash
uv run python scripts/qa/seed_usage_qa056.py
```

Expected: the seed prints two usage events.

If the export button does not update, inspect the export route.

```bash
curl --fail --silent -H 'X-Local-Principal: tenant-admin-acme' -H 'Content-Type: application/json' -d '{"filters":{"tenant_id":"11111111-1111-1111-1111-111111111111"},"requested_group_by":"provider","idempotency_key":"qa056-ui-troubleshoot"}' 'http://127.0.0.1:8000/admin/app/usage/exports?tenant_id=11111111-1111-1111-1111-111111111111'
```

Expected: the response status is `completed`.

If the verifier fails, confirm a non-seeded export exists.

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa056 -c "SELECT usage_export_request_id, status, row_count FROM usage_export_requests ORDER BY created_at DESC LIMIT 5;"
```

Expected: at least one completed export has an ID other than the seeded qa056
export ID.

If Globex shows Acme usage, stop validation.

Expected: cross-tenant data leakage is a blocker.

If unsafe text appears in the page, save the screenshot and stop validation.

Expected: redaction failures are blockers.

## Related Files

- `specs/056-usage-react-live-data/qa056.md`
- `specs/056-usage-react-live-data/qa056_user_guide.md`
- `specs/056-usage-react-live-data/.env.qa056`
- `scripts/qa/seed_usage_qa056.py`
- `scripts/qa/verify_usage_qa056.py`
- `specs/_autopilot/remove-mock-data-roadmap/056-usage-react-live-data/validation.yml`
- `src/multi_agent_platform/admin/usage/react_usage.py`
- `src/multi_agent_platform/api/routers/admin_react.py`
- `frontend/admin/src/components/usage/UsagePage.tsx`
