# QA063 UI Walkthrough: Admin Design Review Workspace

## Goal

This walkthrough validates the browser experience for qa063.
The target route is `/admin/app/design-reviews`.
The reviewer should prove that the page shows live design-review data.
The reviewer should also prove that empty and denied states are truthful.
The route must work through the existing admin shell.
The workspace must not display fake sessions, fake verdicts, or fake handoffs.
The workspace must not expose raw prompts, completions, provider payloads, secrets, private messages, memory contents, unauthorized payloads, or raw external tool payloads.

## How To Use This Guide

Use this guide after the backend QA seed is complete.
Keep one terminal available for API logs.
Keep one browser window available for the local login flow.
Capture screenshots under `output/playwright/qa063_ui`.
Capture notes under `/tmp/qa063-ui-notes.txt`.
Record only safe session IDs, safe summaries, and expected status labels.
Do not paste raw payloads into screenshots or review notes.
Expected: all browser evidence is safe to attach to a PR.

## Environment Setup

Copy the qa063 environment file.

```bash
cp specs/063-admin-design-review-workspace/.env.qa063 .env
```

Expected: the app points at `multi_agent_platform_qa063`.

Install dependencies.

```bash
uv sync
```

Expected: dependencies are ready.

Prepare PostgreSQL.

```bash
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa063 && createdb -U postgres multi_agent_platform_qa063'
uv run alembic upgrade head
```

Expected: migrations complete.

Seed workspace rows.

```bash
uv run python scripts/qa/seed_design_review_workspace_qa063.py
```

Expected: output contains `Seeded QA063 design review workspace live records`.

Start the API.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected: the server is listening at `http://127.0.0.1:8000`.

Optional worker terminal.

```bash
uv run python -m multi_agent_platform.workers.main
```

Expected: the worker starts without requiring live providers.

## Browser Walkthrough

Open the local login route.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/design-reviews
```

Expected: the local-principal login page appears.
What is happening: the browser is preparing a local test principal.
Why this matters: the workspace must run through the same auth shell as other admin pages.

Choose the Acme tenant admin.
Expected: the browser redirects to `/admin/app/design-reviews`.
What is happening: the local cookie or header principal maps to Acme tenant scope.
Why this matters: tenant-scoped design review records are only visible in tenant scope.

Review the shell.
Expected: the left navigation includes Design Reviews and the active scope identifies Acme.
What is happening: the backend shell navigation has authorized the workspace route.
Why this matters: the workspace must not bypass admin route governance.

Review the page header.
Expected: the page title says Design reviews and the supporting copy describes sessions, rounds, decisions, and handoffs.
What is happening: the React page is rendering backend-owned envelope metadata.
Why this matters: visible copy should describe the user task, not implementation details.

Review summary cards.
Expected: total sessions, active review, manual resolution, and approved handoff counts match the seeded data.
What is happening: the browser is showing aggregate counts from live rows.
Why this matters: operational summaries must not be hard-coded.

Review the session list.
Expected: the seeded Acme session appears with status, active revision, quorum policy, and a select action.
What is happening: the workspace list comes from `/admin/app/design-reviews/bootstrap.json`.
Why this matters: tenant admins need to scan review history quickly.

Open the selected session.
Expected: the detail panel shows the safe request summary and active revision.
What is happening: the selected session detail is loaded from the envelope.
Why this matters: the session detail is the primary review surface.

Review revision summaries.
Expected: revision numbers, author role keys, safe summaries, digests, and previous revision references are visible.
What is happening: immutable revision records are displayed without raw payloads.
Why this matters: reviewers need to compare safe summaries without exposing design contents.

Review round history.
Expected: round number, status, runtime run reference, reviewer count, and quorum count are visible.
What is happening: the workspace is displaying live `design_review_rounds` state.
Why this matters: admins need to know whether the council ran and which runtime run was used.

Review reviewer verdicts.
Expected: each verdict shows reviewer key, verdict, score, blocker count, safe feedback summary, and digest.
What is happening: only safe summaries and digests are shown.
Why this matters: raw provider outputs must remain out of UI evidence.

Review quorum decision.
Expected: approval count, blocking issue count, next action, policy version, and safe rationale are visible.
What is happening: the workspace displays the persisted quorum decision.
Why this matters: admins need to understand why a session passed or needs another step.

Review handoff state.
Expected: approved sessions show a development handoff with safe summary, digest, status, and artifact reference when present.
What is happening: the handoff panel reads live handoff records.
Why this matters: implementation handoff must be traceable and safe.

Review the create form.
Expected: fields are labeled for request summary, quorum policy, and workflow option.
What is happening: the form prepares a live session creation request.
Why this matters: admins need a browser-first intake path.

Submit a safe create request.
Expected: a new session appears after the mutation completes or the page reloads.
What is happening: the form calls the existing session API with an idempotency key.
Why this matters: the UI must write through durable backend services.

Launch a round when an authorized workflow is available.
Expected: the selected session moves to reviewing and a round appears.
What is happening: the workspace calls the coordinator launch API.
Why this matters: the UI must not fabricate runtime execution state.

Open a manual-resolution seeded state when available.
Expected: manual controls appear only for a manual-resolution session.
What is happening: controls are driven by backend coordinator state.
Why this matters: invalid manual actions should not be invited.

Submit a manual decision with a safe rationale.
Expected: the decision appears in manual history and the session state changes according to the action.
What is happening: the workspace calls the coordinator manual-decision API.
Why this matters: human overrides must be durable and audit-safe.

Check empty tenant state.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/design-reviews?tenant_id=22222222-2222-2222-2222-222222222222
```

