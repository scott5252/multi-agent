# Tasks: Prompt Library And Agent Runtime Profiles

**Input**: Design documents from `/Users/scottcornell/src/my-projects/multi-agent/specs/012-prompt-runtime-profiles/`
**Prerequisites**: `/Users/scottcornell/src/my-projects/multi-agent/specs/012-prompt-runtime-profiles/plan.md`, `/Users/scottcornell/src/my-projects/multi-agent/specs/012-prompt-runtime-profiles/spec.md`, `/Users/scottcornell/src/my-projects/multi-agent/specs/012-prompt-runtime-profiles/research.md`, `/Users/scottcornell/src/my-projects/multi-agent/specs/012-prompt-runtime-profiles/data-model.md`, `/Users/scottcornell/src/my-projects/multi-agent/specs/012-prompt-runtime-profiles/contracts/`

**Tests**: TDD is required by the feature request and specification. Write each listed test first and confirm it fails before implementing the matching production task.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently after the shared foundation is complete.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the feature module skeleton and documentation targets.

- [X] T001 Create prompt package skeleton in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/prompts/__init__.py`
- [X] T002 Create agent profile package skeleton in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/agents/__init__.py`
- [X] T003 [P] Create prompt admin template directory with placeholder index in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/prompts/index.html`
- [X] T004 [P] Create agent profile admin template directory with placeholder index in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/agent_profiles/index.html`
- [X] T005 [P] Add feature documentation placeholders in `/Users/scottcornell/src/my-projects/multi-agent/docs/prompt-runtime-profiles.md`
- [X] T006 [P] Add PR note placeholder in `/Users/scottcornell/src/my-projects/multi-agent/docs/prompt-runtime-profiles-pr-notes.md`
- [X] T007 [P] Add testing instruction placeholder in `/Users/scottcornell/src/my-projects/multi-agent/docs/prompt-runtime-profiles-testing.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish persistence, shared schemas, authorization surfaces, router wiring, and repository contracts required by every user story.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T008 [P] Write migration coverage for prompt/profile tables, indexes, constraints, upgrade, and rollback in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/db/test_prompt_runtime_profiles_migration.py`
- [X] T009 [P] Write SQLAlchemy model tests for prompt entities and immutability constraints in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/db/test_prompt_models.py`
- [X] T010 [P] Write SQLAlchemy model tests for agent profile entities, active pointers, grants, and pins in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/db/test_agent_profile_models.py`
- [X] T011 [P] Write repository contract tests for prompt lineage/draft/version/grant queries in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/db/test_prompt_repository.py`
- [X] T012 [P] Write repository contract tests for agent profile draft/version/grant/resolution queries in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/db/test_agent_profile_repository.py`
- [X] T013 [P] Write auth policy tests for prompt/profile web and API surfaces, platform admin grants, tenant admin mutation, and scoped reads in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/auth/test_prompt_runtime_policy.py`
- [X] T014 [P] Write shared API schema tests for safe errors, scope rules, pagination, validation findings, and grant payloads in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/api/test_prompt_runtime_common_schemas.py`
- [X] T015 Implement Alembic migration for prompt/profile persistence, grants, pins, audit records, indexes, and constraints in `/Users/scottcornell/src/my-projects/multi-agent/alembic/versions/0012_prompt_runtime_profiles.py`
- [X] T016 Implement prompt SQLAlchemy models in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/db/models/prompts.py`
- [X] T017 Implement agent profile SQLAlchemy models in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/db/models/agent_profiles.py`
- [X] T018 Register prompt and agent profile models with metadata exports in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/db/models/__init__.py`
- [X] T019 Implement prompt repository methods for drafts, revisions, versions, grants, render tests, validation results, and audit queries in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/db/repositories/prompts.py`
- [X] T020 Implement agent profile repository methods for drafts, versions, active pointers, tenant grants, resolution, and pins in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/db/repositories/agent_profiles.py`
- [X] T021 Implement shared prompt API schema primitives and safe error models in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/schemas/prompts.py`
- [X] T022 Implement shared agent profile API schema primitives and safe error models in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/schemas/agent_profiles.py`
- [X] T023 Add prompt/profile authorization surface entries and scoped action names in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/auth/policy.py`
- [X] T024 Create empty prompt and agent profile router modules with route tags and dependency placeholders, then register them in the FastAPI app in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/routers/admin_prompts.py`, `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/routers/admin_agent_profiles.py`, and `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/main.py`

**Checkpoint**: Persistence, auth, repositories, schemas, and router wiring are ready for story implementation.

---

## Phase 3: User Story 1 - Author And Publish Prompt Versions (Priority: P1) MVP

**Goal**: Authorized platform and tenant admins can create prompt lineages, save draft revisions, validate variables, preview safe fixture rendering, and publish immutable prompt versions.

**Independent Test**: An admin creates a prompt lineage, saves a draft with variables and fixture values, receives blocking validation for mismatch cases, previews safely redacted fixture rendering, publishes a valid immutable version, and cannot mutate the published version.

### Tests for User Story 1

- [X] T025 [P] [US1] Write unit tests for prompt draft creation and stale revision rejection in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/prompts/test_prompt_service.py`
- [X] T026 [P] [US1] Write unit tests for `{{variable_name}}` parsing, malformed syntax rejection, and executable template rejection in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/prompts/test_template.py`
- [X] T027 [P] [US1] Write unit tests for template variable mismatch, missing, unused, duplicate, and malformed declarations in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/prompts/test_validation.py`
- [X] T028 [P] [US1] Write unit tests for safe fixture sanitization and unsafe value rejection in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/prompts/test_fixture_safety.py`
- [X] T029 [P] [US1] Write unit tests for safe preview rendering, redaction categories, missing required fixtures, and no model or live run-data access in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/prompts/test_preview.py`
- [X] T030 [P] [US1] Write unit tests for publish immutability, stale validation rejection, digest persistence, and publication audit summaries in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/prompts/test_publication.py`
- [X] T031 [P] [US1] Write FastAPI contract tests for prompt create, draft save, validate, preview, publish, grant, and safe error payloads in `/Users/scottcornell/src/my-projects/multi-agent/tests/contract/test_prompt_library_contract.py`
- [X] T032 [P] [US1] Write integration tests for prompt JSON API draft creation, validation, preview redaction, publication, and immutable version reads in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_prompts_api.py`

