# Tasks: Admin Console Shell

**Input**: Design documents from `/Users/scottcornell/src/my-projects/multi-agent/specs/010-admin-console-shell/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md
**Tests**: TDD is required by the user request. Write the listed tests first and confirm they fail before implementing each story.
**Naming Note**: This task list uses the requested implementation files `src/multi_agent_platform/api/routers/admin_console.py` and `src/multi_agent_platform/api/ui/admin_console.py`; shared Jinja layout templates remain under `src/multi_agent_platform/web_admin/templates/admin_shell/`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Isolated template or docs task only, per user request
- **[Story]**: User story label for story phases only
- Each checklist item names the exact file to create or update

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare fixtures and inventory needed by every TDD phase.

- [ ] T001 Create admin console local-principal and tenant fixture helpers in `tests/fixtures/admin_console.py`
- [ ] T002 Add rendered HTML assertion helpers for shell landmarks, nav items, scope labels, and flash/state regions in `tests/fixtures/admin_console.py`
- [ ] T003 Add admin console route inventory constants for existing workflow, model-skill, run inspection, and reliability UI paths in `tests/fixtures/admin_console.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared shell contracts, route wiring, auth surfaces, and observability hooks that block every story.

**Critical**: No user story work begins until these tasks pass.

- [ ] T004 Write failing unit tests for `AdminScope`, navigation metadata, breadcrumbs, messages, common states, and shell context serialization in `tests/unit/api/test_admin_console_ui_models.py`
- [ ] T005 Write failing unit tests that assert every route listed in the admin shell UI contract has a non-public protected surface policy, including shell, scope, saved-filter, workflow UI, model-skill UI, run inspection UI, and reliability UI routes, in `tests/unit/auth/test_policy.py`
- [ ] T006 Write failing integration test that `create_app()` mounts the admin console router and admin static assets without breaking existing routers in `tests/integration/api/test_admin_console_shell_routes.py`
- [ ] T007 Implement typed view models and the static navigation registry skeleton in `src/multi_agent_platform/api/ui/admin_console.py`
- [ ] T008 Implement the FastAPI router skeleton for `/admin`, `/admin/scope`, and `/admin/filters/{admin_area}` routes in `src/multi_agent_platform/api/routers/admin_console.py`
- [ ] T009 Register `admin_console_router` in `src/multi_agent_platform/api/main.py`
- [ ] T010 Add protected surface policies for `/admin`, `/admin/scope`, saved-filter actions, model-skill UI routes, run inspection UI routes, reliability UI routes, and every shell-wrapped workflow UI route in `src/multi_agent_platform/auth/policy.py`
- [ ] T011 Add admin-shell audit failure and fail-closed counters in `src/multi_agent_platform/observability/metrics.py`
- [ ] T012 Add redacted admin-shell log context helpers in `src/multi_agent_platform/observability/logging.py`
- [ ] T013 [P] Create the base admin shell template with landmarks, content blocks, and progressive enhancement hooks in `src/multi_agent_platform/web_admin/templates/admin_shell/base.html`
- [ ] T014 Create baseline shell CSS selectors, focus states, and responsive layout rules in `src/multi_agent_platform/web_admin/static/workflow_studio.css`
- [ ] T015 Create optional no-build admin shell JavaScript bootstrap with safe no-op behavior in `src/multi_agent_platform/web_admin/static/admin_shell.js`
- [ ] T016 Confirm foundational tests fail before story implementation by recording expected failing test names in `specs/010-admin-console-shell/testing-instructions.md`

**Checkpoint**: Foundation ready. Shared contracts and route surfaces are defined, failing tests document the next implementation work.

---

## Phase 3: User Story 1 - Navigate By Admin Scope (Priority: P1) MVP

**Goal**: Platform admins, tenant admins, multi-tenant admins, and unauthorized users see correct active scope, navigation, route authorization, and fail-closed behavior.

**Independent Test**: Sign in as platform admin, one-tenant admin, multi-tenant admin, and unauthorized user; verify scope display, role-filtered navigation, forged `tenant_id` rejection, direct-route denial, and audit evidence.

### Tests for User Story 1

