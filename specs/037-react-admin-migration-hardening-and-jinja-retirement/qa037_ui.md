# QA037 UI Walkthrough: React Admin Migration Hardening And Jinja Retirement

## Goal

Validate the browser-first React migration hardening dashboard for QA037.

The walkthrough covers `/admin/app`, `/admin/app/migration`, platform review, tenant administrator review, tenant user review, rollback evidence, route parity evidence, accessibility cues, and redaction expectations.

Use this walkthrough with the automated Playwright command in `validation.yml`.

The reviewer should capture screenshots in `output/playwright/qa037_ui`.

## How To Use This Guide

Start from a clean QA037 environment.

Copy `specs/037-react-admin-migration-hardening-and-jinja-retirement/.env.qa037` to `.env`.

Run the API on `127.0.0.1:8000`.

Run the worker in a second terminal.

Build the React admin bundle before opening the browser.

Do not use production identities or live external systems.

Expected: the browser uses only local-principal sessions.

What is happening: the reviewer opens the same React assets served by the FastAPI app.

Why this matters: rendered screenshots must reflect the production code path without production data.

## Environment Setup

Prepare dependencies and assets.

```bash
test ! -f .env || test -f .env.autopilot-backup || cp .env .env.autopilot-backup
cp specs/037-react-admin-migration-hardening-and-jinja-retirement/.env.qa037 .env
uv sync
cd frontend/admin && npm install && npm run build && cd ../..
```

Expected: Vite writes assets under `src/multi_agent_platform/web_admin/static/react`.

What is happening: the React bundle is compiled before the server tries to serve it.

Why this matters: a stale or missing asset would hide actual UI behavior.

Reset the QA database and seed tenants.

```bash
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa037 && createdb -U postgres multi_agent_platform_qa037'
uv run alembic upgrade head
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa037 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
mkdir -p output/playwright/qa037_ui
```

Expected: only `multi_agent_platform_qa037` is reset.

What is happening: tenant scope tests use deterministic Acme and Globex rows.

Why this matters: cross-tenant denial must not depend on a developer's local database.

Start local processes.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

```bash
uv run python -m multi_agent_platform.workers.main
```

Expected: `http://127.0.0.1:8000/health/live` returns a healthy response.

What is happening: the browser will use the local API and local auth helpers.

Why this matters: UI checks must exercise backend authorization, not static fixtures.

## Browser Walkthrough

Open the login page.

```text
http://127.0.0.1:8000/auth/local-login
```

Expected: local-principal choices are shown.

What is happening: the app offers deterministic local identities from `.env.qa037`.

Why this matters: reviewers can switch roles without Auth0.

Select `platform-admin`.

Open the migration landing page.

```text
http://127.0.0.1:8000/admin/app
```

Expected: the page heading reads `React Admin Migration Hardening`.

What is happening: `/admin/app` renders the standard React shell and loads migration dashboard JSON.

Why this matters: QA037 makes migration hardening the first React admin landing experience.

Capture `qa037-react-home-platform.png`.

Confirm the summary row.

Expected: route count, React primary count, retained fallback count, and blocked count are visible.

What is happening: the React summary mirrors backend route inventory projections.

Why this matters: reviewers can quickly see whether any route is blocked before release.

Review route parity.

Expected: route groups for foundation, operations/workflows, governance/skills/tests, and people/usage/channels are visible for platform admin.

What is happening: platform admin sees all route groups.

Why this matters: platform operators need full migration visibility.

Review retained fallbacks.

Expected: Operations workbench and Workflow builder show retained fallback notices.

What is happening: routes that still require a soak window are kept explicit.

Why this matters: the UI must not imply destructive Jinja deletion before evidence is complete.

Open the direct migration route.

```text
http://127.0.0.1:8000/admin/app/migration
```

Expected: the same migration hardening dashboard appears.

What is happening: direct links preserve the migration page route.

Why this matters: reviewers and operators can bookmark the migration page.

Capture `qa037-react-migration-platform.png`.

Review the rollback panel.

Expected: feature flag label, asset version label, owner, steps, verification steps, and audit reference are visible.

What is happening: rollback data comes from `/admin/app/migration/rollback.json`.

Why this matters: route retirement is not approved without a visible rollback path.

Review performance evidence.

Expected: bootstrap, interactive, and asset budget rows show passing status.

What is happening: deterministic QA037 measurements are shown as safe summaries.

Why this matters: landing on the migration dashboard must remain responsive.

Review accessibility evidence.

Expected: keyboard, focus, landmarks, labels, contrast states, text overlap, desktop, and mobile coverage are visible.

What is happening: reviewers can inspect accessibility-oriented coverage without opening raw audit output.

Why this matters: migration signoff requires browser usability, not just API success.

Review sweeps.

Expected: redaction and tenant isolation sweeps show zero unsafe matches.

What is happening: safe summary rows are rendered from backend projection data.

Why this matters: evidence must be useful while keeping sensitive data hidden.

Switch to `tenant-admin-acme`.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/migration?tenant_id=11111111-1111-1111-1111-111111111111
```

Expected: after sign-in, the dashboard shows Acme scope.

What is happening: the active scope is constrained to Acme.

Why this matters: tenant administrators must not see platform-only rows.

Capture `qa037-react-migration-tenant-admin.png`.

Confirm tenant-safe filtering.

Expected: tenant and mixed rows remain visible; platform-only operations rows are absent.

What is happening: backend projection filters by actor role and active scope.

Why this matters: route inventory can include platform-only content without tenant leakage.

Switch to `tenant-user-acme`.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/migration?tenant_id=11111111-1111-1111-1111-111111111111
```

