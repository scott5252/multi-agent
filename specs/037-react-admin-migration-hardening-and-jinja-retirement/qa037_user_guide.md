# QA037 User Guide: Spec 037 - React Admin Migration Hardening And Jinja Retirement

## Detailed Overview

QA037 is the final review pass for the React admin migration roadmap.

The main screen is the React admin migration hardening dashboard.

You can open it at `/admin/app`.

You can also open it directly at `/admin/app/migration`.

The dashboard tells reviewers which admin routes are now React-primary.

It also tells reviewers which older routes are still retained as fallbacks.

The feature does not delete old Jinja pages during this QA run.

The feature does not require live Auth0.

The feature does not require live Telegram.

The feature does not require live model provider calls.

The feature uses safe summaries instead of sensitive payloads.

The page is intended for platform operators, tenant administrators, tenant users, and reviewers.

Platform operators can see the full migration picture.

Tenant administrators see tenant-safe route decisions.

Tenant users see only user-safe migration guidance.

The dashboard has five major areas.

The first area is the summary header.

The second area is the guidance state panel.

The third area is the route parity matrix.

The fourth area is the rollback plan.

The fifth area contains performance, accessibility, redaction, and tenant isolation evidence.

The route parity matrix lists each admin area.

It shows the React path.

It shows the legacy path.

It shows the current migration decision.

It shows which auth modes were tested.

It shows what evidence supports the decision.

The rollback panel explains how to turn React primary routing back to fallback mode.

The performance panel summarizes local QA route budget evidence.

The accessibility panel summarizes keyboard, focus, landmark, label, contrast, and text-overlap checks.

The sweep panel summarizes redaction and tenant isolation checks.

## Who Should Use This Guide

Use this guide if you are validating QA037 manually.

Use this guide if you need a plain-language checklist.

Use this guide if you are a reviewer who does not normally work in the codebase.

Use this guide if you need to compare platform and tenant views.

Use this guide if you need to decide whether React primary routing is ready.

Use this guide if you need to confirm older pages are still retained safely.

Use `qa037.md` if you need exact curl and test commands.

Use `qa037_ui.md` if you need a screenshot-focused browser walkthrough.

Use the validation manifest if you are running automated Spec Kit QA.

Do not use this guide to run production checks.

Do not use this guide with real customer credentials.

Do not use this guide against a production database.

## Manual QA Prerequisites

You need the repository checked out locally.

You need Docker available for PostgreSQL.

You need Python dependencies installed through `uv`.

You need frontend dependencies installed in `frontend/admin`.

You need the QA037 environment file.

The environment file is `specs/037-react-admin-migration-hardening-and-jinja-retirement/.env.qa037`.

The QA database is `multi_agent_platform_qa037`.

The artifact directory is `.data/qa037-artifacts`.

The screenshot directory is `output/playwright/qa037_ui`.

The browser base URL is `http://127.0.0.1:8000`.

The local login URL is `http://127.0.0.1:8000/auth/local-login`.

The platform identity is `platform-admin`.

The Acme tenant admin identity is `tenant-admin-acme`.

The Acme tenant user identity is `tenant-user-acme`.

The Globex tenant admin identity is `tenant-admin-globex`.

Back up any existing `.env` before copying `.env.qa037`.

Build the React assets before opening the browser.

Run the API before starting the walkthrough.

Keep terminal logs available for reviewer notes.

## Step-by-Step Manual QA

Step 1: copy the QA037 environment file.

Run `cp specs/037-react-admin-migration-hardening-and-jinja-retirement/.env.qa037 .env`.

Expected result: `.env` points to `multi_agent_platform_qa037`.

Step 2: build the React admin bundle.

Run `cd frontend/admin && npm install && npm run build && cd ../..`.

Expected result: React assets are written to the admin static directory.

Step 3: start PostgreSQL.

Run `docker compose up -d postgres`.

Expected result: PostgreSQL is running locally.

Step 4: reset the QA037 database.

Run the reset command from `qa037.md`.

Expected result: only the QA037 database is dropped and recreated.

Step 5: run Alembic migrations.

Run `uv run alembic upgrade head`.

Expected result: the schema is current.

Step 6: seed Acme and Globex tenants.

Use the seed command from `qa037.md`.

Expected result: Acme and Globex tenant rows exist.

Step 7: start the API.

Run `uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000`.

Expected result: `http://127.0.0.1:8000/health/live` returns healthy.

Step 8: start the worker.

Run `uv run python -m multi_agent_platform.workers.main`.

Expected result: the worker stays running.

Step 9: open `http://127.0.0.1:8000/auth/local-login`.

Expected result: local-principal sign-in choices are visible.

Step 10: choose `platform-admin`.

Expected result: the browser is signed in as platform administrator.

Step 11: open `http://127.0.0.1:8000/admin/app`.

Expected result: the heading says `React Admin Migration Hardening`.

Step 12: confirm the summary cards.

Expected result: destination, React-primary, fallback, retirement-ready, and blocked counts are visible.

Step 13: inspect migration guidance states.

Expected result: retained fallback guidance is visible.

Step 14: inspect the route parity matrix.

Expected result: React paths, legacy paths, decisions, evidence, auth modes, and audit references are visible.

Step 15: inspect retained fallback rows.

Expected result: operations and workflow fallback notices are explicit.

Step 16: inspect retirement-ready rows.

Expected result: rows marked retirement-ready also show parity evidence.

