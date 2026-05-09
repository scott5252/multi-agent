# Quickstart: Model-Backed Graph Role Executor

## Prerequisites

```bash
uv sync
docker compose up -d postgres
uv run alembic upgrade head
```

## Run Focused Tests

```bash
uv run pytest \
  tests/unit/runtime/orchestration/test_model_backed_roles.py \
  tests/unit/runtime/orchestration/test_graph_roles.py \
  tests/unit/bootstrap/test_worker_gateway_bootstrap.py \
  tests/contract/test_model_backed_role_executor_contracts.py \
  tests/integration/runtime/test_model_backed_graph_execution.py \
  --no-cov
```

## Run Spec QA

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh \
  specs/061-model-backed-graph-role-executor

uv run python scripts/qa/run_spec_qa.py \
  specs/_autopilot/scenario-enhancement-roadmap/061-model-backed-graph-role-executor/validation.yml

uv run python scripts/qa/run_playwright_ui.py \
  specs/_autopilot/scenario-enhancement-roadmap/061-model-backed-graph-role-executor/validation.yml \
  --start-processes
```

## Run Curl Regression

```bash
docker compose up -d postgres
uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py \
  --output-dir .data/curl_test_runs/qa061-after-spec
```

## Manual Validation Notes

- Confirm deterministic graph execution still passes without model-backed pins.
- Confirm mocked model-backed execution uses `ModelGateway` and records safe
  usage/provenance.
- Confirm missing pins, denied policy, cross-tenant context, malformed output,
  and unsafe output fail closed with safe error codes.
- Confirm no QA artifact, screenshot, log, response, or stored metadata exposes
  raw prompts, completions, provider payloads, credentials, memory contents,
  private channel payloads, unauthorized payloads, or raw external tool payloads.
