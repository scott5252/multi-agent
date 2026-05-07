# Tasks: No-Jinja React Host, Auth, Shell Utilities, And Local Login

**Input**: Design artifacts from `specs/039-no-jinja-react-host-auth-shell-utilities-and-local-login/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`

## Phase 1: Setup

- [x] T001 Verify `.specify/feature.json` points to `specs/039-no-jinja-react-host-auth-shell-utilities-and-local-login`
- [x] T002 [P] Review Spec 038 shell/auth inventory group in `specs/038-jinja-surface-inventory-and-deletion-plan/jinja_inventory.json`
- [x] T003 [P] Confirm current shell/auth TemplateResponse references in `src/multi_agent_platform/api/routers/admin_react.py`, `src/multi_agent_platform/api/routers/admin_console.py`, and `src/multi_agent_platform/api/routers/auth.py`

## Phase 2: Tests First

- [x] T004 [P] [US1] Add contract tests for non-Jinja React host metadata and safe HTML in `tests/contract/test_admin_react_no_jinja_host_contract.py`
- [x] T005 [P] [US1] Add integration tests proving `/admin`, `/admin/app`, `/admin/app/migration`, `/admin/app/{path}`, and old shell utility URLs do not render TemplateResponse in `tests/integration/api/test_admin_react_no_jinja_host_routes.py`
- [x] T006 [P] [US2] Add integration tests for local-principal login envelope, submit, logout, disabled mode, unsafe redirect rejection, and Auth0-shaped no-bypass behavior in `tests/integration/api/test_auth_local_login_react.py`
- [x] T007 [P] [US3] Add integration tests for saved-filter React envelope/mutations, denied states, tenant scope, and old `/admin/filters/{admin_area}` redirect behavior in `tests/integration/api/test_admin_shell_saved_filters_react.py`
- [x] T008 [P] [US1] Add unit tests for React host HTML rendering, asset manifest fallback, CSP/cache hints, and redaction in `tests/unit/api/test_admin_react_host_renderer.py`
- [x] T009 [P] [US2] Add schema tests for local-login contracts and safe problem responses in `tests/unit/api/test_auth_react_schema.py`
- [x] T010 [P] [US3] Add frontend tests for React local-login, saved-filter management, denied/unavailable states, and shell redirects in `frontend/admin/src/App.test.tsx` and new component tests under `frontend/admin/src/components/auth/` and `frontend/admin/src/components/savedFilters/`

## Phase 3: User Story 1 - Non-Jinja React Host (Priority: P1)

**Goal**: Admin entry and React deep-link routes serve a non-Jinja React host or safe non-Jinja responses.

**Independent Test**: Run T004, T005, T008, `npm run build`, and browser smoke against `/admin/app`.

- [x] T011 [US1] Add non-Jinja React host renderer helpers in `src/multi_agent_platform/api/routers/admin_react.py`
- [x] T012 [US1] Replace `TemplateResponse("admin_react/app.html")` calls for `/admin/app`, `/admin/app/migration`, `/admin/app/channels`, and React SPA fallback routes in `src/multi_agent_platform/api/routers/admin_react.py`
- [x] T013 [US1] Add safe asset manifest and unavailable HTML behavior for missing Vite assets in `src/multi_agent_platform/api/routers/admin_react.py`
- [x] T014 [US1] Convert `/admin` landing and shell error rendering to redirect or non-Jinja safe responses in `src/multi_agent_platform/api/routers/admin_console.py`
- [x] T015 [US1] Preserve tenant/query/saved-filter intent for `/admin`, `/admin/scope`, and React host redirects using existing safe redirect helpers in `src/multi_agent_platform/api/ui/admin_console.py` and `src/multi_agent_platform/api/routers/admin_console.py`
- [x] T016 [US1] Update React fallback unavailable copy so the action targets React recovery paths in `frontend/admin/src/App.tsx` and `frontend/admin/src/components/StatePanel.tsx`

## Phase 4: User Story 2 - React Local Login (Priority: P2)

**Goal**: Local-principal login no longer depends on `auth/local_login.html` and keeps auth decisions server-owned.

**Independent Test**: Run T006, T009, and Playwright login flows for platform-admin, tenant-admin-acme, and user.

- [x] T017 [US2] Add local-login Pydantic contracts to `src/multi_agent_platform/api/schemas/auth.py`
- [x] T018 [US2] Add local-login JSON envelope, JSON submit, logout redirect sanitization, and non-Jinja disabled/problem responses in `src/multi_agent_platform/api/routers/auth.py`
- [x] T019 [US2] Add action-token or CSRF-equivalent validation for local-login submit in `src/multi_agent_platform/api/routers/auth.py`
- [x] T020 [US2] Add generated local-login TypeScript contracts and client helper in `frontend/admin/src/api/client.ts`
- [x] T021 [US2] Implement non-Jinja local-login HTML backed by server-owned JSON in `src/multi_agent_platform/api/routers/auth.py`
- [x] T022 [US2] Add client helpers for local-login envelope and submit in `frontend/admin/src/api/client.ts`
- [x] T023 [US2] Extend generated TypeScript contracts with local-login schemas via `scripts/frontend/generate_admin_react_types.py` and `frontend/admin/src/api/generated/reactAdminApi.ts`

