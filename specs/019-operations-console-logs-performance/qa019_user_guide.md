# QA019 User Guide: Operations Console Logs And Performance

## Detailed Overview

This guide helps a reviewer validate the Operations Console.
The Operations Console is a platform-admin and auditor view.
It lives at `/admin/operations`.
It is designed for incident review and operational triage.
It shows platform health in one browser screen.
It shows dependency readiness.
It shows worker and queue pressure.
It shows database pool pressure.
It shows object-storage status.
It shows model-provider health.
It shows Telegram and channel readiness.
It shows reliability breaker state.
It shows retry and dead-letter pressure.
It shows request latency.
It shows run lifecycle throughput.
It shows model latency.
It shows token throughput.
It shows error rate.
It shows redacted operational logs.
It supports filters for trace id.
It supports filters for tenant id.
It supports filters for run id.
It supports filters for component.
It supports filters for severity.
It supports filters for status.
It supports filters for dependency.
It supports a bounded row limit.
It can export redacted CSV evidence.
It stores exports through the existing artifact provider.
It records export evidence through existing inspection-access audit records.
It does not use raw log files as the source of truth.
It does not render prompts.
It does not render model responses.
It does not render channel messages.
It does not render secrets.
It does not render credentials.
It does not render memory content.
It does not render raw payloads.
It does not render stack traces.
It denies tenant admins in this first release.
It allows platform admins and auditors with explicit operations permissions.
The main review goal is to prove the console is useful, safe, and bounded.

## Who Should Use This Guide

Use this guide if you are a manual QA reviewer.
Use this guide if you are reviewing a pull request.
Use this guide if you need screenshot evidence.
Use this guide if you need to validate redaction.
Use this guide if you need to validate tenant isolation.
Use this guide if you need to validate CSV export behavior.
Use this guide if you need to confirm local QA setup.
You do not need production credentials.
You do not need real model provider credentials.
You do not need real Telegram credentials.
You do not need direct database access for normal browser checks.
You should be comfortable copying commands.
You should be comfortable opening a local browser.
You should keep notes about any unexpected value that appears.
You should never paste real customer data into this QA environment.

## Manual QA Prerequisites

Confirm Python 3.12 is available.
Confirm `uv` is installed.
Confirm Docker Compose v2 is available.
Confirm the repository is checked out locally.
Confirm you are on the QA019 feature branch.
Confirm no unrelated local server is using port 8000.
Confirm no unrelated local database named `multi_agent_platform_qa019` matters.
Confirm you can run shell commands from the repository root.
Confirm the QA environment file exists.
Confirm the QA guide exists.
Confirm the UI walkthrough exists.
Confirm the testing instructions exist.
Confirm the PR review notes exist.
Confirm the README mentions the Operations Console.
Confirm `docs/quickstart.md` mentions QA019 validation.

Copy the QA environment file.

```bash
test ! -f .env || cp .env .env.autopilot-backup
cp specs/019-operations-console-logs-performance/.env.qa019 .env
```

Expected result: `.env` now points to `multi_agent_platform_qa019`.
Expected result: local-principal mode is enabled.
Expected result: the storage root is `.data/qa019-artifacts`.

Install dependencies.

```bash
uv sync
```

Expected result: dependency installation exits with code 0.

Start PostgreSQL.

```bash
docker compose up -d postgres
```

Expected result: PostgreSQL is running locally.

Reset the QA database.

```bash
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa019 && createdb -U postgres multi_agent_platform_qa019'
```

Expected result: only `multi_agent_platform_qa019` is reset.

Apply migrations.

```bash
uv run alembic upgrade head
```

Expected result: all existing migrations apply successfully.
Expected result: no new operations-console migration is required.

Seed QA tenant rows.

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa019 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING;"
```

Expected result: Acme and Globex tenant ids exist for access-audit evidence.
Expected result: tenant-denial checks can return `403` instead of a setup error.

Create artifact directories.

```bash
mkdir -p .data/qa019-artifacts output/playwright/qa019_ui
```

Expected result: local export and screenshot directories exist.

Start the API.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected result: `http://127.0.0.1:8000/health/live` responds.

Start the worker in a second shell if you are validating runtime readiness.

```bash
uv run python -m multi_agent_platform.workers.main
```

Expected result: the worker starts without real provider credentials.

## Step-by-Step Manual QA