- [ ] T017 [US1] Write failing navigation filtering tests for platform, tenant, multi-tenant, suspended tenant, forged tenant, and unauthorized principals in `tests/unit/api/test_admin_console_access.py`
- [ ] T018 [US1] Write failing scope resolution tests for platform scope omission and tenant scope `tenant_id` validation in `tests/unit/api/test_admin_console_access.py`
- [ ] T019 [US1] Write failing integration tests for `/admin` scope display, navigation groups, and tenant scope links in `tests/integration/api/test_admin_console_shell_routes.py`
- [ ] T020 [US1] Write failing authorization tests for denied shell access, direct destination denial, indeterminate decisions, and audit-persistence failure in `tests/integration/api/test_admin_console_shell_authorization.py`
- [ ] T021 [US1] Write failing audit tests for one itemized navigation visibility record per request and separate direct destination decisions in `tests/unit/audit/test_admin_console_audit.py`

### Implementation for User Story 1

- [ ] T022 [US1] Implement scope option resolution, active-scope validation, invalid-scope clearing, and safe redirect targets in `src/multi_agent_platform/api/ui/admin_console.py`
- [ ] T023 [US1] Implement authorization-aware navigation filtering by role, active tenant scope, required scope, route surface policy, and active URL matcher in `src/multi_agent_platform/api/ui/admin_console.py`
- [ ] T024 [US1] Implement required navigation, direct destination, scope selection, and audit-failure orchestration helpers in `src/multi_agent_platform/api/ui/admin_console.py`
- [ ] T025 [US1] Implement `/admin` landing and `/admin/scope` redirect handlers with validated `tenant_id` propagation in `src/multi_agent_platform/api/routers/admin_console.py`
- [ ] T026 [US1] Implement fail-closed 403/503 rendering for denied, unavailable, or unaudited admin access decisions in `src/multi_agent_platform/api/routers/admin_console.py`
- [ ] T027 [US1] Add navigation audit event builders and safe payload fields for role context, active scope, item outcomes, reason category, and trace id in `src/multi_agent_platform/audit/service.py`
- [ ] T028 [P] [US1] Create the authorization-filtered primary navigation partial in `src/multi_agent_platform/web_admin/templates/admin_shell/navigation.html`
- [ ] T029 [P] [US1] Create the active scope selector and scope display partial in `src/multi_agent_platform/web_admin/templates/admin_shell/scope_selector.html`
- [ ] T030 [P] [US1] Create the fail-closed unavailable page template in `src/multi_agent_platform/web_admin/templates/admin_shell/unavailable.html`

**Checkpoint**: User Story 1 is independently functional and testable as the MVP.

---

## Phase 4: User Story 2 - Use A Consistent Console Layout (Priority: P2)

**Goal**: Existing workflow, model-skill, run inspection, and reliability UI pages render inside the shared shell while preserving original route identities.

**Independent Test**: Visit every existing server-rendered admin UI route directly and through shell navigation; verify shared layout, route preservation, breadcrumbs, active nav, scope propagation, and links to the existing pages.

### Tests for User Story 2

- [ ] T031 [US2] Write failing contract tests for the shell context contract, OpenAPI routes, and tenant query parameter behavior in `tests/contract/test_admin_console_shell_contract.py`
- [ ] T032 [US2] Write failing integration tests that shell links reach workflow, model-skill, run inspection, and reliability UI routes without replacing their paths in `tests/integration/api/test_admin_console_shell_routes.py`
- [ ] T033 [US2] Write failing template rendering tests for base landmarks, skip link, labeled admin navigation, `aria-current`, breadcrumbs, and content block output in `tests/integration/api/test_admin_console_templates.py`
- [ ] T034 [US2] Write failing route tests that direct bookmarked admin UI pages render with shell context and validated `tenant_id` when authorized in `tests/integration/api/test_admin_console_shell_routes.py`

### Implementation for User Story 2

