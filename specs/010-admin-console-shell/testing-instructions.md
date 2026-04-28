# Testing Instructions: Admin Console Shell

## Purpose

Use this checklist to verify Spec `010` without relying on verbal context.
It covers platform scope, tenant scope, navigation groups, route preservation,
authorization-aware menus, direct denial, audits, common states, safe messages,
saved filters, existing page links, optional enhancement/no-JS fallback
behavior, three-action navigation reachability, and active-scope
identification within 5 seconds.

## Local Setup

```bash
cp specs/010-admin-console-shell/.env.qa010 .env
uv sync
docker compose up -d postgres
docker compose exec -T postgres sh -c \
  'psql -U postgres -d postgres -tc "SELECT 1 FROM pg_database WHERE datname = '\''multi_agent_platform_qa010'\''" | grep -q 1 || createdb -U postgres multi_agent_platform_qa010'
uv run alembic upgrade head
```

Expected: the app uses local-principal auth, PostgreSQL database
`multi_agent_platform_qa010`, and `.data/qa010-artifacts`.

## Principals

- `platform-admin`: platform scope, platform navigation, tenant entry when
  authorized.
- `tenant-admin-acme`: tenant scope for Acme.
- `tenant-admin-globex`: cross-tenant negative-path checks.
- `operator-acme`: same-tenant non-admin denial.

## Manual Route Checks

Start the API:

```bash
uv run uvicorn multi_agent_platform.api.main:app --reload
```

Open or curl:

```bash
curl -sS -H "X-Local-Principal: platform-admin" \
  http://127.0.0.1:8000/admin -o /tmp/qa010-platform.html
curl -sS -H "X-Local-Principal: tenant-admin-acme" \
  "http://127.0.0.1:8000/admin?tenant_id=11111111-1111-1111-1111-111111111111" \
  -o /tmp/qa010-tenant.html
```

Expected: platform output identifies platform scope; tenant output identifies
tenant scope. Both include labeled admin navigation, breadcrumbs, and one main
landmark.

Verify direct pages:

```bash
for path in \
  /admin/workflows/ui \
  /admin/config/ui \
  /admin/config/ui/history \
  /admin/runs \
  /admin/reliability/ui/ \
  /admin/reliability/ui/breakers \
  /admin/reliability/ui/dead-letters
do
  curl -sS -H "X-Local-Principal: tenant-admin-acme" \
    "http://127.0.0.1:8000${path}?tenant_id=11111111-1111-1111-1111-111111111111" \
    -o "/tmp/qa010-${path//\//-}.html"
done
```

Expected: every response renders the shared shell while preserving the route.

## Negative Paths

```bash
curl -sS -w "%{http_code}\n" -o /tmp/qa010-forged.html \
  -H "X-Local-Principal: tenant-admin-acme" \
  "http://127.0.0.1:8000/admin?tenant_id=22222222-2222-2222-2222-222222222222"
```

Expected: `403`, safe wording, no raw tenant labels from the unauthorized
tenant, and no secret/prompt/memory payloads.

```bash
curl -sS -w "%{http_code}\n" -o /tmp/qa010-non-admin.html \
  -H "X-Local-Principal: operator-acme" \
  http://127.0.0.1:8000/admin
```

Expected: the non-admin is denied and protected navigation does not render.

## Saved Filters

```bash
curl -sS -w "%{http_code}\n" -o /tmp/qa010-save-filter.txt \
  -H "X-Local-Principal: tenant-admin-acme" \
  -X POST \
  "http://127.0.0.1:8000/admin/filters/workflows?tenant_id=11111111-1111-1111-1111-111111111111" \
  -d 'filter_key=workflow-list' \
  -d 'display_name=Drafts' \
  -d 'criteria={"status":"draft"}' \
  -d 'return_to=/admin/workflows/ui'
```

Expected: `303` redirect. The filter is stored only for the Acme tenant scope.

```bash
curl -sS -H "X-Local-Principal: tenant-admin-acme" \
  "http://127.0.0.1:8000/admin/filters/workflows?tenant_id=11111111-1111-1111-1111-111111111111" \
  -o /tmp/qa010-filters.html
```

Expected: the `Drafts` filter appears with safe criteria summary and
tenant-scoped restore/delete links.

## Redaction Scan

```bash
if grep -RniE 'password|api[_-]?key|secret-value|traceback|raw prompt|memory payload' /tmp/qa010-*.html /tmp/qa010-*.txt; then
  echo "Unexpected sensitive text found"
  exit 1
else
  echo "Redaction scan passed"
fi
```

Expected: `Redaction scan passed`.

## Focused Automated Evidence

```bash
uv run pytest --no-cov \
  tests/unit/api/test_admin_console_ui_models.py \
  tests/unit/api/test_admin_console_access.py \
  tests/unit/api/test_admin_console_filters.py \
  tests/unit/auth/test_admin_console_policy.py \
  tests/unit/audit/test_admin_console_audit.py \
  tests/unit/db/test_admin_console_models.py \
  tests/unit/db/test_admin_console_repository.py \
  tests/integration/api/test_admin_console_shell_routes.py \
  tests/integration/api/test_admin_console_shell_authorization.py \
  tests/integration/api/test_admin_console_templates.py \
  tests/integration/api/test_admin_console_shell_states.py \
  tests/integration/api/test_admin_console_shell_saved_filters.py \
  tests/integration/db/test_admin_console_migration.py \
  tests/contract/test_admin_console_shell_contract.py \
  tests/docs/test_admin_console_shell_docs.py
```

Expected: all focused admin shell tests pass.

Latest local evidence: `39 passed in 2.34s`.

## Full Quality Gates

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected: all commands pass before review completion.

Latest full coverage evidence: `470 passed, 1 warning in 38.81s` with
`90.04%` total coverage.
