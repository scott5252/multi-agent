# Quickstart: Operations And Run Debug React Live Data

## Goal

Validate that the React operations workbench and run-debug routes render live
operational evidence, truthful empty states, persisted export evidence, and
safe redacted summaries without deterministic QA029 workbench rows.

## Local Setup

1. Sync dependencies:

   ```bash
   uv sync
   npm install --prefix frontend/admin
   ```

2. Prepare a qa057 database:

   ```bash
   cp specs/057-operations-and-run-debug-react-live-data/.env.qa057 .env
   uv run alembic upgrade head
   uv run python scripts/qa/seed_operations_qa057.py
   ```

3. Start the API:

   ```bash
   uv run uvicorn multi_agent_platform.api.main:app --reload
   ```

4. Open the operations workbench:

   ```text
   http://127.0.0.1:8000/admin/app/operations?tenant_id=11111111-1111-1111-1111-111111111111
   ```

## Fixture-Removal Inventory

- `src/multi_agent_platform/operations/workbench.py`: remove deterministic
  QA029 cards, logs, run-debug rows, gateway attempts, deliveries, reliability
  items, fallback export snapshots, and fixed evidence references.
- `src/multi_agent_platform/api/routers/admin_react.py`: wire operations,
  run-debug, and export routes to live async builders and scoped dependencies.
- `src/multi_agent_platform/api/schemas/admin_workbench.py`: update schema
  states and export statuses when live unavailable, denied, queued, validation,
  and not-found outcomes need explicit representation.
- `frontend/admin/src/components/workbench/`: keep React bound to backend-owned
  contracts and update tests/test data to live-like qa057 fixtures only.
- `tests/integration/test_admin_react_routes.py`: verify seeded, empty,
  Auth0-shaped, local-principal, export, run-debug, and cross-tenant behavior.
- `tests/performance/operations/`: verify bounded workbench and run-debug
  queries.

## Expected Behavior

- Acme seeded scope shows live health, pressure, run-debug, likely-cause,
  reliability, log, delivery, usage, skill, and export evidence.
- Globex scope shows truthful empty states with no invented incidents or runs.
- Direct run-debug links resolve only authorized live runs.
- Creating an export from the UI persists a workbench export record and exposes
  safe artifact metadata only.
- JSON responses, screenshots, docs, exports, and logs exclude raw secrets,
  credential values, provider authorization headers, prompts, completions,
  memory contents, raw run payloads, private messages, raw tool payloads, local
  paths, stack traces, and unauthorized tenant labels.

## Validation Commands

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/057-operations-and-run-debug-react-live-data
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/remove-mock-data-roadmap/057-operations-and-run-debug-react-live-data/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/057-operations-and-run-debug-react-live-data/validation.yml --start-processes
uv run python scripts/qa/verify_operations_qa057.py
uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa057-after-spec
```
