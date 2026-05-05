# QA028 UI Walkthrough

## Goal

QA028 UI validation proves the React admin patterns page renders safe page envelopes, tables, filters, forms, validation feedback, stale conflict messaging, idempotency feedback, export snapshots, and shell context.

The route under review is `/admin/app/patterns`.

The route is harmless.

The route does not mutate real domain records.

The route exists so later React admin pages can copy safe patterns.

## How To Use This Guide

Use a private browser window or a clean local browser profile.

Start from `.env.qa028`.

Capture screenshots when instructed.

Record reviewer notes for any overlap, clipping, unclear focus, missing validation, or unsafe text.

Do not type real secrets into the sample form.

Do not type prompts, completions, memory, provider payloads, or external tool payloads into the sample form.

Expected: screenshots show only safe sample values.

## Environment Setup

Prepare the environment:

```bash
cp specs/028-react-admin-data-contracts-and-form-patterns/.env.qa028 .env
uv sync
cd frontend/admin
npm install
npm run build
cd ../..
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa028 && createdb -U postgres multi_agent_platform_qa028'
uv run alembic upgrade head
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa028 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
mkdir -p .data/qa028-artifacts output/playwright/qa028_ui
```

Expected: database and assets are ready.

What is happening: the sample page will load from FastAPI and fetch `/admin/app/patterns.json`.

Why this matters: the browser sees only backend-owned contract data.

Start the API:

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected: `http://127.0.0.1:8000/health/live` responds.

Start the worker:

```bash
uv run python -m multi_agent_platform.workers.main
```

Expected: worker starts without live provider calls.

## Browser Walkthrough

### Step 1: Denied Patterns Route

Open:

```text
http://127.0.0.1:8000/admin/app/patterns
```

Expected: a 401 response appears when not logged in.

Expected: no table, form, filter, export, or sample record appears.

What is happening: the React shell route is guarded before the sample page can render.

Why this matters: protected page contracts do not leak through unauthenticated routes.

### Step 2: Local Login

Open:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/patterns
```

Choose `tenant-admin-acme`.

Expected: the browser redirects to `/admin/app/patterns`.

Expected: the shell shows `React Admin`.

Expected: the active scope shows `Acme`.

What is happening: the local-principal cookie authorizes the shell and patterns envelope.

Why this matters: local QA proves the same route a non-technical tenant admin would use.

Screenshot evidence: `output/playwright/qa028_ui/qa028-react-patterns-page.png`.

### Step 3: Review The Page Envelope

Find the heading `Forms and data patterns`.

Expected: the page explains harmless sample contracts.

Expected: no raw JSON blob is shown.

Expected: no local filesystem path is shown.

What is happening: the page renders a generated `AdminPageEnvelope`.

Why this matters: future pages can share one safe envelope model.

### Step 4: Review The Table

Find `Sample records`.

Expected: `Workflow readiness review` appears.

Expected: the status badge says `ready`.

Expected: the scope column says `Acme`.

Expected: the footer says `Sorted by Name`.

What is happening: the table renders backend-bounded sample records.

Why this matters: future data tables should not invent filters or raw IDs in the browser.

### Step 5: Review Filters

Find the `Status` filter options.

Expected: `Ready` appears as an allowed filter option.

Expected: no free-form unsafe filter input appears.

What is happening: filter choices come from the backend filter profile.

Why this matters: server-owned filters prevent cross-tenant discovery.

### Step 6: Review The Form

Find the `Sample action` form.

Expected: `Sample name` appears.

Expected: `Outcome` appears.

Expected: `Preview result` appears.

Leave `Sample name` blank and click `Preview result`.

Expected: `validation error` appears.

Expected: `Enter a sample name.` appears next to the field.

What is happening: backend field errors map to rendered controls.

Why this matters: future forms can show precise validation without exposing stack traces.

Screenshot evidence: `output/playwright/qa028_ui/qa028-react-patterns-validation.png`.

### Step 7: Review Stale Conflict

Type `Preview` into Sample name.

Type `stale` into Outcome.

Click `Preview result`.

Expected: `stale conflict` appears.

Expected: the recovery guidance says the sample has a newer safe revision.

What is happening: stale revision metadata is rendered as safe recovery guidance.

Why this matters: future optimistic concurrency failures need understandable recovery.

### Step 8: Review Replay

Type `replay` into Outcome.

Click `Preview result`.

Expected: `replayed` appears.

Expected: the message says no duplicate side effect was applied.

What is happening: idempotency replay metadata is rendered without raw request data.

Why this matters: admins need confidence that repeated submissions are safe.

### Step 9: Review Export Snapshot

Click `Export preview`.

Expected: `Sample export snapshot is ready as a safe artifact reference.` appears.

Expected: `artifact-ref-qa028-tenant` appears.

Expected: no `/Users/` path appears.

What is happening: React displays a safe artifact reference, not exported content.

Why this matters: future exports must not leak local paths or raw payloads.

Screenshot evidence: `output/playwright/qa028_ui/qa028-react-patterns-export.png`.

### Step 10: Mobile And Keyboard Check

Resize the browser below 900 pixels wide.

Expected: shell navigation collapses.

Expected: the table remains readable or scroll-free at the captured width.

Press Tab through the page.

Expected: focus reaches filter links, the form fields, Preview result, and Export preview.

What is happening: Spec 028 reuses the Spec 027 shell and focus styles.

Why this matters: later domain forms must remain keyboard reachable.

## Required Automated Evidence

Run QA document validation:

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/028-react-admin-data-contracts-and-form-patterns
```

