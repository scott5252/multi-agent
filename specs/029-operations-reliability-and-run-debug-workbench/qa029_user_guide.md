# QA029 User Guide: Spec 029 - Operations, Reliability, And Run Debug Workbench

## Detailed Overview

QA029 adds a React operations workbench to the admin console.

The workbench is designed for operational triage.

It gives administrators one place to review health, pressure, run debug, reliability recovery, and export evidence.

The first screen is the usable workbench, not a marketing page.

Platform administrators can see platform-level summaries.

Tenant administrators can see tenant-limited summaries.

Auditors can review platform summaries without using unsafe live systems.

The workbench intentionally uses deterministic QA data in local validation.

The workbench does not contact a live model provider.

The workbench does not contact Telegram.

The workbench does not run external connector tools.

The backend creates the summaries.

The React app displays the summaries.

The browser must not invent filters, statuses, export references, or run facts.

The page should feel like a dense operations tool.

It should be readable at a glance.

It should make likely causes easy to find.

It should make run debug details easy to connect.

It should show export evidence as artifact references, not local files.

The most important safety rule is simple.

No raw sensitive operational data should be visible.

Do not accept a screenshot that shows raw prompts.

Do not accept a screenshot that shows raw completions.

Do not accept a screenshot that shows memory contents.

Do not accept a screenshot that shows private channel messages.

Do not accept a screenshot that shows raw provider responses.

Do not accept a screenshot that shows Telegram updates.

Do not accept a screenshot that shows connector outputs.

Do not accept a screenshot that shows stack traces.

Do not accept a screenshot that shows local filesystem paths.

Do not accept a screenshot that shows `qa029-secret-value`.

Do not accept an Acme tenant screenshot that shows Globex data.

The expected output is safe summary text.

The expected export output is `artifact-ref-qa029-platform` or `artifact-ref-qa029-tenant`.

The expected run title is `Daily briefing graph run`.

The expected platform card includes `Provider health`.

The expected tenant cards include `Tenant run health` and `Tenant delivery`.

## Who Should Use This Guide

Use this guide if you are manually reviewing QA029 in a browser.

Use this guide if you need a plain-language checklist.

Use this guide if you are not changing code but need to verify the feature.

Use this guide if you need to compare platform and tenant behavior.

Use this guide if you need to confirm redaction and tenant isolation.

Developers should also run `qa029.md`.

UI reviewers should also run `qa029_ui.md`.

This guide assumes the local application runs on `http://127.0.0.1:8000`.

This guide assumes the QA environment file is `.env.qa029`.

This guide assumes Acme uses tenant ID `11111111-1111-1111-1111-111111111111`.

This guide assumes Globex uses tenant ID `22222222-2222-2222-2222-222222222222`.

## Manual QA Prerequisites

Start from the repository root.

Copy the environment file.

```bash
cp specs/029-operations-reliability-and-run-debug-workbench/.env.qa029 .env
```

Install dependencies.

```bash
uv sync
```

Build the React admin bundle.

```bash
cd frontend/admin
npm install
npm run build
cd ../..
```

Start PostgreSQL.

```bash
docker compose up -d postgres
```

Reset the QA029 database.

```bash
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa029 && createdb -U postgres multi_agent_platform_qa029'
```

Run migrations.

```bash
uv run alembic upgrade head
```

Seed Acme and Globex tenants.

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa029 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
```

Create evidence directories.

```bash
mkdir -p .data/qa029-artifacts output/playwright/qa029_ui
```

Start the API.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Start the worker in another terminal.

```bash
uv run python -m multi_agent_platform.workers.main
```

Confirm the API is live.

```text
http://127.0.0.1:8000/health/live
```

Expected result: the health endpoint responds.

Expected result: local login shows `platform-admin`, `auditor`, `tenant-admin-acme`, and `tenant-admin-globex`.

## Step-by-Step Manual QA

Step 1: open the denied route.

```text
http://127.0.0.1:8000/admin/app/operations
```

Expected result: the route is not accessible before login.

Expected result: no workbench content appears.

Record whether the page shows a safe authentication message.

Step 2: open local login.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/operations
```

Choose `platform-admin`.

Expected result: the browser redirects to `/admin/app/operations`.

Expected result: the shell says `React Admin`.

Expected result: the page says `Operations workbench`.

Capture `output/playwright/qa029_ui/qa029-react-operations-platform.png` if running manually with your own screenshot tool.

Step 3: review platform cards.

Find `Health`.

Find `Queue pressure`.

Find `Provider health`.

Expected result: each card has a status badge.

Expected result: each card has safe summary text.

Expected result: no card shows raw logs or raw payload text.

Step 4: review likely causes.

Find `Likely causes`.

Find `Model gateway`.

Find `retryable_timeout`.

Expected result: the next step points toward provider health and gateway diagnostics.

Expected result: no provider authorization header appears.

Step 5: review health panels.

Find `Capacity and dependencies`.

Find `Runnable queue`.

Find `Telegram`.

Expected result: the panel says safe polling is available.

Expected result: values fit inside their panels.

Step 6: review run debug.

Find `Daily briefing graph run`.

Find `Calendar branch`.