### Implementation for User Story 1

- [X] T033 [P] [US1] Implement prompt domain enums and value objects in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/prompts/models.py`
- [X] T034 [P] [US1] Implement prompt template parser and safe renderer in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/prompts/template.py`
- [X] T035 [P] [US1] Implement fixture safety classifiers and sanitizers in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/prompts/fixture_safety.py`
- [X] T036 [US1] Implement prompt validation rules for variable mismatch, fixture completeness, allowed categories, and publication readiness in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/prompts/validation.py`
- [X] T037 [US1] Implement prompt audit summary helpers for create, save, validate, preview, publish, grant, and denied attempts in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/prompts/audit.py`
- [X] T038 [US1] Implement prompt service for lineage creation, draft revision saves, validation persistence, safe preview, immutable publish, and platform-to-tenant grants in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/prompts/service.py`
- [X] T039 [US1] Implement prompt request/response schemas for create, draft save, validation, preview, publish, versions, grants, and history in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/schemas/prompts.py`
- [X] T040 [US1] Implement prompt admin JSON API endpoints in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/routers/admin_prompts.py`
- [X] T041 [US1] Wire prompt service dependencies and repository factories in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/bootstrap/container.py`

**Checkpoint**: User Story 1 is independently functional through JSON API and domain services.

---

## Phase 4: User Story 2 - Manage Prompt Lifecycle Without Breaking Runs (Priority: P2)

**Goal**: Admins can retire prompt versions from new use, preserve historical review and run references, and enforce tenant isolation and platform prompt grants.

**Independent Test**: An admin retires an active prompt version, sees it excluded from new-use selectors and Spec 007 prompt reference creation, and confirms pinned historical workflows and runs still review the immutable version under authorization.

### Tests for User Story 2

- [X] T042 [P] [US2] Write unit tests for prompt retirement state transitions, historical-only visibility, and immutable content preservation in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/prompts/test_retirement.py`
- [X] T043 [P] [US2] Write unit tests for tenant isolation, platform prompt version grants, revoked grants, and safe forbidden/not-found behavior in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/prompts/test_tenant_isolation.py`
- [ ] T044 [P] [US2] Write integration tests for retired prompt versions staying reviewable through workflow bundle and run pins in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/runtime/test_prompt_profile_pinning.py`
- [ ] T045 [P] [US2] Write integration tests for Spec 007 model-skill prompt reference validation against active, retired, unauthorized, wrong-scope, and digest-mismatched prompt versions in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/model_skill_config/test_prompt_reference_library_integration.py`
- [X] T046 [P] [US2] Write FastAPI contract tests for prompt retirement, grant visibility, historical review, and safe audit history in `/Users/scottcornell/src/my-projects/multi-agent/tests/contract/test_prompt_lifecycle_contract.py`

### Implementation for User Story 2

- [X] T047 [US2] Extend prompt service retirement, selector eligibility, historical review, and grant revocation behavior in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/prompts/service.py`
- [X] T048 [US2] Implement prompt version visibility and new-use eligibility repository queries in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/db/repositories/prompts.py`
- [ ] T049 [US2] Integrate prompt version validation into model-skill config prompt references in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/config/service.py`
- [ ] T050 [US2] Include prompt library version ids and digests in model-skill provenance resolution in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/config/resolver.py`
- [ ] T051 [US2] Persist published workflow and run prompt pins without rewriting historical runs in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/runtime/versioning.py`
- [X] T052 [US2] Extend prompt API retirement, grant, version detail, and history endpoints in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/routers/admin_prompts.py`

**Checkpoint**: User Story 2 prevents retired or unauthorized prompt versions from new use while preserving authorized historical review.

---

## Phase 5: User Story 3 - Configure Agent Runtime Profiles (Priority: P3)

**Goal**: Admins can create, validate, activate, resolve, retire, and pin governed runtime profiles for agent and sub-agent keys.

**Independent Test**: An admin creates a profile draft, attaches active authorized prompt versions, validates model routing, memory policy, skill requirements, tool expectations, output contracts, and test suites, activates an immutable profile version, and workflow validation resolves it with tenant-over-platform precedence.

### Tests for User Story 3

- [X] T053 [P] [US3] Write unit tests for agent profile creation, draft revision saves, stale save rejection, and activation immutability in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/agents/test_profile_service.py`
- [ ] T054 [P] [US3] Write unit tests for profile prompt reference validation, retired prompt blocking, unauthorized platform prompt grants, and purpose compatibility in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/agents/test_prompt_reference_validation.py`
- [ ] T055 [P] [US3] Write unit tests for memory policy validation and compatibility with existing memory policy rules in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/agents/test_memory_policy_validation.py`
- [X] T056 [P] [US3] Write unit tests for skill requirement validation, tool policy expectations, output contract expectations, and test-suite requirement blocking findings in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/agents/test_profile_validation.py`
- [X] T057 [P] [US3] Write unit tests for tenant-over-platform profile resolution, platform fallback grants, conflict detection, and no-profile blocking findings in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/agents/test_profile_resolution.py`
- [ ] T058 [P] [US3] Write integration tests for workflow draft validation consuming active runtime profiles and prompt library references in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/workflows/test_prompt_profile_workflow_validation.py`
- [ ] T059 [P] [US3] Write integration tests for run acceptance and dynamic first-use pinning of prompt/profile versions before side effects in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/runtime/test_prompt_profile_pinning.py`
- [X] T060 [P] [US3] Write FastAPI contract tests for profile create, draft save, validate, activate, retire, grant, resolve, and history endpoints in `/Users/scottcornell/src/my-projects/multi-agent/tests/contract/test_agent_profiles_contract.py`
- [ ] T061 [P] [US3] Write runtime profile resolution contract tests from the design artifact in `/Users/scottcornell/src/my-projects/multi-agent/tests/contract/test_runtime_profile_resolution_contract.py`