Expected: Globex has no Acme sessions and shows a truthful empty state.
What is happening: tenant scope has changed.
Why this matters: cross-tenant data leakage is a release blocker.

Capture a screenshot.

```bash
mkdir -p output/playwright/qa063_ui
```

Expected: the screenshot folder exists.
What is happening: manual evidence is prepared.
Why this matters: reviewers need a stable visual artifact.

## Required Automated Evidence

Run the backend verifier.

```bash
uv run python scripts/qa/verify_design_review_workspace_qa063.py | tee /tmp/qa063-ui-verify.txt
```

Expected: verification reports live workspace data.

Run frontend tests.

```bash
npm --prefix frontend/admin test -- DesignReviewWorkspace
```

Expected: component tests pass.

Run frontend typecheck.

```bash
npm --prefix frontend/admin run typecheck
```

Expected: TypeScript passes.

Run core backend checks.

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected: all checks pass.

Run the Playwright manifest.

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/scenario-enhancement-roadmap/063-admin-design-review-workspace/validation.yml --start-processes
```

Expected: the browser flow captures the qa063 screenshot.

## UI Evidence Checklist

- Screenshot shows the Design reviews workspace.
- Screenshot shows Acme scope.
- Screenshot shows a seeded live session.
- Screenshot shows safe revision or round information.
- Screenshot does not show raw prompt or provider payload text.
- Screenshot does not show secret-like values.
- Empty tenant check shows no Acme records.
- Manual action controls appear only in manual state.
- Create and launch controls have visible labels.
- Keyboard focus is visible on buttons and form fields.
- Tables have headers.
- Error states show safe summaries only.

## Acceptance Notes Template

- Route opened:
- Principal selected:
- Tenant scope:
- Seeded session visible:
- Round history visible:
- Verdict summaries visible:
- Quorum decision visible:
- Handoff visible:
- Empty tenant checked:
- Redaction checked:
- Screenshot path:
- Reviewer note:

## Troubleshooting

If the login route does not load, check the API terminal.
If the page stays loading, check `/admin/app/bootstrap.json`.
If the workspace says unavailable, check `/tmp/qa063-api.log`.
If no sessions are visible for Acme, rerun the seed script.
If the create form fails, copy only the safe error summary.
If launch is disabled, confirm a workflow option exists.
If manual controls are missing, confirm the session is in manual resolution.
If Globex sees Acme data, stop and file a tenant-isolation defect.
If visible copy includes implementation-framework labels, stop and file a copy defect.
If raw payload text appears, stop and file a redaction defect.

## Related Files

- `specs/063-admin-design-review-workspace/qa063.md`
- `specs/063-admin-design-review-workspace/.env.qa063`
- `specs/_autopilot/scenario-enhancement-roadmap/063-admin-design-review-workspace/validation.yml`
- `frontend/admin/src/components/designReviews/DesignReviewWorkspacePage.tsx`
- `frontend/admin/src/components/designReviews/DesignReviewWorkspacePage.test.tsx`
- `src/multi_agent_platform/admin/design_review/react_workspace.py`
- `src/multi_agent_platform/api/schemas/admin_design_review_workspace.py`
- `scripts/qa/seed_design_review_workspace_qa063.py`
- `scripts/qa/verify_design_review_workspace_qa063.py`
- `output/playwright/qa063_ui`
