# Quickstart: Admin Console Shell

**Feature**: Admin Console Shell
**Date**: 2026-04-27

## Prerequisites

```bash
uv sync
uv run alembic upgrade head
```

For local-principal testing, configure deterministic principals with platform
admin, tenant admin, multi-tenant admin, and unauthorized roles. Auth0 mode must
use the same route/scope behavior through JWT-backed principals and role
grants.

## Run The App

```bash
uv run uvicorn multi_agent_platform.api.main:app --reload
```

Open:

- `http://127.0.0.1:8000/admin`
- `http://127.0.0.1:8000/admin/workflows/ui`
- `http://127.0.0.1:8000/admin/config/ui`
- `http://127.0.0.1:8000/admin/runs`
- `http://127.0.0.1:8000/admin/reliability/ui/`

Tenant scope links include `?tenant_id=<tenant-uuid>`. Platform scope links
omit `tenant_id`.

## Validation Workflow

1. Sign in or send local-principal headers as a platform admin.
2. Confirm `/admin` shows platform scope, platform-allowed navigation, and
   tenant-entry options only when authorized.
3. Switch to a tenant scope through `/admin/scope?tenant_id=<tenant>&next=/admin`.
4. Confirm navigation, breadcrumbs, page links, saved filters, and forms include
   the selected `tenant_id`.
5. Visit each wrapped page directly and through shell navigation:
   workflows, model-skill config/history/provenance, run inspection/replay, and
   reliability dashboard/breakers/dead letters.
6. Repeat as a single-tenant admin, multi-tenant admin, and unauthorized user.
7. Try a forged `tenant_id` and confirm fail-closed behavior without protected
   details.
8. Save and restore filters on filterable pages, then switch scope and confirm
   filters from another scope are not applied.
9. Trigger empty, filtered-empty, denied, unavailable, and validation states and
   verify safe wording.
10. Simulate audit persistence failure and confirm protected rendering/actions
    are blocked with safe unavailable state plus log/metric evidence.
11. Verify optional enhancement/no-JS fallback by disabling JavaScript and
    confirming `/admin`, direct shell-wrapped pages, scope links, breadcrumbs,
    common states, and saved-filter forms remain usable.
12. Confirm an authorized reviewer can reach workflow, model-skill,
    run-inspection, and reliability destinations in three navigation actions or
    fewer and can identify active scope within 5 seconds.

## Automated Checks

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest tests/unit/api/test_admin_shell_ui_models.py
uv run pytest tests/unit/api/test_admin_shell_access.py
uv run pytest tests/unit/api/test_admin_shell_filters.py
uv run pytest tests/integration/api/test_admin_console_shell_routes.py
uv run pytest tests/integration/api/test_admin_console_shell_authorization.py
uv run pytest tests/integration/api/test_admin_console_shell_saved_filters.py
uv run pytest tests/docs/test_admin_console_shell_docs.py
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Final focused admin shell check:

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

## Review Evidence

Delivery must include:

- `docs/admin-console-shell.md`
- `specs/010-admin-console-shell/testing-instructions.md`
- `specs/010-admin-console-shell/pr-review-notes.md`
- README update covering active scope, navigation groups, common states, safe
  messages, saved filters, and existing page locations
- Coverage output showing at least 90 percent coverage for submitted shell code
