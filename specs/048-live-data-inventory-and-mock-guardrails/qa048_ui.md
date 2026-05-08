# QA048 UI Walkthrough: Live Data Inventory And Mock Guardrails

## Goal

Prove the React migration hardening workspace renders backend-owned live-data inventory evidence for qa048.

This walkthrough focuses on what a reviewer can see in the browser.

- The migration page loads through local-principal auth.
- The new `Live-data guardrails` panel is visible.
- The panel shows mapped findings, route targets, computed metadata, and evidence IDs.
- Refresh re-fetches backend JSON without leaking unsafe content.
- The screenshot and reviewer notes can be attached to qa048 evidence.

## How To Use This Guide

Use this guide after the backend focused tests pass.

Save notes under `/tmp/qa048-ui-evidence.txt`.

Save screenshots under `output/playwright/qa048_ui`.

Expected: UI evidence references qa048, captures the live-data panel, and avoids raw secrets, raw prompts, private messages, local absolute paths, and stack traces.

What is happening: the reviewer verifies visible React state after the backend route returns a safe JSON dashboard.

Why this matters: qa048 is a guardrail spec; the UI must make the warning state understandable without relying on test-only fixture data.

## Environment Setup

Copy the environment and build the React assets before the browser walkthrough.

```bash
test ! -f .env || cp .env .env.autopilot-backup
cp specs/048-live-data-inventory-and-mock-guardrails/.env.qa048 .env
uv sync
cd frontend/admin && npm run build
```

Expected: `.env.qa048` is active and React assets build successfully.

What is happening: the FastAPI app will serve the built migration hardening page and the live-data inventory endpoint.

Why this matters: the browser proof must exercise the same built assets used by the backend static route.

Run the backend process when performing manual review.

```bash
uv run uvicorn multi_agent_platform.api.main:app --reload
```

Expected: the app listens on `127.0.0.1:8000`.

What is happening: FastAPI serves `/auth/local-login`, `/admin/app/migration`, and `/admin/app/migration/live-data-inventory.json`.

Why this matters: the local browser path mirrors the automated Playwright flow.

## Browser Walkthrough

### Step 1. Open Local Login

Open `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/migration`.

Expected: the local-principal login page shows available principals.

What is happening: local auth mode exposes deterministic QA principals from `.env.qa048`.

Why this matters: reviewers can prove the browser session is authorized without Auth0 or live identity providers.

### Step 2. Sign In As Platform Admin

Choose `platform-admin`.

Expected: the browser redirects to `/admin/app/migration`.

What is happening: the app sets the local principal cookie and loads the migration hardening shell.

Why this matters: the live-data inventory covers platform-wide admin React routes.

### Step 3. Confirm Migration Header

Find the heading `React-only browser UI`.

Expected: summary counts and the `Refresh` button are visible.

What is happening: `fetchMigrationHardeningDashboard` has loaded `/admin/app/migration/bootstrap.json`.

Why this matters: the new panel is rendered inside the established migration workspace.

### Step 4. Confirm Jinja Inventory Still Renders

Find the heading `React-only readiness`.

Expected: the final decommission summary remains visible above the live-data panel.

What is happening: qa048 keeps Spec 047 decommission evidence visible while adding mock-data inventory evidence.

Why this matters: mock-data cleanup begins after React-only migration decommission remains stable.

### Step 5. Confirm Live-Data Guardrails

Find the heading `Live-data guardrails`.

Expected: the panel displays counts for findings, mapped entries, blocking entries, computed entries, routes, and seeded scans.

What is happening: the React panel is rendering `LiveDataInventoryDashboard.summary`.

Why this matters: reviewers can see that current findings are mapped and blocking findings are zero.

### Step 6. Review Findings Table

Scan the `Source`, `Replacement`, `Marker`, and `Evidence` columns.

Expected: mapped rows show repository-relative source paths and replacement specs from 049 through 058.

What is happening: current legacy markers are retained only as mapped cleanup work.

Why this matters: qa048 should create accountability, not hide remaining fixture debt.

### Step 7. Review Route Targets

Find the `Route targets` list.

Expected: GET and POST `/admin/app` routes are listed with principal and state expectations.

What is happening: the route-target registry tells later specs which empty and seeded states must stop using mock data.

Why this matters: Specs 049 through 058 need an executable inventory instead of a loose narrative.

### Step 8. Review Evidence

Find `live-data-scanner` or `qa048-live-data-source-scan`.

Expected: evidence references point to relative test files and safe QA IDs.

What is happening: the backend emits reviewer-safe evidence IDs rather than raw logs.

