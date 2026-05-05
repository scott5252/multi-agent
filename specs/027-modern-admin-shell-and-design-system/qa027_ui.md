# QA027 UI Walkthrough

## Goal

QA027 UI validation proves that the modern React admin shell is understandable, responsive, keyboard reachable, and safe for local-principal platform and tenant administrators.

The page under review is `/admin/app`.

The browser must render only metadata that the backend authorized.

The shell must show active scope, navigation, breadcrumbs, page actions, notifications, command search, saved filter presentation, common states, and fallback links to existing Jinja admin pages.

This walkthrough does not validate migrated domain pages.

This walkthrough does not create workflows, providers, credentials, Telegram settings, or connector calls.

## How To Use This Guide

Use a clean local browser profile or a private window.

Start from a fresh API process after copying `.env.qa027` to `.env`.

Capture screenshots when this guide says `Expected:`.

Record reviewer notes when this guide says `What is happening:` or `Why this matters:`.

Do not paste real secrets or private tenant data into the browser.

Keep browser zoom at 100 percent for screenshots unless testing responsive behavior.

Use the automated Playwright command at the end to capture canonical screenshots.

Expected: manual screenshots and automated screenshots agree on the key shell signals.

## Environment Setup

Prepare the local QA environment:

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

Expected: the React build succeeds and `multi_agent_platform_qa027` is migrated.

What is happening: the browser will load FastAPI-served static assets built from `frontend/admin`.

Why this matters: the reviewer sees the same asset path and settings used by the automated gate.

Start the API:

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected: `http://127.0.0.1:8000/health/live` is reachable.

Start the worker in a second terminal for parity with automated validation:

```bash
uv run python -m multi_agent_platform.workers.main
```

Expected: the worker starts and remains idle for this UI-only walkthrough.

## Browser Walkthrough

### Step 1: Denied Shell Access

Open the protected shell without logging in:

```text
http://127.0.0.1:8000/admin/app
```

Expected: the browser displays a 401 response with `missing local principal header or cookie`.

Expected: no admin navigation list appears.

What is happening: the shell route is guarded before the React app can render.

Why this matters: unauthorized users cannot see navigation labels, scope labels, command results, or fallback destinations.

Screenshot evidence: save or compare with `output/playwright/qa027_ui/qa027-react-shell-denied.png`.

### Step 2: Local Login As Acme Tenant Admin

Open the local login flow:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app
```

Select `tenant-admin-acme`.

Expected: the browser redirects to `/admin/app`.

Expected: the page heading is `React Admin`.

Expected: the scope control shows `Acme`.

Expected: the principal summary shows `Acme Tenant Admin` or `Tenant Admin` depending on the local catalog display.

What is happening: the local-principal cookie is set and the backend sends shell bootstrap metadata for the Acme tenant scope.

Why this matters: tenant admins need a persistent, obvious scope signal before using any admin area.

Screenshot evidence: save or compare with `output/playwright/qa027_ui/qa027-react-shell-authenticated.png`.

### Step 3: Review Desktop Navigation

At desktop width, inspect the left navigation.

Expected: the product label is `Multi-Agent Admin`.

Expected: navigation groups and destinations are readable.

Expected: `Workflow Registry` links to the existing workflow admin route.

Expected: labels do not overlap the content area.

What is happening: React renders the backend navigation presentation model.

Why this matters: the browser is not deciding which destinations are visible.

Reviewer note: record whether active scope and fallback labels are clear enough for a non-technical admin.

### Step 4: Review Breadcrumbs And Page Actions

Inspect the top bar.

Expected: breadcrumbs include `Admin` and `React Admin`.

Expected: the `Existing console` action links to `/admin`.

Expected: the `Workflows` action links to the existing workflow UI and preserves tenant scope when needed.

Expected: notification text says existing pages remain active.

What is happening: the shared shell provides context while keeping Jinja domain pages available.

Why this matters: Spec 027 prepares a shell; it does not retire existing admin pages.

Reviewer note: record whether the fallback route language feels clear.

### Step 5: Review Command Search

Focus the field labeled `Search authorized admin destinations`.

Type:

```text
workflow
```

Expected: `Workflow Registry` appears as a command result.

Expected: `Open Workflows` appears as the safe description.

Expected: no Globex label appears while logged in as Acme.

Expected: no raw prompt, completion, memory, provider response, credential value, or stack trace appears.

What is happening: React asks `/admin/app/search.json` for authorized command metadata.

Why this matters: command access helps navigation only if the backend keeps it scoped and redacted.

Screenshot evidence: save or compare with `output/playwright/qa027_ui/qa027-react-shell-search.png`.

### Step 6: Review Saved Filters And Common State

Inspect the saved filters panel and the state panel.

Expected: saved filters show an empty safe panel when no backend filter metadata exists.

Expected: the partial-data state uses safe summary text.

Expected: there are no stack traces or raw exception messages.

What is happening: common state components render backend-provided safe descriptors.

Why this matters: later React domain pages can reuse the same safe state language.

Reviewer note: capture a screenshot if text wraps strangely or overlaps.

### Step 7: Review Mobile Drawer

Resize the browser to a narrow mobile width.

Click the menu icon button.

Expected: the navigation drawer opens.

Expected: the active scope remains visible in the top area.

Expected: navigation text remains readable and does not overlap.

Expected: selecting a navigation link closes or leaves the drawer in an expected browser navigation state.

What is happening: the desktop sidebar collapses into an authenticated drawer.

Why this matters: admins using tablets or narrow windows must still understand where they are.

Reviewer note: capture any clipped labels or unreachable controls.

### Step 8: Keyboard Pass

Reload `/admin/app`.

Press Tab repeatedly.

Expected: focus is visible on the menu button, command input, page actions, and links.

Expected: focus order moves through the shell without disappearing.

Expected: Escape closes explicit drawers or dialogs when open.

What is happening: React primitives and shell controls expose accessible names and focus styles.

Why this matters: the design system must be safe for keyboard-only reviewers before domain pages depend on it.

Reviewer note: record the first place focus is confusing, if any.

### Step 9: Disabled React Route Fallback

Open:

```text
http://127.0.0.1:8000/admin/app/workflows
```

Expected: the page shows `React route not migrated`.

Expected: the page offers `Open existing page`.

Expected: the existing page link points to `/admin/workflows/ui`.

What is happening: a future React route is intentionally disabled and points back to the authorized server-rendered destination.

Why this matters: React shell rollout remains reversible while domain migrations are still pending.

### Step 10: Cross-Tenant Browser Check

While logged in as `tenant-admin-acme`, open:

```text
http://127.0.0.1:8000/admin/app/bootstrap.json?tenant_id=22222222-2222-2222-2222-222222222222
```

Expected: the response is denied.

Expected: `Globex` does not appear.

What is happening: the backend rejects a tenant admin trying to inspect a different tenant scope.

Why this matters: the browser shell cannot become a cross-tenant discovery surface.

## Required Automated Evidence

Run QA document validation:

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/027-modern-admin-shell-and-design-system
```

