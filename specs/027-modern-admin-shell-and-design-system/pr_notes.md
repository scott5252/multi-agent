# Spec 027 Reviewer Notes: Modern Admin Shell And Design System

## Summary

Spec 027 builds on the React admin foundation by replacing the minimal shell
with a modern shared admin shell and local design system.

The implementation keeps existing Jinja admin pages active while `/admin/app`
renders backend-authorized shell metadata, active scope, breadcrumbs, page
actions, notifications, common states, saved-filter presentation, and safe
command search.

## Main Files

- `src/multi_agent_platform/api/routers/admin_react.py`
- `src/multi_agent_platform/api/schemas/admin_react.py`
- `scripts/frontend/generate_admin_react_types.py`
- `frontend/admin/src/App.tsx`
- `frontend/admin/src/components/shell/AdminShell.tsx`
- `frontend/admin/src/components/shell/CommandMenu.tsx`
- `frontend/admin/src/components/primitives/index.tsx`
- `frontend/admin/src/components/states/CommonState.tsx`
- `frontend/admin/src/components/savedFilters/SavedFilterChips.tsx`
- `frontend/admin/src/styles/tokens.css`
- `frontend/admin/src/styles/admin.css`

## Security And Isolation Notes

- The existing backend admin navigation registry remains authoritative.
- React renders only shell, navigation, scope, and command records returned by
  protected backend routes.
- `/admin/app/search.json` uses the same tenant scope checks as bootstrap.
- Cross-tenant bootstrap and search requests fail closed without leaking tenant
  labels.
- Shell notifications and state summaries are safe summaries, not raw payloads.
- Existing Jinja routes remain available as fallbacks until later migration
  specs explicitly enable React domain routes.

## Validation Log

- `uv run pytest tests/unit/api/test_admin_react_schema.py tests/contract/test_admin_react_contract.py tests/integration/test_admin_react_routes.py --no-cov`: passed.
- `cd frontend/admin && npm run typecheck`: passed.
- `cd frontend/admin && npm run test -- --run`: passed.
- `cd frontend/admin && npm run build`: passed and produced FastAPI static React assets.
- `uv run python scripts/frontend/generate_admin_react_types.py --check`: passed.
- `uv run ruff check .`: passed.
- `uv run ruff format --check .`: passed.
- `bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/027-modern-admin-shell-and-design-system`: passed.
- `uv run mypy src`: passed inside Spec QA.
- `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90`: passed inside Spec QA.
- `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui-roadmap/027-modern-admin-shell-and-design-system/validation.yml`: passed after final frontend placeholder polish.
- `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/027-modern-admin-shell-and-design-system/validation.yml --start-processes`: passed after final frontend placeholder polish.

## Full Gate Evidence

- QA document validator passed for `qa027.md`, `qa027_ui.md`, and `.env.qa027`.
- Spec QA reset `multi_agent_platform_qa027`, seeded Acme and Globex, started API and worker processes, exercised React shell API and command-search routes, and ran backend/frontend quality commands.
- Playwright captured denied, authenticated, and command-search browser flows.
- Screenshots were visually reviewed after refreshing the final React bundle.

## Evidence Paths

- Manual API evidence: `/tmp/qa027-*`
- Playwright screenshots: `output/playwright/qa027_ui`
- Denied screenshot: `output/playwright/qa027_ui/qa027-react-shell-denied.png`
- Authenticated screenshot: `output/playwright/qa027_ui/qa027-react-shell-authenticated.png`
- Command search screenshot: `output/playwright/qa027_ui/qa027-react-shell-search.png`
- QA guide: `specs/027-modern-admin-shell-and-design-system/qa027.md`
- UI walkthrough: `specs/027-modern-admin-shell-and-design-system/qa027_ui.md`
- Manual user guide: `specs/027-modern-admin-shell-and-design-system/qa027_user_guide.md`
- QA environment: `specs/027-modern-admin-shell-and-design-system/.env.qa027`