## Phase 5: User Story 3 - Shell Utilities And Saved Filters (Priority: P3)

**Goal**: Shared shell utilities, saved-filter management, denied states, and unavailable states work through React or non-Jinja compatibility responses.

**Independent Test**: Run T007, T010, saved-filter browser checks, and denied/unavailable route checks.

- [x] T024 [US3] Add saved-filter React envelope schemas to `src/multi_agent_platform/api/schemas/admin_react.py`
- [x] T025 [US3] Convert saved-filter list/create/delete browser routes to JSON/redirect handlers in `src/multi_agent_platform/api/routers/admin_console.py`
- [x] T026 [US3] Implement React saved-filter management components in `frontend/admin/src/components/savedFilters/SavedFilterManagementPage.tsx`
- [x] T027 [US3] Wire saved-filter management route in `frontend/admin/src/App.tsx` and `frontend/admin/src/routes.tsx`
- [x] T028 [US3] Add client helpers for saved-filter mutations in `frontend/admin/src/api/client.ts`
- [x] T029 [US3] Update shell navigation/search destinations for React shell utility routes in `src/multi_agent_platform/api/routers/admin_react.py`
- [x] T030 [US3] Add retirement evidence for Spec 039 shell/auth inventory decisions to `specs/039-no-jinja-react-host-auth-shell-utilities-and-local-login/pr_notes.md`

## Phase 6: Deletion And Evidence

- [x] T031 Delete `src/multi_agent_platform/web_admin/templates/admin_react/app.html` after T004/T005/T008 pass
- [x] T032 Delete `src/multi_agent_platform/web_admin/templates/auth/local_login.html` after T006/T009/T010 pass
- [x] T033 Retain with blocker evidence `src/multi_agent_platform/web_admin/templates/admin_shell/base.html`, `breadcrumbs.html`, `flash_messages.html`, `index.html`, `navigation.html`, `saved_filters.html`, `saved_filters_page.html`, `scope_selector.html`, `state.html`, and `unavailable.html` because later domain Jinja routes still extend the shared shell
- [x] T034 Retain with blocker evidence `src/multi_agent_platform/web_admin/static/admin_shell.js` because shared shell templates remain until later domain routes are converted
- [x] T035 Update scanner expectations and Spec 039 evidence in `specs/039-no-jinja-react-host-auth-shell-utilities-and-local-login/pr_notes.md`

## Phase 7: Polish And Validation

- [x] T036 [P] Create QA guide in `specs/039-no-jinja-react-host-auth-shell-utilities-and-local-login/qa039.md`
- [x] T037 [P] Create UI walkthrough in `specs/039-no-jinja-react-host-auth-shell-utilities-and-local-login/qa039_ui.md`
- [x] T038 [P] Create QA environment file in `specs/039-no-jinja-react-host-auth-shell-utilities-and-local-login/.env.qa039`
- [x] T039 [P] Create user guide in `specs/039-no-jinja-react-host-auth-shell-utilities-and-local-login/qa039_user_guide.md`
- [x] T040 Run `bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/039-no-jinja-react-host-auth-shell-utilities-and-local-login`
- [x] T041 Run targeted backend tests for Spec 039 route/schema/contract coverage
- [x] T042 Run `cd frontend/admin && npm test -- --run` for changed React components
- [x] T043 Run `cd frontend/admin && npm run build`
- [x] T044 Run `uv run ruff check .`, `uv run ruff format --check .`, and `uv run mypy src`
- [x] T045 Run Spec 039 validation and Playwright through `scripts/qa/run_spec_qa.py` and `scripts/qa/run_playwright_ui.py`

## Dependencies

- Setup tasks T001-T003 must complete before tests and implementation.
- Tests T004-T010 should be created before corresponding implementation tasks.
- US1 (T011-T016) blocks template deletion of `admin_react/app.html` and shell redirects.
- US2 (T017-T023) blocks deletion of `auth/local_login.html`.
- US3 (T024-T030) blocks deletion of `admin_shell/*.html` and `admin_shell.js`.
- Deletion tasks T031-T034 must not run until their corresponding route/import tests pass.
- Validation tasks T040-T045 require QA docs T036-T039 and PR notes T035.

## Parallel Execution Examples

- T004, T005, T006, T007, T008, T009, and T010 can be prepared in parallel because they target distinct test files.
- T020/T021 can proceed after T017/T018 contract shape is known, while T024/T025 saved-filter backend work proceeds separately.
- T036, T037, T038, and T039 can be drafted in parallel once implementation behavior is stable.

## Implementation Strategy

1. Land host/auth/shell tests first and watch them fail on current Jinja behavior.
2. Implement the non-Jinja host and redirect path as the MVP.
3. Port local-login and saved-filter management through backend-owned contracts.
4. Delete only shell/auth templates and assets proven obsolete by tests and scanner evidence.
5. Finish QA docs, validation, and Playwright before advancing to Spec 040.
