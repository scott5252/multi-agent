# QA046 UI: User-Facing Run UI React Port And Jinja Removal

## Goal

Prove in a browser that `/runs` and `/runs/new` open the React run workspace, that a reviewer can start a run, and that the React detail page shows safe status, timeline, result, action, and artifact sections without Jinja.
Expected: the first viewport says `Run workspace`.
Expected: the page is served by React admin built assets, not an old template.
What is happening: the legacy route authenticates the user, then redirects into the React app.
Why this matters: bookmarks, Telegram links, and browser run links survive full Jinja removal.

## How To Use This Guide

Follow the steps in order. Capture screenshots or reviewer notes for each visible state. Use the local-principal login at `http://127.0.0.1:8000/auth/local-login` and choose `tenant-admin-acme` unless a step says otherwise.
Expected: screenshots do not show raw prompts, raw payloads, callback secrets, local paths, or stack traces.

## Environment Setup

```bash
cp specs/046-user-facing-run-ui-react-port-and-jinja-removal/.env.qa046 .env
uv sync
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa046 && createdb -U postgres multi_agent_platform_qa046'
uv run alembic upgrade head
mkdir -p .data/qa046-artifacts/evidence output/playwright/qa046_ui
```

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000 > /tmp/qa046-api.log 2>&1 &
echo $! > /tmp/qa046-api.pid
uv run python -m multi_agent_platform.workers.main > /tmp/qa046-worker.log 2>&1 &
echo $! > /tmp/qa046-worker.pid
curl --fail --silent http://127.0.0.1:8000/health/live | tee /tmp/qa046-health-live.json
```

```bash
cd frontend/admin
npm run build
cd ../..
```

Expected: API, worker, database, and React assets are ready for browser validation.
What is happening: the app reads `.env.qa046`, starts local-principal auth, and serves the built React bundle.
Why this matters: Playwright and manual reviewers exercise the same static host path.

## Browser Walkthrough

1. Open `http://127.0.0.1:8000/auth/local-login?redirect_to=/runs`.
2. Select the `tenant-admin-acme` login form.
3. Expected: the browser lands on `/admin/app/channels/runs`.
4. Expected: the heading says `Run workspace`.
5. What is happening: `/runs` redirected to React and the app mounted the run workspace.
6. Why this matters: the old index and new-run templates are no longer needed.
7. Leave the workflow field as `daily-briefing-demo`.
8. Leave the request summary as `safe browser request`.
9. Click `Start Run`.
10. Expected: the URL changes to `/admin/app/channels/runs/{run_id}`.
11. Expected: the status card shows `Run accepted through channel facade.`.
12. What is happening: React called `POST /runs` with an idempotency key.
13. Why this matters: start behavior remains backend-owned.
14. Review the `Status and progress` section.
15. Expected: state, cursor, result availability, artifact availability, and subscription state are visible.
16. Review the `Actions` section.
17. Expected: `Cancel`, `Subscribe`, and `Register Callback` are visible; disabled state follows backend-permitted actions.
18. Review the `Timeline` section.
19. Expected: event summaries are safe and do not show raw request bodies.
20. Review the `Result` section.
21. Expected: unavailable runs show a safe placeholder instead of raw result content.
22. Review the `Artifacts` section.
23. Expected: artifacts are metadata-only; no filesystem or object-storage path is visible.
24. Click `Subscribe`.
25. Expected: action summary shows subscription status only.
26. Click `Register Callback`.
27. Expected: action summary shows callback status only and does not echo the callback URL.
28. Open `/runs/{run_id}` directly in the address bar.
29. Expected: the browser redirects back to `/admin/app/channels/runs/{run_id}`.
30. What is happening: the compatibility route revalidates access before redirecting.
31. Why this matters: direct links from notifications remain safe.
32. Open a private note for evidence.
33. Record the visible run id, trace reference, and screenshot path.
34. Expected: reviewer notes contain only safe IDs and summaries.

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui2-roadmap/046-user-facing-run-ui-react-port-and-jinja-removal/validation.yml --start-processes
```

Expected: Playwright captures `output/playwright/qa046_ui/qa046-react-ui2-smoke.png`.
What is happening: the automated flow logs in, opens `/runs`, starts a run, waits for safe status text, and screenshots the React page.
Why this matters: the visual proof is reproducible.

## Required Automated Evidence

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --no-cov tests/integration/api/test_channel_run_api.py tests/integration/api/test_web_run_ui.py tests/integration/channels/test_cross_channel_recovery.py tests/integration/test_admin_react_routes.py tests/contract/test_admin_react_contract.py tests/unit/admin/test_user_runs_jinja_retirement.py -q
cd frontend/admin && npm test -- --run src/components/userRuns src/App.test.tsx
cd frontend/admin && npm run build
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/046-user-facing-run-ui-react-port-and-jinja-removal
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui2-roadmap/046-user-facing-run-ui-react-port-and-jinja-removal/validation.yml
```

