# QA053 User Guide: Spec 053 - Test Bench React Live Data

## Detailed Overview

QA053 verifies the Test Bench workspace in the React admin app.

The workspace helps authorized tenant admins review agent test suites.

It also shows test cases, assertions, run progress, run diagnostics, artifacts,
publish-gate evidence, and safe audit-style timeline records.

Before this spec, the React test bench page could show deterministic production
rows that looked like real test results.

This spec changes that behavior.

The page must now show records from the database or a clear empty state.

The database rows are created by the QA seed script.

The browser action for this QA run is saving a suite.

That action is safe because it updates suite metadata only.

It never calls a live provider.

It never calls Telegram.

It never calls an external connector.

It never resolves credentials.

It never displays raw prompts.

It never displays raw completions.

It never displays raw transcripts.

It never displays connector payloads.

It never displays local filesystem paths.

The seeded suite is `QA053 live daily briefing release gate`.

The seeded Acme tenant can see it.

The seeded Globex tenant must not see it.

The expected browser result is an accepted suite-save message.

The expected database result is a suite revision of 3 or higher.

## Who Should Use This Guide

Use this guide if you are manually reviewing qa053.

Use it if you need to confirm browser behavior after automated tests pass.

Use it if you need screenshots for a reviewer.

Use it if you need to verify tenant isolation.

Use it if you need to verify redaction safety.

Use it if you need to explain the feature to a non-developer reviewer.

You do not need to know the code internals to follow this guide.

You do need terminal access to the repository.

You do need Docker and PostgreSQL available locally.

You do need the local app to run against `.env.qa053`.

You should not use production credentials.

You should not use production databases.

You should not call live external services.

You should stop if a step asks for production access.

## Manual QA Prerequisites

Confirm you are in the repository root.

```bash
pwd
```

Expected result: the path ends in `multi-agent`.

Copy the QA environment.

```bash
cp specs/053-test-bench-react-live-data/.env.qa053 .env
```

Expected result: `.env` now contains `APP_NAME=multi-agent-platform-qa053`.

Install dependencies.

```bash
uv sync
```

Expected result: dependencies are installed.

Start PostgreSQL.

```bash
docker compose up -d postgres
```

Expected result: PostgreSQL is running locally.

Reset the QA database.

```bash
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa053 && createdb -U postgres multi_agent_platform_qa053'
```

Expected result: only `multi_agent_platform_qa053` is recreated.

Run database migrations.

```bash
uv run alembic upgrade head
```

Expected result: migrations finish successfully.

Seed local tenants.

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa053 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
```

Expected result: Acme and Globex are available.

Seed the QA053 test bench records.

```bash
uv run python scripts/qa/seed_test_bench_qa053.py
```

Expected result: the command prints `Seeded QA053 test bench live records`.

Start the app.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected result: the app is available on `http://127.0.0.1:8000`.

## Step-by-Step Manual QA

Open the local login page.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/test-bench
```

Expected result: the local login page appears.

Select `tenant-admin-acme`.

Expected result: the browser opens the Test Bench page.

Find the page title.

Expected result: `Test Bench` is visible.

Find the seeded suite.

Expected result: `QA053 live daily briefing release gate` is visible.

Find the seeded case.

Expected result: `Briefing summary contract` is visible.

Find the default safe mode.

Expected result: `mock_model` is visible.

Find the gate status.

Expected result: the current gate shows passing evidence before mutation.

Find the diagnostic section.

Expected result: failed run diagnostics are summarized safely.

Click `Save suite`.

Expected result: a result panel appears.

Read the result panel.

Expected result: the result status is `accepted`.

Read the result summary.

Expected result: the summary says the suite was saved with repository-backed
target revision binding.

Run the database verifier.

```bash
uv run python scripts/qa/verify_test_bench_qa053.py
```

Expected result: the verifier prints `Verified QA053 test bench suite persistence`.

Open the Globex version of the route.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/test-bench
```

Select `tenant-admin-globex`.

Expected result: the page does not show the Acme seeded suite.

Return to Acme if you need to capture the screenshot.

Expected result: the Acme seeded suite is visible again.

## Expected Results

The Acme page loads without JavaScript errors.

The Acme page shows a live seeded suite.

The Acme page shows a live seeded case.

The Acme page shows live run summaries.

The Acme page shows live publish-gate evidence.

The Acme page shows live artifact metadata.

The Acme page shows safe audit-style timeline records.

The Acme page can save the suite.

The suite-save result is accepted.

The verifier sees suite revision 3 or higher.

The Globex page does not show the Acme seeded suite.

The route responses do not include unsafe content.

The screenshot path is `output/playwright/qa053_ui/qa053-live-data-ui-api-smoke.png`.

The curl test artifact path is `.data/curl_test_runs/qa053-after-spec`.

## Evidence To Capture

Capture a screenshot after the suite-save result appears.

Capture `/tmp/qa053-quality-evidence.txt`.

Capture `/tmp/qa053-api-evidence.txt`.

Capture `/tmp/qa053-ui-action-evidence.txt`.

Capture `/tmp/qa053-post-ui-evidence.txt`.

Capture the Playwright screenshot path.

Capture the post-UI verifier output.

Capture the focused backend test result.

Capture the frontend typecheck result.

Capture the frontend build result.

Capture the curl-test summary.

Do not capture unsafe payloads.

Do not paste credential values.

Do not paste raw prompts or completions.

Do not paste private local paths.

## Security And Redaction Checks

Search the browser page for unsafe labels.

Expected result: `raw prompt` is absent.

Expected result: `raw completion` is absent.

Expected result: `raw transcript` is absent.

Expected result: `resolved credential` is absent.

Expected result: `authorization header` is absent.

Expected result: `connector payload` is absent.

Expected result: `storage path` is absent.

Expected result: `Globex` is absent from Acme-only seeded evidence.

Search the API response samples.

Expected result: unsafe labels are absent from JSON responses.

Search the screenshot.

Expected result: unsafe labels are absent from visible UI evidence.

## Tenant Isolation Checks

Sign in as `tenant-admin-acme`.

Expected result: the seeded QA053 suite is visible.

Sign out or open a new login session.

Sign in as `tenant-admin-globex`.

Expected result: the seeded QA053 suite is not visible.

Call the Globex bootstrap JSON route.

```bash
curl --fail --silent -H 'X-Local-Principal: tenant-admin-globex' 'http://127.0.0.1:8000/admin/app/test-bench/bootstrap.json?tenant_id=22222222-2222-2222-2222-222222222222'
```

Expected result: the response contains `No test bench records found`.

Expected result: the response does not contain `QA053 live daily briefing release gate`.

What this proves: tenant-scoped repository filters are active.

## Troubleshooting

If the page is empty for Acme, rerun the seed script.

If the suite-save result is missing, check the browser console.

If the verifier reports revision 2, the browser action did not persist.

If the route returns 403, confirm the local principal matches the tenant.

If Globex can see Acme records, stop and report a tenant isolation blocker.

If unsafe content appears, stop and report a redaction blocker.

If Playwright cannot find `Save suite`, confirm the seeded suite exists.

If the API process cannot start, inspect `/tmp/qa053-api.log`.

If the worker process cannot start, inspect `/tmp/qa053-worker.log`.

If frontend build fails, run `npm run --prefix frontend/admin typecheck`.

If Python quality checks fail, run the focused test command from `qa053.md`.

If curl validation fails, keep `queue.json` on spec 053 and repair before
moving on.
