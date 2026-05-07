# Prompt Runtime Profiles Testing

## Focused Commands

```bash
uv run pytest --no-cov \
  tests/unit/prompts \
  tests/unit/agents \
  tests/unit/api/test_prompt_runtime_ui_models.py \
  tests/unit/audit/test_prompt_runtime_audit.py \
  tests/unit/audit/test_prompt_runtime_observability.py \
  tests/unit/audit/test_prompt_runtime_audit_fail_closed.py \
  tests/contract/test_prompt_library_contract.py \
  tests/contract/test_prompt_lifecycle_contract.py \
  tests/contract/test_agent_profiles_contract.py \
  tests/contract/test_runtime_profile_resolution_contract.py \
  tests/contract/test_prompt_runtime_profiles_contract.py \
  tests/integration/api/test_admin_prompts_api.py \
  tests/integration/api/test_admin_prompts_ui.py \
  tests/integration/api/test_admin_agent_profiles_ui.py \
  tests/integration/api/test_prompt_runtime_browser_flows.py \
  tests/integration/api/test_agent_profile_browser_flows.py \
  tests/integration/api/test_prompt_runtime_admin_navigation.py \
  tests/integration/api/test_prompt_runtime_rate_limits.py \
  tests/integration/model_skill_config/test_prompt_reference_library_integration.py \
  tests/integration/runtime/test_prompt_profile_pinning.py \
  tests/integration/workflows/test_prompt_profile_workflow_validation.py \
  tests/performance/prompt_runtime/test_prompt_runtime_latency.py \
  tests/docs/test_prompt_runtime_profiles_docs.py
```

## Required Quality Gates

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

## Spec 012 V2 Gateway Verification

```bash
uv run pytest tests/unit/model_providers tests/unit/bootstrap tests/unit/runtime tests/unit/reliability
uv run pytest tests/contract/test_runtime_gateway_execution_contract.py
uv run pytest tests/integration/runtime tests/integration/workers tests/integration/model_providers
uv run pytest tests/integration/api/test_admin_model_provider_probe_limits.py
uv run pytest tests/docs/test_prompt_runtime_profiles_v2_docs.py
```

Spec 012 V2 acceptance requires `ModelGateway` for model-backed runtime, profile
test bench, and model-backed workflow validation calls; duplicate gateway,
probe, and catalog operations must recover through logical operation
identities; direct provider SDK or HTTP calls outside adapter modules must be
blocked by guardrail tests.

## Captured Evidence

- Completion pass for legacy prompt/profile browser workflows
  (2026-04-28):
  - `uv run pytest --no-cov tests/integration/api/test_prompt_runtime_browser_flows.py tests/integration/api/test_agent_profile_browser_flows.py`: 2 passed. These historical tests covered prompt save, validation, preview, publish, retire, grants, profile policy sections, activation, grants, resolution, retire, and cross-tenant denial paths before the React-only browser decommission.
  - `uv run pytest --no-cov tests/unit/api/test_prompt_runtime_ui_routes.py tests/unit/api/test_admin_agent_profiles_routes.py tests/integration/api/test_admin_prompts_api.py tests/integration/api/test_prompt_runtime_browser_flows.py tests/integration/api/test_agent_profile_browser_flows.py tests/contract/test_prompt_runtime_profiles_contract.py tests/contract/test_prompt_library_contract.py tests/contract/test_agent_profiles_contract.py tests/contract/test_prompt_lifecycle_contract.py tests/unit/auth/test_prompt_runtime_policy.py tests/unit/agents/test_profile_service.py tests/unit/agents/test_prompt_reference_validation.py tests/unit/agents/test_profile_resolution.py tests/unit/prompts/test_tenant_isolation.py`: 23 passed.
  - `uv run ruff check .`: passed.
  - `uv run ruff format --check .`: passed, 643 files already formatted.
  - `uv run mypy src`: passed, 240 source files checked.
  - `uv run pytest --no-cov`: 628 passed, 1 existing SQLAlchemy table-cycle warning.
- `uv run ruff check .`: passed.
- `uv run ruff format --check .`: passed, 643 files already formatted.
- `uv run mypy src`: passed, 240 source files checked.
- `uv run alembic upgrade head && uv run alembic downgrade 0012_prompt_runtime_profiles && uv run alembic upgrade head`: passed, confirming the additive V2 gateway migration upgrades and rolls back without destructive Spec 012 rewrites.
- `uv run pytest --no-cov tests/unit/bootstrap/test_container_model_gateway_factories.py tests/unit/model_providers/test_gateway_dependency_lifecycle.py tests/unit/bootstrap/test_worker_gateway_bootstrap.py tests/integration/workers/test_worker_gateway_readiness.py tests/integration/db/test_prompt_runtime_profiles_v2_gateway_migration.py tests/unit/db/test_model_provider_operation_repository.py tests/unit/runtime/orchestration/test_model_gateway_invocation.py tests/integration/runtime/test_prompt_profile_gateway_pinning.py tests/integration/runtime/test_profile_test_bench_gateway.py tests/unit/agents/test_profile_gateway_routing_context.py tests/contract/test_runtime_gateway_execution_contract.py tests/integration/workflows/test_workflow_validation_model_gateway.py tests/unit/reliability/test_gateway_retry_decisions.py tests/unit/reliability/test_gateway_breaker_decisions.py tests/integration/runtime/test_gateway_operation_recovery.py tests/integration/api/test_admin_provider_probe_recovery.py tests/integration/model_providers/test_catalog_sync_recovery.py tests/integration/api/test_admin_model_provider_probe_limits.py tests/unit/model_providers/test_provider_probe_audit.py tests/unit/guardrails/test_model_gateway_only_provider_calls.py tests/integration/runtime/test_model_gateway_guardrails.py tests/unit/model_providers/test_gateway_safe_observability.py tests/integration/model_providers/test_gateway_attempt_evidence.py tests/integration/model_skill_config/test_prompt_profile_gateway_provenance.py tests/docs/test_prompt_runtime_profiles_v2_docs.py tests/integration/api/test_prompt_runtime_v2_browser_regression.py`: 35 passed.
- `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90`: 625 passed, 1 SQLAlchemy table-cycle warning, total coverage 90.03%.
- `bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/012-prompt-runtime-profiles`: passed.

## Spec 012 V2 Evidence Notes

- Runtime execution, profile test bench calls, and model-backed workflow validation route through `ModelGateway` with tenant, run, step, trace, idempotency, prompt version, profile version, model routing, and safe policy context.
- Gateway invocations, provider probes, and catalog sync operations persist logical operation identities, child physical attempts, duplicate suppression, authoritative outcome reuse, and safe recovery summaries.
- Admin provider probes enforce rate limits and bounded-operation checks before provider activity, and denied or throttled attempts record safe audit evidence.
- Retry and circuit breaker summaries are recorded on gateway attempts with normalized provider outcomes and no raw prompt, completion, credential, token, API key, endpoint secret, unsafe preview, or cross-tenant content.
- Static and behavioral guardrails enforce direct provider calls only inside the explicit `ModelGateway` adapter allowlist.
- New V2 provenance joins immutable prompt/profile pins with provider gateway operation metadata for new runs while historical pre-V2 records report metadata unavailable instead of receiving backfilled rewrites.

## Manual Evidence

Use `specs/012-prompt-runtime-profiles/qa012.md` for copy/paste setup,
deterministic seed data, API checks, browser checks, negative-path checks,
security scans, expected outputs, troubleshooting, and acceptance evidence.

Record the command output, browser URLs visited, audit/redaction scan results,
and any known gaps in the PR notes before review.
