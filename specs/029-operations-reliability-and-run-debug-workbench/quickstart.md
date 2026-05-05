# Quickstart: Operations, Reliability, And Run Debug Workbench

## Local Setup

```bash
uv sync
cd frontend/admin
npm install
npm run build
cd ../..
docker compose up -d postgres
uv run alembic upgrade head
```

Start the application:

```bash
uv run uvicorn multi_agent_platform.api.main:app --reload
```

Start the worker when validating run and reliability summaries:

```bash
uv run python -m multi_agent_platform.workers.main
```

## Browser Entry

Open the local-principal login flow:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/operations
```

Use `platform-admin` for the platform workbench.

Use `tenant-admin-acme` for tenant-limited behavior.

## API Smoke Checks

Platform workbench:

```bash
curl --fail --silent --show-error \
  -H "X-Local-Principal: platform-admin" \
  "http://127.0.0.1:8000/admin/app/operations.json"
```

Tenant-limited workbench:

```bash
curl --fail --silent --show-error \
  -H "X-Local-Principal: tenant-admin-acme" \
  "http://127.0.0.1:8000/admin/app/operations.json?tenant_id=11111111-1111-1111-1111-111111111111"
```

Denied route:

```bash
test "$(curl --silent --output /tmp/qa029-denied.json --write-out '%{http_code}' \
  "http://127.0.0.1:8000/admin/app/operations.json")" = "401"
```

Safe export:

```bash
curl --fail --silent --show-error \
  -X POST \
  -H "X-Local-Principal: platform-admin" \
  "http://127.0.0.1:8000/admin/app/operations/export"
```

## Focused Validation

```bash
uv run pytest --no-cov \
  tests/unit/api/test_admin_workbench_schema.py \
  tests/unit/operations/test_workbench_service.py \
  tests/contract/test_admin_react_contract.py \
  tests/integration/test_admin_react_routes.py \
  tests/performance/operations/test_workbench_queries.py
cd frontend/admin && npm run typecheck && npm run test && npm run build
cd ../..
uv run python scripts/frontend/generate_admin_react_types.py --check
```

## Full QA029 Validation

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/029-operations-reliability-and-run-debug-workbench
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui-roadmap/029-operations-reliability-and-run-debug-workbench/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/029-operations-reliability-and-run-debug-workbench/validation.yml --start-processes
```

## Expected Evidence

- Platform summary shows health, pressure, provider/channel, reliability, and safe logs.
- Tenant summary hides platform-only provider, queue, and shared dependency details.
- Run debug summary shows timeline, branches, joins, gateway attempts, tool calls, deliveries, lineage, and replay links.
- Export returns an artifact reference, redaction summary, and audit reference.
- No raw secrets, prompts, completions, memory, private messages, provider payloads, Telegram updates, tool payloads, stack traces, local paths, or unauthorized tenant labels appear.