Find `Weather branch`.

Find `OpenAI provider`.

Find `Daily briefing weather`.

Find `Morning briefing alias`.

Expected result: the graph, provider, connector, and delivery summaries are connected on one page.

Expected result: the summaries do not show private message text.

Step 7: review reliability.

Find `Recovery posture`.

Find `Model gateway breaker`.

Find `Weather branch retry`.

Find `Replay requires confirmation`.

Expected result: replay is described as confirmation-gated.

Expected result: clicking around does not execute a live remediation.

Step 8: review export.

Click `Export evidence`.

Expected result: `artifact-ref-qa029-platform` appears.

Expected result: `audit-workbench-export-qa029-platform` appears.

Expected result: the redaction summary is visible.

Expected result: no local file path appears.

Step 9: review tenant scope.

Open local login again.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/operations
```

Choose `tenant-admin-acme`.

Expected result: the browser redirects to `/admin/app/operations`.

Expected result: the active scope shows Acme.

Expected result: `Tenant run health` appears.

Expected result: `Tenant delivery` appears.

Expected result: `Provider health` does not appear.

Step 10: review tenant export.

Click `Export evidence`.

Expected result: `artifact-ref-qa029-tenant` appears.

Expected result: no Globex text appears.

Step 11: test cross-tenant URL.

While signed in as Acme, open:

```text
http://127.0.0.1:8000/admin/app/operations?tenant_id=22222222-2222-2222-2222-222222222222
```

Expected result: access is denied.

Expected result: Globex content is not visible.

Step 12: test platform auditor.

Open local login again.

Choose `auditor`.

Expected result: the platform workbench loads.

Expected result: the auditor can review operational summaries.

Expected result: no unsafe action is exposed as a live remediation.

## Expected Results

The denied route fails closed.

The platform workbench loads for `platform-admin`.

The platform workbench loads for `auditor`.

The tenant workbench loads for `tenant-admin-acme`.

The tenant workbench hides platform-only provider health.

The tenant workbench does not mention Globex.

The cross-tenant URL is denied.

The run debug area shows graph branches.

The run debug area shows gateway attempt categories.

The run debug area shows connector policy outcome.

The run debug area shows Telegram delivery status categories.

The reliability area shows breaker, retry, dead-letter, and confirmation summaries.

The export action returns an artifact reference.

The export action returns an audit reference.

The export action does not reveal a local path.

The page remains readable on desktop.

The page remains readable on a narrow browser width.

## Evidence To Capture

Capture the denied route result.

Capture the platform workbench.

Capture the platform export result.

Capture the tenant workbench.

Capture the tenant export result.

Capture the cross-tenant denial result.

Record the browser and viewport size.

Record whether all cards are readable.

Record whether any text overlaps.

Record whether any keyboard focus is unclear.

Record whether any unsafe text appears.

Record all screenshot paths.

Recommended screenshot paths:

```text
output/playwright/qa029_ui/qa029-react-operations-denied.png
output/playwright/qa029_ui/qa029-react-operations-platform.png
output/playwright/qa029_ui/qa029-react-operations-export.png
output/playwright/qa029_ui/qa029-react-operations-tenant.png
```

## Security And Redaction Checks

Search the visible page for `qa029-secret-value`.

Search the visible page for `/Users/`.

Search the visible page for `raw provider response`.

Search the visible page for `raw tool result`.

Search the visible page for `private channel message`.

Search the visible page for `provider authorization`.

Expected result: none of those strings appear.

If any of those strings appear, stop validation and file a defect.

Check export output for artifact references.

Expected result: export references begin with `artifact-ref-qa029`.

Expected result: export references do not begin with `/`.

Check run debug details.

Expected result: details are categories and summaries, not raw operational data.

## Tenant Isolation Checks

Use `tenant-admin-acme` for Acme checks.

Expected result: Acme can open `/admin/app/operations`.

Expected result: Acme cannot open Globex scope by query parameter.

Expected result: Acme does not see Globex in cards, logs, exports, or errors.

Use `tenant-admin-globex` only to confirm that Globex login exists.

Do not use Globex data as expected Acme evidence.

Check that platform-only provider health is hidden for Acme.

Expected result: tenant users see tenant operational context and partial-data explanations.

Expected result: platform-only pressure remains hidden.

## Troubleshooting

If the browser shows an asset error, rebuild the React admin bundle.

If local login does not list QA principals, copy `.env.qa029` to `.env` again.

If the API cannot start, check whether port 8000 is already in use.

If the database is missing tenants, rerun the seed command.

If the page shows stale content from a prior spec, rebuild assets and hard refresh the browser.

If Playwright cannot click local login, inspect whether the login page changed.

If the export button does not update, inspect `/tmp/qa029-api.log`.

If the tenant page shows platform provider health, treat that as a scope regression.

If the page shows Globex while signed in as Acme, treat that as a tenant isolation regression.

If the page shows `qa029-secret-value`, treat that as a redaction regression.

If the page shows `/Users/`, treat that as an artifact safety regression.

If layout text overlaps, capture a screenshot and record viewport width.

If automated validation fails but manual behavior looks right, rerun the exact command from `qa029.md` and compare output.