Why this matters: evidence is useful for signoff without exposing sensitive payloads.

### Step 9. Refresh The Page Data

Click `Refresh`.

Expected: the page remains on `/admin/app/migration`, the live-data panel remains visible, and no error state appears.

What is happening: the page re-runs the dashboard, route, rollback, Jinja inventory, and live-data inventory fetches.

Why this matters: refresh proves the panel is backed by live JSON endpoints instead of static fixture text.

### Step 10. Capture Screenshot

Capture a full-page screenshot named `qa048-live-data-ui-api-smoke.png`.

Expected: the screenshot includes the migration header and the `Live-data guardrails` panel.

What is happening: screenshot evidence records the warning-state inventory.

Why this matters: the autopilot can attach a clear visual proof for qa048 completion.

## Required Automated Evidence

### UI automation

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/048-live-data-inventory-and-mock-guardrails/validation.yml --start-processes
```

Expected: Playwright opens local login, signs in, clicks Refresh, expects `Live-data guardrails`, expects `Route targets`, and saves the qa048 screenshot.

What is happening: automated UI QA exercises the same visible path as the manual walkthrough.

Why this matters: the spec cannot be marked complete from API evidence alone.

### Frontend test automation

```bash
cd frontend/admin && npm test -- --run src/components/migrationHardening src/App.test.tsx
```

Expected: migration hardening tests pass, including the live-data panel test.

What is happening: component-level tests verify render behavior, fallback state, and safe text expectations.

Why this matters: the UI remains stable even if the optional inventory fetch is temporarily unavailable.

### Quality gates

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected: quality gates pass before reviewer signoff.

What is happening: backend source, typing, formatting, and coverage gates run alongside UI proof.

Why this matters: the live-data inventory touches API contracts, domain service code, generated TS, and React components.

## UI Evidence Checklist

- Expected: screenshot includes `Live-data guardrails`.
- Expected: screenshot includes `Route targets`.
- Expected: screenshot includes zero blocking findings or the blocking count metric.
- Expected: screenshot includes mapped or warning status, because later specs still have cleanup work.
- Expected: screenshot does not include raw prompt text.
- Expected: screenshot does not include credential values.
- Expected: screenshot does not include local absolute paths.
- Expected: screenshot does not include unauthorized tenant labels.
- Expected: `/tmp/qa048-ui-evidence.txt` records the browser URL, principal, screenshot path, and validation manifest path.
- Expected: reviewer notes mention that qa048 warning state is intentional until Specs 049 through 058 complete.

## Acceptance Notes Template

```text
QA id: qa048
Browser route: http://127.0.0.1:8000/admin/app/migration
Principal: platform-admin
Visible panel: Live-data guardrails
Refresh result: pass
Screenshot: output/playwright/qa048_ui/qa048-live-data-ui-api-smoke.png
Unsafe text sweep: pass
Reviewer conclusion: qa048 UI evidence accepted
```

Expected: the note can be copied into the spec status file or PR notes after validation.

What is happening: reviewer-visible proof is separated from raw command output.

Why this matters: the QA trail stays concise and safe.

## Troubleshooting

- If local login is unavailable, verify `.env.qa048` was copied and `AUTH_MODE=local_principal` is active.
- If `platform-admin` does not appear, verify `LOCAL_PRINCIPAL_CATALOG_JSON` is present in `.env.qa048`.
- If the migration page shows dependency unavailable, check the API terminal and rerun focused backend tests.
- If `Live-data guardrails` is missing, verify the generated TypeScript contract and frontend build are current.
- If Refresh fails, inspect the network request for `/admin/app/migration/live-data-inventory.json`.
- If evidence IDs are missing, rerun the backend route test and contract test.
- If screenshot text overlaps on mobile or desktop, fix CSS before accepting qa048 UI evidence.
- If unsafe text appears, stop and replace the exposed value with an existing safe summary or reference ID.

## Related Files

- `specs/048-live-data-inventory-and-mock-guardrails/.env.qa048`
- `specs/048-live-data-inventory-and-mock-guardrails/qa048.md`
- `specs/_autopilot/remove-mock-data-roadmap/048-live-data-inventory-and-mock-guardrails/validation.yml`
- `src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py`
- `src/multi_agent_platform/api/routers/admin_react.py`
- `frontend/admin/src/components/migrationHardening/LiveDataInventoryPanel.tsx`
- `frontend/admin/src/components/migrationHardening/MigrationHardeningPage.tsx`
- `frontend/admin/src/test/migrationHardeningTestData.ts`
- `frontend/admin/src/components/migrationHardening/LiveDataInventoryPanel.test.tsx`
