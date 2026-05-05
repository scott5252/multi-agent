# Spec 026 Reviewer Notes: React Admin UI Foundation

## Summary

Spec 026 adds a React admin shell at `/admin/app` while preserving the existing
server-rendered admin console and domain pages.

The backend owns the browser bootstrap contract through FastAPI routes for the
HTML shell, bootstrap JSON, config JSON, and manifest JSON.

The frontend is a Vite, React, and TypeScript workspace under `frontend/admin`.

## Main Files

- `src/multi_agent_platform/api/routers/admin_react.py`
- `src/multi_agent_platform/api/schemas/admin_react.py`
- `src/multi_agent_platform/web_admin/templates/admin_react/app.html`
- `frontend/admin/src/App.tsx`
- `frontend/admin/src/components/AdminShell.tsx`
- `frontend/admin/src/api/generated/reactAdminApi.ts`
- `scripts/frontend/generate_admin_react_types.py`

## Security And Isolation Notes

- `/admin/app` uses the existing authorized-principal dependency.
- Bootstrap data is built from backend admin shell scope and navigation helpers.
- Cross-tenant bootstrap requests fail closed.
- Manifest summaries expose public asset URLs only, not local filesystem paths.
- Future React domain routes stay disabled and point to existing Jinja routes.

## Validation Log

- `uv run pytest tests/unit/api/test_admin_react_schema.py tests/contract/test_admin_react_contract.py tests/integration/test_admin_react_routes.py --no-cov`: passed.
- `cd frontend/admin && npm run test`: passed.
- `cd frontend/admin && npm run typecheck`: passed after installing Node dependencies.
- `cd frontend/admin && npm run build`: passed and produced FastAPI static React assets.
- `uv run python scripts/frontend/generate_admin_react_types.py --check`: passed.
- `uv run ruff check src/multi_agent_platform/api/routers/admin_react.py src/multi_agent_platform/api/schemas/admin_react.py tests/unit/api/test_admin_react_schema.py tests/contract/test_admin_react_contract.py tests/integration/test_admin_react_routes.py scripts/frontend/generate_admin_react_types.py`: passed.
- `uv run mypy src/multi_agent_platform/api/routers/admin_react.py src/multi_agent_platform/api/schemas/admin_react.py`: passed.
- `uv run ruff check .`: passed.
- `uv run ruff format --check .`: passed.
- `uv run mypy src`: passed.
- `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90`: passed inside Spec QA with 988 passing tests and coverage above 90 percent after the manifest test was made deterministic.
- `bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/026-react-admin-ui-foundation`: passed.
- `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui-roadmap/026-react-admin-ui-foundation/validation.yml`: passed.
- `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/026-react-admin-ui-foundation/validation.yml --start-processes`: passed.

## Full Gate Evidence

- QA document validator passed for `qa026.md`, `qa026_ui.md`, and `.env.qa026`.
- Spec QA reset `multi_agent_platform_qa026`, seeded Acme and Globex, started API and worker processes, exercised React admin API routes, and ran backend/frontend quality commands.
- Playwright captured the denied, authenticated, and disabled-route browser flows.

## Evidence Paths

- Manual API evidence: `/tmp/qa026-*`
- Playwright screenshots: `output/playwright/qa026_ui`
- Denied screenshot: `output/playwright/qa026_ui/qa026-react-ui-denied.png`
- Authenticated screenshot: `output/playwright/qa026_ui/qa026-react-ui-authenticated.png`
- Disabled-route screenshot: `output/playwright/qa026_ui/qa026-react-ui-disabled-route.png`
- QA guide: `specs/026-react-admin-ui-foundation/qa026.md`
- UI walkthrough: `specs/026-react-admin-ui-foundation/qa026_ui.md`
- Manual user guide: `specs/026-react-admin-ui-foundation/qa026_user_guide.md`
- QA environment: `specs/026-react-admin-ui-foundation/.env.qa026`