- [ ] T035 [US2] Update workflow UI route handlers to build shell context while preserving `/admin/workflows/ui`, draft editor, and version detail paths in `src/multi_agent_platform/api/routers/admin_workflow_ui.py`
- [ ] T036 [US2] Add model-skill UI route handlers for `/admin/config/ui`, `/admin/config/ui/history`, and `/admin/config/ui/runs/{workflow_run_id}/provenance` in `src/multi_agent_platform/api/routers/admin_model_skill_config.py`
- [ ] T037 [US2] Update run inspection UI route handlers to build shell context for run search, detail, and replay pages in `src/multi_agent_platform/api/routers/admin_run_inspection.py`
- [ ] T038 [US2] Update reliability UI route handlers to build shell context for dashboard, breakers, and dead letters pages in `src/multi_agent_platform/api/ui/reliability_controls.py`
- [ ] T039 [US2] Add shell context builder entry points for existing workflow page models in `src/multi_agent_platform/api/ui/admin_workflows.py`
- [ ] T040 [US2] Add shell context builder entry points for model-skill config, history, and run provenance page models in `src/multi_agent_platform/api/ui/model_skill_config.py`
- [ ] T041 [US2] Add shell context builder entry points for run inspection, run detail, and replay page models in `src/multi_agent_platform/api/ui/run_details.py`
- [ ] T042 [US2] Add shell context builder entry points for reliability dashboard, breakers, and dead-letter page models in `src/multi_agent_platform/api/ui/reliability_controls.py`
- [ ] T043 [P] [US2] Convert workflow list template to extend the shell base in `src/multi_agent_platform/web_admin/templates/workflows/index.html`
- [ ] T044 [P] [US2] Convert workflow draft editor template to extend the shell base in `src/multi_agent_platform/web_admin/templates/workflows/draft_editor.html`
- [ ] T045 [P] [US2] Convert workflow version detail template to extend the shell base in `src/multi_agent_platform/web_admin/templates/workflows/version_detail.html`
- [ ] T046 [P] [US2] Convert model-skill config template to extend the shell base in `src/multi_agent_platform/web_admin/templates/model_skill_config/index.html`
- [ ] T047 [P] [US2] Convert model-skill history template to extend the shell base in `src/multi_agent_platform/web_admin/templates/model_skill_config/history.html`
- [ ] T048 [P] [US2] Convert model-skill run provenance template to extend the shell base in `src/multi_agent_platform/web_admin/templates/model_skill_config/run_provenance.html`
- [ ] T049 [P] [US2] Convert run inspection list template to extend the shell base in `src/multi_agent_platform/web_admin/templates/runs/index.html`
- [ ] T050 [P] [US2] Convert run detail template to extend the shell base in `src/multi_agent_platform/web_admin/templates/runs/detail.html`
- [ ] T051 [P] [US2] Convert run replay template to extend the shell base in `src/multi_agent_platform/web_admin/templates/runs/replay.html`
- [ ] T052 [P] [US2] Convert reliability dashboard template to extend the shell base in `src/multi_agent_platform/web_admin/templates/reliability/index.html`
- [ ] T053 [P] [US2] Convert reliability breakers template to extend the shell base in `src/multi_agent_platform/web_admin/templates/reliability/breakers.html`
- [ ] T054 [P] [US2] Convert reliability dead letters template to extend the shell base in `src/multi_agent_platform/web_admin/templates/reliability/dead_letters.html`
- [ ] T055 [P] [US2] Create the breadcrumb partial used by every shell-wrapped page in `src/multi_agent_platform/web_admin/templates/admin_shell/breadcrumbs.html`
- [ ] T056 [US2] Add shell layout, navigation, breadcrumb, scope, and page action styling in `src/multi_agent_platform/web_admin/static/workflow_studio.css`
- [ ] T057 [US2] Add optional tenant-scope and menu enhancement behavior that leaves server-rendered navigation functional without JavaScript in `src/multi_agent_platform/web_admin/static/admin_shell.js`

**Checkpoint**: Existing admin pages keep their routes and render through the shared frame.

---

## Phase 5: User Story 3 - Recover From Empty, Error, And Flash States Safely (Priority: P3)

**Goal**: Shared empty, error, denied, partial, unavailable, validation, and flash states are consistent, actionable, and free of protected details.

**Independent Test**: Trigger empty lists, filtered-empty lists, missing resources, denied destinations, validation failures, action success/failure flashes, partial dependencies, and unexpected errors; verify safe wording and correct scope binding.

### Tests for User Story 3

- [ ] T058 [US3] Write failing unit tests for common state factories, safe action filtering, and state type distinctions in `tests/unit/api/test_admin_console_ui_models.py`
- [ ] T059 [US3] Write failing unit tests for breadcrumb and flash sanitization of secrets, prompt text, memory content, run payloads, stack traces, and cross-tenant labels in `tests/unit/api/test_admin_console_ui_models.py`
- [ ] T060 [US3] Write failing integration tests for empty, filtered-empty, denied, unavailable, validation, partial, and unexpected-error state rendering in `tests/integration/api/test_admin_console_shell_states.py`
- [ ] T061 [US3] Write failing integration tests that flash messages remain associated with the correct principal and active scope in `tests/integration/api/test_admin_console_shell_states.py`

