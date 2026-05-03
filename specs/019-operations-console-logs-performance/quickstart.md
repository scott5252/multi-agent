# Quickstart: Operations Console Logs And Performance

## Local QA Setup

1. Sync dependencies:

   ```bash
   uv sync
   ```

2. Copy the QA environment:

   ```bash
   cp specs/019-operations-console-logs-performance/.env.qa019 .env
   ```

3. Start PostgreSQL and reset the QA database:

   ```bash
   docker compose up -d postgres
   docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa019 && createdb -U postgres multi_agent_platform_qa019'
   uv run alembic upgrade head
   ```

4. Start the API:

   ```bash
   uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
   ```

5. In another terminal, start the worker:

   ```bash
   uv run python -m multi_agent_platform.workers.main
   ```

## Browser Validation

1. Open `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/operations`.
2. Choose `platform-admin`.
3. Verify the page title is `Operations Console`.
4. Confirm the dashboard shows health, dependencies, capacity, provider,
   Telegram/channel, usage, reliability, latency, throughput, error, and log
   sections.
5. Apply a filter such as `component=gateway` or a seeded `trace_id`.
6. Confirm the logs remain redacted.
7. Run an export and confirm artifact metadata is returned.

## API Checks

```bash
curl --fail --silent http://127.0.0.1:8000/health/live
curl --fail --silent http://127.0.0.1:8000/health/ready
curl --fail --silent http://127.0.0.1:8000/version
curl --fail --silent http://127.0.0.1:8000/dependencies
curl --fail --silent -H 'X-Local-Principal: platform-admin' http://127.0.0.1:8000/admin/operations/api/dashboard
curl --fail --silent -H 'X-Local-Principal: platform-admin' http://127.0.0.1:8000/admin/operations/api/logs
```

## Quality Gates

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

## Redaction Checks

The UI, JSON APIs, CSV exports, screenshots, and audit metadata must not contain:

- raw prompts or completions
- model responses
- raw Telegram/channel messages
- secrets, credential values, API keys, tokens, or authorization headers
- raw provider payloads
- memory content
- stack traces or tracebacks
- unauthorized tenant data
