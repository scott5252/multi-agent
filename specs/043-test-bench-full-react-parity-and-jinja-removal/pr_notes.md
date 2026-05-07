# PR Notes: Spec 043

## Summary

- Moves agent/workflow test bench browser journeys fully to React under
  `/admin/app/test-bench`.
- Converts old `/admin/agent-tests/ui...` browser routes to authenticated
  redirects or safe non-Jinja problem responses.
- Preserves old suite, case, and run form POST behavior, then redirects to React
  with mutation state.
- Deletes `agent_tests` Jinja templates and adds scanner tests proving the
  router no longer renders them.
- Adds backend, contract, docs, generated type, and React component coverage for
  legacy route context, artifact/gate unavailable states, and redaction-safe test
  bench data.

## Validation

- `uv run ruff check .`
- `uv run ruff format --check .`
- `uv run mypy src`
- `uv run pytest --no-cov tests/integration/api/test_admin_agent_tests_legacy_redirects.py tests/integration/api/test_admin_agent_tests_api.py tests/integration/test_admin_react_routes.py tests/contract/test_admin_react_contract.py tests/unit/admin/test_test_bench_jinja_retirement.py tests/unit/admin/test_test_bench_react_service.py tests/unit/api/test_admin_test_bench_schema.py tests/performance/test_bench/test_react_test_bench_queries.py tests/docs/test_agent_test_bench_docs.py -q`
- `cd frontend/admin && npm test -- --run src/components/testBench src/App.test.tsx`
- `cd frontend/admin && npm run build`
- `bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/043-test-bench-full-react-parity-and-jinja-removal`
- `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui2-roadmap/043-test-bench-full-react-parity-and-jinja-removal/validation.yml`
- `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui2-roadmap/043-test-bench-full-react-parity-and-jinja-removal/validation.yml --start-processes`

## Reviewer Focus

- Verify old `/admin/agent-tests/ui`, `/admin/agent-tests/ui/suites/new`,
  `/admin/agent-tests/ui/suites/{suite_id}`, and
  `/admin/agent-tests/ui/runs/{run_id}` URLs redirect to `/admin/app/test-bench`
  with safe context.
- Verify old suite, case, and run form POSTs still perform backend mutations
  before redirecting to React.
- Verify React test bench payloads contain safe summaries, checksums, audit
  references, and artifact references, not raw prompts, completions, memory
  contents, storage paths, headers, or private payloads.
- Verify tenant-scoped routes fail closed and do not reveal unauthorized suite
  or run labels.
