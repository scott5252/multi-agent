# PR Review Notes: Agent And Workflow Test Bench

## Scope

Spec 015 adds a tenant-scoped agent and workflow test bench for admins. The
slice introduces durable suite, case, assertion, run, run-step, and publication
requirement metadata; deterministic sandbox execution; safe redaction helpers;
admin JSON APIs; server-rendered admin UI pages; local-principal permissions;
and publish gate evidence summaries.

## Reviewer Focus

- Confirm `/admin/agent-tests/ui` is reachable from the admin shell in tenant
  scope.
- Confirm `/admin/agent-tests` APIs enforce tenant isolation for suites, cases,
  runs, and gate evaluation.
- Confirm mock model, mock tools, and real-model-side-effects-disabled modes do
  not perform external writes.
- Confirm approved real probes fail closed without explicit approval metadata.
- Confirm fixture, transcript, prompt, provider, credential, tool, and artifact
  values are summarized or redacted before display.
- Confirm publish gate evidence accepts only current passing runs for the
  candidate target version.
- Confirm docs and QA files are self-contained for `multi_agent_platform_qa015`.

## Safe Limitations

- QA015 uses deterministic sandbox execution and mocked provider metadata.
- Large artifact payload storage is represented through safe metadata and
  references in this slice.
- Rich asynchronous worker orchestration for long-running bench runs can be
  extended later without changing the safe-mode contract.

## Required Evidence

- `.specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/015-agent-workflow-test-bench`
- `uv run pytest --no-cov tests/unit/testing/agent_bench tests/unit/db/test_agent_tests_models.py tests/unit/db/test_agent_tests_repository.py tests/unit/api/test_agent_test_schemas.py tests/unit/auth/test_agent_test_policy.py tests/unit/admin/test_publish_gate.py tests/contract/test_agent_test_bench_contract.py tests/integration/runtime/test_agent_workflow_test_bench_gateway.py tests/integration/api/test_admin_agent_tests_api.py`
- `uv run ruff check .`
- `uv run ruff format --check .`
- `uv run mypy src`
- `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90`
- `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/015-agent-workflow-test-bench/validation.yml`
- `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/015-agent-workflow-test-bench/validation.yml --start-processes`

## Files To Inspect

- `src/multi_agent_platform/testing/agent_bench/service.py`
- `src/multi_agent_platform/testing/agent_bench/sandbox.py`
- `src/multi_agent_platform/testing/agent_bench/redaction.py`
- `src/multi_agent_platform/db/models/agent_tests.py`
- `src/multi_agent_platform/db/repositories/agent_tests.py`
- `src/multi_agent_platform/api/routers/admin_agent_tests.py`
- `src/multi_agent_platform/web_admin/templates/agent_tests/`
- `src/multi_agent_platform/auth/policy.py`
- `src/multi_agent_platform/admin/workflow_registry/publish_gate.py`
- `tests/integration/api/test_admin_agent_tests_api.py`
- `specs/015-agent-workflow-test-bench/qa015.md`
- `specs/015-agent-workflow-test-bench/qa015_ui.md`
- `specs/015-agent-workflow-test-bench/qa015_user_guide.md`
