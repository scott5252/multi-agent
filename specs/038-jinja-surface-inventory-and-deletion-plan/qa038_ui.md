# QA038 UI Walkthrough: Jinja Surface Inventory And Deletion Plan

## Goal

Validate the browser-first React migration dashboard for QA038.

This walkthrough proves that the Jinja inventory is visible to reviewers, grouped by future removal spec, and safe to inspect before any deletion starts.

The reviewer should capture screenshots in `output/playwright/qa038_ui`.

## How To Use This Guide

Start from a clean QA038 environment.

Copy `specs/038-jinja-surface-inventory-and-deletion-plan/.env.qa038` to `.env`.

Run the API on `127.0.0.1:8000`.

Run the worker in a second terminal.

Build the React admin bundle before opening the browser.

Do not use production identities, live external systems, or real credentials.

Expected: the browser uses only local-principal sessions.

What is happening: the reviewer opens the same React assets served by the FastAPI app.

Why this matters: screenshots must reflect the production code path without production data.

## Environment Setup

Prepare dependencies and assets.

```bash
test ! -f .env || test -f .env.autopilot-backup || cp .env .env.autopilot-backup
cp specs/038-jinja-surface-inventory-and-deletion-plan/.env.qa038 .env
uv sync
cd frontend/admin && npm install && npm run build && cd ../..
```

Expected: Vite writes assets under `src/multi_agent_platform/web_admin/static/react`.

What is happening: the React bundle is compiled before the server tries to serve it.

Why this matters: stale assets can hide the inventory panel.

Reset the QA database and seed tenants.

```bash
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa038 && createdb -U postgres multi_agent_platform_qa038'
uv run alembic upgrade head
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa038 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
mkdir -p output/playwright/qa038_ui
```

Expected: only `multi_agent_platform_qa038` is reset.

What is happening: tenant scope tests use deterministic Acme and Globex rows.

Why this matters: cross-tenant denial must not depend on a developer local database.

Start local processes.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

```bash
uv run python -m multi_agent_platform.workers.main
```

Expected: `http://127.0.0.1:8000/health/live` returns a healthy response.

What is happening: the browser uses the local API and local auth helpers.

Why this matters: UI checks exercise backend authorization, not static fixtures.

## Browser Walkthrough

Open the local login page.

```text
http://127.0.0.1:8000/auth/local-login
```

Expected: local-principal choices are shown.

What is happening: the app offers deterministic local identities from `.env.qa038`.

Why this matters: reviewers can switch roles without Auth0.

Select `platform-admin`.

Open the migration page.

```text
http://127.0.0.1:8000/admin/app/migration
```

Expected: the page heading includes `Migration` and the dashboard loads without a browser error.

What is happening: the React route requests migration shell, dashboard, route groups, rollback, and Jinja inventory data.

Why this matters: the inventory is reviewed in the same route operators use for migration hardening.

Capture `qa038-react-migration-platform.png`.

Review the summary header.

Expected: the summary mentions Jinja inventory totals and blocked items.

What is happening: `MigrationSummaryHeader` reads inventory summary data from the backend dashboard.

Why this matters: reviewers can see deletion readiness before opening detailed groups.

Review the `Deletion readiness` section.

Expected: the panel shows template, route, asset, direct-link, blocked, and safe counts.

What is happening: the React panel renders `JinjaInventoryDashboard.summary`.

Why this matters: the first reviewer scan should show that no deletion is currently approved.

Review group headings.

Expected: groups are labeled for specs 039 through 047, including shell auth, workflows, governance, skills, test bench, operations usage, channels memberships, user runs, and Jinja infrastructure.

What is happening: the scanner groups inventory by planned removal spec.

Why this matters: each future deletion task has a bounded owner.

Review representative rows.

Expected: rows show surface label, item type, repo-relative path, replacement target, readiness classification, notes, evidence references, and blocker references.

What is happening: the table displays the first rows for each group.

Why this matters: reviewers can inspect concrete surfaces without opening raw scanner output.

Review readiness badges.

Expected: badges include `Blocked`, `Compatibility needed`, and `Parity missing`; no badge says `Safe to delete` for this spec.

What is happening: all inventory items remain retained until later specs prove parity.

Why this matters: Spec 038 is inventory only.

Review source paths.

Expected: paths look like `src/multi_agent_platform/...` or `specs/...`, not local absolute paths.

What is happening: the scanner serializes repo-relative paths only.

Why this matters: screenshot and JSON evidence should not expose workstation locations.

Review evidence references.

Expected: evidence labels look like `scanner-qa038`, `template-response-scan`, `asset-usage-scan`, or spec evidence ids.

What is happening: the scanner emits compact evidence identifiers rather than raw payloads.

Why this matters: reviewer notes stay safe to attach to issues and pull requests.

Open developer tools network inspection if needed.

Expected: `/admin/app/migration/jinja-inventory.json` returns status 200 for the authorized role and does not include unsafe text.

What is happening: the React page uses the protected JSON route.

Why this matters: UI parity depends on backend-owned contracts rather than hard-coded fixtures.

Switch roles through the local login page.

```text
http://127.0.0.1:8000/auth/local-login
```

Expected: selecting `tenant-admin-acme` signs in as the Acme tenant administrator.

What is happening: the local-principal cookie changes role context.

Why this matters: tenant-scoped screenshots must use the same UI path as platform screenshots.

Open Acme tenant migration scope.

```text
http://127.0.0.1:8000/admin/app/migration?tenant_id=11111111-1111-1111-1111-111111111111
```

Expected: the page loads and platform-only operations deletion rows are not visible in tenant-only context.

