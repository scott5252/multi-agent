# Quickstart: Token Usage And Cost Analytics

## Local Setup

1. Copy the QA environment after implementation:

   ```bash
   cp specs/016-token-usage-cost-analytics/.env.qa016 .env
   ```

2. Install dependencies:

   ```bash
   uv sync
   ```

3. Start PostgreSQL and reset only the QA database:

   ```bash
   docker compose up -d postgres
   docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa016 && createdb -U postgres multi_agent_platform_qa016'
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

1. Visit `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/usage`.
2. Sign in as the QA platform admin.
3. Open `Usage Analytics` from the admin navigation.
4. Verify the dashboard renders summary cards, filters, rollups, event
   drilldown rows, and an export action.
5. Switch to tenant scope and verify only that tenant's usage appears.
6. Sign in as the cross-tenant QA admin and verify other-tenant usage is not
   visible.
7. Trigger a CSV export from the dashboard and verify the export detail page
   shows safe metadata, row count, status, artifact reference, and no raw model
   content.

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

- Passing normalization and pricing tests for complete, partial, malformed, and
  estimated provider usage.
- Passing ModelGateway capture test proving safe usage events are recorded.
- Passing dashboard and export tests for platform admin, tenant admin, and
  denied access.
- Passing redaction tests proving stored events, exports, and audits contain no
  raw prompts, completions, secrets, memory content, or provider credentials.
- Screenshots under `output/playwright/qa016_ui`.