### Implementation for User Story 3

- [X] T062 [P] [US3] Implement agent profile domain enums and value objects in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/agents/models.py`
- [X] T063 [P] [US3] Implement profile validation rules for prompts, model routing hints, memory policy, skill requirements, tool expectations, output contracts, and test suites in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/agents/validation.py`
- [X] T064 [P] [US3] Implement tenant-over-platform profile resolution and conflict findings in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/agents/resolution.py`
- [X] T065 [US3] Implement agent profile service for draft saves, validation evidence, activation, active pointer updates, retirement, grants, and history in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/agents/service.py`
- [X] T066 [US3] Implement agent profile request/response schemas for profile create, draft save, validation, activation, retirement, grants, resolution, and history in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/schemas/agent_profiles.py`
- [X] T067 [US3] Implement agent profile admin JSON API endpoints in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/routers/admin_agent_profiles.py`
- [ ] T068 [US3] Add prompt/profile workflow validation adapter for workflow drafts and publications in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/prompts/workflow_hooks.py`
- [ ] T069 [US3] Connect workflow registry validation to prompt/profile findings and authorized detail links in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/admin/workflow_registry/validation.py`
- [ ] T070 [US3] Add model-skill prompt reference integration hooks for profile prompt references in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/agents/model_skill_integration.py`
- [ ] T071 [US3] Add memory policy compatibility helpers used by profile validation in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/memory/policy.py`
- [ ] T072 [US3] Persist run acceptance and dynamic first-use prompt/profile pins in orchestration before model, tool, or memory side effects in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/runtime/orchestration/service.py`
- [X] T073 [US3] Wire agent profile service dependencies and repository factories in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/bootstrap/container.py`

