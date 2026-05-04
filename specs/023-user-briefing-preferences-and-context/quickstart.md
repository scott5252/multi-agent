# Quickstart: User Briefing Preferences And Context

## Local QA Setup

```bash
uv sync
cp specs/023-user-briefing-preferences-and-context/.env.qa023 .env
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa023 && createdb -U postgres multi_agent_platform_qa023'
uv run alembic upgrade head
```

Seed QA tenants if needed:

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa023 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
```

Start services:

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
uv run python -m multi_agent_platform.workers.main
```

## Browser Flow

1. Open `/auth/local-login?redirect_to=/admin/briefing-preferences`.
2. Select `platform-admin` or `tenant-admin-acme`.
3. Save a profile with:
   - Location: `Providence, RI`
   - Timezone: `America/New_York`
   - Topics: `AI, markets, product launches`
   - VIP senders: `sarah@example.com, legal@example.com`
   - Workday: `09:00` to `17:30`
   - Commute mode: `driving`
   - Calendar ref: `delegated:calendar:primary`
   - Email ref: `delegated:gmail:primary`
   - Style: `standard`
   - Scheduled time: `08:00`
4. Reload the page and verify the editable form restores values.
5. Confirm the admin summary shows counts and safe labels, not raw VIP senders or raw account references.

## API Checks

```bash
curl --fail --silent -H 'X-Local-Principal: tenant-admin-acme' \
  'http://127.0.0.1:8000/admin/briefing-preferences/api/profile?tenant_id=11111111-1111-1111-1111-111111111111'
```

```bash
curl --fail --silent -H 'X-Local-Principal: tenant-admin-acme' \
  -H 'Content-Type: application/json' \
  -X POST 'http://127.0.0.1:8000/admin/briefing-preferences/api/resolve' \
  --data '{"tenant_id":"11111111-1111-1111-1111-111111111111","principal_id":"tenant-admin-acme","source_channel":"telegram","trace_id":"trace-qa023"}'
```

## Telegram Alias Context Check

After creating the Telegram `Morning briefing` alias, send the webhook update
for a linked Acme user. The accepted run input must include
`briefing_preferences.revision_id`, `briefing_preferences.preferences`, and
`briefing_preferences.safe_summary` when a profile exists.

## Validation

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/023-user-briefing-preferences-and-context/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/023-user-briefing-preferences-and-context/validation.yml --start-processes
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```
