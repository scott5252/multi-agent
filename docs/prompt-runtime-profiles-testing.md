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

## Captured Evidence

- `uv run ruff check .`: passed.
- `uv run ruff format --check .`: passed, 612 files already formatted.
- `uv run mypy src`: passed.
- `uv run alembic upgrade head`: passed.
- `uv run alembic downgrade 0011_model_provider_gateway && uv run alembic upgrade head`: passed.
- `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90`: 589 passed, 1 SQLAlchemy table-cycle warning, total coverage 90.00%.
- `bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/012-prompt-runtime-profiles`: passed.

## Manual Evidence

Use `specs/012-prompt-runtime-profiles/qa012.md` for copy/paste setup,
deterministic seed data, API checks, browser checks, negative-path checks,
security scans, expected outputs, troubleshooting, and acceptance evidence.

Record the command output, browser URLs visited, audit/redaction scan results,
and any known gaps in the PR notes before review.
