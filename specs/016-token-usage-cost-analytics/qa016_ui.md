# QA016 UI: Token Usage And Cost Analytics

## Goal

Validate Spec 016 through the server-rendered admin browser UI. A reviewer can
start from a clean local environment, sign in with local-principal cards, open
Usage Analytics, inspect safe rollups and event rows, create a CSV export, and
verify tenant isolation and redaction evidence without production credentials.

## How To Use This Guide

Use Terminal A for the API server.
Use Terminal B for setup and evidence commands.
Use a browser for the primary walkthrough.
Save screenshots under `output/playwright/qa016_ui`.
Save notes under `/tmp/qa016-*`.
Use `platform-admin` for platform scope checks.
Use `tenant-admin-acme` for Acme tenant checks.
Use `tenant-admin-globex` for denial checks.

## Environment Setup

### UI Setup Step 1 - Back Up Environment

```bash
test ! -f .env || cp .env .env.autopilot-backup
```

Expected: no output.

What is happening: the current `.env` is copied aside.

Why this matters: QA016 should not permanently replace local settings.

### UI Setup Step 2 - Copy QA016 Environment

```bash
cp specs/016-token-usage-cost-analytics/.env.qa016 .env
```

Expected: no output.

What is happening: local-principal auth, fake `qa016/` secret references,
`multi_agent_platform_qa016`, and `.data/qa016-artifacts` are configured.

Why this matters: the UI walkthrough must stay local and deterministic.

### UI Setup Step 3 - Install Dependencies

```bash
uv sync
```

Expected: dependency sync completes without errors.

What is happening: project dependencies are installed.

Why this matters: the API server, tests, and Playwright wrapper need the local
environment.

### UI Setup Step 4 - Start PostgreSQL

```bash
docker compose up -d postgres
```

Expected: postgres starts or is already running.

What is happening: local database infrastructure is available.

Why this matters: admin pages read persisted usage metadata.

### UI Setup Step 5 - Reset QA016 Database

```bash
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa016 && createdb -U postgres multi_agent_platform_qa016'
```

Expected: the command exits successfully.

What is happening: only the QA016 database is reset.

Why this matters: browser evidence should not mix with old local data.

### UI Setup Step 6 - Run Migrations

```bash
uv run alembic upgrade head
```

Expected: migration head is reached.

What is happening: usage analytics tables and admin dependencies are created.

Why this matters: `/admin/usage` depends on persisted tables.

### UI Setup Step 7 - Prepare Screenshot Directories

```bash
mkdir -p output/playwright/qa016_ui .data/qa016-artifacts /tmp
```

Expected: no output.

What is happening: screenshot and artifact directories are available.

Why this matters: reviewer evidence should be easy to locate.

### UI Setup Step 8 - Start API

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected: Terminal A shows the API server listening.

What is happening: the local FastAPI app is serving admin pages.

Why this matters: browser QA uses the real server-rendered UI.

## Browser Walkthrough

### Browser Step 1 - Open Local Login

