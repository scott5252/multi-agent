# Testing Instructions: Live Model Credential Resolution For Gateway Calls

## Focused Tests

```bash
uv run pytest --no-cov \
  tests/unit/model_providers/test_secret_references.py \
  tests/unit/model_providers/test_probes.py \
  tests/unit/model_providers/test_model_provider_service.py \
  tests/unit/model_providers/test_gateway.py \
  tests/unit/model_providers/test_adapters.py \
  tests/unit/model_providers/test_validation.py \
  tests/unit/api/test_model_provider_schemas.py \
  tests/unit/bootstrap/test_container_model_gateway_factories.py \
  tests/unit/bootstrap/test_worker_gateway_bootstrap.py \
  tests/integration/runtime/test_gateway_operation_recovery.py \
  tests/integration/model_providers/test_gateway_attempt_evidence.py
```

## QA Scripts

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/025-live-model-credential-resolution-for-gateway-calls/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/025-live-model-credential-resolution-for-gateway-calls/validation.yml --start-processes
```

## Full Quality Gates

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

## Reviewer Notes

- Use only `.env.qa025` with `multi_agent_platform_qa025`.
- Do not use real OpenAI, local model, Telegram, Gmail, Calendar, weather, or tool credentials.
- Confirm provider connections store safe references only.
- Confirm OpenAI probes and runtime gateway calls resolve credentials at call time.
- Confirm local OpenAI-compatible providers may run without credentials only for allowlisted local endpoints.
- Confirm missing or unresolved credentials produce `secret_reference_invalid`.
- Confirm no persisted evidence, rendered page, JSON response, log, README text, or QA artifact contains raw resolved credential values.