**Checkpoint**: User Story 3 is independently functional through JSON API, validation hooks, resolution, and runtime pinning.

---

## Phase 6: User Story 4 - Use A Browser-Based Admin Experience (Priority: P4)

**Goal**: Platform and tenant admins can use browser screens to complete prompt library and runtime profile workflows without command-line or raw database access.

**Independent Test**: An authorized admin completes list, create, edit draft, validate, preview, publish, retire, activate, resolution preview, history, and safe denial flows through the shared admin shell.

### Tests for User Story 4

- [ ] T074 [P] [US4] Write admin UI rendering tests for prompt list, create/edit, preview, detail, history, and disabled action states in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_prompts_ui.py`
- [ ] T075 [P] [US4] Write admin UI rendering tests for profile list, create/edit, detail, resolution preview, history, activation, and retirement states in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_agent_profiles_ui.py`
- [ ] T076 [P] [US4] Write browser-flow tests for non-developer prompt authoring, validation, safe preview redaction, publish, retire, and history review in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_prompt_runtime_browser_flows.py`
- [ ] T077 [P] [US4] Write browser-flow tests for profile creation, validation, activation, tenant fallback resolution, retirement, and history review in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_agent_profile_browser_flows.py`
- [ ] T078 [P] [US4] Write shared admin shell navigation tests proving Prompt Library and Agent Profiles are available to authorized platform and tenant admins with scope-aware controls in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_prompt_runtime_admin_navigation.py`
- [ ] T079 [P] [US4] Write unit tests for prompt/profile UI view models hiding unauthorized content and preserving submitted stale form fields in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/api/test_prompt_runtime_ui_models.py`

### Implementation for User Story 4