Expected: the validator passes.

Run frontend and backend checks:

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

Expected: all listed commands pass.

Run the complete Playwright UI validation:

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/027-modern-admin-shell-and-design-system/validation.yml --start-processes
```

Expected: `Playwright UI validation completed`.

Expected: `output/playwright/qa027_ui/qa027-react-shell-denied.png` exists.

Expected: `output/playwright/qa027_ui/qa027-react-shell-authenticated.png` exists.

Expected: `output/playwright/qa027_ui/qa027-react-shell-search.png` exists.

## UI Evidence Checklist

- Denied page screenshot captured.
- Authenticated shell screenshot captured.
- Command search screenshot captured.
- Mobile drawer reviewer note captured.
- Keyboard reviewer note captured.
- Fallback route reviewer note captured.
- No cross-tenant tenant label observed.
- No secret value observed.
- No local filesystem path observed.
- No raw prompt or completion observed.
- No raw provider or tool payload observed.
- No overlapping shell text observed.

Expected: every checklist item is complete before accepting QA027.

## Acceptance Notes Template

Reviewer:

Date:

Browser:

Viewport sizes checked:

Login principal:

Denied access result:

Authenticated shell result:

Command search result:

Mobile drawer result:

Keyboard result:

Fallback route result:

Screenshots:

- `output/playwright/qa027_ui/qa027-react-shell-denied.png`
- `output/playwright/qa027_ui/qa027-react-shell-authenticated.png`
- `output/playwright/qa027_ui/qa027-react-shell-search.png`

Security notes:

- No secrets observed.
- No cross-tenant data observed.
- No raw payloads observed.

## Troubleshooting

If the login page does not show `tenant-admin-acme`, confirm `.env` was copied from `.env.qa027` and restart the API.

If `/admin/app` still returns denied after login, clear cookies for `127.0.0.1` and repeat the local login flow.

If the page loads without styling, run `cd frontend/admin && npm run build`.

If command search does not update after typing, check the browser network panel for `/admin/app/search.json`.

If search returns 403, confirm the URL includes the Acme tenant scope and the Acme tenant row exists.

If text overlaps on mobile, capture the screenshot and mark the responsive check as failed.

If a screenshot includes a real local path, stop and inspect manifest sanitization before proceeding.

If Playwright times out at login, confirm the API process is using `AUTH_MODE=local_principal`.

Expected: troubleshooting resolves local setup issues without changing authorization behavior.

## Related Files

- `specs/027-modern-admin-shell-and-design-system/qa027.md`
- `specs/027-modern-admin-shell-and-design-system/qa027_user_guide.md`
- `specs/027-modern-admin-shell-and-design-system/.env.qa027`
- `specs/_autopilot/react-ui-roadmap/027-modern-admin-shell-and-design-system/validation.yml`
- `frontend/admin/src/components/shell/AdminShell.tsx`
- `frontend/admin/src/components/shell/CommandMenu.tsx`
- `frontend/admin/src/components/shell/ShellTopbar.tsx`
- `frontend/admin/src/components/shell/ShellSidebar.tsx`
- `frontend/admin/src/components/primitives/index.tsx`
- `frontend/admin/src/components/states/CommonState.tsx`
- `frontend/admin/src/styles/admin.css`
- `frontend/admin/src/styles/tokens.css`