Expected: tenant user sees user-safe migration coverage and a limited-scope state.

What is happening: tenant user rendering uses the tenant-user React shell branch.

Why this matters: user-safe briefing/channel context can remain available without admin route details.

Capture `qa037-react-migration-tenant-user.png`.

Try cross-tenant access as Acme tenant admin.

```text
http://127.0.0.1:8000/admin/app/migration?tenant_id=22222222-2222-2222-2222-222222222222
```

Expected: the request is denied and does not reveal the unauthorized tenant label.

What is happening: scope resolution fails closed before dashboard data is projected.

Why this matters: direct links cannot bypass tenant isolation.

Capture `qa037-react-migration-denied.png`.

Inspect mobile layout.

Set viewport to approximately `390x844` and reload `/admin/app/migration`.

Expected: summary metrics stack, route table remains horizontally scrollable, and text does not overlap.

What is happening: migration panels use stable grid and table dimensions.

Why this matters: QA037 requires desktop and mobile evidence before route retirement review.

Capture `qa037-react-migration-mobile.png`.

## Required Automated Evidence

Run frontend checks.

```bash
cd frontend/admin && npm run typecheck && npm run test && npm run build && cd ../..
```

Expected: all frontend checks pass.

What is happening: React types, component tests, and production build are verified.

Why this matters: browser behavior must remain covered after migration hardening.

Run focused backend checks.

```bash
uv run pytest --no-cov tests/unit/api/test_admin_migration_hardening_react_schema.py tests/unit/admin/test_migration_hardening_service.py tests/performance/migration_hardening/test_react_migration_hardening_queries.py tests/contract/test_admin_react_contract.py tests/integration/test_admin_react_routes.py
```

Expected: focused backend checks pass.

What is happening: API contracts, route policies, and local/auth0-shaped paths are validated.

Why this matters: the browser page depends on safe backend projections.

Run full quality checks.

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected: all quality gates pass.

What is happening: QA037 is checked against the same project-wide quality bar.

Why this matters: final migration hardening should not make unrelated project quality worse.

Run automated browser validation.

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/037-react-admin-migration-hardening-and-jinja-retirement/validation.yml --start-processes
```

Expected: screenshots are written to `output/playwright/qa037_ui`.

What is happening: Playwright logs in with local principals and checks key text in real browser pages.

Why this matters: manual review and automation see the same screens.

## UI Evidence Checklist

- `qa037-react-home-platform.png`
- `qa037-react-migration-platform.png`
- `qa037-react-migration-tenant-admin.png`
- `qa037-react-migration-tenant-user.png`
- `qa037-react-migration-denied.png`
- `qa037-react-migration-mobile.png`
- Terminal output for frontend checks.
- Terminal output for focused backend checks.
- Terminal output for redaction scan.

Expected: screenshots show stable panels, readable tables, and no overlapping text.

What is happening: reviewer evidence links visual behavior back to the QA037 route inventory.

Why this matters: final migration signoff requires UI evidence, not only JSON responses.

## Acceptance Notes Template

Reviewer:

Date:

Viewport set:

Identity paths checked:

Screenshots captured:

Route groups reviewed:

Retained fallback notes reviewed:

Rollback plan reviewed:

Performance and accessibility evidence reviewed:

Redaction and tenant isolation sweeps reviewed:

Expected: all template fields are filled before signoff.

What is happening: QA notes identify exactly what was reviewed.

Why this matters: future route retirement can refer to QA037 evidence.

## Troubleshooting

If the page shows only loading text, rebuild the React bundle.

If login choices are missing, confirm `.env.qa037` is copied to `.env`.

If Acme tenant scope is unavailable, reseed tenants in `multi_agent_platform_qa037`.

If screenshots are blank, confirm the API process is still running.

If cross-tenant denial shows the other tenant label, stop QA and file a blocker.

If text overlaps on mobile, capture the screenshot and file a UI regression.

If route parity rows are missing, fetch `/admin/app/migration/routes.json` and compare JSON to the screen.

If rollback rows are missing, fetch `/admin/app/migration/rollback.json`.

Expected: troubleshooting should resolve local setup issues without production access.

What is happening: failures are narrowed to environment, process, data, or rendering causes.

Why this matters: reviewers can separate expected retained fallbacks from actual regressions.

## Related Files

- `qa037.md`
- `qa037_user_guide.md`
- `.env.qa037`
- `frontend/admin/src/components/migrationHardening/MigrationHardeningPage.tsx`
- `frontend/admin/src/components/migrationHardening/MigrationParityMatrix.tsx`
- `frontend/admin/src/components/migrationHardening/RollbackPlanPanel.tsx`
- `frontend/admin/src/components/migrationHardening/PerformanceBudgetPanel.tsx`
- `frontend/admin/src/components/migrationHardening/AccessibilityAuditPanel.tsx`
- `frontend/admin/src/components/migrationHardening/MigrationSweepPanel.tsx`
- `output/playwright/qa037_ui`

Expected: reviewer evidence maps back to implementation and QA files.

What is happening: documentation, screenshots, and code remain traceable.

Why this matters: QA037 is the final checkpoint for the React admin migration roadmap.
