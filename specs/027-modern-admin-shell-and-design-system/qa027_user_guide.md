# QA027 User Guide: Spec 027 - Modern Admin Shell And Design System

## Detailed Overview

Spec 027 introduces a modern React admin shell for the Multi-Agent Platform.

The shell is the frame around future admin pages.

It includes navigation, scope display, breadcrumbs, page actions, command search, saved filter presentation, notifications, and common status states.

The shell is available at `/admin/app`.

The older server-rendered admin pages remain active.

Domain pages such as workflow registry, operations, usage, memberships, Telegram configuration, and skill registry still open through their existing routes.

The goal is not to replace every admin screen yet.

The goal is to create a shared, understandable, safe starting point for future React admin migrations.

The backend decides which navigation items the reviewer may see.

The backend decides whether the reviewer is in platform scope or tenant scope.

The backend decides which command search results are safe.

The browser renders the data it receives.

The browser must not create hidden navigation or unsafe search destinations by itself.

The browser must not show secrets.

The browser must not show raw prompts or completions.

The browser must not show memory contents.

The browser must not show private channel messages.

The browser must not show raw provider payloads.

The browser must not show raw external tool payloads.

The browser must not show another tenant's labels to a tenant administrator.

For QA027, the main tenant is Acme.

The Acme tenant ID is `11111111-1111-1111-1111-111111111111`.

The cross-tenant safety tenant is Globex.

The Globex tenant ID is `22222222-2222-2222-2222-222222222222`.

The local test database is `multi_agent_platform_qa027`.

The local evidence directory is `.data/qa027-artifacts`.

The Playwright screenshot directory is `output/playwright/qa027_ui`.

## Who Should Use This Guide

Use this guide if you are manually reviewing the React admin shell.

Use this guide if you are not planning to edit code.

Use this guide if you need plain-language steps for browser review.

Use this guide if you are checking tenant isolation and redaction.

Use this guide if you are checking whether the new shell is understandable to platform administrators.

Use this guide if you are checking whether the shell is understandable to tenant administrators.

Developers can use `qa027.md` for the API and database command checklist.

Developers can use `qa027_ui.md` for the shorter browser walkthrough.

Non-developer reviewers can follow this file from top to bottom.

## Manual QA Prerequisites

Confirm that the repository is on branch `codex/027-modern-admin-shell-and-design-system`.

Confirm that the feature directory exists at `specs/027-modern-admin-shell-and-design-system`.

Confirm that the environment file exists at `specs/027-modern-admin-shell-and-design-system/.env.qa027`.

Confirm that the API can run locally on `http://127.0.0.1:8000`.

Confirm that PostgreSQL is available through Docker Compose.

Confirm that frontend dependencies have been installed in `frontend/admin`.

Confirm that the React assets have been built with `npm run build`.

Confirm that the Acme and Globex tenant rows have been seeded.

Confirm that no real production credential is present in `.env`.

Confirm that `.env` contains `AUTH_MODE=local_principal`.

Confirm that `.env` contains `REACT_ADMIN_ENABLED=true`.

Confirm that `.env` contains `FILESYSTEM_STORAGE_ROOT=.data/qa027-artifacts`.

Confirm that `.env` contains `multi_agent_platform_qa027`.

Confirm that `.env` contains only fake `qa027/` secret references.

Use this setup command sequence when preparing a fresh machine:

```bash
cp specs/027-modern-admin-shell-and-design-system/.env.qa027 .env
uv sync
cd frontend/admin
npm install
npm run build
cd ../..
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa027 && createdb -U postgres multi_agent_platform_qa027'
uv run alembic upgrade head
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa027 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
mkdir -p .data/qa027-artifacts output/playwright/qa027_ui
```

Start the API in one terminal:

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Start the worker in another terminal for parity with the automated gate:

```bash
uv run python -m multi_agent_platform.workers.main
```

## Step-by-Step Manual QA

Step 1: Open the shell without logging in.

Visit `http://127.0.0.1:8000/admin/app`.

You should see a denied response.

The response should mention `missing local principal header or cookie`.

You should not see the admin navigation.

You should not see `Acme`.

You should not see `Globex`.

Record a screenshot or reviewer note.

Step 2: Open the local login page.

Visit `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app`.

Choose `tenant-admin-acme`.

The browser should redirect to `/admin/app`.

You should see the page title `React Admin`.

You should see the active scope `Acme`.

You should see navigation on desktop.

You should see an `Existing console` action.

Record the authenticated shell screenshot.

Step 3: Inspect the navigation.

Find the `Multi-Agent Admin` product label.

Find the `Workflow Registry` destination.

Confirm that the link points to the existing workflow admin page.

Confirm that the page still looks like a shell rather than a marketing page.

Confirm that the navigation labels are readable.

Confirm that the content does not overlap the navigation.

Step 4: Inspect breadcrumbs and actions.

Find the breadcrumb labeled `Admin`.

Find the breadcrumb labeled `React Admin`.

Find the action labeled `Existing console`.

Find the action labeled `Workflows`.

Confirm that these actions are links, not unsafe browser-generated commands.

Confirm that the notification says existing pages remain active.

Step 5: Use command search.

Click the search input labeled `Search authorized admin destinations`.

Type `workflow`.

Confirm that `Workflow Registry` appears.

Confirm that `Open Workflows` appears as the description.

Confirm that no Globex label appears.

Confirm that no raw payload appears.

Record the command search screenshot.

Step 6: Inspect saved filters.

Find the saved filters panel.

If there are no saved filters, the panel should say that saved filters from existing admin pages will appear when available.

The panel should not expose raw criteria.

The panel should not create unvalidated destinations in the browser.

