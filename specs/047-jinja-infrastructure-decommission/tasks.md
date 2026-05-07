# Tasks: Jinja Infrastructure Decommission

**Input**: Design documents from `specs/047-jinja-infrastructure-decommission/`

## Phase 1: Setup And Final Inventory

- [x] T001 Confirm Specs 038 through 046 are completed in specs/_autopilot/react-ui2-roadmap/queue.json
- [x] T002 [P] Inventory remaining template provider references in src/multi_agent_platform/bootstrap/container.py
- [x] T003 [P] Inventory remaining server template files under src/multi_agent_platform/web_admin/templates
- [x] T004 [P] Inventory legacy static files under src/multi_agent_platform/web_admin/static outside static/react
- [x] T005 [P] Inventory jinja2 dependency entries in pyproject.toml and uv.lock

## Phase 2: Tests First

- [x] T006 [P] Add runtime import, file, dependency, and route scanner coverage in tests/unit/admin/test_jinja_infrastructure_decommission.py
- [x] T007 [P] Update tests/unit/bootstrap/test_container.py to assert the container has no template renderer
- [x] T008 [P] Update tests/unit/api/test_dependency_helpers.py to remove workflow_ui_templates expectations
- [x] T009 [P] Update tests/unit/config/test_settings.py to remove web_admin_templates_dir expectations
- [x] T010 [P] Replace Jinja inventory scanner tests with final decommission inventory/service tests
- [x] T011 [P] Update integration route tests for React-only migration evidence and non-Jinja compatibility handlers
- [x] T012 [P] Update frontend migration hardening tests for React-only decommission language

## Phase 3: Backend Infrastructure Removal

- [x] T013 Remove Starlette templating imports, build_template_renderer, and workflow_ui_templates from src/multi_agent_platform/bootstrap/container.py
- [x] T014 Remove web_admin_templates_dir setting from src/multi_agent_platform/config/settings.py
- [x] T015 Remove obsolete Jinja inventory scanner service from src/multi_agent_platform/admin/migration_hardening
- [x] T016 Update migration hardening service to return final React-only decommission evidence
- [x] T017 Update src/multi_agent_platform/api/routers/admin_react.py migration inventory endpoint to expose final decommission inventory
- [x] T018 Update local login HTML in src/multi_agent_platform/api/routers/auth.py to avoid deleted legacy CSS
- [x] T019 Delete src/multi_agent_platform/web_admin/templates
- [x] T020 Delete legacy static JS/CSS outside src/multi_agent_platform/web_admin/static/react
- [x] T021 Remove jinja2 from pyproject.toml and refresh uv.lock

## Phase 4: Frontend React-Only Evidence

- [x] T022 Update generated/admin React contracts for final decommission inventory shape if schema names change
- [x] T023 Update frontend/admin/src/api/client.ts migration inventory helper naming/copy
- [x] T024 Update migration hardening components to show React-only decommission summary and no retained fallback copy
- [x] T025 Update frontend migration test data and App tests for final state
- [x] T026 Run generated TypeScript contract check

## Phase 5: Docs And Evidence

- [x] T027 Update AGENTS.md current technology/project structure notes to React-only browser UI
- [x] T028 Update README.md and docs/quickstart.md to remove Jinja fallback claims
- [x] T029 Update architecture/admin docs to remove current template/static references or mark them retired
- [x] T030 Update specs/038-jinja-surface-inventory-and-deletion-plan/pr_notes.md with final decommission evidence
- [x] T031 Create `.env.qa047`
- [x] T032 Create `qa047.md`
- [x] T033 Create `qa047_ui.md`
- [x] T034 Create `qa047_user_guide.md`
- [x] T035 Create `pr_notes.md`
- [x] T036 Patch validation.yml to use local-principal login and React-only migration/run journeys

## Phase 6: Validation

- [x] T037 Run focused backend tests from quickstart
- [x] T038 Run frontend migration tests and App tests
- [x] T039 Run frontend typecheck and build
- [x] T040 Run QA document validation
- [x] T041 Run generated contract check
- [x] T042 Run `uv run ruff check .`
- [x] T043 Run `uv run ruff format --check .`
- [x] T044 Run `uv run mypy src`
- [x] T045 Run full pytest coverage gate
- [x] T046 Run `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui2-roadmap/047-jinja-infrastructure-decommission/validation.yml`
- [x] T047 Run `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui2-roadmap/047-jinja-infrastructure-decommission/validation.yml --start-processes`
- [x] T048 Inspect Playwright screenshot under output/playwright/qa047_ui

## Dependencies

- Tests T006-T012 before implementation changes.
- Backend cleanup T013-T021 before scanners are expected to pass.
- Frontend updates T022-T026 after backend schema/contract changes.
- Docs and QA artifacts T027-T036 before validation.
- Validation T037-T048 last.
