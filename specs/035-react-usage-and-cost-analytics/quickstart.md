# Quickstart: React Usage And Cost Analytics

## Scope

Spec 035 adds a React workspace at `/admin/app/usage` for safe usage and cost
analytics. The existing server-rendered `/admin/usage` pages and Spec 016 APIs
remain available as fallbacks.

## Local Setup

```bash
uv sync
uv run alembic upgrade head
cd frontend/admin
npm install
npm run typecheck
npm run test
npm run build
```

## Backend Validation

Run focused backend tests after implementation:

```bash
uv run pytest --no-cov \
  tests/unit/api/test_admin_usage_react_schema.py \
  tests/unit/admin/usage/test_react_usage_service.py \
  tests/performance/usage/test_react_usage_queries.py \
  tests/contract/test_admin_react_contract.py \
  tests/integration/test_admin_react_routes.py
```

Run full static and generated-type checks:

```bash
uv run python scripts/frontend/generate_admin_react_types.py --check
uv run mypy src
uv run ruff check .
uv run ruff format --check .
```

## QA Validation

Spec QA must use the generated QA035 environment and validation manifest:

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh \
  specs/035-react-usage-and-cost-analytics

uv run python scripts/qa/run_spec_qa.py \
  specs/_autopilot/react-ui-roadmap/035-react-usage-and-cost-analytics/validation.yml

uv run python scripts/qa/run_playwright_ui.py \
  specs/_autopilot/react-ui-roadmap/035-react-usage-and-cost-analytics/validation.yml \
  --start-processes
```

## Manual Reviewer Walkthrough

1. Start the API with `uv run uvicorn multi_agent_platform.api.main:app --reload`.
2. Start the React admin app with `npm run dev` in `frontend/admin` if testing
   Vite directly, or use the built assets through FastAPI.
3. Sign in as a platform administrator in local-principal mode.
4. Open `/admin/app/usage`.
5. Confirm the default last 7 days dashboard shows tokens, estimated cost,
   event count, latency, unavailable usage, and confidence coverage.
6. Switch grouping to provider, model, workflow, agent, sub-agent, prompt,
   execution mode, principal, tenant when authorized, gateway operation,
   physical attempt, graph node, and governed tool where options are available.
7. Open a rollup drilldown and confirm rows are bounded to 100 safe events.
8. Create a CSV export and confirm status, row count, filter snapshot, artifact
   reference, checksum prefix, and audit reference are safe.
9. Sign in as `tenant-admin-acme` and confirm the page shows only Acme data,
   tenant-scoped filters, tenant exports, and safe denial for platform-wide or
   Globex requests.

## Performance Bounds

- Dashboard bootstrap returns no more than 8 cards, 31 trend points, 25 rollup
  rows, 100 drilldown preview rows, and 10 recent export summaries.
- Event drilldown returns no more than 100 rows.
- Export generation uses existing Spec 016 export limits and never renders raw
  CSV contents in the browser.
- Deterministic fixture dashboard queries should stay under 300ms p95.

## Redaction Scan

QA evidence must not contain unsafe markers:

```bash
rg -n "qa035-secret-value|raw prompt|raw completion|memory content|authorization header|provider token|credential value|credential reference|raw tool payload|/Users/|unauthorized tenant label|private message" \
  /tmp/qa035-* output/playwright/qa035_ui || true
```

Any match outside intentional documentation text is a blocker.