### Implementation for User Story 3

- [ ] T062 [US3] Implement common state factories, safe summaries, support trace ids, and allowed next action filtering in `src/multi_agent_platform/api/ui/admin_console.py`
- [ ] T063 [US3] Implement breadcrumb, flash message, validation error, and operational failure sanitizers in `src/multi_agent_platform/api/ui/admin_console.py`
- [ ] T064 [US3] Wire workflow page empty and error conditions into shared common states in `src/multi_agent_platform/api/ui/admin_workflows.py`
- [ ] T065 [US3] Wire model-skill page empty and error conditions into shared common states in `src/multi_agent_platform/api/ui/model_skill_config.py`
- [ ] T066 [US3] Wire run inspection page empty and error conditions into shared common states in `src/multi_agent_platform/api/ui/run_details.py`
- [ ] T067 [US3] Wire reliability page empty and error conditions into shared common states in `src/multi_agent_platform/api/ui/reliability_controls.py`
- [ ] T068 [P] [US3] Create the shared common-state partial in `src/multi_agent_platform/web_admin/templates/admin_shell/state.html`
- [ ] T069 [P] [US3] Create the scope-bound flash message partial in `src/multi_agent_platform/web_admin/templates/admin_shell/flash_messages.html`
- [ ] T070 [US3] Add visual state, alert/status region, and safe message styling in `src/multi_agent_platform/web_admin/static/workflow_studio.css`

**Checkpoint**: Common states and flash messages are safe and consistent across shell-wrapped pages.

---

## Phase 6: User Story 4 - Resume Useful Filtered Views (Priority: P4)

**Goal**: Useful filters are persisted server-side by user, admin area, and platform or tenant scope, then restored only after validation and audit.

**Independent Test**: Save filters on filterable admin pages, restore them in the same scope, switch tenant scope, attempt malformed/unauthorized criteria, and verify criteria are rejected or dropped safely with audit evidence.

### Tests for User Story 4

- [ ] T071 [US4] Write failing SQLAlchemy model tests for admin saved filter fields, scope constraints, safe JSON columns, and uniqueness rules in `tests/unit/db/test_admin_console_models.py`
- [ ] T072 [US4] Write failing migration tests for `admin_saved_filters` columns, foreign keys, indexes, and downgrade behavior in `tests/integration/db/test_admin_console_migration.py`
- [ ] T073 [US4] Write failing repository tests for scoped saved-filter create, update, list, restore timestamp, delete, and not-found behavior in `tests/unit/db/test_admin_console_repository.py`
- [ ] T074 [US4] Write failing validator tests for useful filter profiles, unsupported criteria, malformed criteria, unauthorized criteria, and safe label generation in `tests/unit/api/test_admin_console_filters.py`
- [ ] T075 [US4] Write failing integration tests for saved-filter list, save, restore, delete, tenant switching, scope mismatch, and audit evidence in `tests/integration/api/test_admin_console_shell_saved_filters.py`

### Implementation for User Story 4

- [ ] T076 [US4] Add the `AdminSavedFilter` SQLAlchemy model in `src/multi_agent_platform/db/models/admin_console.py`
- [ ] T077 [US4] Export the admin console model metadata in `src/multi_agent_platform/db/models/__init__.py`
- [ ] T078 [US4] Add Alembic migration for `admin_saved_filters` with scope constraints and scoped indexes in `alembic/versions/0010_admin_console_shell.py`
- [ ] T079 [US4] Implement scoped saved-filter repository methods in `src/multi_agent_platform/db/repositories/admin_console.py`
- [ ] T080 [US4] Implement filter profile definitions, criterion normalization, safe summary generation, and restore validation in `src/multi_agent_platform/api/ui/admin_console.py`
- [ ] T081 [US4] Implement saved-filter list, save, restore, and delete handlers with validated scope and safe redirects in `src/multi_agent_platform/api/routers/admin_console.py`
- [ ] T082 [US4] Add saved-filter restoration audit event builders and fail-closed behavior in `src/multi_agent_platform/audit/service.py`
- [ ] T083 [US4] Expose useful workflow list filter definitions to the shell in `src/multi_agent_platform/api/ui/admin_workflows.py`
- [ ] T084 [US4] Expose useful model-skill history filter definitions to the shell in `src/multi_agent_platform/api/ui/model_skill_config.py`
- [ ] T085 [US4] Expose useful run inspection filter definitions to the shell in `src/multi_agent_platform/api/ui/run_details.py`
- [ ] T086 [US4] Expose useful reliability breaker and dead-letter filter definitions to the shell in `src/multi_agent_platform/api/ui/reliability_controls.py`
- [ ] T087 [P] [US4] Create saved-filter controls and restore summary partial in `src/multi_agent_platform/web_admin/templates/admin_shell/saved_filters.html`
- [ ] T088 [US4] Add optional saved-filter form enhancement and delete fallback handling in `src/multi_agent_platform/web_admin/static/admin_shell.js`