Open the local login page.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/operations
```

Expected result: the page title says `Local Login`.
Expected result: `platform-admin` appears as a sign-in choice.
Expected result: `auditor` appears as a sign-in choice.
Expected result: tenant admins may appear but should not reach the console.

Click `platform-admin`.
Expected result: the browser lands on `/admin/operations`.
Expected result: the page title says `Operations Console`.
Expected result: the admin shell is visible.
Expected result: the navigation includes `Operations Console`.
Expected result: the page uses platform scope.

Review the redaction notice.
Expected result: it explains that raw prompts are excluded.
Expected result: it explains that model responses are excluded.
Expected result: it explains that channel messages are excluded.
Expected result: it explains that secrets are excluded.
Expected result: it explains that credentials are excluded.
Expected result: it explains that payloads are excluded.
Expected result: it explains that memory content is excluded.
Expected result: it explains that stack traces are excluded.

Review the System Health card.
Expected result: the card shows a readable status.
Expected result: dependency checks are summarized.
Expected result: unavailable required dependencies produce a not-ready state.
Expected result: degraded dependencies produce a degraded state.

Review Worker Capacity.
Expected result: runnable queue depth is visible.
Expected result: delayed queue depth is visible.
Expected result: active leases are visible.
Expected result: retry backlog is visible.
Expected result: dead-letter count is visible.

Review DB Pool Pressure.
Expected result: p95 wait time is visible.
Expected result: in-use connection count is visible.
Expected result: available connection count is visible.
Expected result: high wait time reads as degraded.

Review Object Storage.
Expected result: the configured storage provider name is visible.
Expected result: artifact in-flight count is visible.
Expected result: no secret storage credentials are visible.

Review Model Providers.
Expected result: configured provider count is visible.
Expected result: health state is visible.
Expected result: provider links point to authorized model-provider pages.
Expected result: no API key is visible.
Expected result: no Authorization header is visible.

Review Telegram And Channels.
Expected result: channel readiness is summarized.
Expected result: fake QA secret references may appear as safe references.
Expected result: raw Telegram tokens do not appear.
Expected result: private message text does not appear.

Review Reliability State.
Expected result: open breaker count is visible.
Expected result: retry pressure is visible.
Expected result: dead-letter pressure is visible.
Expected result: links point to reliability controls when authorized.

Review latency and throughput cards.
Expected result: request latency is visible.
Expected result: run throughput is visible.
Expected result: token throughput is visible.
Expected result: error rate is visible.
Expected result: empty local data is presented as safe zero or empty state.

Review dependency rows.
Expected result: each dependency has a name.
Expected result: each dependency has a required flag.
Expected result: each dependency has a status.
Expected result: details are short and safe.
Expected result: stack traces are not shown.

Review the log filter form.
Expected result: trace id can be entered.
Expected result: tenant id can be entered.
Expected result: run id can be entered.
Expected result: component can be entered.
Expected result: severity can be entered.
Expected result: status can be entered.
Expected result: dependency can be entered.
Expected result: limit can be changed.
Expected result: the limit stays bounded.

Submit a simple filter.
Expected result: the page reloads or updates with the selected filters.
Expected result: displayed rows match the selected filter.
Expected result: the filter summary is safe.
Expected result: no raw operational payload appears.

Review operational log rows.
Expected result: each row has a source.
Expected result: each row has a timestamp.
Expected result: each row has a component.
Expected result: each row has a severity.
Expected result: each row has a status.
Expected result: each row has a safe summary.
Expected result: details are redacted.
Expected result: sensitive values are shown as `[redacted]` when present.
Expected result: run links point to run inspection when available.
Expected result: provider links point to model-provider pages when available.
Expected result: usage links point to usage dashboards when available.

Export the current filter set.
Expected result: the platform admin can submit an export.
Expected result: the response includes an export id.
Expected result: the response includes an artifact URI.
Expected result: the response includes a SHA-256 checksum.
Expected result: the response includes a row count.
Expected result: the response includes an audit event id.
Expected result: the CSV is stored under `.data/qa019-artifacts`.
Expected result: the CSV does not contain raw prompts.
Expected result: the CSV does not contain model responses.
Expected result: the CSV does not contain channel messages.
Expected result: the CSV does not contain secrets.
Expected result: the CSV does not contain stack traces.

Sign out or use a fresh browser context.
Sign in as `auditor`.
Open `/admin/operations`.
Expected result: the auditor can inspect operations data.
Expected result: auditor access still uses redaction.
Expected result: auditor access does not expose tenant-admin controls.
Expected result: auditor exports require explicit operations export permission.

Sign out or use a fresh browser context.
Sign in as `tenant-admin-acme`.
Open `/admin/operations`.
Expected result: access is denied.
Expected result: no platform dashboard cards are visible.
Expected result: no platform operational rows are visible.
Expected result: no export button is usable.

Check the API dashboard.

```bash
curl --fail --silent -H "X-Local-Principal: platform-admin" \
  http://127.0.0.1:8000/admin/operations/api/dashboard
