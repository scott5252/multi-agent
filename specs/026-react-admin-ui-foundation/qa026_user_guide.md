# QA026 User Guide: Spec 026 - React Admin UI Foundation

## Detailed Overview

QA026 introduces the first React-based admin shell for the platform.

The shell lives at `/admin/app`.

It is a foundation for later React migration specs.

It is not a replacement for the existing admin console yet.

The current admin console is still built with server-rendered Jinja pages.

Those Jinja pages remain available.

The React shell gives reviewers a safe browser entry point.

It proves that React can be mounted inside the existing FastAPI application.

It proves that browser assets can be served from `/admin/static/react`.

It proves that the backend owns the bootstrap contract.

The bootstrap contract is the data the browser needs before it renders the admin shell.

That data includes a safe principal summary.

That data includes the active admin scope.

That data includes available scope choices.

That data includes authorized navigation items.

That data includes feature flags.

That data includes version metadata.

That data includes a public asset manifest summary.

It must not include raw credentials.

It must not include authorization headers.

It must not include raw prompts.

It must not include raw completions.

It must not include memory contents.

It must not include private external payloads.

The React shell is protected by the same backend authorization model as the Jinja admin console.

An unauthenticated browser should not see the shell.

A non-admin tenant user should not see the shell.

A tenant admin should see only their own tenant scope.

A platform admin can use platform scope.

The shell is deliberately modest.

Its job is to establish the safe app frame.

Its job is to establish generated TypeScript contracts.

Its job is to establish Vite build output.

Its job is to establish Playwright validation.

Its job is to establish reversible migration guardrails.

Future specs will migrate individual domain pages.

QA026 keeps those future routes disabled.

When a reviewer opens a future route such as `/admin/app/workflows`, the React app should explain that the route has not migrated.

The page should offer a link back to the existing authorized page.

That behavior protects current workflows during the migration.

The most important reviewer question is simple.

Can the React shell open safely for the right people.

Can it fail closed for the wrong people.

Can it preserve the existing admin console.

Can it avoid leaking sensitive data.

## Who Should Use This Guide

Use this guide if you are manually reviewing QA026.

Use this guide if you want a plain-language explanation before running command checks.

Use this guide if you are a product reviewer checking the visible behavior.

Use this guide if you are a QA reviewer gathering screenshots.

Use this guide if you are a security reviewer focused on redaction.

Use this guide if you are a tenant-isolation reviewer.

Use this guide if you are validating a pull request.

Use this guide if you need to explain the React migration guardrails to another reviewer.

Developers should still run the focused tests.

Developers should still run the full quality commands.

Non-developers can rely on the browser sections and evidence checklist.

The companion `qa026.md` is the command-line QA guide.

The companion `qa026_ui.md` is the browser walkthrough.

The companion `.env.qa026` file defines the local QA environment.

The validation manifest drives automated API and Playwright checks.

## Manual QA Prerequisites

You need the repository checkout.

You need Docker available.

You need the `uv` command.

You need Node available for the React workspace.

Use Node `20.19` or newer and lower than `26`.

You need a browser.

You do not need Auth0 credentials.

You do not need OpenAI credentials.

You do not need Telegram credentials.

You do not need connector credentials.

You do not need real customer data.

Use only the local QA principals in `.env.qa026`.

Use only the QA database named `multi_agent_platform_qa026`.

Use only fake `qa026/` secret references.

Back up an existing `.env` file before copying `.env.qa026`.

Run database migrations before opening the browser.

Seed the Acme and Globex tenants before testing tenant behavior.

Build the React assets before testing the full browser shell.

Start the API on `http://127.0.0.1:8000`.

The worker can run, but QA026 does not depend on worker behavior.

Prepare a folder or notes file for screenshots.

The suggested evidence prefix is `/tmp/qa026-`.

Automated Playwright screenshots are stored under `output/playwright/qa026_ui`.

## Step-by-Step Manual QA

Step 1: Copy `specs/026-react-admin-ui-foundation/.env.qa026` to `.env`.

