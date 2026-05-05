# PR Notes: React Agent And Workflow Test Bench

## Summary

Implemented an additive React test bench workspace at `/admin/app/test-bench`.

The backend adds safe test bench schemas, deterministic aggregation builders,
protected React routes, policy surface entries, generated TypeScript contracts,
and focused unit/integration/performance coverage.

The frontend adds a browser-first test bench page with suite authoring, case
authoring, target revision binding, structured assertion summaries, safe
execution mode selection, deterministic run launch, progress, run details,
trace and artifact evidence, publish gate evidence, and governance audit
timeline sections.

Existing Jinja agent test bench pages remain available.

## Safety Notes

- Raw fixture bodies are not returned to React.
- Raw prompts, completions, transcripts, memory contents, connector payloads,
  credential values, provider tokens, authorization headers, local paths, and
  artifact storage paths are rejected by schema validators.
- Mock model and tool execution is the default local safe mode.
- Side-effect-disabled gateway mode is explicit.
- Live dependency probe mode fails closed in local QA.
- React renders backend-owned pass/fail/gate/audit state and does not evaluate
  test results locally.
- Artifact evidence is represented as metadata references only.
- Cross-tenant access returns safe denial summaries.

## Validation

```bash
uv run pytest --no-cov \
  tests/unit/api/test_admin_test_bench_schema.py \
  tests/unit/admin/test_test_bench_react_service.py \
  tests/performance/test_bench/test_react_test_bench_queries.py \
  tests/contract/test_admin_react_contract.py \
  tests/integration/test_admin_react_routes.py
```

Result: passed, 39 tests.

```bash
cd frontend/admin
npm run typecheck
npm run test
cd ../..
```

Result: passed.

```bash
uv run python scripts/frontend/generate_admin_react_types.py --check
```

Result: passed.

```bash
uv run ruff check src/multi_agent_platform/api/schemas/admin_test_bench.py src/multi_agent_platform/testing/agent_bench/react_test_bench.py src/multi_agent_platform/api/routers/admin_react.py tests/unit/api/test_admin_test_bench_schema.py tests/unit/admin/test_test_bench_react_service.py tests/performance/test_bench/test_react_test_bench_queries.py tests/contract/test_admin_react_contract.py tests/integration/test_admin_react_routes.py
```

Result: passed.

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/033-react-agent-and-workflow-test-bench
```

Result: passed.

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui-roadmap/033-react-agent-and-workflow-test-bench/validation.yml
```

Result: passed after QA033 database reset, curl/API checks, QA document
validation, Ruff, format, mypy, full coverage, focused backend tests, frontend
typecheck/tests/build, and generated contract drift check.

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/033-react-agent-and-workflow-test-bench/validation.yml --start-processes
```

Result: passed.

## QA Evidence

- `output/playwright/qa033_ui/qa033-react-test-bench-denied.png`
- `output/playwright/qa033_ui/qa033-react-test-bench-tenant.png`
- `output/playwright/qa033_ui/qa033-react-test-bench-authoring.png`
- `output/playwright/qa033_ui/qa033-react-test-bench-run.png`
- `output/playwright/qa033_ui/qa033-react-test-bench-result.png`
- `output/playwright/qa033_ui/qa033-react-test-bench-gates.png`
- `output/playwright/qa033_ui/qa033-react-test-bench-audit.png`

Redaction scan:

```bash
rg -n "qa033-secret-value|raw prompt|raw completion|resolved credential|authorization header|provider token|private message|connector request|connector response|raw tool output|raw transcript|stack trace|/Users/|Globex" /tmp/qa033-* output/playwright/qa033_ui || true
```

Result: no matches.

## Reviewer Checklist

- Confirm suite and case save results are backend mutation summaries.
- Confirm safe execution mode defaults to mock model and tools.
- Confirm live dependency probe mode fails closed locally.
- Confirm run details show diagnostic and trace summaries without raw runtime data.
- Confirm artifact evidence exposes metadata references only.
- Confirm publish gates represent current target revision evidence.
- Confirm generated TypeScript contracts are current.
- Confirm no screenshots or JSON evidence include unsafe text.
- Confirm existing Jinja routes still render.