```

Expected result: JSON returns successfully.
Expected result: JSON contains only safe operational metadata.

Check the API logs.

```bash
curl --fail --silent -H "X-Local-Principal: auditor" \
  "http://127.0.0.1:8000/admin/operations/api/logs?limit=25"
```

Expected result: JSON returns successfully.
Expected result: JSON rows are bounded by limit.
Expected result: JSON rows are redacted.

Check tenant denial through the API.

```bash
test "$(curl --silent --output /tmp/qa019-denied.json --write-out '%{http_code}' \
  -H "X-Local-Principal: tenant-admin-acme" \
  http://127.0.0.1:8000/admin/operations/api/dashboard)" = "403"
```

Expected result: the command exits with code 0.
Expected result: `/tmp/qa019-denied.json` does not contain platform data.

## Expected Results

The console loads for `platform-admin`.
The console loads for `auditor`.
The console denies `tenant-admin-acme`.
The console denies `tenant-admin-globex`.
The dashboard summarizes health and capacity.
The dashboard summarizes provider and channel readiness.
The dashboard summarizes reliability pressure.
The dashboard summarizes usage and latency.
The log table shows safe operational metadata.
The filter form narrows rows.
The export flow stores redacted CSV artifacts.
Export metadata includes a checksum.
Export metadata includes a row count.
Export metadata includes an audit event id.
Screenshots are safe to attach to a review.
The feature works without real provider credentials.
The feature works without real Telegram credentials.
The feature works without raw log files.
The feature reuses existing persistence.

## Evidence To Capture

Capture `output/playwright/qa019_ui/01-local-login.png`.
Capture `output/playwright/qa019_ui/02-operations-console-logs-performance-target.png`.
Capture `output/playwright/qa019_ui/03-operations-console-logs-performance-direct-target.png`.
Save `/tmp/qa019-dashboard.json`.
Save `/tmp/qa019-logs.json`.
Save `/tmp/qa019-export.json`.
Save `/tmp/qa019-denied.json`.
Save `/tmp/qa019-api.log` if a server error occurs.
Save `/tmp/qa019-worker.log` if worker readiness matters.
Record the focused test command result.
Record the full quality gate result.
Record any redaction concern with the exact field name.
Record any tenant isolation concern with the principal used.
Record any export concern with the export id.

## Security And Redaction Checks

Search the page for real API keys.
Search the page for Authorization headers.
Search the page for raw prompts.
Search the page for model completions.
Search the page for channel messages.
Search the page for secret values.
Search the page for credentials.
Search the page for memory content.
Search the page for raw payloads.
Search the page for stack traces.
Search JSON responses for the same forbidden values.
Search CSV exports for the same forbidden values.
Search screenshots for the same forbidden values.
Expected result: no forbidden value is present.
Expected result: sensitive keys are masked or omitted.
Expected result: sensitive values are `[redacted]` or replaced by safe text.
Expected result: safe summaries remain useful for operational review.

## Tenant Isolation Checks

Use `platform-admin` for platform review.
Use `auditor` for audit review.
Use `tenant-admin-acme` for denial review.
Use `tenant-admin-globex` for denial review.
Attempt `/admin/operations` as `tenant-admin-acme`.
Expected result: access is denied.
Attempt `/admin/operations/api/dashboard` as `tenant-admin-acme`.
Expected result: HTTP status is 403.
Attempt `/admin/operations/api/logs` as `tenant-admin-acme`.
Expected result: HTTP status is 403.
Attempt `/admin/operations/api/logs/export` as `tenant-admin-acme`.
Expected result: export is denied.
Expected result: no platform records are returned.
Expected result: no cross-tenant labels are returned.
Expected result: no artifact is created for unauthorized export.

## Troubleshooting

If the login page is missing, confirm `AUTH_MODE=local_principal`.
If `platform-admin` is missing, confirm `LOCAL_PRINCIPAL_CATALOG_JSON`.
If the API does not start, confirm port 8000 is free.
If database migration fails, confirm PostgreSQL is running.
If the database name is wrong, recopy `.env.qa019`.
If exports fail, confirm `.data/qa019-artifacts` exists.
If the page is empty, remember a fresh QA database may have sparse data.
If logs are empty, seed runtime, usage, gateway, or audit events through tests.
If screenshots show secrets, stop and treat it as a release blocker.
If tenant admins can load the console, stop and treat it as a release blocker.
If CSV exports contain forbidden content, stop and treat it as a release blocker.
If Playwright cannot launch, run the focused API and unit tests first.
If quality coverage fails, run the full suite from a clean environment.
If a command fails unexpectedly, save the command, exit code, and output.
If `.env` was overwritten, restore `.env.autopilot-backup` after review.