- [ ] T080 [US4] Implement prompt admin HTML routes and form handlers for list, new, edit, detail, preview, history, publish, retire, and grants in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/routers/admin_prompts.py`
- [ ] T081 [US4] Implement agent profile admin HTML routes and form handlers for list, new, edit, detail, resolve, history, activate, retire, and grants in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/routers/admin_agent_profiles.py`
- [ ] T082 [US4] Implement prompt UI view models for scope-aware controls, validation messages, preview redaction, and historical review in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/ui/prompts.py`
- [ ] T083 [US4] Implement agent profile UI view models for prompt selectors, policy sections, validation messages, resolution preview, and historical review in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/ui/agent_profiles.py`
- [ ] T084 [P] [US4] Implement prompt list, edit, detail, history, and preview templates in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/prompts/index.html`, `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/prompts/edit.html`, `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/prompts/detail.html`, `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/prompts/history.html`, and `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/prompts/preview.html`
- [ ] T085 [P] [US4] Implement agent profile list, edit, detail, history, and resolution templates in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/agent_profiles/index.html`, `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/agent_profiles/edit.html`, `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/agent_profiles/detail.html`, `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/agent_profiles/history.html`, and `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/agent_profiles/resolve.html`
- [ ] T086 [US4] Add Prompt Library and Agent Profiles entries to authorization-aware shared shell navigation for all authorized admin users in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/routers/admin_console.py`
- [ ] T087 [P] [US4] Add progressive enhancement JavaScript for fixture rows, validation refresh, preview refresh, policy sections, and unsaved-change prompts in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/static/prompt_runtime.js`
- [ ] T088 [P] [US4] Add restrained shared-shell CSS extensions for prompt/profile forms, tables, validation panels, previews, and history timelines in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/static/workflow_studio.css`
- [ ] T089 [US4] Surface prompt/profile validation findings and authorized links in workflow studio pages in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/workflows/draft_editor.html`

**Checkpoint**: User Story 4 makes the full feature available through the browser UI for authorized platform and tenant admins.

---

## Phase 7: User Story 5 - Audit, Review, And Delivery Evidence (Priority: P5)

**Goal**: Auditors, maintainers, and reviewers can inspect safe history, audit evidence, docs, PR notes, testing instructions, README updates, and coverage evidence.

**Independent Test**: A reviewer follows the documentation and PR notes to verify safe audit records, redaction, authorization denials, browser UI flows, API contracts, migration behavior, and >=90 percent coverage.

### Tests for User Story 5

- [ ] T090 [P] [US5] Write audit/redaction unit tests for prompt/profile lifecycle events, denied attempts, preview summaries, validation summaries, and no protected content leakage in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/audit/test_prompt_runtime_audit.py`
- [ ] T091 [P] [US5] Write docs tests covering prompt runtime docs, testing instructions, PR review notes, quickstart links, and README links in `/Users/scottcornell/src/my-projects/multi-agent/tests/docs/test_prompt_runtime_profiles_docs.py`
- [ ] T092 [P] [US5] Write API contract coverage test that compares implemented prompt/profile endpoints to the OpenAPI contract in `/Users/scottcornell/src/my-projects/multi-agent/tests/contract/test_prompt_runtime_profiles_contract.py`
- [ ] T093 [P] [US5] Write performance smoke tests that seed 10k prompt versions and 5k profile versions, assert prompt/profile list p95 <= 200 ms, template validation p95 <= 100 ms for 64 KB prompts with 100 variables, safe fixture preview p95 <= 150 ms, and workflow prompt/profile validation overhead p95 <= 50 ms per 100 referenced agents in `/Users/scottcornell/src/my-projects/multi-agent/tests/performance/prompt_runtime/test_prompt_runtime_latency.py`
- [ ] T094 [P] [US5] Write observability tests for structured logs, metrics, trace correlation, safe timeline/debug entries, and no protected content leakage in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/audit/test_prompt_runtime_observability.py`
- [ ] T095 [P] [US5] Write tests proving security-critical prompt/profile mutations fail closed when audit persistence is unavailable, including publish, retire, activate, grant, denied preview, selection, workflow-validation, and runtime-pinning events in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/audit/test_prompt_runtime_audit_fail_closed.py`
- [ ] T096 [P] [US5] Write API tests proving prompt/profile validation and preview endpoints enforce existing admin rate limits, bounded request sizes, tenant-scoped filters, and safe rejection responses in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_prompt_runtime_rate_limits.py`

