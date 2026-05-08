# QA056 User Guide: Spec 056 - Usage React Live Data

## Detailed Overview

This guide explains how to review the qa056 usage analytics feature.

The feature changes the admin Usage page so it reads live platform data.

The page no longer depends on fixed QA035 usage events in production code.

The page now asks the backend for usage totals, trend data, rollups,
drilldowns, and export evidence.

The backend reads persisted rows from `llm_usage_events`.

The backend reads pricing evidence from `llm_pricing_versions`.

The backend reads export evidence from `usage_export_requests`.

The backend reads tenant display labels from the tenant table.

The UI shows summary cards for token totals, estimated cost, event counts,
latency, unavailable usage, and confidence coverage.

The UI shows a trend chart based on the selected date range.

The UI shows rollups by tenant, provider, model, workflow, agent, prompt,
execution mode, gateway operation, physical attempt, and governed tool.

The UI shows a safe event drilldown table.

The UI shows export status and artifact evidence.

The UI can create a new export through the backend.

The export action should create a database row.

The export action should return a safe artifact reference.

The export action should not expose local file paths.

The export action should not expose storage provider URLs.

The feature intentionally keeps confidence labels visible.

Some usage may be confirmed.

Some usage may be estimated.

Some usage may be partial.

Some usage may have missing pricing.

Some usage may be unavailable.

These states are expected and helpful.

The UI should not hide missing data by inventing totals or costs.

The qa056 seed creates Acme usage evidence.

The qa056 seed leaves Globex empty.

The empty Globex state is important.

It proves the page does not borrow data from another tenant.

It also proves the page does not fall back to fixed sample rows.

The manual review should confirm both seeded and empty behavior.

The automated Playwright review should click the export button.

The post-UI verifier should confirm the export exists in the database.

The curl regression should run after the spec-specific checks.

## Who Should Use This Guide

Use this guide if you are doing manual QA for qa056.

Use this guide if you need to understand what the Usage page is supposed to do.

Use this guide if you are reviewing screenshots or API evidence.

Use this guide if you need to distinguish an expected empty state from a bug.

Use this guide if you need to verify tenant isolation.

Use this guide if you need to verify redaction.

You do not need to understand the implementation code to follow the guide.

You do need access to the local repository.

You do need Docker available for PostgreSQL.

You do need the local Python and Node dependencies installed through the repo
commands.

You should save notes while testing.

You should save screenshots while testing.

You should stop if you find secret leakage.

You should stop if Globex can see Acme usage.

You should stop if the export action does not persist evidence.

## Manual QA Prerequisites

Run commands from the repository root.

Use the qa056 environment file.

```bash
cp specs/056-usage-react-live-data/.env.qa056 .env
```

Expected: `.env` now points at `multi_agent_platform_qa056`.

Install dependencies.

```bash
uv sync
```

Expected: dependencies are available.

Start PostgreSQL.

```bash
docker compose up -d postgres
```

Expected: PostgreSQL is running.

Reset the QA database.

```bash
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa056 && createdb -U postgres multi_agent_platform_qa056'
```

Expected: only the qa056 database is reset.

Run migrations.

```bash
uv run alembic upgrade head
```

Expected: database tables exist.

Seed tenants.

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa056 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
```

Expected: Acme and Globex are present.

Seed usage data.

```bash
uv run python scripts/qa/seed_usage_qa056.py
```

Expected: the command prints `Seeded QA056 usage live records`.

Start the API.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected: the local app is available at `http://127.0.0.1:8000`.

Start the worker in another terminal when collecting final evidence.

```bash
uv run python -m multi_agent_platform.workers.main
```

Expected: the worker starts in local QA mode.

Open the local login page.

Use `http://127.0.0.1:8000/auth/local-login`.

Expected: local principal options are visible.

## Step-by-Step Manual QA

Step 1: sign in as `tenant-admin-acme`.

Use this URL:

`http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/usage?tenant_id=11111111-1111-1111-1111-111111111111`

Expected: the browser redirects to the Usage page.

Step 2: confirm the page title.

Expected: the title says `Usage and Cost Analytics`.

Step 3: confirm the tenant.

Expected: the active tenant is Acme.

Step 4: confirm the date range.

Expected: the selected range is `Last 30 days`.

Step 5: inspect the summary cards.

Expected: Total tokens is `1,860`.

Expected: Usage events is `2`.

Expected: Estimated cost is present.

Expected: Confidence coverage is present.

Step 6: inspect the state panel.

Expected: missing pricing or reconciliation-pending information is visible.

Step 7: inspect the trend section.

Expected: the trend has points for the selected window.

Expected: seeded event days have event counts.

Step 8: inspect the rollup section.

Expected: provider or tenant rows are visible.

Expected: row totals match the two seeded events.

Step 9: change the rollup group.

Select Provider if available.

Expected: `openai` and `local-compatible` are visible.

Step 10: open a drilldown.

Click a `View` button on a rollup row.

Expected: the Safe events table updates.

Expected: event rows show Acme only.

Expected: event rows show safe provider, model, workflow, and audit references.

Step 11: review governed tool attribution.

Expected: at least one row mentions `Usage export metadata lookup`.

Step 12: create an export.

Click `Export CSV`.

Expected: the export panel status becomes `completed`.

Expected: the export panel shows row count `2`.

