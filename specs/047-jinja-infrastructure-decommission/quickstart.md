# Quickstart: Jinja Infrastructure Decommission

## Scope

Spec 047 removes the final server-side template runtime and leaves the browser UI React-only. Vite static output under `src/multi_agent_platform/web_admin/static/react` remains active.

## Setup

```bash
uv sync
uv run alembic upgrade head
```

## Focused Checks

```bash
uv run pytest --no-cov \
  tests/unit/admin/test_jinja_infrastructure_decommission.py \
  tests/unit/bootstrap/test_container.py \
  tests/unit/config/test_settings.py \
  tests/unit/api/test_dependency_helpers.py \
  tests/unit/admin/test_migration_hardening_service.py \
  tests/integration/api/test_auth_routes.py \
  tests/integration/api/test_local_browser_login.py \
  tests/integration/api/test_web_run_ui.py \
  tests/integration/test_admin_react_routes.py -q
```

## Frontend Checks

```bash
cd frontend/admin
npm test -- --run src/components/migrationHardening src/App.test.tsx
npm run typecheck
npm run build
```

## Full Validation

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/047-jinja-infrastructure-decommission
uv run python scripts/frontend/generate_admin_react_types.py --check
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui2-roadmap/047-jinja-infrastructure-decommission/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui2-roadmap/047-jinja-infrastructure-decommission/validation.yml --start-processes
```

## Manual Evidence

- Open `/admin/app/migration` as `platform-admin` and confirm the page states the browser UI is React-only.
- Open `/auth/local-login?redirect_to=/admin/app/migration` and confirm the login page renders without a stylesheet dependency on deleted legacy static assets.
- Open `/runs` as `tenant-admin-acme` and confirm it redirects to `/admin/app/channels/runs`.
- Search runtime source for `jinja2`, `Jinja2Templates`, `TemplateResponse`, and `workflow_ui_templates`; only tests/spec artifacts may mention removed symbols as historical evidence.