### Implementation for User Story 5

- [ ] T097 [US5] Add prompt/profile redaction categories for fixtures, rendered previews, prompt content, profile policies, and denied selections in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/audit/classification.py`
- [ ] T098 [US5] Add safe audit capture builders for prompt/profile lifecycle, validation, preview, grants, denied access, workflow validation, and pinning events in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/audit/capture.py`
- [ ] T099 [US5] Add structured prompt/profile lifecycle, validation, preview, workflow-validation, and runtime-pinning log events with trace/run/tenant/scope correlation in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/audit/capture.py` and related prompt/profile services
- [ ] T100 [US5] Add Prometheus metrics for prompt/profile validation outcomes, preview safety rejections, publish/activate/retire attempts, grant changes, workflow-validation findings, and runtime pinning in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/observability/metrics.py`
- [ ] T101 [US5] Implement fail-closed audit persistence handling for security-critical prompt/profile mutations while allowing safe read-only history views to degrade with safe error states in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/audit/capture.py`, `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/prompts/service.py`, and `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/agents/service.py`
- [ ] T102 [US5] Wire prompt/profile validation and preview routes through existing admin rate-limit and bounded-operation controls, including request-size checks for fixture sets and prompt content in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/routers/admin_prompts.py` and `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/routers/admin_agent_profiles.py`
- [ ] T103 [US5] Implement safe history aggregation plus prompt/profile timeline and debugging evidence for admin pages and APIs in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/prompts/audit.py` and `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/agents/service.py`
- [ ] T104 [P] [US5] Document prompt lifecycle, variable validation, safe previews, immutable versions, retirement, profile contracts, scope rules, workflow validation, model-skill references, audit behavior, observability, fail-closed audit behavior, bounded preview/validation controls, and browser usage in `/Users/scottcornell/src/my-projects/multi-agent/docs/prompt-runtime-profiles.md`
- [ ] T105 [P] [US5] Document reviewer testing instructions for API, browser, migration, auth, audit, observability, rate limits, workflow, model-skill, runtime pinning, docs, coverage evidence, timed browser acceptance criteria, and locate-without-assistance acceptance checks in `/Users/scottcornell/src/my-projects/multi-agent/docs/prompt-runtime-profiles-testing.md`
- [ ] T106 [P] [US5] Write PR review notes covering immutable versions, tenant grants, preview safety, redaction, workflow validation, model-skill routing, runtime provenance, observability, fail-closed audit behavior, bounded preview/validation controls, browser UI coverage, risks, and rollback/retirement behavior in `/Users/scottcornell/src/my-projects/multi-agent/docs/prompt-runtime-profiles-pr-notes.md`
- [ ] T107 [P] [US5] Update local reviewer quickstart with prompt/profile browser URLs and acceptance flows in `/Users/scottcornell/src/my-projects/multi-agent/docs/quickstart.md`
- [ ] T108 [P] [US5] Update project README with prompt library, agent profile, browser UI, and reviewer documentation links in `/Users/scottcornell/src/my-projects/multi-agent/README.md`

**Checkpoint**: User Story 5 provides safe auditability and reviewer-ready delivery evidence.

---

## Final Phase: Polish & Cross-Cutting Concerns

**Purpose**: Validate the full delivery, clean up, and ensure all acceptance evidence is present.

- [ ] T109 [P] Run `uv run ruff check .`, resolve prompt/profile lint issues, and record evidence in `/Users/scottcornell/src/my-projects/multi-agent/docs/prompt-runtime-profiles-testing.md`
- [ ] T110 [P] Run `uv run ruff format --check .`, resolve formatting drift, and record evidence in `/Users/scottcornell/src/my-projects/multi-agent/docs/prompt-runtime-profiles-testing.md`
- [ ] T111 [P] Run `uv run mypy src`, resolve prompt/profile typing issues, and record evidence in `/Users/scottcornell/src/my-projects/multi-agent/docs/prompt-runtime-profiles-testing.md`
- [ ] T112 Run Alembic upgrade and downgrade smoke validation for prompt/profile migration in `/Users/scottcornell/src/my-projects/multi-agent/alembic/versions/0012_prompt_runtime_profiles.py`
- [ ] T113 Run full pytest with coverage >=90 percent and update missing evidence references in `/Users/scottcornell/src/my-projects/multi-agent/docs/prompt-runtime-profiles-testing.md`
- [ ] T114 Run timed browser acceptance flows with local admin UI, record prompt publish completion under 7 minutes, profile activation completion under 10 minutes, and history/validation/audit discoverability results for acceptance participants in `/Users/scottcornell/src/my-projects/multi-agent/docs/prompt-runtime-profiles-pr-notes.md`
- [ ] T115 Verify no raw secrets, credential values, unauthorized run content, or unsafe rendered previews appear in prompt/profile records, logs, pages, telemetry, or audit summaries and record evidence in `/Users/scottcornell/src/my-projects/multi-agent/docs/prompt-runtime-profiles-testing.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately.
- **Foundational (Phase 2)**: Depends on Phase 1 and blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational; delivers the MVP prompt library.
- **User Story 2 (Phase 4)**: Depends on User Story 1 prompt versions and repositories.
- **User Story 3 (Phase 5)**: Depends on User Story 1 active prompt versions and foundational repositories; can proceed in parallel with User Story 2 after prompt publication support exists.
- **User Story 4 (Phase 6)**: Depends on User Stories 1-3 service/API behavior for complete browser workflows.
- **User Story 5 (Phase 7)**: Depends on lifecycle and UI behavior for final audit and reviewer evidence.
- **Polish**: Depends on all desired user stories being complete.