Expected: the export panel shows an artifact reference that starts with
`usage-export:`.

Expected: the export panel shows a checksum prefix.

Step 13: save a screenshot.

Save it as `output/playwright/qa056_ui/qa056-manual-usage-page.png`.

Expected: the screenshot includes the summary, rollup, drilldown, and export
panel.

Step 14: run the verifier.

```bash
uv run python scripts/qa/verify_usage_qa056.py
```

Expected: the verifier prints `Verified QA056 usage live-data persistence`.

Step 15: sign in as `tenant-admin-globex`.

Use this URL:

`http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/usage?tenant_id=22222222-2222-2222-2222-222222222222`

Expected: the page shows an empty usage state.

Step 16: inspect Globex page text.

Expected: it says `No usage events`.

Expected: it does not show Acme workflow labels.

Expected: it does not show Acme trace references.

Expected: it does not show Acme export references.

Step 17: return to Acme if needed.

Expected: Acme still shows the seeded usage rows.

## Expected Results

Acme should show two usage events.

Acme should show `1,860` total tokens.

Acme should show at least one completed export.

Acme should show a safe `usage-export:` artifact reference.

Acme should show safe workflow and tool attribution.

Acme should show missing pricing or reconciliation-pending state.

Globex should show no usage events.

Globex should not show Acme rows.

Globex should not show Acme export references.

The export action should persist a new database row.

The post-UI verifier should pass after the export action.

The browser should not show raw secrets.

The browser should not show raw prompts.

The browser should not show raw completions.

The browser should not show storage file URIs.

The browser should not show local filesystem paths.

The browser should not show stack traces.

The API should return safe JSON contracts.

The UI should remain usable when pricing metadata is missing.

The UI should remain usable when the tenant has no usage events.

## Evidence To Capture

Capture the Acme Usage page screenshot.

Capture the Globex empty Usage page screenshot.

Capture the export panel after clicking `Export CSV`.

Capture verifier output.

Capture focused backend test output.

Capture focused frontend test output.

Capture Playwright output.

Capture curl regression output.

Use these filenames:

- `/tmp/qa056-ui-reviewer-notes.txt`
- `/tmp/qa056-ui-verifier-output.txt`
- `/tmp/qa056-api-evidence.txt`
- `/tmp/qa056-db-evidence.txt`
- `/tmp/qa056-validation-evidence.txt`
- `output/playwright/qa056_ui/qa056-live-data-ui-api-smoke.png`

Expected: evidence files do not include raw prompts or secrets.

Expected: evidence files use qa056 names.

Expected: evidence can be reviewed without private credentials.

## Security And Redaction Checks

Search screenshots and API samples for unsafe content.

Unsafe content includes raw prompts.

Unsafe content includes raw completions.

Unsafe content includes authorization headers.

Unsafe content includes credential values.

Unsafe content includes provider tokens.

Unsafe content includes memory payloads.

Unsafe content includes storage file URIs.

Unsafe content includes local filesystem paths.

Unsafe content includes stack traces.

Unsafe content includes unauthorized tenant data.

Run the API redaction scan from `qa056.md`.

Expected: the scan exits successfully.

If unsafe text appears, stop and record a blocker.

If an artifact reference begins with `file:`, stop and record a blocker.

If a browser row shows raw payload content, stop and record a blocker.

If a tenant can see another tenant's usage events, stop and record a blocker.

## Tenant Isolation Checks

Acme tenant ID is `11111111-1111-1111-1111-111111111111`.

Globex tenant ID is `22222222-2222-2222-2222-222222222222`.

Acme is seeded with usage events.

Globex is intentionally empty.

Sign in as Acme tenant admin first.

Expected: Acme usage rows are visible.

Sign in as Globex tenant admin second.

Expected: Globex sees no usage events.

Try the cross-tenant API check from `qa056.md`.

Expected: the request returns `403`.

Try the denied export API check from `qa056.md`.

Expected: the export response status is `denied`.

Do not treat the Globex shell scope option as leaked usage data.

Tenant navigation can show authorized tenant scope names.

Usage rows, drilldowns, and exports must not leak across tenant scope.

## Troubleshooting

If the page does not load, check API health.

```bash
curl --fail --silent http://127.0.0.1:8000/health/live
```

Expected: health returns success.

If Acme shows no usage data, rerun the seed script.

```bash
uv run python scripts/qa/seed_usage_qa056.py
```

Expected: the seed prints two usage events.

If export creation does not complete, confirm artifact storage exists.

```bash
mkdir -p .data/qa056-artifacts
```

Expected: the export route can write under the QA artifact root.

If the verifier fails, confirm the browser export was clicked.

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa056 -c "SELECT usage_export_request_id, status, row_count FROM usage_export_requests ORDER BY created_at DESC LIMIT 5;"
```

Expected: at least one completed export exists in addition to the seeded export.

If Globex shows Acme data, stop validation.

Expected: tenant leakage is a blocker.

If redaction fails, stop validation.

Expected: secret or raw payload leakage is a blocker.

If frontend tests fail because text changed, compare the rendered text to the
backend contract before updating tests.

Expected: tests should follow safe contract text, not old QA035 fixture names.

If backend tests fail around datetime ranges, confirm the seed uses current
timestamps inside the last-30-days window.

Expected: seeded events are inside the default dashboard range.
