# QA053 UI Walkthrough: Test Bench React Live Data

## Goal

Guide a reviewer through browser evidence for qa053.

Expected: the React test bench workspace loads from live backend records.

Expected: the browser shows the seeded `QA053 live daily briefing release gate`
only after the QA seed command persists it.

Expected: the reviewer can click `Save suite` and see an accepted mutation
result.

Expected: the post-UI verifier proves the suite revision changed after the
browser action.

Expected: the browser never displays unsafe prompt, completion, transcript,
credential, connector, or local path content.

What is happening: the page is using `/admin/app/test-bench/bootstrap.json` and
related JSON routes rather than fixed production helper rows.

Why this matters: qa053 is only done if browser-visible data is backed by the
same database rows the API and verifier inspect.

## How To Use This Guide

Use this walkthrough with `qa053.md`.

Save screenshots under `output/playwright/qa053_ui`.

Save reviewer notes under `/tmp/qa053-ui-reviewer-notes.txt`.

Save browser console notes under `/tmp/qa053-ui-console-notes.txt`.

Save post-action API notes under `/tmp/qa053-ui-post-api-notes.txt`.

Expected: screenshot filenames include qa053.

Expected: notes mention the local principal and tenant being reviewed.

Expected: API notes identify the suite id safely.

Expected: reviewer notes avoid copying any unsafe payload content.

What is happening: automated Playwright follows the same flow as this manual
walkthrough.

Why this matters: manual evidence and automated evidence should match.

## Environment Setup

Copy the QA environment.

```bash
cp specs/053-test-bench-react-live-data/.env.qa053 .env
```

Expected: `.env` now contains `APP_NAME=multi-agent-platform-qa053`.

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

Reset the qa053 database.

```bash
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa053 && createdb -U postgres multi_agent_platform_qa053'
```

Expected: only the qa053 database is recreated.

Run migrations.

```bash
uv run alembic upgrade head
```

Expected: migrations complete successfully.

Seed tenants.

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa053 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
```

Expected: Acme and Globex exist.

Seed the test bench records.

```bash
uv run python scripts/qa/seed_test_bench_qa053.py
```

Expected: the command prints the seeded suite id.

Start the app.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected: `http://127.0.0.1:8000/health/live` returns healthy.

## Browser Walkthrough

Open the local login route.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/test-bench
```

Expected: the local-principal login page appears.

Choose the Acme tenant admin principal.

```text
tenant-admin-acme
```

Expected: the browser redirects to `/admin/app/test-bench`.

Confirm the page title.

```text
Test Bench
```

Expected: the page title is visible.

Confirm the seeded suite.

```text
QA053 live daily briefing release gate
```

Expected: the seeded suite appears.

Confirm the seeded case.

```text
Briefing summary contract
```

Expected: the case appears in the suite and case forms section.

Confirm the publish-gate evidence.

```text
Current target revision has passing evidence.
```

Expected: the gate evidence is passed before the suite-save action.

Confirm the failed diagnostic is summarized.

```text
Blocked side-effect assertion failed
```

Expected: the diagnostic appears without unsafe payload details.

Click `Save suite`.

```text
Save suite
```

Expected: the page shows an accepted suite result.

Confirm the mutation summary.

```text
Test suite saved with repository-backed target revision binding.
```

Expected: the browser reports the backend mutation result.

Capture a screenshot.

```bash
mkdir -p output/playwright/qa053_ui
```

Expected: screenshot evidence can be saved in the qa053 output directory.

Run the post-UI verifier.

```bash
uv run python scripts/qa/verify_test_bench_qa053.py
```

Expected: the verifier reports suite revision 3 or higher.

What is happening: the browser sends a POST to `/admin/app/test-bench/suites`.

Why this matters: the QA action proves durable backend mutation instead of
static rendering.

## Required Automated Evidence

Run document validation.

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/053-test-bench-react-live-data
```

Expected: QA docs pass validation.

Run spec API validation.

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/remove-mock-data-roadmap/053-test-bench-react-live-data/validation.yml
```

Expected: route, redaction, and quality checks pass.

Run Playwright validation.

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/053-test-bench-react-live-data/validation.yml --start-processes
```

Expected: the browser action and screenshot complete.

Run focused frontend tests.

```bash
npm run --prefix frontend/admin test -- --run src/components/testBench
```

Expected: all test bench component tests pass.

Run frontend typecheck.

```bash
npm run --prefix frontend/admin typecheck
```

Expected: TypeScript typecheck passes.

Run frontend build.

```bash
npm run --prefix frontend/admin build
```

Expected: the React build succeeds.

Run backend quality checks.

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected: each backend quality command passes.

## UI Evidence Checklist

Capture the login principal.

Expected: the principal is `tenant-admin-acme`.

Capture the page title.

Expected: the title is `Test Bench`.

Capture the seeded suite name.

Expected: the suite name includes `QA053 live daily briefing release gate`.

Capture the suite-save result.

Expected: the result status is `accepted`.

Capture the post-UI verifier output.

Expected: the verifier prints `Verified QA053 test bench suite persistence`.

Capture the Globex empty-state check.

Expected: Globex does not show the Acme suite.

Capture redaction notes.

Expected: no unsafe prompt, completion, transcript, credential, connector, or
path content appears.

## Acceptance Notes Template

Reviewer:

Date:

Browser:

Principal: tenant-admin-acme

Tenant: Acme

Screenshot path: output/playwright/qa053_ui/qa053-live-data-ui-api-smoke.png

Post-UI verifier: passed

API route evidence: passed

Redaction check: passed

Tenant isolation check: passed

What is happening: the page reflects seeded live database records and then
persists a suite-save mutation.

Why this matters: the UI is no longer dependent on deterministic production
fixtures.

## Troubleshooting

If the login page is unavailable, confirm the API process is running.

If the page is empty for Acme, rerun the seed script.

If the suite-save button does not respond, inspect the browser console.

If the suite-save result is stale, reload and retry once.

If the verifier still sees revision 2, the POST did not reach the backend.

If Globex sees the Acme suite, stop and investigate tenant filtering.

If the screenshot contains unsafe content, stop and inspect safe projection code.

If Playwright fails to find text, compare the API response with the browser.

Expected: troubleshooting does not require production credentials.

Expected: fixes remain scoped to qa053 test bench surfaces.

## Related Files

- `specs/053-test-bench-react-live-data/qa053.md`
- `specs/053-test-bench-react-live-data/qa053_user_guide.md`
- `specs/053-test-bench-react-live-data/.env.qa053`
- `scripts/qa/seed_test_bench_qa053.py`
- `scripts/qa/verify_test_bench_qa053.py`
- `frontend/admin/src/components/testBench/TestBenchPage.tsx`
- `src/multi_agent_platform/testing/agent_bench/react_test_bench.py`
- `specs/_autopilot/remove-mock-data-roadmap/053-test-bench-react-live-data/validation.yml`
