# Quickstart: Test Bench Full React Parity And Jinja Removal

## Purpose

Validate that the test bench browser experience is React-only while backend JSON APIs, tenant isolation, redaction, safe execution modes, publish-gate evidence, and old direct links continue to work safely.

## Local Environment

1. `uv sync`
2. `uv run alembic upgrade head`
3. `uv run python scripts/frontend/generate_admin_react_types.py --check`
4. `cd frontend/admin && npm test -- --run src/components/testBench src/App.test.tsx`
5. `cd frontend/admin && npm run build`

## Focused Backend Checks

Run:

```bash
uv run pytest --no-cov \
  tests/integration/api/test_admin_agent_tests_legacy_redirects.py \
  tests/integration/api/test_admin_agent_tests_api.py \
  tests/integration/test_admin_react_routes.py \
  tests/contract/test_admin_react_contract.py \
  tests/unit/admin/test_test_bench_jinja_retirement.py \
  tests/unit/admin/test_test_bench_react_service.py \
  tests/unit/api/test_admin_test_bench_schema.py \
  tests/performance/test_bench/test_react_test_bench_queries.py
```

Expected result: legacy `/admin/agent-tests/ui...` GET routes redirect to React or return safe non-Jinja problems, legacy form posts preserve mutation behavior with React redirects, and no deleted `agent_tests` template is referenced.

## Browser QA

Use `AUTH_MODE=local_principal` and the QA env generated for this spec:

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui2-roadmap/043-test-bench-full-react-parity-and-jinja-removal/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui2-roadmap/043-test-bench-full-react-parity-and-jinja-removal/validation.yml --start-processes
```

The Playwright run must capture a nonblank React test bench screenshot showing suite management, run diagnostics, artifact metadata, publish-gate evidence, and legacy route redirect evidence without unsafe raw content.

## Manual Reviewer Spot Checks

- Open `/admin/agent-tests/ui?tenant_id=<acme>` and confirm it lands on `/admin/app/test-bench`.
- Open `/admin/agent-tests/ui/suites/<suite_id>?tenant_id=<acme>` and confirm the React suite context is preserved.
- Open `/admin/agent-tests/ui/runs/<run_id>?tenant_id=<acme>` and confirm run diagnostics render through React.
- Try a cross-tenant tenant id and confirm safe denial without protected labels.
- Search for `agent_tests` templates and `TemplateResponse` use in `admin_agent_tests.py`; only non-Jinja API behavior should remain.
