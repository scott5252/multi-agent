# Quickstart: React Workflow Builder

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

Start the worker when validating publish and runtime-readiness summaries:

```bash
uv run python -m multi_agent_platform.workers.main
```

## Browser Entry

Open the local-principal login flow:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/workflows
```

Use `tenant-admin-acme` to validate tenant-scoped draft authoring.

Use `platform-admin` to validate platform workflow administration.

Use `auditor` only for read/review paths when available.

## API Smoke Checks

Builder shell:

```bash
curl --fail --silent --show-error \
  -H "X-Local-Principal: tenant-admin-acme" \
  "http://127.0.0.1:8000/admin/app/workflows?tenant_id=11111111-1111-1111-1111-111111111111"
```

Builder envelope:

```bash
curl --fail --silent --show-error \
  -H "X-Local-Principal: tenant-admin-acme" \
  "http://127.0.0.1:8000/admin/app/workflows/builder.json?tenant_id=11111111-1111-1111-1111-111111111111"
```

Reference lookups:

```bash
curl --fail --silent --show-error \
  -H "X-Local-Principal: tenant-admin-acme" \
  "http://127.0.0.1:8000/admin/app/workflows/lookups.json?tenant_id=11111111-1111-1111-1111-111111111111"
```

Denied route:

```bash
test "$(curl --silent --output /tmp/qa030-denied.json --write-out '%{http_code}' \
  "http://127.0.0.1:8000/admin/app/workflows/builder.json")" = "401"
```

## Focused Validation

```bash
uv run pytest --no-cov \
  tests/unit/api/test_admin_workflow_builder_schema.py \
  tests/unit/admin/test_workflow_builder_service.py \
  tests/contract/test_admin_react_contract.py \
  tests/integration/test_admin_react_routes.py \
  tests/performance/workflows/test_workflow_builder_queries.py
cd frontend/admin && npm run typecheck && npm run test && npm run build
cd ../..
uv run python scripts/frontend/generate_admin_react_types.py --check
```

## Full QA030 Validation

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/030-react-workflow-builder
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui-roadmap/030-react-workflow-builder/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/030-react-workflow-builder/validation.yml --start-processes
```

## Expected Evidence

- Builder route denies unauthenticated access.
- Tenant admin can load guided workflow builder.
- Platform admin can load platform workflow builder.
- Draft can be edited and saved explicitly.
- Validation runs on demand and after save.
- Graph canvas has list/keyboard alternatives.
- Publish gate blocks missing or stale evidence.
- Publish gate accepts ready fixture after explicit confirmation.
- Stale revision conflicts show safe recovery.
- No raw secrets, prompts, completions, memory, private messages, provider responses, Telegram updates, connector outputs, local paths, stack traces, or unauthorized tenant labels appear.