### User Story Dependencies

- **US1 (P1)**: Starts after Foundational; no dependency on other user stories.
- **US2 (P2)**: Starts after US1 prompt publication exists.
- **US3 (P3)**: Starts after US1 prompt publication exists; workflow/runtime pinning tasks depend on active prompt/profile service contracts.
- **US4 (P4)**: Starts after API/service contracts for US1-US3 are available; template work can begin from view model contracts.
- **US5 (P5)**: Starts after audit actions and UI/API flows exist; docs placeholders can be drafted earlier but final evidence depends on implementation.

### Within Each User Story

- Write tests first and confirm they fail before implementation.
- Implement domain models/helpers before services.
- Implement repositories before services that persist state.
- Implement services before routers and UI handlers.
- Implement API schemas before routers.
- Implement UI view models before templates.
- Complete each checkpoint before using the story as a dependency for later stories.

---

## Parallel Opportunities

- Phase 1 placeholder files T003-T007 can run in parallel.
- Phase 2 test tasks T008-T014 can run in parallel, then implementation tasks T015-T024 should proceed by dependency order.
- US1 tests T025-T032 can run in parallel; parser, fixture safety, and domain models T033-T035 can run in parallel before validation and service work.
- US2 tests T042-T046 can run in parallel once US1 contracts exist.
- US3 tests T053-T061 can run in parallel; models, validation, and resolution T062-T064 can run in parallel before service and integration tasks.
- US4 tests T074-T079 can run in parallel; prompt and profile template tasks T084-T085 can run in parallel with JavaScript/CSS tasks T087-T088 after view model contracts are known.
- US5 tests T090-T096 can run in parallel; docs and review-note tasks T104-T108 can run in parallel after implementation behavior is stable.

## Parallel Example: User Story 1

