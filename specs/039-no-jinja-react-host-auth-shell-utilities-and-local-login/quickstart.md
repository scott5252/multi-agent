# Quickstart: No-Jinja React Host, Auth, Shell Utilities, And Local Login

## Local Setup

1. Install dependencies:

   ```bash
   uv sync
   cd frontend/admin && npm install
   ```

2. Build the React admin assets:

   ```bash
   cd frontend/admin && npm run build
   ```

3. Start the API in local-principal mode using the Spec 039 QA environment:

   ```bash
   cp specs/039-no-jinja-react-host-auth-shell-utilities-and-local-login/.env.qa039 .env
   uv run alembic upgrade head
   uv run uvicorn multi_agent_platform.api.main:app --reload
   ```

## Manual Smoke

1. Open `/auth/local-login?redirect_to=/admin/app`.
2. Select `platform-admin` and submit.
3. Confirm `/admin/app` loads the React shell and not a Jinja-rendered page.
4. Open `/admin`, `/admin/scope?next=/admin/app/migration`, and `/admin/filters/workflows`.
5. Confirm each old route redirects or returns a non-Jinja safe response.
6. Open saved-filter management in React and exercise list/create/update/delete paths.
7. Open a denied tenant/platform route as a lower-privilege local principal and confirm the response is redaction-safe.

## Automated Validation

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/039-no-jinja-react-host-auth-shell-utilities-and-local-login
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui2-roadmap/039-no-jinja-react-host-auth-shell-utilities-and-local-login/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui2-roadmap/039-no-jinja-react-host-auth-shell-utilities-and-local-login/validation.yml --start-processes
```

## Evidence Expectations

- Backend route tests prove Auth0-shaped allowed, unauthenticated, unauthorized, cross-tenant, redirect, logout, saved-filter, and non-Jinja response cases.
- Frontend tests prove the local-login, saved-filter, shell state, command/search, and unavailable/denied components render safe states.
- Route/import scanners prove Spec 039 admin/auth entry routes do not call `TemplateResponse` and deleted shell/auth templates are no longer referenced.
- Playwright captures `output/playwright/qa039_ui/qa039-react-ui2-smoke.png`.
