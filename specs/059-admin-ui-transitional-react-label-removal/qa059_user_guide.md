# QA059 User Guide: Spec 059 - Admin UI Transitional React Label Removal

## Detailed Overview

Spec 059 cleans up the last implementation-era labels in the admin browser UI.

The product should be presented as Admin.

The old implementation wording should not appear in everyday page titles,
breadcrumbs, navigation, document titles, error states, or fallback copy.

The migration evidence page may still explain technical context for reviewers.

The transitional label gate makes that distinction explicit.

It lists blocked findings when user-visible wording still needs cleanup.

It lists allowed references when the term is only an internal identifier,
historical evidence id, or developer-only implementation note.

For this QA pass, the gate must report zero blocked findings.

The UI screenshots must show Admin terminology.

The route responses must remain redaction-safe.

The database uses QA data only.

External providers, Telegram, connectors, and real credentials are disabled.

This guide is written for a manual QA reviewer who does not need to change code.

## Who Should Use This Guide

Use this guide if you are validating the final admin terminology cleanup.

Use this guide if you are reviewing Playwright screenshots.

Use this guide if you are confirming route scanner evidence.

Use this guide if you need to explain why some technical references remain.

Use this guide if you are checking that no tenant data leaks across scopes.

Use this guide if you are checking that no secrets appear in QA artifacts.

Do not use this guide to validate a production deployment.

Do not use this guide with real provider credentials.

Do not use this guide with real Telegram tokens.

Do not use this guide to approve a Git commit.

The user will commit after all work is complete.

## Manual QA Prerequisites

Work from the repository root.

Use the QA059 environment file.

Confirm Docker is running.

Confirm PostgreSQL can start through Docker Compose.

Confirm Node dependencies are available for the frontend.

Confirm Playwright Chromium is installed.

Confirm `.env.qa059` exists.

Confirm `specs/_autopilot/remove-mock-data-roadmap/059-admin-ui-transitional-react-label-removal/validation.yml` exists.

Confirm the QA seed script exists.

Confirm the QA verifier script exists.

Confirm no command points at a production database.

Prepare the environment:

```bash
cp specs/059-admin-ui-transitional-react-label-removal/.env.qa059 .env
uv sync
docker compose up -d postgres
```

Reset and seed the QA database:

```bash
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa059 && createdb -U postgres multi_agent_platform_qa059'
uv run alembic upgrade head
uv run python scripts/qa/seed_transitional_labels_qa059.py
```

Expected result: the seed script prints `Seeded QA059 transitional label records`.

Expected result: the seed script prints `external_calls=0`.

## Step-by-Step Manual QA

Start the API in one terminal.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Start the worker in another terminal.

```bash
uv run python -m multi_agent_platform.workers.main
```

Open local login:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app
```

Choose `platform-admin`.

Expected result: the Admin shell opens.

Expected result: the top heading says `Admin`.

Expected result: navigation labels use domain names.

Expected result: the UI does not show `React Admin`.

Open the skills page:

```text
http://127.0.0.1:8000/admin/app/skills
```

Expected result: the page shows `Skill lifecycle`.

Expected result: the page does not add implementation labels to navigation.

Open the migration page:

```text
http://127.0.0.1:8000/admin/app/migration
```

Expected result: the title is `Admin browser UI`.

Expected result: the route table says `Admin and legacy destinations`.

Expected result: the readiness panel says `Browser UI readiness`.

Expected result: the live-data panel says `Live-data guardrails`.

Expected result: the terminology panel says `Transitional label gate`.

Expected result: the terminology panel says the Admin terminology gate passed.

Run the automated UI flow:

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/059-admin-ui-transitional-react-label-removal/validation.yml --start-processes
```

Expected result: `output/playwright/qa059_ui/qa059-admin-entry.png` exists.

Expected result: `output/playwright/qa059_ui/qa059-domain-pages.png` exists.

Run the route verifier:

```bash
uv run python scripts/qa/verify_transitional_labels_qa059.py
```

Expected result: output includes `blocked_count=0`.

Expected result: output includes `ci_status=pass`.

## Expected Results

Admin entry copy uses Admin terminology.

Domain pages use domain terminology.

Fallback host HTML uses Admin terminology.

API error details use Admin terminology.

Migration evidence uses Admin as the product label.

Allowed implementation references remain narrow and explained.

The transitional label gate route returns `blocked_count` equal to zero.

The route response does not contain `React Admin`.

The route response does not contain `React-only`.

The route response does not contain absolute home-directory paths.

The route response does not contain raw prompts.

The route response does not contain raw completions.

The route response does not contain private messages.

The route response does not contain raw tool payloads.

The route response does not contain real credentials.

The Playwright screenshots are safe to store as QA evidence.

The curl regression can run after the spec validation passes.

## Evidence To Capture

Capture the QA docs validation result.

Capture the spec QA validation result.

Capture the Playwright command result.

Capture `qa059-admin-entry.png`.

Capture `qa059-domain-pages.png`.

Capture `.data/qa059-artifacts/transitional-label-gate-report.json`.

Capture the generated type check result.

Capture the frontend test result.

Capture the full backend quality result.

Capture `.data/curl_test_runs/qa059-after-spec`.

Capture any manual reviewer notes in `/tmp/qa059-review-notes.md`.

Record the principal used for review.

Record the active scope used for review.

Record the final queue state after validation completes.

Record that no intermediate Git commit was required.

## Security And Redaction Checks

Check route responses for raw secrets.

Check route responses for provider tokens.

Check route responses for Telegram token text.

Check route responses for authorization headers.

Check route responses for raw prompts.

Check route responses for raw completions.

Check route responses for memory content.

Check route responses for private messages.

Check route responses for raw tool payloads.

Check route responses for local filesystem paths.

Check screenshots for private tenant data.

Expected result: no unsafe value is visible.

If an unsafe value is visible, stop validation.

## Tenant Isolation Checks

Use `platform-admin` for platform review.

Use `tenant-admin-acme` for tenant review.

Use Globex only as a denied scope check.

Call the transitional label route with Acme tenant scope.

Expected result: the Acme route succeeds.

Call the transitional label route with Globex tenant scope while signed in as
Acme.

Expected result: the Globex route returns 403.

Expected result: the 403 body does not include Globex details.

Expected result: the 403 body does not include the QA059 gate payload.

Do not proceed if cross-tenant data appears.

## Troubleshooting

If the login page does not load, check the API process.

If the API cannot start, check `.env`.

If the database connection fails, recreate `multi_agent_platform_qa059`.

If the seed script fails, check Alembic migrations.

If the skills page is empty, rerun the seed script.

If the migration page fails, inspect `/tmp/qa059-api.log`.

If Playwright fails to click login, confirm local-principal auth is enabled.

If screenshots are blank, rerun Playwright with processes started.

If generated types are stale, run the type generator.

If the scanner reports blockers, search the surfaced file and replace the
blocked wording.

If a blocked label appears only in developer-only evidence, confirm the scanner
classification and rationale.

If a blocked label appears in normal UI, fix the UI before continuing.

If the curl test fails, inspect `.data/curl_test_runs/qa059-after-spec`.

If validation is fixed, rerun the failed command and any downstream command.

Do not commit between these repair loops.