```bash
Task: "Write unit tests for prompt draft creation and stale revision rejection in /Users/scottcornell/src/my-projects/multi-agent/tests/unit/prompts/test_prompt_service.py"
Task: "Write unit tests for {{variable_name}} parsing, malformed syntax rejection, and executable template rejection in /Users/scottcornell/src/my-projects/multi-agent/tests/unit/prompts/test_template.py"
Task: "Write unit tests for template variable mismatch, missing, unused, duplicate, and malformed declarations in /Users/scottcornell/src/my-projects/multi-agent/tests/unit/prompts/test_validation.py"
Task: "Write FastAPI contract tests for prompt create, draft save, validate, preview, publish, grant, and safe error payloads in /Users/scottcornell/src/my-projects/multi-agent/tests/contract/test_prompt_library_contract.py"
```

## Parallel Example: User Story 3

```bash
Task: "Write unit tests for agent profile creation, draft revision saves, stale save rejection, and activation immutability in /Users/scottcornell/src/my-projects/multi-agent/tests/unit/agents/test_profile_service.py"
Task: "Write unit tests for memory policy validation and compatibility with existing memory policy rules in /Users/scottcornell/src/my-projects/multi-agent/tests/unit/agents/test_memory_policy_validation.py"
Task: "Write unit tests for tenant-over-platform profile resolution, platform fallback grants, conflict detection, and no-profile blocking findings in /Users/scottcornell/src/my-projects/multi-agent/tests/unit/agents/test_profile_resolution.py"
Task: "Write runtime profile resolution contract tests from the design artifact in /Users/scottcornell/src/my-projects/multi-agent/tests/contract/test_runtime_profile_resolution_contract.py"
```

## Parallel Example: User Story 4

```bash
Task: "Write admin UI rendering tests for prompt list, create/edit, preview, detail, history, and disabled action states in /Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_prompts_ui.py"
Task: "Write admin UI rendering tests for profile list, create/edit, detail, resolution preview, history, activation, and retirement states in /Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_agent_profiles_ui.py"
Task: "Write shared admin shell navigation tests proving Prompt Library and Agent Profiles are available to authorized platform and tenant admins with scope-aware controls in /Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_prompt_runtime_admin_navigation.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup.
2. Complete Phase 2 foundation.
3. Complete Phase 3 prompt authoring and publication.
4. Validate prompt draft creation, template validation, variable mismatch handling, safe preview redaction, publication immutability, API contracts, and coverage for US1.

### Incremental Delivery

1. Add US1 prompt authoring and immutable publication.
2. Add US2 retirement, grants, tenant isolation, historical review, and model-skill prompt reference integration.
3. Add US3 runtime profiles, workflow validation, profile resolution, and run pinning.
4. Add US4 browser UI as the primary admin experience for all authorized platform and tenant admins.
5. Add US5 audit, docs, PR notes, testing instructions, README links, and final evidence.

### Final Validation Commands

```bash
uv sync
uv run alembic upgrade head
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
uv run uvicorn multi_agent_platform.api.main:app --reload
```

### Browser Validation URLs

```text
http://127.0.0.1:8000/admin/prompt-runtime/prompts
http://127.0.0.1:8000/admin/prompt-runtime/profiles
http://127.0.0.1:8000/admin/prompt-runtime/profiles/resolve
```

## Notes

- Every task above follows the required `- [ ] T### [P?] [US?] Description with file path` checklist format.
- `[P]` tasks touch distinct files and can run in parallel after their phase prerequisites are satisfied.
- Browser UI tasks are required acceptance scope, not optional polish.
- Tenant admins must be able to use the browser UI for tenant-scoped prompt/profile work; platform admins must be able to use it for platform-scoped assets and per-version tenant grants.
- Platform prompt/profile versions are tenant-visible only through explicit per-version grants.
- Prompt previews, logs, audit records, and rendered pages must never include raw secrets, credential values, provider tokens, unauthorized run content, protected cross-tenant content, or unsafe rendered prompts.
