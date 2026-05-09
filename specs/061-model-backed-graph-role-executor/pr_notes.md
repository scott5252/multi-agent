# PR Notes: Spec 061 - Model-Backed Graph Role Executor

## Summary

Spec 061 adds a governed model-backed role executor for workflow graph nodes.

Deterministic role execution remains the default.

Model-backed execution is selected only through explicit role execution mode.

The model-backed path resolves tenant-scoped model, prompt, profile, provider,
and policy pins before invoking the gateway.

The runtime calls `ModelGateway` instead of provider clients directly.

Structured model output is parsed, redaction-checked, validated against role
output contracts, and returned as safe graph-compatible evidence.

Usage, provenance, payload digest, and artifact references are preserved in
`RoleExecutionResult` metadata.

Worker bootstrap and orchestration polling now pass optional model gateway,
configuration, and storage dependencies into graph execution.

## Validation

Focused backend validation:

```bash
uv run pytest tests/contract/test_model_backed_role_executor_contracts.py tests/unit/runtime/orchestration/test_model_backed_roles.py tests/unit/runtime/orchestration/test_graph_roles.py tests/unit/bootstrap/test_worker_gateway_bootstrap.py tests/integration/runtime/test_model_backed_graph_execution.py --no-cov
```

QA document validation:

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/061-model-backed-graph-role-executor
```

Spec Kit QA:

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/scenario-enhancement-roadmap/061-model-backed-graph-role-executor/validation.yml
```

Playwright UI smoke:

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/scenario-enhancement-roadmap/061-model-backed-graph-role-executor/validation.yml --start-processes
```

Full curl regression:

```bash
uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa061-after-spec
```

## Curl Testing Note

Spec 061 does not add or change a public/admin/runtime JSON API route family.

`curl_testing.md` does not require a new section for this spec.

The full multi-agent curl regression remains required after QA061 validation.

