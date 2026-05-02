# Testing Instructions: Agent And Workflow Test Bench

## Setup

```bash
test ! -f .env || cp .env .env.autopilot-backup
cp specs/015-agent-workflow-test-bench/.env.qa015 .env
uv sync
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa015 && createdb -U postgres multi_agent_platform_qa015'
uv run alembic upgrade head
mkdir -p .data/qa015-artifacts output/playwright/qa015_ui
```

Seed Acme and Globex tenants with the SQL block in `qa015.md`.

## Focused Automated Tests

```bash
uv run pytest --no-cov \
  tests/unit/testing/agent_bench \
  tests/unit/db/test_agent_tests_models.py \
  tests/unit/db/test_agent_tests_repository.py \
  tests/unit/api/test_agent_test_schemas.py \
  tests/unit/auth/test_agent_test_policy.py \
  tests/unit/admin/test_publish_gate.py \
  tests/contract/test_agent_test_bench_contract.py \
  tests/integration/runtime/test_agent_workflow_test_bench_gateway.py \
  tests/integration/api/test_admin_agent_tests_api.py \
  tests/docs/test_agent_test_bench_docs.py
```

## QA Document Validation

```bash
.specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/015-agent-workflow-test-bench
```

## API Validation

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/015-agent-workflow-test-bench/validation.yml
```

## Browser Validation

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/015-agent-workflow-test-bench/validation.yml --start-processes
```

## Quality Gates

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

## Manual Browser Path

1. Open `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/agent-tests/ui?tenant_id=11111111-1111-1111-1111-111111111111`.
2. Sign in as `tenant-admin-acme`.
3. Create `QA015 Draft Workflow Guard`.
4. Add `Passing intake case` with the fixture and assertions from `qa015_ui.md`.
5. Run once with `mock_model`.
6. Run once with `real_model_side_effects_disabled`.
7. Confirm blocked side effects, redaction notice, trace steps, usage, latency,
   and publish gate readiness.
8. Sign in as `tenant-admin-globex` and confirm Acme suite data is denied.

## Acceptance Criteria

- No raw fake secret value appears in API responses or rendered HTML.
- Globex cannot see Acme suite, run, fixture, transcript, target, or artifact
  metadata.
- Approved real dependency probes are rejected without approval metadata.
- The current target version has ready publish gate evidence after a passing
  run.
- A stale target version remains blocked.
