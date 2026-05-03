# Quickstart: User And Tenant Membership Administration

## Local Setup

```bash
uv sync
cp specs/018-user-tenant-membership-administration/.env.qa018 .env
createdb multi_agent_platform_qa018 || true
uv run alembic upgrade head
uv run uvicorn multi_agent_platform.api.main:app --reload
```

Expected: the API starts on `http://127.0.0.1:8000` with
`AUTH_MODE=local_principal`.

## Browser Flow

1. Open `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/memberships`.
2. Select `platform-admin`.
3. Verify the page title is `Membership Administration`.
4. Create an Acme invitation with `reviewer@example.com`.
5. Submit the same invitation again and verify the existing invitation is
   replayed.
6. Switch to `tenant-admin-acme` and verify only Acme memberships are visible.
7. Attempt a platform-role assignment as the tenant admin and verify it fails.

Expected: UI renders masked email text, role summaries, membership status, and
safe access history without passwords or raw secrets.

## API Smoke Flow

```bash
curl -sS -H "X-Local-Principal: platform-admin" \
  http://127.0.0.1:8000/admin/memberships/api/users | jq .

curl -sS -X POST -H "X-Local-Principal: platform-admin" \
  -H "Content-Type: application/json" \
  http://127.0.0.1:8000/admin/memberships/api/invitations \
  -d '{"tenant_id":"11111111-1111-1111-1111-111111111111","email":"Reviewer@Example.com","requested_roles":["tenant_user"],"idempotency_key":"qa018-reviewer"}' | jq .
```

Expected: responses include masked email display and no password fields.

## Quality Gates

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/018-user-tenant-membership-administration/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/018-user-tenant-membership-administration/validation.yml --start-processes
```
