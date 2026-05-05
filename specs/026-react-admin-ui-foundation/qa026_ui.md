# QA026 UI: React Admin UI Foundation

## Goal

Use a browser to verify that QA026 adds an authenticated React admin shell at
`/admin/app` while preserving the existing server-rendered admin console.

This walkthrough focuses on what a reviewer can see and capture.

The React shell should show safe identity, scope, navigation, version, feature
flag, and asset-state information.

Future domain pages should still route reviewers back to the existing Jinja
admin pages until later migration specs explicitly enable them.

## How To Use This Guide

Start from a clean local checkout.

Use `.env.qa026`.

Run the setup commands before opening a browser.

Use a normal browser session or the Playwright validation command.

Capture screenshots under `/tmp/qa026-*` or review the automated screenshots
under `output/playwright/qa026_ui`.

Do not use real credentials.

Do not paste real customer data into any page.

Keep this walkthrough beside `qa026.md`.

The command-line guide proves route and payload behavior.

This UI guide proves browser-visible behavior.

## Environment Setup

Prepare the application.

```bash
test ! -f .env || test -f .env.autopilot-backup || cp .env .env.autopilot-backup
cp specs/026-react-admin-ui-foundation/.env.qa026 .env
uv sync
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa026 && createdb -U postgres multi_agent_platform_qa026'
uv run alembic upgrade head
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa026 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
mkdir -p .data/qa026-artifacts output/playwright/qa026_ui
```

Expected:

- The QA026 database is ready.
- The Acme and Globex tenant rows exist.
- The local-principal catalog from `.env.qa026` is active.

Build the React assets.

```bash
cd frontend/admin
npm install
npm run build
cd ../..
```

Expected:

- Static React assets are available from `/admin/static/react`.
- The API can serve the React host page without a separate Vite dev server.

Start the API.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected:

- The API is reachable at `http://127.0.0.1:8000`.
- The browser can open `http://127.0.0.1:8000/auth/local-login`.

Optional worker terminal.

```bash
uv run python -m multi_agent_platform.workers.main
```

Expected:

- The worker starts, but QA026 browser checks do not depend on it.

## Browser Walkthrough

1. Open the denied page first.

URL:

```text
http://127.0.0.1:8000/admin/app
```

Expected:

- The page does not show the React admin shell.
- The browser shows a safe `missing local principal header or cookie` response.
- No tenant label appears.

What is happening:

- The backend rejects browser access before any bootstrap data is returned.

Why this matters:

- The React mount does not bypass existing authentication.

Evidence:

- Save a screenshot as `/tmp/qa026-denied-browser.png`.

2. Open the local login page.

