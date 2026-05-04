# QA023 UI: User Briefing Preferences And Context

## Goal

Guide a browser reviewer through the Daily Intelligence Briefing preference UI,
safe admin summaries, and redaction checks for `/admin/briefing-preferences`.

## Environment Setup

Copy the environment:

```bash
cp specs/023-user-briefing-preferences-and-context/.env.qa023 .env
```

Prepare the database:

```bash
uv sync
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa023 && createdb -U postgres multi_agent_platform_qa023'
uv run alembic upgrade head
```

Seed tenants:

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa023 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING;"
```

Start the API:

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

## Browser Walkthrough

### 1. Open Local Login

URL:
`http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/briefing-preferences`

Expected: the page title or visible content includes `Local Login`.

Evidence: save `01-local-login.png`.

### 2. Sign In As Platform Admin

Action: select `platform-admin`.

Expected: `/admin/briefing-preferences` opens and shows `Briefing Preferences`.

Expected: if no tenant is selected, the page shows safe empty-state copy and no
raw credentials.

Evidence: save `02-user-briefing-preferences-and-context-target.png`.

### 3. Switch To Acme Tenant Scope

Action: choose the Acme tenant scope if available, or open:

```text
http://127.0.0.1:8000/admin/briefing-preferences?tenant_id=11111111-1111-1111-1111-111111111111
```

Expected: page remains under the admin shell and shows `Safe Admin Summaries`.

Evidence: save `03-user-briefing-preferences-and-context-direct-target.png`.

### 4. Save A User Profile

Sign in as `tenant-admin-acme` and open:

```text
http://127.0.0.1:8000/admin/briefing-preferences?tenant_id=11111111-1111-1111-1111-111111111111
```

Use these values:

- Location: `Providence, RI`
- Timezone: `America/New_York`
- News topics: `AI, markets, product launches`
- VIP senders: `sarah@example.com, legal@example.com`
- Workday start: `09:00`
- Workday end: `17:30`
- Commute mode: `driving`
- Calendar ref: `delegated:calendar:primary`
- Email ref: `delegated:gmail:primary`
- Style: `standard`
- Scheduled: checked
- Scheduled time: `08:00`

Expected: save redirects back to the page and the form restores the values.

### 5. Inspect Safe Admin Summary

Sign in as `platform-admin` and open the Acme tenant scoped page again.

Expected:

- `sarah@example.com` is not visible.
- `s***@example.com` is visible as masked evidence.
- `delegated:calendar:primary` is not visible.
- `delegated:***` is visible.
- Revision id and content digest evidence are visible through API summary.

### 6. Tenant Isolation

Sign in as `tenant-admin-globex` and try:

```text
http://127.0.0.1:8000/admin/briefing-preferences?tenant_id=11111111-1111-1111-1111-111111111111
```

Expected: access is denied or redirected through a safe error state.

## Playwright Evidence

The configured validation file captures:

- `01-local-login.png`
- `02-user-briefing-preferences-and-context-target.png`
- `03-user-briefing-preferences-and-context-direct-target.png`
