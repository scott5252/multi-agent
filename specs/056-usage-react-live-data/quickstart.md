# Quickstart: Usage React Live Data

## Goal

Validate that the React usage analytics workspace renders live usage data,
truthful empty states, and persisted export evidence without deterministic
qa035 fixture events.

## Local Setup

1. Sync dependencies:

   ```bash
   uv sync
   npm install --prefix frontend/admin
   ```

2. Prepare a qa056 database:

   ```bash
   cp specs/056-usage-react-live-data/.env.qa056 .env
   uv run alembic upgrade head
   uv run python scripts/qa/seed_usage_qa056.py
   ```

3. Start the API:

   ```bash
   uv run uvicorn multi_agent_platform.api.main:app --reload
   ```

4. Open the usage workspace:

   ```text
   http://127.0.0.1:8000/admin/app/usage?tenant_id=11111111-1111-1111-1111-111111111111
   ```

## Expected Behavior

- Acme scope shows seeded live usage totals, trend points, rollups, drilldown
  rows, confidence states, and export history.
- Globex scope shows a truthful empty state with no invented usage or exports.
- Creating an export from the UI persists a `usage_export_requests` row and
  returns artifact metadata only after storage-backed completion.
- JSON responses, screenshots, docs, and export metadata exclude raw prompts,
  completions, secrets, credentials, run payloads, tool payloads, local paths,
  stack traces, and unauthorized tenant labels.

## Fixture-Removal Inventory

- `src/multi_agent_platform/admin/usage/react_usage.py`: remove production
  `USAGE_EVENTS`, fixed qa035 timestamps, fixed export IDs, and hard-coded
  tenant labels; replace them with live `UsageRepository` and
  `UsageAnalyticsService` inputs.
- `src/multi_agent_platform/api/routers/admin_react.py`: wire usage routes to
  async live builders with request-scoped repository, service, and storage
  dependencies.
- `frontend/admin/src/components/usage/UsagePage.tsx`: keep the browser bound
  to backend routes and use the export API for write-through export creation.
- `tests/unit/admin/usage/test_react_usage_service.py`: replace production
  fixture expectations with seeded and empty live database expectations.
- `tests/integration/test_admin_react_routes.py`: seed persisted usage rows for
  route tests and verify seeded, empty, export, and cross-tenant behavior.
- `frontend/admin/src/api/generated/reactAdminApi.ts`: regenerated after schema
  enum updates for missing, reconciliation-pending, queued, validation,
  conflict, and unavailable states.

## Validation Commands

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/056-usage-react-live-data
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/remove-mock-data-roadmap/056-usage-react-live-data/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/056-usage-react-live-data/validation.yml --start-processes
uv run python scripts/qa/verify_usage_qa056.py
uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa056-after-spec
```