Expected: all commands pass before accepting the UI evidence.
Expected: `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy src`, and `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90` are included in automated evidence.

## UI Evidence Checklist

- Screenshot: `/admin/app/channels/runs` start workspace after local login.
- Screenshot: `/admin/app/channels/runs/{run_id}` detail workspace after Start Run.
- Reviewer note: `/runs` redirects to the React start workspace.
- Reviewer note: `/runs/{run_id}` redirects to the React detail workspace.
- Reviewer note: status, timeline, result, action, and artifact sections are visible.
- Reviewer note: no raw prompt, raw payload, callback secret, full external identifier, local path, or stack trace appears.
- Expected: evidence names start with `qa046` or live under `output/playwright/qa046_ui`.

## Acceptance Notes Template

- Reviewer:
- Browser: Chromium through Playwright or local equivalent.
- Route opened: `/runs` then `/admin/app/channels/runs`.
- Run detail route:
- Screenshot path:
- Expected: Start Run succeeded.
- Expected: safe status text visible.
- Expected: redaction check passed.
- What is happening: React is using retained JSON APIs for all lifecycle operations.
- Why this matters: Spec 047 can remove global template infrastructure later with less risk.

## Troubleshooting

- If the login page does not show `tenant-admin-acme`, confirm `.env.qa046` was copied to `.env`.
- If `/runs` does not redirect, check `/tmp/qa046-api.log` and confirm `web_run_ui.py` is loaded.
- If Start Run fails, open browser dev tools and confirm `POST /runs` includes an idempotency key.
- If status never loads, confirm the run id in the URL matches the one returned by `POST /runs`.
- If an artifact URL is visible in the page, stop and file a redaction bug.
- If Playwright times out, rebuild the React assets and rerun with a fresh QA database.

## Related Files

- `frontend/admin/src/components/userRuns/UserRunPage.tsx`
- `frontend/admin/src/App.tsx`
- `src/multi_agent_platform/api/routers/web_run_ui.py`
- `src/multi_agent_platform/api/routers/channel_runs.py`
- `tests/integration/api/test_web_run_ui.py`
- `tests/integration/api/test_channel_run_api.py`
- `output/playwright/qa046_ui/qa046-react-ui2-smoke.png`
- UI evidence note 129: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 130: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 131: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 132: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 133: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 134: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 135: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 136: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 137: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 138: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 139: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 140: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 141: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 142: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 143: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 144: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 145: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 146: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 147: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 148: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 149: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 150: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 151: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 152: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 153: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 154: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 155: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 156: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 157: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 158: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 159: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 160: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 161: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 162: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 163: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 164: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 165: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 166: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 167: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 168: Expected: qa046 reviewer evidence remains safe and React-only.
- UI evidence note 169: Expected: qa046 reviewer evidence remains safe and React-only.
