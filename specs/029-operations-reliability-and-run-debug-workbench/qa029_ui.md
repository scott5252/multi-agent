# QA029 UI Walkthrough

## Goal

QA029 UI validation proves the React operations workbench renders safe operational summaries for platform and tenant administrators.

The route under review is `/admin/app/operations`.

The browser should show health cards, likely causes, reliability recovery, run debug details, safe logs, and export evidence.

The browser should not show raw prompts, completions, memory contents, private channel messages, provider responses, Telegram updates, connector outputs, stack traces, local paths, raw credentials, or unauthorized tenant labels.

The workbench uses deterministic QA029 data.

The workbench does not call live providers.

The workbench does not call Telegram.

The workbench does not call external tools.

Expected: screenshots show only safe summaries and artifact references.

## How To Use This Guide

Use a private browser window or a clean local browser profile.

Start from `.env.qa029`.

Capture screenshots when instructed.

Record reviewer notes for overlap, clipping, unclear focus, unsafe text, missing status context, or confusing tenant scope.

Do not paste real secrets into the browser.

Do not paste raw prompts, completions, memory, private messages, provider responses, Telegram updates, connector outputs, stack traces, or local paths into reviewer notes.

Expected: QA evidence can be shared with reviewers without redaction cleanup.

What is happening: the browser is exercising the same route non-developer admins will use.

Why this matters: UI validation catches layout and copy regressions that API tests cannot see.

## Environment Setup

Prepare the environment:

```bash
cp specs/029-operations-reliability-and-run-debug-workbench/.env.qa029 .env
uv sync
cd frontend/admin
npm install
npm run build
cd ../..
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa029 && createdb -U postgres multi_agent_platform_qa029'
uv run alembic upgrade head
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa029 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
mkdir -p .data/qa029-artifacts output/playwright/qa029_ui
```

Expected: database, React assets, and evidence folders are ready.

What is happening: the local app will serve the production React bundle backed by QA029 settings.

Why this matters: screenshots represent the same asset path FastAPI uses.

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

What is happening: operational pages can resolve shell and runtime settings.

Why this matters: the workbench should behave in the full local stack.

## Browser Walkthrough

### Step 1: Denied Operations Route

Open:

```text
http://127.0.0.1:8000/admin/app/operations
```

Expected: a 401 response appears when not logged in.

Expected: no workbench cards appear.

Expected: no run debug evidence appears.

Expected: no export reference appears.

What is happening: the shell route is guarded before React data can render.

Why this matters: protected operational summaries cannot leak anonymously.

Screenshot evidence: `output/playwright/qa029_ui/qa029-react-operations-denied.png`.

### Step 2: Platform Login

Open:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/operations
```

Choose `platform-admin`.

Expected: the browser redirects to `/admin/app/operations`.

Expected: the shell shows `React Admin`.

Expected: the page heading says `Operations workbench`.

Expected: the active scope is platform-oriented.

What is happening: the local-principal cookie authorizes the platform workbench envelope.

Why this matters: platform operators need one place to begin incident triage.

Screenshot evidence: `output/playwright/qa029_ui/qa029-react-operations-platform.png`.

### Step 3: Review Platform Summary Cards

Find `Health`.

Find `Queue pressure`.

Find `Provider health`.

Expected: `Health` shows a degraded status.

Expected: `Queue pressure` shows runnable work.

Expected: `Provider health` shows a safe provider summary.

Expected: no raw provider response is visible.

What is happening: backend-owned cards summarize platform pressure.

Why this matters: platform-only details stay centralized in the backend contract.

### Step 4: Review Likely Causes

Find `Likely causes`.

Expected: `Model gateway` appears.

Expected: `retryable_timeout` appears.

Expected: the next step points to provider health and gateway diagnostics.

What is happening: the workbench maps symptoms to safe likely-cause categories.

Why this matters: operators can decide where to go next without seeing raw payloads.

### Step 5: Review Health Panels

Find `Capacity and dependencies`.

Expected: `Runnable queue` appears.

Expected: `Telegram` appears as degraded.

Expected: `safe polling available` appears.

What is happening: the page combines capacity and dependency signals.

Why this matters: the workbench gives useful context without forcing log spelunking.

### Step 6: Review Run Debug

Find `Daily briefing graph run`.

Expected: `Calendar branch` appears.

Expected: `Weather branch` appears.

Expected: `OpenAI provider` appears.

Expected: `Weather connector` appears.

Expected: `Morning briefing alias` appears.

What is happening: run debug connects graph branches, gateway attempts, tool calls, and delivery attempts.

Why this matters: a run-centered view helps operators identify whether the issue is graph, provider, connector, or delivery related.

### Step 7: Review Reliability Recovery

Find `Recovery posture`.

Expected: `Model gateway breaker` appears.

Expected: `Weather branch retry` appears.

Expected: `Replay requires confirmation` appears.

Expected: confirmation language is visible but no unsafe replay action is executed.

What is happening: recovery items are previews and links, not live remediations.

Why this matters: potentially risky recovery paths must remain explicit and auditable.

### Step 8: Review Export Evidence

Find `Export evidence`.

Click `Export evidence`.

Expected: `artifact-ref-qa029-platform` appears.

Expected: `audit-workbench-export-qa029-platform` appears.

Expected: redaction summary appears.

Expected: no local filesystem path appears.

What is happening: export returns artifact and audit references.

Why this matters: operators can hand off evidence without exposing raw operational payloads.

Screenshot evidence: `output/playwright/qa029_ui/qa029-react-operations-export.png`.

### Step 9: Tenant Login

Open:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/operations
```

