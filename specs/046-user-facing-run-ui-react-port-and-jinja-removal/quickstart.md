# Quickstart: User-Facing Run UI React Port And Jinja Removal

## Scope

Spec 046 proves the user-facing `/runs` browser surface is React-only while retaining the JSON lifecycle APIs used by web, API, and Telegram channels. Admin run inspection templates were retired by Spec 044 and are not reopened here.

## Existing Surface Inventory

- Deleted templates remain absent:
  - `src/multi_agent_platform/web_admin/templates/runs/index.html`
  - `src/multi_agent_platform/web_admin/templates/runs/detail.html`
  - `src/multi_agent_platform/web_admin/templates/runs/replay.html`
- Retained browser compatibility router:
  - `src/multi_agent_platform/api/routers/web_run_ui.py`
- Retained lifecycle API router:
  - `src/multi_agent_platform/api/routers/channel_runs.py`
- React destinations:
  - `/admin/app/channels/runs`
  - `/admin/app/channels/runs/{run_id}`

## Focused Backend Validation

```bash
uv run pytest --no-cov \
  tests/integration/api/test_channel_run_api.py \
  tests/integration/api/test_web_run_ui.py \
  tests/integration/channels/test_cross_channel_recovery.py \
  tests/integration/test_admin_react_routes.py \
  tests/contract/test_admin_react_contract.py \
  tests/unit/admin/test_user_runs_jinja_retirement.py \
  -q
```

## Focused Frontend Validation

```bash
cd frontend/admin
npm test -- --run src/components/userRuns src/App.test.tsx
npm run build
```

## QA Validation

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh \
  specs/046-user-facing-run-ui-react-port-and-jinja-removal

uv run python scripts/qa/run_spec_qa.py \
  specs/_autopilot/react-ui2-roadmap/046-user-facing-run-ui-react-port-and-jinja-removal/validation.yml

uv run python scripts/qa/run_playwright_ui.py \
  specs/_autopilot/react-ui2-roadmap/046-user-facing-run-ui-react-port-and-jinja-removal/validation.yml \
  --start-processes
```

## Manual Smoke

1. Start the API with `AUTH_MODE=local_principal`.
2. Log in with the local tenant user.
3. Start a run through the React run workspace or retained `/runs` JSON API.
4. Open `/runs` and confirm the browser lands on `/admin/app/channels/runs`.
5. Open `/runs/{run_id}` and confirm the browser lands on `/admin/app/channels/runs/{run_id}`.
6. Confirm status, timeline, permitted actions, result availability, artifact metadata, subscription/callback actions, and safe unavailable states render without raw payloads.
