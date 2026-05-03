# Quickstart: Telegram Configuration Console

## Local QA Setup

1. Install dependencies:

   ```bash
   uv sync
   ```

2. Start PostgreSQL and migrate:

   ```bash
   docker compose up -d postgres
   uv run alembic upgrade head
   ```

3. Use the QA017 environment:

   ```bash
   cp specs/017-telegram-configuration-console/.env.qa017 .env
   ```

4. Start the API:

   ```bash
   uv run uvicorn multi_agent_platform.api.main:app --reload
   ```

5. Open the local login page:

   ```text
   http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/telegram
   ```

6. Sign in as `platform-admin` for platform readiness and as
   `tenant-admin-acme` for tenant-scoped controls.

## API Smoke Checks

```bash
curl --fail --silent -H "X-Local-Principal: platform-admin" \
  http://127.0.0.1:8000/admin/telegram/api/readiness

curl --fail --silent -H "X-Local-Principal: tenant-admin-acme" \
  http://127.0.0.1:8000/admin/telegram/api/config

curl --fail --silent -X POST -H "X-Local-Principal: tenant-admin-acme" \
  http://127.0.0.1:8000/admin/telegram/api/webhook/validate
```

## Browser Checks

- `/admin/telegram` renders inside the admin shell.
- Provider readiness shows reference labels only.
- Tenant form updates preserve tenant scope.
- Stale revision submissions show conflict and do not overwrite current values.
- Link token issue shows the raw token once; token lists show only fingerprint.
- Linked identities show masked Telegram user/chat identifiers.
- Diagnostics contain categories, status, trace id, and safe summaries only.

## Quality Gates

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```