URL:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app
```

Expected:

- The page title is `Choose a local principal`.
- `Acme Tenant Admin` is visible.
- `Acme Tenant User` is visible.
- `Globex Tenant Admin` is visible.
- `Platform Admin` is visible.

What is happening:

- Local QA mode lists deterministic principals from `.env.qa026`.

Why this matters:

- Reviewers can test role and tenant differences without Auth0.

Evidence:

- Save a screenshot as `/tmp/qa026-local-login.png`.

3. Sign in as `tenant-admin-acme`.

Action:

- In the `Acme Tenant Admin` card, click `Sign In`.

Expected:

- The browser redirects to `/admin/app`.
- The React shell loads.
- The top content shows `React Admin`.
- The sidebar brand shows `React Foundation`.
- The page includes an `Existing console` link.

What is happening:

- The local login route sets the QA cookie and the React app requests bootstrap metadata from the backend.

Why this matters:

- Authenticated browser sessions use the same protected FastAPI route as curl checks.

Evidence:

- Save a screenshot as `/tmp/qa026-react-admin-acme.png`.

4. Review the scope summary.

Expected:

- The active scope reads as Acme or as the Acme tenant scope.
- The displayed principal is the Acme tenant admin.
- No token subject, raw authorization header, prompt body, completion body, memory content, or secret value appears.

What is happening:

- The browser renders only the safe summary returned by `/admin/app/bootstrap.json`.

Why this matters:

- The React shell must not expand its bootstrap contract into sensitive fields.

Evidence:

- Add a reviewer note that the scope and principal display are safe.

5. Review navigation.

Expected:

- Navigation groups are visible.
- Navigation items link to existing authorized Jinja pages.
- Items are labeled as existing pages.
- The React shell does not pretend domain pages have migrated.

What is happening:

- The backend converts the existing admin navigation model into a React-safe payload.

Why this matters:

- QA026 is a foundation spec and should preserve existing domain workflows.

Evidence:

- Save a screenshot as `/tmp/qa026-navigation.png`.

6. Open the existing console link.

Action:

- Click `Existing console`.

Expected:

- The browser opens `/admin`.
- The existing server-rendered admin shell remains available.
- The page is still protected by the local-principal cookie.

What is happening:

- The React shell points back to the current Jinja admin home instead of replacing it.

Why this matters:

- The migration is reversible and does not remove the old console.

Evidence:

- Save a screenshot as `/tmp/qa026-existing-console.png`.

7. Return to the React shell.

URL:

```text
http://127.0.0.1:8000/admin/app
```

Expected:

- The React shell opens without another login prompt.
- The cookie-based local principal is still accepted.

What is happening:

- The browser sends the local QA cookie that was set during login.

Why this matters:

- Browser validation can use the same local-principal flow later React specs will reuse.

8. Open a disabled future React route.

URL:

```text
http://127.0.0.1:8000/admin/app/workflows
```

Expected:

- The page shows `React route not migrated`.
- The page explains that this admin area still opens in the existing authorized console.
- The page includes `Open existing page`.

What is happening:

- The React app detects that `workflows` is a future route and renders a safe fallback state.

Why this matters:

- Future routes stay disabled until their own specs pass validation.

Evidence:

- Save a screenshot as `/tmp/qa026-disabled-workflows.png`.

9. Click `Open existing page`.

Expected:

- The browser opens `/admin/workflows/ui`.
- The existing workflow studio route remains reachable.
- Any tenant scope already authorized by the backend remains controlled by the server-rendered page.

What is happening:

- The disabled route points reviewers to the Jinja route that still owns the workflow domain.

Why this matters:

- QA026 does not silently change domain behavior.

10. Switch to `tenant-user-acme`.

Action:

- Open `http://127.0.0.1:8000/auth/local-logout?redirect_to=/auth/local-login?redirect_to=/admin/app`.
- Return to `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app`.
- Click `Sign In` in the `Acme Tenant User` card.

Expected:

- The browser cannot open the React admin shell.
- The response is denied.
- No admin navigation or tenant list is displayed.

What is happening:

- The backend treats the React shell as an admin surface and rejects the non-admin principal.

Why this matters:

- The new route does not broaden admin visibility to ordinary tenant users.

Evidence:

- Save a screenshot as `/tmp/qa026-tenant-user-denied.png`.

11. Switch to `tenant-admin-globex`.

Action:

- Sign out.
- Sign in as `Globex Tenant Admin`.
- Open `/admin/app`.

Expected:

- The React shell opens for the Globex administrator.
- The active scope is Globex.
- Acme-only scope details are not shown.

What is happening:

- Each tenant admin receives bootstrap metadata for their own tenant context.

Why this matters:

- QA026 must keep tenant-specific browser state isolated.

Evidence:

- Save a screenshot as `/tmp/qa026-globex-admin.png`.

12. Check built asset unavailable behavior if needed.

Action:

- Stop the API.
- Move `src/multi_agent_platform/web_admin/static/react/manifest.json` aside.
- Restart the API.
- Sign in again and open `/admin/app`.
- Restore the manifest and rebuild after the check.

Expected:

- The fallback HTML says React admin built assets are unavailable.
- The message uses a normalized reason such as `manifest_missing`.
- The page does not show filesystem paths.

What is happening:

- The Jinja host template renders a safe fallback before browser JavaScript can load.

Why this matters:

- Broken builds should fail safely.

Evidence:

