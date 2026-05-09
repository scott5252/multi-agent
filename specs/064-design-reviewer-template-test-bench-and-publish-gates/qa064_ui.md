# QA064 UI Walkthrough: Design Reviewer Template Setup

## Goal

This walkthrough validates the browser-facing qa064 experience.
The Admin design review workspace now shows Design Reviewer Council template setup state.
The setup state must come from backend live data.
The page must show when current required evidence is passing.
The page must show model backed safe evidence in plain user-facing language.
The page must keep design review sessions empty when only template setup has run.
The page must let a tenant admin run setup from an explicit action.
The page must not hide setup behind fixtures.
The page must not expose raw prompts, completions, provider payloads, secrets, private messages, memory contents, or raw tool payloads.
Expected: the browser confirms current required evidence and publish readiness without showing sensitive content.

## How To Use This Guide

Run commands from the repository root.
Use the qa064 environment file.
Use local-principal login.
Use Acme for the success path.
Use Globex for empty and denial checks.
Capture screenshots under `output/playwright/qa064_ui`.
Save notes under `/tmp/qa064-ui-notes.txt`.
Keep notes limited to safe IDs, status names, and visible UI copy.
Expected: a reviewer can reproduce the same page state from a clean database.

## Environment Setup

Copy the environment file.

```bash
cp specs/064-design-reviewer-template-test-bench-and-publish-gates/.env.qa064 .env
```

Expected: `.env.qa064` is the active environment.

Install dependencies and prepare the database.

```bash
uv sync
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa064 && createdb -U postgres multi_agent_platform_qa064'
uv run alembic upgrade head
```

Expected: the qa064 database is ready.

Seed the council template before the automated browser flow.

```bash
uv run python scripts/qa/seed_design_review_template_qa064.py | tee /tmp/qa064-ui-seed.txt
```

Expected: output contains `Seeded QA064 design review council template evidence`.

Start the API.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000 | tee /tmp/qa064-ui-api.log
```

Expected: the API is available at `http://127.0.0.1:8000`.

## Browser Walkthrough

1. Open the local login page.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/design-reviews
```

Expected: the local login page lists available local principals.
What is happening: the browser is using local-principal authentication for deterministic QA.
Why this matters: the reviewer can prove authorization without external identity services.

2. Select the Acme tenant admin principal.

Expected: the browser opens the Design reviews workspace.
What is happening: Acme tenant scope is applied to the Admin shell.
Why this matters: all template and session data must be tenant-scoped.

3. Inspect the workspace page title.

Expected: the page title is `Design reviews`.
What is happening: the existing React workspace route is loaded.
Why this matters: qa064 extends the workspace without replacing the product surface.

4. Inspect the template setup panel.

Expected: the panel says `Council template has current required evidence.`
What is happening: the panel reads backend `template_setup` state.
Why this matters: users see real publish readiness instead of sample copy.

5. Inspect evidence mode labels.

Expected: the panel shows `deterministic` and `model backed safe`.
What is happening: evidence modes are translated to safe UI labels.
Why this matters: local QA proves model-boundary behavior without live provider side effects.

6. Inspect publish gate status.

Expected: the panel shows that publish readiness is ready.
What is happening: the backend evaluated current workflow draft evidence.
Why this matters: stale evidence must not allow publication.

7. Inspect the session list.

Expected: there are no design review sessions after template setup alone.
What is happening: template setup created workflow and test-bench state, not fake sessions.
Why this matters: the Admin workspace remains live-data only.

8. Refresh the page.

Expected: the template setup panel remains ready.
What is happening: idempotent setup evidence is durable.
Why this matters: readiness should survive navigation and browser refresh.

9. Trigger the setup action if the panel offers it.

Expected: the action completes without duplicating visible template state.
What is happening: the browser posts to the tenant-scoped install route.
Why this matters: Admin setup is explicit and replay-safe.

10. Open the Globex tenant workspace through local login.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/design-reviews?tenant_id=22222222-2222-2222-2222-222222222222
```

Expected: Acme template state is not shown to Globex.
What is happening: tenant scope changes to Globex.
Why this matters: cross-tenant leakage would invalidate the release.

11. Capture the Acme ready-state screenshot.