Step 7: Inspect the common state panel.

Find the partial-data state.

The state should use safe language.

The state should not include a stack trace.

The state should not include a raw exception message.

The state should not include secrets.

Step 8: Check mobile layout.

Resize the browser to a narrow width.

Find the menu icon button.

Open the mobile navigation drawer.

Confirm that navigation remains readable.

Confirm that the active scope remains visible.

Confirm that text does not overlap.

Confirm that the drawer does not hide all primary actions.

Record a reviewer note.

Step 9: Check keyboard navigation.

Reload `/admin/app`.

Press Tab repeatedly.

Confirm that focus is visible.

Confirm that focus reaches the menu button, command search, actions, and links.

Open the drawer and press Escape.

Confirm that the drawer closes or focus returns safely.

Record a reviewer note.

Step 10: Check disabled React route fallback.

Visit `http://127.0.0.1:8000/admin/app/workflows`.

Confirm that the page says `React route not migrated`.

Confirm that the page offers `Open existing page`.

Confirm that the link points to `/admin/workflows/ui`.

This is expected behavior for Spec 027.

Step 11: Check cross-tenant denial.

While still logged in as Acme, visit `http://127.0.0.1:8000/admin/app/bootstrap.json?tenant_id=22222222-2222-2222-2222-222222222222`.

Confirm that the request is denied.

Confirm that the response does not include `Globex`.

Record a reviewer note.

Step 12: Run the automated browser validation when possible.

Use this command:

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/027-modern-admin-shell-and-design-system/validation.yml --start-processes
```

Confirm that Playwright captures the denied, authenticated, and command search screenshots.

## Expected Results

The denied shell route returns 401 before rendering React navigation.

The authenticated shell route renders `React Admin`.

The authenticated shell route renders `Acme` for the Acme tenant admin.

The desktop layout has a persistent navigation area.

The mobile layout has a drawer navigation pattern.

The top bar shows breadcrumbs.

The top bar shows page actions.

The notification area uses safe summary copy.

The command search field is present.

Searching for `workflow` returns `Workflow Registry`.

Saved filters render as safe presentation only.

Common states render safe copy.

The disabled workflow React route keeps an existing-page fallback.

Cross-tenant bootstrap is denied.

Cross-tenant denial does not leak `Globex`.

No raw secrets are visible.

No filesystem path is visible.

No raw prompt or completion is visible.

No raw memory content is visible.

No raw provider payload is visible.

No raw tool payload is visible.

No visible text overlaps at desktop or mobile widths.

## Evidence To Capture

Capture the denied route screenshot.

Capture the authenticated shell screenshot.

Capture the command search screenshot.

Capture a mobile drawer reviewer note.

Capture a keyboard navigation reviewer note.

Capture a disabled-route fallback reviewer note.

Capture a cross-tenant denial reviewer note.

Keep automated screenshots under `output/playwright/qa027_ui`.

Keep curl evidence under `/tmp/qa027-*` when running API checks.

Keep a final reviewer summary in `specs/027-modern-admin-shell-and-design-system/pr_notes.md` if you are the implementer.

Recommended evidence paths:

- `output/playwright/qa027_ui/qa027-react-shell-denied.png`
- `output/playwright/qa027_ui/qa027-react-shell-authenticated.png`
- `output/playwright/qa027_ui/qa027-react-shell-search.png`
- `/tmp/qa027-bootstrap-acme.json`
- `/tmp/qa027-search-acme.json`
- `/tmp/qa027-cross-tenant.json`
- `/tmp/qa027-search-cross-tenant.json`

## Security And Redaction Checks

Check the shell for credential values.

Check the shell for `qa027-secret-value`.

Check the shell for local filesystem paths.

Check the shell for raw prompts.

Check the shell for raw completions.

Check the shell for memory contents.

Check the shell for private channel messages.

Check the shell for raw provider responses.

Check the shell for raw tool payloads.

Check the shell for stack traces.

Check the shell for authorization headers.

Check command search results for tenant-safe labels only.

Stop the review if any forbidden value appears.

## Tenant Isolation Checks

Review the authenticated shell as `tenant-admin-acme`.

Confirm that active scope is Acme.

Confirm that the Acme tenant ID is preserved where tenant scope is needed.

Confirm that command search does not show Globex.

Open the Globex bootstrap URL while logged in as Acme.

Confirm that the request is denied.

Confirm that the response does not mention Globex.

Repeat the local login flow as `platform-admin` if platform-scope review is required.

Confirm that platform scope does not pretend to be a tenant.

Confirm that platform-admin navigation is still backend-provided.

## Troubleshooting

If the login page does not show local principals, restart the API after copying `.env.qa027`.

If `/admin/app` shows a blank page, rebuild React assets with `cd frontend/admin && npm run build`.

If styling is missing, verify that `/admin/static/react` assets are available.

If Acme does not appear, confirm the Acme tenant row exists in `multi_agent_platform_qa027`.

If command search does not return Workflow Registry, inspect the browser network call to `/admin/app/search.json`.

If search returns denied, confirm the login cookie belongs to `tenant-admin-acme`.

If Globex appears during an Acme tenant review, stop and report a tenant isolation failure.

If any secret-like value appears, stop and report a redaction failure.

If mobile text overlaps, capture the screenshot and report a responsive layout failure.

If keyboard focus disappears, report an accessibility failure.

If automated Playwright validation fails at startup, confirm Docker PostgreSQL is running.

If full quality gates fail, inspect the first failing command and do not accept QA027 until it passes.

The main quality commands are:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
cd frontend/admin
npm run typecheck
npm run test
npm run build
cd ../..
```
