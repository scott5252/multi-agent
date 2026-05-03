# QA016 User Guide: Token Usage And Cost Analytics

## Detailed Overview

This guide helps non-developer reviewers validate token usage and cost
analytics in the local QA environment.
The feature records normalized usage events for model calls that pass through
ModelGateway.
Each event is tenant-scoped.
Each event stores safe identifiers.
Each event stores token counts when providers return them.
Each event stores estimated cost using internal pricing metadata.
Each event stores whether values are estimated, confirmed, unavailable, or
malformed.
The dashboard appears in the admin console at `/admin/usage`.
The dashboard supports platform-wide review for platform admins.
The dashboard supports tenant-only review for tenant admins.
The export flow creates CSV reports from safe normalized usage rows.
The export flow must not expose raw prompts.
The export flow must not expose raw completions.
The export flow must not expose secrets.
The export flow must not expose memory content.
The export flow must not expose provider credentials.
The export flow must not expose unauthorized run content.
The first QA slice uses deterministic local data and mocked gateway paths.
No real provider credential is required.
No production endpoint is required.
No production database is used.

## Who Should Use This Guide

Use this guide if you review admin dashboards.
Use this guide if you review billing or finance evidence.
Use this guide if you verify tenant isolation.
Use this guide if you verify redaction behavior.
Use this guide if you collect screenshots for a PR.
You do not need to understand the source code.
You do need access to the local development machine.
You do need Terminal access.
You do need a browser.
You should stop if any command mentions a production host.
You should stop if any command asks for a real provider API key.
You should stop if any page displays raw prompt or completion text.

## Manual QA Prerequisites

Open Terminal A.
Open Terminal B.
Open a browser.
Start from the repository root.
Back up the existing local environment file.
Copy the QA016 environment file.
Install dependencies.
Start PostgreSQL.
Reset only `multi_agent_platform_qa016`.
Run Alembic migrations.
Start the API.
Keep the API terminal open.
Use local-principal login only.
Use `platform-admin` for platform checks.
Use `tenant-admin-acme` for Acme checks.
Use `tenant-admin-globex` for Globex checks.
Store screenshots under `output/playwright/qa016_ui`.
Store generated artifacts under `.data/qa016-artifacts`.

## Step-by-Step Manual QA

Step 1: Run `test ! -f .env || cp .env .env.autopilot-backup`.
Expected result: the command prints no output.
Step 2: Run `cp specs/016-token-usage-cost-analytics/.env.qa016 .env`.
Expected result: the command prints no output.
Step 3: Run `uv sync`.
Expected result: dependencies install without errors.
Step 4: Run `docker compose up -d postgres`.
Expected result: PostgreSQL is running locally.
Step 5: Reset only the QA016 database.
Expected result: `multi_agent_platform_qa016` is recreated.
Step 6: Run `uv run alembic upgrade head`.
Expected result: all migrations apply.
Step 7: Start the API on `127.0.0.1:8000`.
Expected result: the server starts and keeps running.
Step 8: Visit `/auth/local-login?redirect_to=/admin/usage`.
Expected result: the Local Login page appears.
Step 9: Sign in as `platform-admin`.
Expected result: the Usage Analytics page opens.
Step 10: Confirm the page title is `Usage Analytics`.
Expected result: the title is visible.
Step 11: Confirm the redaction notice is visible.
Expected result: it says only normalized counts and safe identifiers are shown.
Step 12: Review the summary cards.
Expected result: Events, Total tokens, Estimated cost, and Confirmed are shown.
Step 13: Review Provider and Model filters.
Expected result: both filters accept safe text values.
Step 14: Change Group to `provider`.
Expected result: the selected value remains after submitting.
Step 15: Review the rollup table.
Expected result: the table shows group, events, tokens, and cost micros.
Step 16: Review the events table.
Expected result: the table shows safe identifiers and numeric usage data.
Step 17: Submit Export CSV.
Expected result: the browser redirects to a Usage Export page.
Step 18: Review export status.
Expected result: status and row count are visible.
Step 19: Review artifact metadata.
Expected result: an artifact URI appears only for completed authorized export.
Step 20: Return to `/admin/usage`.
Expected result: dashboard still renders.
Step 21: Sign out or open a fresh browser context.
Expected result: the previous principal no longer controls the next check.
Step 22: Sign in as `tenant-admin-acme`.
Expected result: Acme tenant scope is available.
Step 23: Open `/admin/usage?tenant_id=11111111-1111-1111-1111-111111111111`.
Expected result: Acme usage scope is accepted.
Step 24: Try filtering by provider `openai`.
Expected result: the page renders without cross-tenant data.
Step 25: Sign in as `tenant-admin-globex`.
Expected result: Globex tenant scope is available.
Step 26: Try the same Acme URL.
Expected result: the request is denied or unavailable, not leaked.
Step 27: Return to Globex tenant scope.
Expected result: Globex can access only Globex scope.
Step 28: Run the focused automated tests.
Expected result: all focused usage tests pass.
Step 29: Run Playwright validation.
Expected result: login and target screenshots are created.
Step 30: Run the full quality gate if requested.
Expected result: lint, formatting, typing, and coverage pass.