Expected: The application runs in local-principal mode.

Step 2: Run `uv sync`.

Expected: Python dependencies are installed.

Step 3: Start PostgreSQL with Docker Compose.

Expected: The local PostgreSQL service is reachable.

Step 4: Drop and recreate `multi_agent_platform_qa026`.

Expected: The QA database starts clean.

Step 5: Run Alembic migrations.

Expected: The database schema is current.

Step 6: Seed the Acme and Globex tenants.

Expected: Acme uses tenant id `11111111-1111-1111-1111-111111111111`.

Expected: Globex uses tenant id `22222222-2222-2222-2222-222222222222`.

Step 7: Run `npm install` inside `frontend/admin`.

Expected: The React workspace dependencies install without vulnerabilities that block the run.

Step 8: Run `npm run build` inside `frontend/admin`.

Expected: Static React assets are written under `src/multi_agent_platform/web_admin/static/react`.

Step 9: Start the FastAPI server.

Expected: `http://127.0.0.1:8000/health/live` responds.

Step 10: Open `http://127.0.0.1:8000/admin/app` before signing in.

Expected: The browser shows a safe missing local principal message.

Step 11: Save a denied screenshot.

Expected: The screenshot does not show tenant navigation.

Step 12: Open `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app`.

Expected: The local login page appears.

Step 13: Review the listed local principals.

Expected: `Acme Tenant Admin` is visible.

Expected: `Acme Tenant User` is visible.

Expected: `Globex Tenant Admin` is visible.

Expected: `Platform Admin` is visible.

Step 14: Sign in as `Acme Tenant Admin`.

Expected: The browser redirects to `/admin/app`.

Step 15: Review the React shell heading.

Expected: The page shows `React Admin`.

Step 16: Review the shell brand.

Expected: The sidebar shows `React Foundation`.

Step 17: Review the topbar.

Expected: The topbar includes `Existing console`.

Step 18: Review the scope summary.

Expected: The active tenant is Acme.

Step 19: Review the navigation list.

Expected: Navigation links point to existing admin pages.

Step 20: Click `Existing console`.

Expected: The existing server-rendered `/admin` console opens.

Step 21: Return to `http://127.0.0.1:8000/admin/app`.

Expected: The React shell opens again without another login prompt.

Step 22: Open `http://127.0.0.1:8000/admin/app/workflows`.

Expected: The page shows `React route not migrated`.

Step 23: Click `Open existing page`.

Expected: The browser opens `/admin/workflows/ui`.

Step 24: Sign out.

Expected: The local QA cookie is cleared.

Step 25: Sign in as `Acme Tenant User`.

Expected: The React admin shell is denied.

Step 26: Sign out again.

Expected: The browser is ready for the next principal.

Step 27: Sign in as `Globex Tenant Admin`.

Expected: The React shell opens for Globex.

Step 28: Compare the visible tenant scope.

Expected: Globex scope is visible and Acme scope details are not shown.

Step 29: Run the focused backend tests.

Expected: Schema, contract, and route tests pass.

Step 30: Run the frontend typecheck, tests, and build.

Expected: All frontend checks pass.

Step 31: Run the QA document validator.

Expected: QA documents pass the local validation script.

Step 32: Run the Spec QA validation manifest.

Expected: API, database, and quality commands pass.

Step 33: Run the Playwright validation manifest.

Expected: Denied, authenticated, and disabled-route screenshots are captured.

## Expected Results

Authenticated admin users can open `/admin/app`.

Unauthenticated requests fail with `401`.

Non-admin tenant users fail with `403`.

Cross-tenant bootstrap requests fail with `403`.

Denied responses do not leak the other tenant name.

The React shell shows safe principal data.

The React shell shows safe tenant scope data.

The React shell shows authorized navigation.

The React shell links back to the existing admin console.

The existing admin console remains available.

Future React domain routes remain disabled.

Disabled future routes show a safe fallback message.

Disabled future routes link to existing Jinja pages.

Manifest summaries use public asset paths.