**Checkpoint**: Saved filters work only within the authorized user and scope boundary.

---

## Phase 7: User Story 5 - Review Delivery Evidence (Priority: P5)

**Goal**: Maintainers can review coverage, docs, PR notes, testing instructions, and README guidance for the admin shell feature.

**Independent Test**: Review the submitted docs and evidence; confirm coverage, route preservation, scope behavior, authorization, audit, safe states, saved filters, and existing admin links are covered without verbal explanation.

### Tests for User Story 5

- [ ] T089 [US5] Write failing docs tests that require admin shell concepts, scopes, navigation groups, common states, safe messages, saved filters, audit expectations, route preservation, testing instructions, PR notes, README guidance, coverage evidence, and optional enhancement/no-JS fallback validation in `tests/docs/test_admin_console_shell_docs.py`

### Implementation for User Story 5

- [ ] T090 [P] [US5] Create operator documentation for scopes, navigation, route preservation, common states, safe messages, saved filters, audit expectations, and troubleshooting in `docs/admin-console-shell.md`
- [ ] T091 [P] [US5] Expand reviewer testing instructions for platform admin, tenant admin, multi-tenant admin, unauthorized users, tenant switching, direct denial, audits, common states, flash messages, saved filters, existing page links, optional enhancement/no-JS fallback behavior, three-action navigation reachability, and active-scope identification within 5 seconds in `specs/010-admin-console-shell/testing-instructions.md`
- [ ] T092 [P] [US5] Create PR review notes covering scope handling, authorization, denied navigation, audit coverage, safe messages, shared states, route preservation, saved filters, coverage, and known risks in `specs/010-admin-console-shell/pr-review-notes.md`
- [ ] T093 [P] [US5] Update administrator-facing README guidance for `/admin`, active scope, navigation groups, common states, safe messages, saved filters, and existing admin page locations in `README.md`
- [ ] T094 [P] [US5] Update quickstart validation steps with final admin shell commands and expected coverage command in `specs/010-admin-console-shell/quickstart.md`

**Checkpoint**: Review evidence is present and docs tests can pass.

---

## Final Phase: Polish & Cross-Cutting Concerns

**Purpose**: Finish validation, quality gates, and review evidence after desired user stories are complete.

