# Quickstart: Agent And Workflow Test Bench

## Local Setup

1. Copy the QA environment after implementation:

   ```bash
   cp specs/015-agent-workflow-test-bench/.env.qa015 .env
   ```

2. Install dependencies:

   ```bash
   uv sync
   ```

3. Start PostgreSQL and reset only the QA database:

   ```bash
   docker compose up -d postgres
   docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa015 && createdb -U postgres multi_agent_platform_qa015'
   ```

4. Run migrations:

   ```bash
   uv run alembic upgrade head
   ```

5. Start the API and worker:

   ```bash
   uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
   uv run python -m multi_agent_platform.workers.main
   ```

## Browser Smoke Flow

1. Visit `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/agent-tests/ui`.
2. Sign in as the QA platform admin.
3. Create a suite named `QA015 Draft Workflow Guard`.
4. Set target type to `workflow_draft`, target id to
   `qa015-draft-triage`, target version to `draft-rev-1`, safe mode to
   `mock_model`, and pass threshold to `1.0`.
5. Add a passing case with fixture input:

   ```json
   {"request": "summarize intake", "priority": "routine"}
   ```

6. Add deterministic assertions:

   ```json
   [
     {"kind": "deterministic", "path": "status", "comparator": "equals", "expected_value": "passed"},
     {"kind": "deterministic", "path": "contract.summary", "comparator": "contains", "expected_value": "intake"}
   ]
   ```

7. Run the suite in mock model mode.
8. Open the run detail page and verify pass/fail status, model/provider
   summary, prompt/profile references, token usage, latency, redacted
   transcript summary, blocked side-effect count, and artifact metadata.
9. Switch to the cross-tenant QA admin and verify the suite/run cannot be seen.

## API Smoke Flow

Use the browser flow as the primary reviewer path. API checks are for contract
evidence and automation:

```bash
curl --fail --silent http://127.0.0.1:8000/health/live
curl --fail --silent http://127.0.0.1:8000/health/ready
curl --fail --silent http://127.0.0.1:8000/version
curl --fail --silent http://127.0.0.1:8000/dependencies
```

## Quality Gates

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

## Expected Evidence

- Passing suite/case CRUD tests.
- Passing sandbox run tests for mock model, mocked provider, side-effect
  blocking, deterministic assertions, evaluator assertions, redaction, and
  usage capture.
- Passing API and UI tests for unauthorized denial and tenant isolation.
- Passing publish-gate tests for missing, stale, failing, and current passing
  evidence.
- Screenshots under `output/playwright/qa015_ui`.