Step 17: inspect the rollback panel.

Expected result: feature flag, asset version, owner, steps, verification steps, and audit reference are visible.

Step 18: inspect the performance panel.

Expected result: bootstrap, interactive, and asset budget rows all show passing status.

Step 19: inspect the accessibility panel.

Expected result: keyboard, focus, landmarks, labels, contrast states, and text-overlap all show passing status.

Step 20: inspect the sweep panel.

Expected result: redaction and tenant isolation sweeps show zero unsafe matches.

Step 21: capture a platform screenshot.

Expected result: save it under `output/playwright/qa037_ui`.

Step 22: open `http://127.0.0.1:8000/admin/app/migration`.

Expected result: the same migration hardening dashboard loads.

Step 23: sign in as `tenant-admin-acme`.

Expected result: Acme scope is active.

Step 24: open `/admin/app/migration?tenant_id=11111111-1111-1111-1111-111111111111`.

Expected result: tenant-safe route rows are visible.

Step 25: confirm platform-only operations rows are not visible to the Acme tenant admin.

Expected result: tenant filtering is clear and safe.

Step 26: sign in as `tenant-user-acme`.

Expected result: the user-safe migration view loads.

Step 27: confirm user-scope guidance is visible.

Expected result: tenant user does not see tenant-admin-only route decisions.

Step 28: try a Globex tenant id while signed in as Acme tenant admin.

Expected result: the page is denied and does not reveal the Globex tenant name.

Step 29: set a mobile viewport.

Expected result: panels stack, text remains readable, and the route table can scroll horizontally.

Step 30: run the redaction scan from `qa037.md`.

Expected result: no unsafe matches are found in `/tmp/qa037-*` or `output/playwright/qa037_ui`.

## Expected Results

The React admin migration dashboard loads from `/admin/app`.

The direct migration route loads from `/admin/app/migration`.

Platform administrators can see all route groups.

Tenant administrators can see tenant-safe route groups.

Tenant users can see only user-safe migration guidance.

Cross-tenant requests are denied.

Denied responses do not name unauthorized tenants.

Retained fallback routes remain visible as fallbacks.

No route is presented as destructively deleted.

Rollback steps are visible.

Performance budget status is visible.

Accessibility audit status is visible.

Redaction sweep status is visible.

Tenant isolation sweep status is visible.

Desktop screenshots are readable.

Mobile screenshots are readable.

No text overlaps in the reviewed viewports.

No sensitive payload appears in screenshots or saved `/tmp/qa037-*` evidence.

## Evidence To Capture

Capture a screenshot of `/admin/app` as platform administrator.

Capture a screenshot of `/admin/app/migration` as platform administrator.

Capture a screenshot of `/admin/app/migration` as Acme tenant administrator.

Capture a screenshot of `/admin/app/migration` as Acme tenant user.

Capture a screenshot of the denied cross-tenant state.

Capture a mobile screenshot.

Save curl output for the platform dashboard.

Save curl output for the tenant dashboard.

Save curl output for the tenant user dashboard.

Save curl output for route groups.

Save curl output for rollback JSON.

Save redaction scan output.

Save focused backend test output.

Save frontend check output.

Save Playwright validation output.

## Security And Redaction Checks

Check that screenshots do not contain unsafe marker text.

Check that JSON evidence does not contain unsafe marker text.

Check that denied responses do not reveal unauthorized tenant names.

Check that route entries contain safe summaries only.

Check that rollback evidence does not include credentials.

Check that performance evidence does not include local machine paths.

Check that accessibility evidence does not include raw audit dumps.

Check that tenant user output does not include tenant admin rows.

Run the redaction scan from `qa037.md`.

Expected result: the redaction scan exits successfully.

## Tenant Isolation Checks

Sign in as platform administrator.

Expected result: platform administrator sees all route groups.

Sign in as Acme tenant administrator.

Expected result: Acme tenant administrator sees tenant-safe and mixed rows only.

Sign in as Acme tenant user.

Expected result: Acme tenant user sees user-safe rows and limited-scope guidance.

Use the Globex tenant id while signed in as Acme tenant administrator.

Expected result: access is denied.

Inspect the denied response.

Expected result: the response does not expose the Globex tenant name.

Review screenshots.

Expected result: screenshots match the signed-in identity and active tenant scope.

## Troubleshooting

If local login choices are missing, confirm `.env.qa037` was copied to `.env`.

If the page stays on loading, rebuild the React admin bundle.

If the API is down, restart `uvicorn`.

If the worker exits, restart the worker command.

If Acme scope is unavailable, reseed tenants.

If the route matrix is empty for platform admin, fetch `/admin/app/migration/routes.json`.

If rollback data is missing, fetch `/admin/app/migration/rollback.json`.

If the tenant admin sees platform-only rows, stop QA and file a blocker.

If the tenant user sees admin-only rows, stop QA and file a blocker.

If cross-tenant denial reveals Globex, stop QA and file a blocker.

If the mobile layout overlaps, capture a screenshot and file a UI issue.

If tests fail, rerun only the focused failing command first.

If the full QA wrapper fails, inspect the first failing command and keep the `/tmp/qa037-*` file.

If redaction scan fails, remove unsafe saved evidence and rerun the scan.

If Playwright screenshots are blank, confirm browser automation can reach `http://127.0.0.1:8000`.

Expected result: reviewers can distinguish local setup problems from product regressions.