- [ ] T095 Run `uv run ruff check .` and fix reported admin console lint issues in `src/multi_agent_platform/api/ui/admin_console.py`
- [ ] T096 Run `uv run ruff format --check .` and fix formatting issues in `src/multi_agent_platform/api/routers/admin_console.py`
- [ ] T097 Run `uv run mypy src` and fix type issues in `src/multi_agent_platform/api/ui/admin_console.py`
- [ ] T098 Run focused admin console test files and record the passing command list in `specs/010-admin-console-shell/testing-instructions.md`
- [ ] T099 Run `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90` and record coverage evidence in `specs/010-admin-console-shell/pr-review-notes.md`
- [ ] T100 Review route preservation, tenant-scope query behavior, three-action navigation reachability, active-scope identification timing, and the 150 ms p95 admin shell request budget against the UI contract; record known risks and p95 timing evidence in `specs/010-admin-console-shell/pr-review-notes.md`
- [ ] T101 Update `AGENTS.md` recent changes if the admin shell implementation materially changes commands, project structure, or technology notes in `AGENTS.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup and blocks all user stories.
- **US1 (Phase 3)**: Depends on Foundational and is the MVP.
- **US2 (Phase 4)**: Depends on US1 shell scope/navigation helpers.
- **US3 (Phase 5)**: Depends on US1 and US2 shell context being available.
- **US4 (Phase 6)**: Depends on US1 scope/audit helpers and US2 wrapped filterable pages.
- **US5 (Phase 7)**: Can start after Foundational for docs scaffolding, but final content depends on US1-US4 behavior.
- **Polish**: Depends on all desired stories.

### User Story Dependencies

- **US1 Navigate By Admin Scope (P1)**: First deliverable after Foundational. No dependency on other stories.
- **US2 Consistent Console Layout (P2)**: Depends on US1 for active scope and authorized navigation.
- **US3 Empty/Error/Flash States (P3)**: Depends on US1/US2 shell context and templates.
- **US4 Saved Filters (P4)**: Depends on US1 scope/audit helpers and US2 page integration.
- **US5 Delivery Evidence (P5)**: Documents and verifies the completed scope.

### TDD Order Within Each Story

- Write the story's test tasks first.
- Run the targeted tests and confirm they fail for the expected reason.
- Implement Python models/services/helpers before route handlers.
- Implement route handlers before templates that consume their context.
- Complete template/docs tasks marked `[P]` only when their context contracts are stable.
- Re-run targeted tests before moving to the next story.

---

## Parallel Opportunities

- `[P]` is intentionally limited to isolated template or docs tasks.
- In US1, T028-T030 can be worked in parallel once T022-T026 define the shell context names.
- In US2, T043-T055 can be worked in parallel after T035-T042 establish shell context contracts for existing pages.
- In US3, T068-T069 can be worked in parallel after T062-T063 define state and message fields.
- In US4, T087 can be worked in parallel after T080 defines saved-filter view fields.
- In US5, T090-T094 can be worked in parallel after the relevant behavior and evidence are known.

## Parallel Example: User Story 1

```text
Task: "Create the authorization-filtered primary navigation partial in src/multi_agent_platform/web_admin/templates/admin_shell/navigation.html"
Task: "Create the active scope selector and scope display partial in src/multi_agent_platform/web_admin/templates/admin_shell/scope_selector.html"
Task: "Create the fail-closed unavailable page template in src/multi_agent_platform/web_admin/templates/admin_shell/unavailable.html"
```

## Parallel Example: User Story 2

```text
Task: "Convert workflow list template to extend the shell base in src/multi_agent_platform/web_admin/templates/workflows/index.html"
Task: "Convert model-skill config template to extend the shell base in src/multi_agent_platform/web_admin/templates/model_skill_config/index.html"
Task: "Convert run inspection list template to extend the shell base in src/multi_agent_platform/web_admin/templates/runs/index.html"
Task: "Convert reliability dashboard template to extend the shell base in src/multi_agent_platform/web_admin/templates/reliability/index.html"
```

## Parallel Example: User Story 5

```text
Task: "Create operator documentation in docs/admin-console-shell.md"
Task: "Create reviewer testing instructions in specs/010-admin-console-shell/testing-instructions.md"
Task: "Create PR review notes in specs/010-admin-console-shell/pr-review-notes.md"
Task: "Update administrator-facing README guidance in README.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup and Foundational tasks.
2. Complete US1 tests and verify they fail.
3. Implement scope resolution, navigation filtering, route authorization, and audit fail-closed behavior.
4. Validate platform-admin, tenant-admin, multi-tenant-admin, and unauthorized-user behavior through US1 tests.
5. Stop and review before wrapping every existing admin page.

### Incremental Delivery

1. US1 gives a secure console landing page with active scope and audited navigation.
2. US2 wraps existing admin destinations without replacing routes.
3. US3 adds consistent safe states and messages.
4. US4 adds scoped saved filters for useful list/investigation pages.
5. US5 packages review evidence, docs, README guidance, and coverage proof.

### Quality Gates

1. Run targeted tests for each completed story.
2. Run `uv run ruff check .`.
3. Run `uv run ruff format --check .`.
4. Run `uv run mypy src`.
5. Run `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90`.

## Notes

- Direct route identities must remain unchanged for all existing admin pages.
- Platform scope omits `tenant_id`; tenant scope requires a server-validated `tenant_id` query parameter.
- Audit persistence failure blocks protected rendering/actions.
- Templates must remain server-rendered and usable when `admin_shell.js` is unavailable.
- Saved filters are included because the spec requires persisted server-side filters where useful.