## Expected Results

The local login page appears.
The platform admin can open `/admin/usage`.
The tenant admin can open only their tenant usage scope.
The cross-tenant tenant admin cannot view another tenant.
The dashboard has filters.
The dashboard has summary cards.
The dashboard has rollups.
The dashboard has event drilldown rows or a safe empty state.
The dashboard has export controls.
The export detail page renders safe metadata.
The export row count matches the active filters.
The export artifact path stays inside `.data/qa016-artifacts`.
No raw prompt text is visible.
No raw completion text is visible.
No secret value is visible.
No memory content is visible.
No provider credential is visible.
No unauthorized run content is visible.
No command requires production credentials.
No command resets a non-QA database.

## Evidence To Capture

Capture the local login screenshot.
Capture the `/admin/usage` dashboard screenshot.
Capture the filtered dashboard screenshot.
Capture the export detail screenshot.
Capture a note that platform admin could see platform scope.
Capture a note that Acme tenant admin could see Acme scope.
Capture a note that Globex tenant admin was denied Acme scope.
Capture focused pytest output.
Capture Ruff output.
Capture mypy output.
Capture Playwright output paths.
Capture any unexpected error message.
Do not capture raw provider credentials.
Do not paste secrets into reviewer notes.
Do not include production URLs in evidence.

## Security And Redaction Checks

Look for raw prompt text.
Look for raw completion text.
Look for `api_key`.
Look for `authorization`.
Look for `password`.
Look for credential values.
Look for memory snippets.
Look for transcript payloads.
Look for provider request bodies.
Look for provider response bodies.
Expected result: none of these appear in dashboard rows.
Expected result: none of these appear in export CSV content.
Expected result: docs mention these words only as forbidden categories.
If protected content appears, mark the QA result as failed.

## Tenant Isolation Checks

Platform admin may view platform scope.
Platform admin may view a selected tenant scope.
Tenant admin may view their own tenant scope.
Tenant admin may not view another tenant scope.
Tenant admin may not export another tenant scope.
Future tenant user views, if exposed, must be limited to that principal.
Denied requests should not reveal row counts for unauthorized tenants.
Denied requests should not reveal model ids for unauthorized tenants.
Denied requests should not reveal workflow ids for unauthorized tenants.
Denied requests should not reveal agent keys for unauthorized tenants.

## Troubleshooting

If login fails, confirm `.env` points to `.env.qa016`.
If the API is unreachable, confirm Terminal A is still running.
If database checks fail, confirm only `multi_agent_platform_qa016` was reset.
If the dashboard is empty, that can be valid before usage events are seeded.
If export has zero rows, confirm filters match seeded usage.
If export is denied, confirm the current principal and tenant scope.
If screenshots are missing, rerun the Playwright QA command.
If a command requests credentials, stop and report the issue.
If a page shows raw content, stop and report a redaction failure.