Expected: validation passes.

Run quality commands:

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

Expected: all commands pass.

Run Playwright:

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/028-react-admin-data-contracts-and-form-patterns/validation.yml --start-processes
```

Expected: Playwright UI validation completes.

Expected: QA028 screenshots exist.

## UI Evidence Checklist

- Denied route screenshot or note captured.
- Authenticated patterns page screenshot captured.
- Validation feedback screenshot captured.
- Export snapshot screenshot captured.
- Mobile reviewer note captured.
- Keyboard reviewer note captured.
- No secret value observed.
- No local filesystem path observed.
- No Globex label observed while logged in as Acme.
- No raw prompt, completion, memory, provider payload, or tool payload observed.

Expected: every checklist item is complete.

## Acceptance Notes Template

Reviewer:

Date:

Browser:

Login principal:

Patterns page result:

Validation result:

Stale conflict result:

Replay result:

Export result:

Mobile result:

Keyboard result:

Screenshots:

- `output/playwright/qa028_ui/qa028-react-patterns-page.png`
- `output/playwright/qa028_ui/qa028-react-patterns-validation.png`
- `output/playwright/qa028_ui/qa028-react-patterns-export.png`

Security notes:

- No secrets observed.
- No cross-tenant labels observed.
- No raw payloads observed.

## Troubleshooting

If the page stays on denied after login, clear local cookies and repeat local login.

If `Forms` never appears, rebuild React assets.

If validation text does not appear, check the network request to `/admin/app/patterns/actions/sample`.

If export status includes a filesystem path, fail QA028.

If the table shows Globex while logged in as Acme, fail QA028.

If keyboard focus disappears, capture a note and fail the keyboard check.

Expected: troubleshooting does not require bypassing auth.

## Related Files

- `specs/028-react-admin-data-contracts-and-form-patterns/qa028.md`
- `specs/028-react-admin-data-contracts-and-form-patterns/qa028_user_guide.md`
- `specs/028-react-admin-data-contracts-and-form-patterns/.env.qa028`
- `frontend/admin/src/components/patterns/PatternsPage.tsx`
- `frontend/admin/src/components/forms/AdminForm.tsx`
- `frontend/admin/src/components/data/AdminDataTable.tsx`
- `frontend/admin/src/hooks/useAdminMutation.ts`