- Save a screenshot as `/tmp/qa026-missing-manifest.png`.

## Required Automated Evidence

Run the focused backend tests.

```bash
uv run pytest --no-cov \
  tests/unit/api/test_admin_react_schema.py \
  tests/contract/test_admin_react_contract.py \
  tests/integration/test_admin_react_routes.py
```

Expected:

- The route and contract tests pass.

Run the frontend checks.

```bash
cd frontend/admin
npm run typecheck
npm run test
npm run build
cd ../..
```

Expected:

- TypeScript typecheck passes.
- Vitest tests pass.
- Vite build passes.

Run the full required quality commands.

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected:

- Ruff, format, mypy, and full coverage gates pass.

Run automated Playwright validation.

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/026-react-admin-ui-foundation/validation.yml --start-processes
```

Expected:

- Playwright captures denied, authenticated, and disabled-route screenshots.
- Screenshots are saved under `output/playwright/qa026_ui`.

## UI Evidence Checklist

- `/tmp/qa026-denied-browser.png` shows unauthenticated denial.
- `/tmp/qa026-local-login.png` shows deterministic local principals.
- `/tmp/qa026-react-admin-acme.png` shows the authenticated React shell.
- `/tmp/qa026-navigation.png` shows existing-page navigation.
- `/tmp/qa026-existing-console.png` shows Jinja console preservation.
- `/tmp/qa026-disabled-workflows.png` shows the disabled future route.
- `/tmp/qa026-tenant-user-denied.png` shows non-admin denial.
- `/tmp/qa026-globex-admin.png` shows tenant-specific scope behavior.
- `output/playwright/qa026_ui/qa026-react-ui-denied.png` is captured by automation.
- `output/playwright/qa026_ui/qa026-react-ui-authenticated.png` is captured by automation.
- `output/playwright/qa026_ui/qa026-react-ui-disabled-route.png` is captured by automation.

## Acceptance Notes Template

```text
QA026 UI reviewer:
Browser: local Chromium or equivalent
Login principal used first: tenant-admin-acme
Denied screenshot: /tmp/qa026-denied-browser.png
Authenticated screenshot: /tmp/qa026-react-admin-acme.png
Disabled route screenshot: /tmp/qa026-disabled-workflows.png
Existing console screenshot: /tmp/qa026-existing-console.png
Tenant isolation screenshot: /tmp/qa026-globex-admin.png
Automated Playwright output: output/playwright/qa026_ui
Result: pass or fail with notes
```

Expected:

- A reviewer can map each screenshot to one QA requirement.

## Troubleshooting

If the login page is missing, confirm `.env.qa026` is copied to `.env`.

If the login page shows no principals, confirm `LOCAL_PRINCIPAL_CATALOG_JSON` is intact.

If `tenant-admin-acme` is denied, confirm the Acme tenant seed row exists.

If the React shell keeps loading, open developer tools and check `/admin/app/bootstrap.json`.

If assets are unavailable, run `cd frontend/admin && npm run build`.

If Playwright cannot find `Sign In`, confirm the local login page lists `Acme Tenant Admin`.

If the disabled route does not show `React route not migrated`, confirm browser JavaScript loaded and the URL is `/admin/app/workflows`.

If screenshots contain fake raw secret values, treat the run as failed and inspect bootstrap, config, manifest, and logs.

If the old admin console stops opening, treat the run as failed because QA026 must preserve Jinja fallbacks.

## Related Files

- `specs/026-react-admin-ui-foundation/qa026.md`
- `specs/026-react-admin-ui-foundation/qa026_user_guide.md`
- `specs/026-react-admin-ui-foundation/.env.qa026`
- `frontend/admin/src/App.tsx`
- `frontend/admin/src/components/AdminShell.tsx`
- `frontend/admin/src/routes.tsx`
- `src/multi_agent_platform/api/routers/admin_react.py`
- `src/multi_agent_platform/web_admin/templates/admin_react/app.html`
- `specs/_autopilot/react-ui-roadmap/026-react-admin-ui-foundation/validation.yml`