Open:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/usage
```

Expected: the Local Login page appears.

What is happening: the browser uses local-principal test mode.

Why this matters: QA016 does not require Auth0 or production credentials.

### Browser Step 2 - Sign In As Platform Admin

Select `platform-admin`.

Expected: the browser redirects to `/admin/usage`.

What is happening: the platform administrator has platform usage scope.

Why this matters: platform admins must be able to review all usage.

### Browser Step 3 - Confirm Dashboard Shell

Look for `Usage Analytics`.

Expected: the admin shell and page title render.

What is happening: the new navigation route is available.

Why this matters: reviewers can reach the dashboard through the browser.

### Browser Step 4 - Confirm Redaction Notice

Read the notice near the top of the page.

Expected: it says normalized counts and safe identifiers are shown only.

What is happening: the page declares the redaction contract.

Why this matters: cost analytics must not expose raw model content.

### Browser Step 5 - Use Filters

Set Provider to `openai`, Model to `gpt-test`, and Group to `provider`.

Expected: the page reloads with the selected safe filters.

What is happening: dashboard filters are applied through query parameters.

Why this matters: finance and operations reviewers need filtered analytics.

### Browser Step 6 - Review Rollups

Inspect the Rollups table.

Expected: columns include Group, Events, Tokens, and Cost micros.

What is happening: event rows are summarized by the selected dimension.

Why this matters: dashboards must support rollup views.

### Browser Step 7 - Review Event Rows

Inspect the Events table or empty state.

Expected: rows show safe identifiers, token counts, cost micros, and status.

What is happening: event drilldown uses the same authorization and filters.

Why this matters: reviewers need drilldown without content leakage.

### Browser Step 8 - Create Export

Select `Export CSV`.

Expected: the browser redirects to a Usage Export page.

What is happening: an export request is created from the active filters.

Why this matters: finance workflows need CSV evidence.

### Browser Step 9 - Review Export Detail

Inspect the export status, row count, and artifact metadata.

Expected: metadata is visible and raw content is absent.

What is happening: export payloads are represented through safe metadata.

Why this matters: CSV exports are higher-risk and must stay auditable.

### Browser Step 10 - Acme Tenant Scope

Sign in as `tenant-admin-acme` and open:

```text
http://127.0.0.1:8000/admin/usage?tenant_id=11111111-1111-1111-1111-111111111111
```

Expected: Acme scope is accepted.

What is happening: tenant admin reads their own tenant usage.

Why this matters: tenant admins need self-service visibility.

### Browser Step 11 - Globex Denial

Sign in as `tenant-admin-globex` and open the same Acme URL.

Expected: the request is denied or unavailable.

What is happening: cross-tenant access fails closed.

Why this matters: shared platform usage data must remain isolated.

## Required Automated Evidence

Run Playwright validation:

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/016-token-usage-cost-analytics/validation.yml --start-processes
```

Expected: Playwright completes and saves screenshots.

What is happening: the configured local-login and `/admin/usage` flows run in
a browser.

Why this matters: browser evidence proves the server-rendered UI target exists.

Run quality gates:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected: all quality commands pass.

What is happening: linting, formatting, typing, and coverage are verified.

Why this matters: UI changes are complete only when project gates pass.

## UI Evidence Checklist

- Screenshot of Local Login.
- Screenshot of `/admin/usage`.
- Screenshot of filtered dashboard.
- Screenshot of export detail.
- Reviewer note for platform admin visibility.
- Reviewer note for Acme tenant visibility.
- Reviewer note for Globex denied Acme scope.
- Reviewer note that raw prompts are absent.
- Reviewer note that raw completions are absent.
- Reviewer note that secrets are absent.
- Reviewer note that memory content is absent.
- Reviewer note that provider credentials are absent.

## Acceptance Notes Template

Use this template in reviewer notes:

```text
QA016 UI date:
Branch:
Local login screenshot:
Usage dashboard screenshot:
Export detail screenshot:
Platform admin result:
Acme tenant result:
Globex denial result:
Redaction result:
Playwright result:
Quality gate result:
Open concerns:
```

Expected: every field is filled with a result or an explicit note.

What is happening: the reviewer leaves an audit-friendly trail.

Why this matters: future reviewers can understand what was validated.

## Troubleshooting

- Local login does not appear: confirm the API server is running.
- Usage page returns 401: sign in again through local login.
- Usage page returns 403: confirm the selected principal and tenant scope.
- Dashboard is empty: this is valid before events are seeded.
- Export has zero rows: filters may not match seeded events.
- Export route fails: check `.data/qa016-artifacts` permissions.
- Screenshot command fails: check that port 8000 is available.
- Redaction text appears as raw content: stop and file a failed QA note.
- Production host appears: stop and verify `.env.qa016`.

## Related Files

- `specs/016-token-usage-cost-analytics/qa016.md`
- `specs/016-token-usage-cost-analytics/qa016_user_guide.md`
- `specs/016-token-usage-cost-analytics/testing-instructions.md`
- `specs/_autopilot/016-token-usage-cost-analytics/validation.yml`
- `output/playwright/qa016_ui`