Expected: the screenshot is saved under `output/playwright/qa064_ui`.
What is happening: visual evidence records the ready template panel.
Why this matters: reviewers can inspect the exact browser state.

12. Capture the Globex empty-state screenshot.

Expected: the screenshot shows no Acme records or template state.
What is happening: empty tenant state is visible.
Why this matters: the workspace must be truthful when no live data exists.

## Required Automated Evidence

Run focused Playwright validation.

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/scenario-enhancement-roadmap/064-design-reviewer-template-test-bench-and-publish-gates/validation.yml --start-processes
```

Expected: the flow captures `qa064-scenario-enhancement-smoke.png`.

Run the focused React component tests.

```bash
npm --prefix frontend/admin test -- DesignReviewWorkspace
```

Expected: all DesignReviewWorkspace tests pass.

Run frontend typecheck.

```bash
npm --prefix frontend/admin run typecheck
```

Expected: TypeScript strict mode passes.

Run frontend build.

```bash
npm --prefix frontend/admin run build
```

Expected: Vite emits build assets for FastAPI serving.

Run standard backend checks for release readiness.

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected: all release checks pass.

## UI Evidence Checklist

- Screenshot shows the Design reviews page title.
- Screenshot shows the Acme tenant context.
- Screenshot shows `Council template has current required evidence.`
- Screenshot shows `model backed safe`.
- Screenshot shows ready publish-gate state.
- Screenshot shows no fabricated session rows.
- Screenshot shows no raw prompt content.
- Screenshot shows no raw completion content.
- Screenshot shows no provider payload.
- Screenshot shows no secret-like value.
- Screenshot shows no private channel payload.
- Screenshot shows no memory content.
- Screenshot shows no raw external tool payload.
- Reviewer notes include the screenshot path.
- Reviewer notes include the Playwright command.
- Reviewer notes include the seed and verify evidence paths.
- Expected: evidence proves readiness and redaction in the browser.

## Acceptance Notes Template

Record QA id qa064.
Record browser route `/admin/app/design-reviews`.
Record local login URL `http://127.0.0.1:8000/auth/local-login`.
Record Acme tenant id `11111111-1111-1111-1111-111111111111`.
Record Globex tenant id `22222222-2222-2222-2222-222222222222`.
Record screenshot `output/playwright/qa064_ui/qa064-scenario-enhancement-smoke.png`.
Record seed output `/tmp/qa064-ui-seed.txt`.
Record API log `/tmp/qa064-ui-api.log`.
Record whether ready text appeared.
Record whether model backed safe text appeared.
Record whether sessions were empty after template setup.
Record whether Globex remained isolated.
Record whether any sensitive raw payload appeared.
Expected: acceptance notes are safe to attach to review.

## Troubleshooting

If the browser cannot load, check that the API is listening on port 8000.
If login does not work, confirm `AUTH_MODE=local_principal`.
If Acme does not show ready state, rerun the qa064 seed helper.
If `model backed safe` is missing, inspect the template setup response.
If sessions appear after setup alone, stop and inspect seeded data.
If Globex shows Acme state, stop because tenant isolation has failed.
If screenshots are missing, inspect the Playwright output directory.
If the frontend build fails, run typecheck and inspect the first failing file.
If backend checks fail, run the focused template tests first.
Expected: troubleshooting uses safe logs and does not expose protected payloads.

## Related Files

- `specs/064-design-reviewer-template-test-bench-and-publish-gates/qa064.md`
- `specs/064-design-reviewer-template-test-bench-and-publish-gates/.env.qa064`
- `specs/064-design-reviewer-template-test-bench-and-publish-gates/qa064_user_guide.md`
- `src/multi_agent_platform/admin/design_review/template.py`
- `src/multi_agent_platform/admin/design_review/react_workspace.py`
- `src/multi_agent_platform/api/routers/admin_design_review.py`
- `frontend/admin/src/components/designReviews/DesignReviewWorkspacePage.tsx`
- `frontend/admin/src/styles/admin.css`
- `scripts/qa/seed_design_review_template_qa064.py`
- `scripts/qa/verify_design_review_template_qa064.py`
Expected: a reviewer can trace the browser state to the API and service implementation.