Manifest summaries do not show filesystem paths.

Missing manifest behavior uses a safe unavailable state.

Generated TypeScript contracts stay in sync with backend schemas.

Frontend tests pass.

Backend tests pass.

Full quality gates pass.

## Evidence To Capture

Capture `/tmp/qa026-denied-browser.png`.

Capture `/tmp/qa026-local-login.png`.

Capture `/tmp/qa026-react-admin-acme.png`.

Capture `/tmp/qa026-navigation.png`.

Capture `/tmp/qa026-existing-console.png`.

Capture `/tmp/qa026-disabled-workflows.png`.

Capture `/tmp/qa026-tenant-user-denied.png`.

Capture `/tmp/qa026-globex-admin.png`.

Save `/tmp/qa026-bootstrap-acme.json`.

Save `/tmp/qa026-config.json`.

Save `/tmp/qa026-manifest.json`.

Save `/tmp/qa026-denied-missing.html`.

Save `/tmp/qa026-cross-tenant.json`.

Keep `output/playwright/qa026_ui/qa026-react-ui-denied.png`.

Keep `output/playwright/qa026_ui/qa026-react-ui-authenticated.png`.

Keep `output/playwright/qa026_ui/qa026-react-ui-disabled-route.png`.

Record the focused pytest command result.

Record the frontend typecheck result.

Record the frontend test result.

Record the frontend build result.

Record the QA document validation result.

Record the Spec QA validation result.

Record the Playwright validation result.

## Security And Redaction Checks

Do not use real secrets.

Do not use real provider keys.

Do not use real Auth0 tokens.

Do not use real Telegram tokens.

Do not enter customer data.

Do not capture raw secret values in screenshots.

Check that `qa026-secret-value` is absent from app output.

Check that bootstrap JSON does not include token subjects.

Check that bootstrap JSON does not include authorization headers.

Check that bootstrap JSON does not include raw prompts.

Check that bootstrap JSON does not include raw completions.

Check that bootstrap JSON does not include memory contents.

Check that manifest JSON does not include local filesystem paths.

Check that denied cross-tenant responses do not include the other tenant label.

Check that logs under `/tmp/qa026-api.log` do not show raw secret values.

Check that Playwright screenshots do not show raw secret values.

Treat any sensitive field leak as a failed QA run.

## Tenant Isolation Checks

Acme tenant admin should see Acme scope.

Acme tenant admin should not receive Globex bootstrap data.

Globex tenant admin should see Globex scope.

Globex tenant admin should not see Acme-specific scope labels as active scope.

Tenant user should not open the admin shell.

Platform admin can open platform scope.

Tenant switching should use backend-authorized scope options.

Scope links should preserve only authorized tenant ids.

Denied pages should avoid listing tenant choices.

Cross-tenant JSON responses should avoid leaking tenant names.

Browser state should change after signing out and signing in with another local principal.

Reviewer screenshots should label which principal was used.

## Troubleshooting

If the login page returns `404`, confirm `AUTH_MODE=local_principal`.

If the shell returns `401`, sign in through the local login page.

If the shell returns `403`, choose an admin principal.

If Acme scope is missing, seed the Acme tenant row.

If Globex scope is missing, seed the Globex tenant row.

If the React app shows a loading state for too long, check `/admin/app/bootstrap.json`.

If assets are unavailable, rerun `npm run build` in `frontend/admin`.

If Node typecheck fails, rerun `npm install` in `frontend/admin`.

If Playwright cannot click the login button, confirm the principal card is visible.

If the disabled route does not show its fallback, confirm the URL starts with `/admin/app/`.

If the existing console link fails, treat it as a QA026 regression.

If a full quality gate fails in an unrelated area, record the failing command and keep QA026 focused evidence while repair continues.

If a screenshot contains a fake raw secret value, discard it and investigate the leak before accepting the run.

If the QA database was not reset, rerun the setup steps before comparing tenant results.

If `.env` was overwritten, restore `.env.autopilot-backup` after the QA run.
