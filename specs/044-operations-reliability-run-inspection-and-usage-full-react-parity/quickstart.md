# Quickstart: Operations, Reliability, Run Inspection, And Usage Full React Parity

## Focused Validation

```bash
uv run pytest --no-cov \
  tests/integration/api/test_admin_operations_ui.py \
  tests/integration/api/test_reliability_controls_ui.py \
  tests/integration/api/test_admin_run_inspection_ui.py \
  tests/integration/api/test_web_run_ui.py \
  tests/integration/api/test_admin_usage_ui.py \
  tests/integration/test_admin_react_routes.py \
  tests/contract/test_admin_react_contract.py \
  tests/unit/admin/test_operations_jinja_retirement.py \
  tests/unit/api/test_admin_workbench_schema.py \
  tests/unit/api/test_admin_usage_react_schema.py \
  tests/performance/operations/test_workbench_queries.py \
  tests/performance/usage/test_react_usage_queries.py -q
```

Expected result: old operations, reliability, run inspection, and usage browser
routes redirect to React or return safe non-Jinja problems; retained JSON APIs
continue to serve React; retired templates are not referenced.

## Frontend Validation

```bash
cd frontend/admin
npm test -- --run src/components/workbench src/components/usage src/App.test.tsx
npm run build
cd ../..
```

Expected result: React operations and usage workspaces render safe summaries,
run debug, export metadata, and route handling.

## Manual Browser Checks

- Open `/auth/local-login?redirect_to=/admin/app/operations` and sign in as
  `platform-admin`.
- Confirm `/admin/app/operations` shows operations, reliability, run debug, and
  export metadata.
- Open `/admin/operations` and confirm it redirects to `/admin/app/operations`.
- Open `/admin/reliability/ui/breakers` and confirm it redirects to the React
  reliability panel.
- Open `/admin/runs` and confirm it redirects to React run inspection.
- Open `/runs` and `/runs/{run_id}` with authorized local scope and confirm
  they redirect to React channel run status surfaces.
- Open `/admin/usage` and confirm it redirects to `/admin/app/usage`.
- Open a usage export detail route and confirm React shows only export metadata.
- Search browser text and saved JSON for raw prompts, completions, memory,
  stack traces, storage paths, raw CSV rows, and provider headers.

## Final Validation

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/044-operations-reliability-run-inspection-and-usage-full-react-parity
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui2-roadmap/044-operations-reliability-run-inspection-and-usage-full-react-parity/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui2-roadmap/044-operations-reliability-run-inspection-and-usage-full-react-parity/validation.yml --start-processes
```

Expected result: QA docs, quality gates, full coverage gate, and Playwright
validation pass before advancing to Spec 045.