What is happening: backend scope filtering removes platform-only inventory groups.

Why this matters: tenant reviewers should not see platform-only migration data.

Capture `qa038-react-migration-tenant.png`.

Try a Globex tenant scope while still signed in as Acme.

```text
http://127.0.0.1:8000/admin/app/migration?tenant_id=22222222-2222-2222-2222-222222222222
```

Expected: access is denied or redirected without showing Globex inventory details.

What is happening: the shell fails closed for cross-tenant requests.

Why this matters: denied states must not reveal unauthorized tenant data.

Return to platform admin and refresh.

Expected: the full inventory returns and the panel remains stable after refresh.

What is happening: the page reloads dashboard and standalone inventory data.

Why this matters: reviewer refresh flows must not lose evidence.

Inspect mobile width.

Expected: summary metrics wrap cleanly and table content remains scrollable without text overlap.

What is happening: inventory CSS uses stable grid and table wrappers.

Why this matters: UI evidence should be usable on narrow screens.

Inspect keyboard navigation.

Expected: the page can be reached, scrolled, and reviewed without trapping focus.

What is happening: the panel uses semantic section, heading, table, list, and description elements.

Why this matters: accessibility evidence is part of deletion-grade parity.

## Required Automated Evidence

Run focused UI tests.

```bash
cd frontend/admin
npm test -- --run src/components/migrationHardening/JinjaInventoryPanel.test.tsx src/components/migrationHardening/MigrationHardeningPage.test.tsx src/App.test.tsx
cd ../..
```

Expected: all focused React tests pass.

What is happening: tests render the inventory panel, migration page, and app route with mocked backend responses.

Why this matters: visible rows, blocked state, compatibility labels, and redaction-safe rendering are protected.

Run project quality gates.

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected: each command exits 0.

What is happening: linting, formatting, typing, and coverage run after UI changes.

Why this matters: browser work should not weaken backend contracts or project quality gates.

Run Playwright validation.

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui2-roadmap/038-jinja-surface-inventory-and-deletion-plan/validation.yml --start-processes
```

Expected: Playwright opens `/admin/app/migration`, sees `Migration`, and writes `qa038-react-ui2-smoke.png`.

What is happening: the generated validation manifest drives a browser against local services.

Why this matters: automated evidence confirms the page is not blank or broken.

## UI Evidence Checklist

- Capture platform migration dashboard screenshot.
- Capture tenant migration dashboard screenshot.
- Capture mobile-width inventory screenshot.
- Confirm `Deletion readiness` is visible.
- Confirm inventory summary counts are visible.
- Confirm blocked count is nonzero.
- Confirm safe-to-delete count is zero.
- Confirm at least one blocked row is visible.
- Confirm at least one compatibility-needed row is visible.
- Confirm evidence references are visible.
- Confirm source paths are repo-relative.
- Confirm no local absolute path appears.
- Confirm no unsafe marker appears.
- Confirm tenant-admin view excludes platform-only deletion inventory.
- Confirm cross-tenant view does not reveal Globex data to Acme.

## Acceptance Notes Template

```text
QA ID: qa038
Reviewer:
Browser:
Viewport:
Platform screenshot:
Tenant screenshot:
Mobile screenshot:
Playwright screenshot:
Inventory summary reviewed:
Blocked rows reviewed:
Safe-to-delete rows confirmed zero:
Tenant isolation reviewed:
Redaction reviewed:
Notes:
```

Expected: reviewer notes include screenshots and explicit no-deletion confirmation.

What is happening: UI acceptance evidence is captured in a repeatable format.

Why this matters: later deletion specs need a trusted inventory baseline.

## Troubleshooting

If the page shows a loading error, confirm the API is running and `/health/live` succeeds.

Expected: a healthy API serves React shell and JSON routes.

What is happening: the browser depends on backend routes for dashboard data.

Why this matters: a stopped API can look like a broken frontend.

If the inventory panel is missing, rebuild React assets and restart the API.

Expected: `Deletion readiness` appears after the current bundle is served.

What is happening: old static assets may not include `JinjaInventoryPanel`.

Why this matters: screenshots must represent the current code.

If tenant scope looks too broad, confirm the role selected on `/auth/local-login`.

Expected: `tenant-admin-acme` shows tenant-safe rows, while `platform-admin` can review full service-level inventory.

What is happening: local-principal state controls scope and role filtering.

Why this matters: screenshots from the wrong role can mislead reviewers.

If text overlaps on mobile width, capture the screenshot and stop before approval.

Expected: metric cards and tables remain readable with horizontal table scrolling where needed.

What is happening: inventory tables contain long repo-relative paths.

Why this matters: deletion readiness evidence must be inspectable on supported viewports.

If Playwright times out, check `/tmp/qa038-api.log` and rebuild assets.

Expected: the browser reaches `/admin/app/migration` and sees `Migration`.

What is happening: process startup, database migrations, or asset build may have failed earlier.

Why this matters: the UI runner should only fail for real product issues after setup is healthy.

## Related Files

- `specs/038-jinja-surface-inventory-and-deletion-plan/qa038.md`.
- `specs/038-jinja-surface-inventory-and-deletion-plan/qa038_user_guide.md`.
- `specs/038-jinja-surface-inventory-and-deletion-plan/jinja_inventory.json`.
- `frontend/admin/src/components/migrationHardening/JinjaInventoryPanel.tsx`.
- `frontend/admin/src/components/migrationHardening/MigrationHardeningPage.tsx`.
- `frontend/admin/src/styles/admin.css`.
- `tests/integration/api/test_admin_react_migration_inventory_routes.py`.