Choose `tenant-admin-acme`.

Expected: the browser redirects to `/admin/app/operations`.

Expected: the active scope shows `Acme`.

Expected: `Tenant run health` appears.

Expected: `Tenant delivery` appears.

Expected: `Provider health` does not appear in the tenant workbench.

What is happening: the same React route receives a tenant-scoped envelope.

Why this matters: tenants get actionable context while platform-only pressure remains hidden.

Screenshot evidence: `output/playwright/qa029_ui/qa029-react-operations-tenant.png`.

### Step 10: Tenant Export

Click `Export evidence` in the Acme tenant view.

Expected: `artifact-ref-qa029-tenant` appears.

Expected: the export summary references Acme scope.

Expected: no Globex label appears.

What is happening: export scope follows the active tenant shell context.

Why this matters: handoff evidence must remain tenant scoped.

### Step 11: Cross-Tenant Browser Check

While signed in as `tenant-admin-acme`, open:

```text
http://127.0.0.1:8000/admin/app/operations?tenant_id=22222222-2222-2222-2222-222222222222
```

Expected: access is denied.

Expected: `Globex` does not appear.

Expected: no workbench card appears.

What is happening: scope resolution fails closed before the React shell receives data.

Why this matters: tenant isolation is a core acceptance requirement.

## Required Automated Evidence

Run the QA document validator:

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/029-operations-reliability-and-run-debug-workbench
```

Expected: QA document validation passes.

Run backend quality commands:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected: lint, format, type, and full coverage checks pass.

Run frontend quality commands:

```bash
cd frontend/admin
npm run typecheck
npm run test -- --run
npm run build
cd ../..
```

Expected: TypeScript, Vitest, and Vite build pass.

Run Spec QA:

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui-roadmap/029-operations-reliability-and-run-debug-workbench/validation.yml
```

Expected: command validation passes.

Run Playwright UI validation:

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/029-operations-reliability-and-run-debug-workbench/validation.yml --start-processes
```

Expected: screenshots are created in `output/playwright/qa029_ui`.

What is happening: automated browser flows reproduce the manual route coverage.

Why this matters: visual evidence can be inspected after the command finishes.

## UI Evidence Checklist

- Denied screenshot captured.
- Platform workbench screenshot captured.
- Platform export screenshot captured.
- Tenant workbench screenshot captured.
- Health card text is readable.
- Likely-cause section is readable.
- Run debug section is readable.
- Reliability recovery section is readable.
- Export panel is readable.
- No button text overlaps.
- No table or panel text overflows.
- No local path appears.
- No `qa029-secret-value` appears.
- No Globex label appears in Acme tenant view.
- No raw provider response appears.
- No raw connector output appears.

## Acceptance Notes Template

- Browser:
- Viewport:
- Denied route result:
- Platform route result:
- Tenant route result:
- Export result:
- Cross-tenant result:
- Screenshot paths:
- Accessibility observations:
- Layout observations:
- Redaction observations:
- Tenant isolation observations:
- Remaining concerns:

## Troubleshooting

If local login does not show `platform-admin`, confirm `.env.qa029` was copied to `.env`.

If the page shows a missing asset state, rerun `cd frontend/admin && npm run build`.

If the page shows `React admin unavailable`, inspect `/tmp/qa029-api.log`.

If the tenant page still shows platform-only provider health, stop and log a tenant-scope defect.

If export shows `/Users/`, stop and log an artifact safety defect.

If export shows `qa029-secret-value`, stop and log a redaction defect.

If Playwright screenshots show clipped text, check responsive CSS before accepting the run.

If a click on `Export evidence` does nothing, inspect the browser console and the `/admin/app/operations/export` API response.

If a cross-tenant URL renders Globex content for Acme, stop and log a fail-closed defect.

## Related Files

- `specs/029-operations-reliability-and-run-debug-workbench/qa029.md`
- `specs/029-operations-reliability-and-run-debug-workbench/qa029_user_guide.md`
- `specs/029-operations-reliability-and-run-debug-workbench/.env.qa029`
- `specs/_autopilot/react-ui-roadmap/029-operations-reliability-and-run-debug-workbench/validation.yml`
- `frontend/admin/src/components/workbench/WorkbenchPage.tsx`
- `frontend/admin/src/components/workbench/WorkbenchSummaryGrid.tsx`
- `frontend/admin/src/components/workbench/WorkbenchTimeline.tsx`
- `frontend/admin/src/components/workbench/WorkbenchReliabilityPanel.tsx`
- `frontend/admin/src/components/workbench/WorkbenchExportPanel.tsx`
- `frontend/admin/src/styles/admin.css`
- `output/playwright/qa029_ui`
