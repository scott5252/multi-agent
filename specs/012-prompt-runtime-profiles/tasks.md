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
- [X] T044 [P] [US2] Write integration tests for retired prompt versions staying reviewable through workflow bundle and run pins in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/runtime/test_prompt_profile_pinning.py`
- [X] T045 [P] [US2] Write integration tests for Spec 007 model-skill prompt reference validation against active, retired, unauthorized, wrong-scope, and digest-mismatched prompt versions in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/model_skill_config/test_prompt_reference_library_integration.py`
- [X] T046 [P] [US2] Write FastAPI contract tests for prompt retirement, grant visibility, historical review, and safe audit history in `/Users/scottcornell/src/my-projects/multi-agent/tests/contract/test_prompt_lifecycle_contract.py`

### Implementation for User Story 2

- [X] T047 [US2] Extend prompt service retirement, selector eligibility, historical review, and grant revocation behavior in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/prompts/service.py`
- [X] T048 [US2] Implement prompt version visibility and new-use eligibility repository queries in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/db/repositories/prompts.py`
- [X] T049 [US2] Integrate prompt version validation into model-skill config prompt references in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/config/service.py`
- [X] T050 [US2] Include prompt library version ids and digests in model-skill provenance resolution in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/config/resolver.py`
- [X] T051 [US2] Persist published workflow and run prompt pins without rewriting historical runs in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/runtime/versioning.py`
- [X] T052 [US2] Extend prompt API retirement, grant, version detail, and history endpoints in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/routers/admin_prompts.py`

**Checkpoint**: User Story 2 prevents retired or unauthorized prompt versions from new use while preserving authorized historical review.

---

## Phase 5: User Story 3 - Configure Agent Runtime Profiles (Priority: P3)

**Goal**: Admins can create, validate, activate, resolve, retire, and pin governed runtime profiles for agent and sub-agent keys.

**Independent Test**: An admin creates a profile draft, attaches active authorized prompt versions, validates model routing, memory policy, skill requirements, tool expectations, output contracts, and test suites, activates an immutable profile version, and workflow validation resolves it with tenant-over-platform precedence.

### Tests for User Story 3

- [X] T053 [P] [US3] Write unit tests for agent profile creation, draft revision saves, stale save rejection, and activation immutability in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/agents/test_profile_service.py`
- [X] T054 [P] [US3] Write unit tests for profile prompt reference validation, retired prompt blocking, unauthorized platform prompt grants, and purpose compatibility in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/agents/test_prompt_reference_validation.py`
- [X] T055 [P] [US3] Write unit tests for memory policy validation and compatibility with existing memory policy rules in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/agents/test_memory_policy_validation.py`
- [X] T056 [P] [US3] Write unit tests for skill requirement validation, tool policy expectations, output contract expectations, and test-suite requirement blocking findings in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/agents/test_profile_validation.py`
- [X] T057 [P] [US3] Write unit tests for tenant-over-platform profile resolution, platform fallback grants, conflict detection, and no-profile blocking findings in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/agents/test_profile_resolution.py`
- [X] T058 [P] [US3] Write integration tests for workflow draft validation consuming active runtime profiles and prompt library references in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/workflows/test_prompt_profile_workflow_validation.py`
- [X] T059 [P] [US3] Write integration tests for run acceptance and dynamic first-use pinning of prompt/profile versions before side effects in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/runtime/test_prompt_profile_pinning.py`
- [X] T060 [P] [US3] Write FastAPI contract tests for profile create, draft save, validate, activate, retire, grant, resolve, and history endpoints in `/Users/scottcornell/src/my-projects/multi-agent/tests/contract/test_agent_profiles_contract.py`
- [X] T061 [P] [US3] Write runtime profile resolution contract tests from the design artifact in `/Users/scottcornell/src/my-projects/multi-agent/tests/contract/test_runtime_profile_resolution_contract.py`

### Implementation for User Story 3

- [X] T062 [P] [US3] Implement agent profile domain enums and value objects in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/agents/models.py`
- [X] T063 [P] [US3] Implement profile validation rules for prompts, model routing hints, memory policy, skill requirements, tool expectations, output contracts, and test suites in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/agents/validation.py`
- [X] T064 [P] [US3] Implement tenant-over-platform profile resolution and conflict findings in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/agents/resolution.py`
- [X] T065 [US3] Implement agent profile service for draft saves, validation evidence, activation, active pointer updates, retirement, grants, and history in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/agents/service.py`
- [X] T066 [US3] Implement agent profile request/response schemas for profile create, draft save, validation, activation, retirement, grants, resolution, and history in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/schemas/agent_profiles.py`
- [X] T067 [US3] Implement agent profile admin JSON API endpoints in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/routers/admin_agent_profiles.py`
- [X] T068 [US3] Add prompt/profile workflow validation adapter for workflow drafts and publications in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/prompts/workflow_hooks.py`
- [X] T069 [US3] Connect workflow registry validation to prompt/profile findings and authorized detail links in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/admin/workflow_registry/validation.py`
- [X] T070 [US3] Add model-skill prompt reference integration hooks for profile prompt references in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/agents/model_skill_integration.py`
- [X] T071 [US3] Add memory policy compatibility helpers used by profile validation in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/memory/policy.py`
- [X] T072 [US3] Persist run acceptance and dynamic first-use prompt/profile pins in orchestration before model, tool, or memory side effects in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/runtime/orchestration/service.py`
- [X] T073 [US3] Wire agent profile service dependencies and repository factories in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/bootstrap/container.py`

**Checkpoint**: User Story 3 is independently functional through JSON API, validation hooks, resolution, and runtime pinning.

---

## Phase 6: User Story 4 - Use A Browser-Based Admin Experience (Priority: P4)

**Goal**: Platform and tenant admins can use browser screens to complete prompt library and runtime profile workflows without command-line or raw database access.

**Independent Test**: An authorized admin completes list, create, edit draft, validate, preview, publish, retire, activate, resolution preview, history, and safe denial flows through the shared admin shell.

### Tests for User Story 4

- [X] T074 [P] [US4] Write admin UI rendering tests for prompt list, create/edit, preview, detail, history, and disabled action states in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_prompts_ui.py`
- [X] T075 [P] [US4] Write admin UI rendering tests for profile list, create/edit, detail, resolution preview, history, activation, and retirement states in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_agent_profiles_ui.py`
- [X] T076 [P] [US4] Write browser-flow tests for non-developer prompt authoring, validation, safe preview redaction, publish, retire, and history review in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_prompt_runtime_browser_flows.py`
- [X] T077 [P] [US4] Write browser-flow tests for profile creation, validation, activation, tenant fallback resolution, retirement, and history review in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_agent_profile_browser_flows.py`
- [X] T078 [P] [US4] Write shared admin shell navigation tests proving Prompt Library and Agent Profiles are available to authorized platform and tenant admins with scope-aware controls in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_prompt_runtime_admin_navigation.py`
- [X] T079 [P] [US4] Write unit tests for prompt/profile UI view models hiding unauthorized content and preserving submitted stale form fields in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/api/test_prompt_runtime_ui_models.py`

### Implementation for User Story 4

- [X] T080 [US4] Implement prompt admin HTML routes and form handlers for list, new, edit, detail, preview, history, publish, retire, and grants in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/routers/admin_prompts.py`
- [X] T081 [US4] Implement agent profile admin HTML routes and form handlers for list, new, edit, detail, resolve, history, activate, retire, and grants in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/routers/admin_agent_profiles.py`
- [X] T082 [US4] Implement prompt UI view models for scope-aware controls, validation messages, preview redaction, and historical review in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/ui/prompts.py`
- [X] T083 [US4] Implement agent profile UI view models for prompt selectors, policy sections, validation messages, resolution preview, and historical review in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/ui/agent_profiles.py`
- [X] T084 [P] [US4] Implement prompt list, edit, detail, history, and preview templates in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/prompts/index.html`, `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/prompts/edit.html`, `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/prompts/detail.html`, `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/prompts/history.html`, and `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/prompts/preview.html`
- [X] T085 [P] [US4] Implement agent profile list, edit, detail, history, and resolution templates in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/agent_profiles/index.html`, `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/agent_profiles/edit.html`, `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/agent_profiles/detail.html`, `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/agent_profiles/history.html`, and `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/agent_profiles/resolve.html`
- [X] T086 [US4] Add Prompt Library and Agent Profiles entries to authorization-aware shared shell navigation for all authorized admin users in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/routers/admin_console.py`
- [X] T087 [P] [US4] Add progressive enhancement JavaScript for fixture rows, validation refresh, preview refresh, policy sections, and unsaved-change prompts in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/static/prompt_runtime.js`
- [X] T088 [P] [US4] Add restrained shared-shell CSS extensions for prompt/profile forms, tables, validation panels, previews, and history timelines in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/static/workflow_studio.css`
- [X] T089 [US4] Surface prompt/profile validation findings and authorized links in workflow studio pages in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/workflows/draft_editor.html`

**Checkpoint**: User Story 4 makes the full feature available through the browser UI for authorized platform and tenant admins.

---

## Phase 7: User Story 5 - Audit, Review, And Delivery Evidence (Priority: P5)

**Goal**: Auditors, maintainers, and reviewers can inspect safe history, audit evidence, docs, PR notes, testing instructions, README updates, and coverage evidence.

**Independent Test**: A reviewer follows the documentation and PR notes to verify safe audit records, redaction, authorization denials, browser UI flows, API contracts, migration behavior, and >=90 percent coverage.

### Tests for User Story 5

- [X] T090 [P] [US5] Write audit/redaction unit tests for prompt/profile lifecycle events, denied attempts, preview summaries, validation summaries, and no protected content leakage in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/audit/test_prompt_runtime_audit.py`
- [X] T091 [P] [US5] Write docs tests covering prompt runtime docs, testing instructions, PR review notes, quickstart links, and README links in `/Users/scottcornell/src/my-projects/multi-agent/tests/docs/test_prompt_runtime_profiles_docs.py`
- [X] T092 [P] [US5] Write API contract coverage test that compares implemented prompt/profile endpoints to the OpenAPI contract in `/Users/scottcornell/src/my-projects/multi-agent/tests/contract/test_prompt_runtime_profiles_contract.py`
- [X] T093 [P] [US5] Write performance smoke tests that seed 10k prompt versions and 5k profile versions, assert prompt/profile list p95 <= 200 ms, template validation p95 <= 100 ms for 64 KB prompts with 100 variables, safe fixture preview p95 <= 150 ms, and workflow prompt/profile validation overhead p95 <= 50 ms per 100 referenced agents in `/Users/scottcornell/src/my-projects/multi-agent/tests/performance/prompt_runtime/test_prompt_runtime_latency.py`
- [X] T094 [P] [US5] Write observability tests for structured logs, metrics, trace correlation, safe timeline/debug entries, and no protected content leakage in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/audit/test_prompt_runtime_observability.py`
- [X] T095 [P] [US5] Write tests proving security-critical prompt/profile mutations fail closed when audit persistence is unavailable, including publish, retire, activate, grant, denied preview, selection, workflow-validation, and runtime-pinning events in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/audit/test_prompt_runtime_audit_fail_closed.py`
- [X] T096 [P] [US5] Write API tests proving prompt/profile validation and preview endpoints enforce existing admin rate limits, bounded request sizes, tenant-scoped filters, and safe rejection responses in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_prompt_runtime_rate_limits.py`

### Implementation for User Story 5

- [X] T097 [US5] Add prompt/profile redaction categories for fixtures, rendered previews, prompt content, profile policies, and denied selections in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/audit/classification.py`
- [X] T098 [US5] Add safe audit capture builders for prompt/profile lifecycle, validation, preview, grants, denied access, workflow validation, and pinning events in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/audit/capture.py`
- [X] T099 [US5] Add structured prompt/profile lifecycle, validation, preview, workflow-validation, and runtime-pinning log events with trace/run/tenant/scope correlation in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/audit/capture.py` and related prompt/profile services
- [X] T100 [US5] Add Prometheus metrics for prompt/profile validation outcomes, preview safety rejections, publish/activate/retire attempts, grant changes, workflow-validation findings, and runtime pinning in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/observability/metrics.py`
- [X] T101 [US5] Implement fail-closed audit persistence handling for security-critical prompt/profile mutations while allowing safe read-only history views to degrade with safe error states in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/audit/capture.py`, `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/prompts/service.py`, and `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/agents/service.py`
- [X] T102 [US5] Wire prompt/profile validation and preview routes through existing admin rate-limit and bounded-operation controls, including request-size checks for fixture sets and prompt content in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/routers/admin_prompts.py` and `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/routers/admin_agent_profiles.py`
- [X] T103 [US5] Implement safe history aggregation plus prompt/profile timeline and debugging evidence for admin pages and APIs in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/prompts/audit.py` and `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/agents/service.py`
- [X] T104 [P] [US5] Document prompt lifecycle, variable validation, safe previews, immutable versions, retirement, profile contracts, scope rules, workflow validation, model-skill references, audit behavior, observability, fail-closed audit behavior, bounded preview/validation controls, and browser usage in `/Users/scottcornell/src/my-projects/multi-agent/docs/prompt-runtime-profiles.md`
- [X] T105 [P] [US5] Document reviewer testing instructions for API, browser, migration, auth, audit, observability, rate limits, workflow, model-skill, runtime pinning, docs, coverage evidence, timed browser acceptance criteria, and locate-without-assistance acceptance checks in `/Users/scottcornell/src/my-projects/multi-agent/docs/prompt-runtime-profiles-testing.md`
- [X] T106 [P] [US5] Write PR review notes covering immutable versions, tenant grants, preview safety, redaction, workflow validation, model-skill routing, runtime provenance, observability, fail-closed audit behavior, bounded preview/validation controls, browser UI coverage, risks, and rollback/retirement behavior in `/Users/scottcornell/src/my-projects/multi-agent/docs/prompt-runtime-profiles-pr-notes.md`
- [X] T107 [P] [US5] Update local reviewer quickstart with prompt/profile browser URLs and acceptance flows in `/Users/scottcornell/src/my-projects/multi-agent/docs/quickstart.md`
- [X] T108 [P] [US5] Update project README with prompt library, agent profile, browser UI, and reviewer documentation links in `/Users/scottcornell/src/my-projects/multi-agent/README.md`

**Checkpoint**: User Story 5 provides safe auditability and reviewer-ready delivery evidence.

---

## Final Phase: Polish & Cross-Cutting Concerns

**Purpose**: Validate the full delivery, clean up, and ensure all acceptance evidence is present.

- [X] T109 [P] Run `uv run ruff check .`, resolve prompt/profile lint issues, and record evidence in `/Users/scottcornell/src/my-projects/multi-agent/docs/prompt-runtime-profiles-testing.md`
- [X] T110 [P] Run `uv run ruff format --check .`, resolve formatting drift, and record evidence in `/Users/scottcornell/src/my-projects/multi-agent/docs/prompt-runtime-profiles-testing.md`
- [X] T111 [P] Run `uv run mypy src`, resolve prompt/profile typing issues, and record evidence in `/Users/scottcornell/src/my-projects/multi-agent/docs/prompt-runtime-profiles-testing.md`
- [X] T112 Run Alembic upgrade and downgrade smoke validation for prompt/profile migration in `/Users/scottcornell/src/my-projects/multi-agent/alembic/versions/0012_prompt_runtime_profiles.py`
- [X] T113 Run full pytest with coverage >=90 percent and update missing evidence references in `/Users/scottcornell/src/my-projects/multi-agent/docs/prompt-runtime-profiles-testing.md`
- [X] T114 Run timed browser acceptance flows with local admin UI, record prompt publish completion under 7 minutes, profile activation completion under 10 minutes, and history/validation/audit discoverability results for acceptance participants in `/Users/scottcornell/src/my-projects/multi-agent/docs/prompt-runtime-profiles-pr-notes.md`
- [X] T115 Verify no raw secrets, credential values, unauthorized run content, or unsafe rendered previews appear in prompt/profile records, logs, pages, telemetry, or audit summaries and record evidence in `/Users/scottcornell/src/my-projects/multi-agent/docs/prompt-runtime-profiles-testing.md`

---

## Phase 8: V2 Foundational Gateway Wiring (Blocking Prerequisites)

**Purpose**: Add container-managed gateway dependencies, worker gateway readiness, and additive persistence for gateway/probe/catalog operation identities without changing completed Spec 012 prompt/profile behavior.

**CRITICAL**: These tasks are additive to completed Spec 012 work. Do not mark existing completed Spec 012 tasks incomplete unless a V2 test proves a real regression requiring revision.

- [ ] T116 [P] Write unit tests proving `Container` exposes `ModelProviderRepository`, `ModelProviderService`, `ProviderAdapterRegistry`, `ModelGateway`, provider secret resolver, metrics, tracing, retry, breaker, and audit factories without unmanaged per-request HTTP client lifecycle in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/bootstrap/test_container_model_gateway_factories.py`
- [ ] T117 [P] Write unit tests proving adapter registry lifecycle ownership, container disposal cleanup, and provider secret resolver wiring for gateway adapters in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/model_providers/test_gateway_dependency_lifecycle.py`
- [ ] T118 [P] Write unit tests proving `WorkerBootstrap` exposes gateway-ready dependencies and fails readiness when gateway, repository, adapter, secret, retry, breaker, metrics, tracing, or audit dependencies are unavailable in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/bootstrap/test_worker_gateway_bootstrap.py`
- [ ] T119 [P] Write migration tests for additive V2 gateway operation, provider probe operation, catalog sync operation, physical attempt, uniqueness, lookup index, upgrade, and downgrade behavior in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/db/test_prompt_runtime_profiles_v2_gateway_migration.py`
- [ ] T120 [P] Write repository tests for gateway/probe/catalog logical operation identity creation, duplicate lookup, authoritative outcome reuse, physical attempt numbering, and recovery queries in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/db/test_model_provider_operation_repository.py`
- [ ] T121 Implement additive Alembic migration for V2 gateway operation identities, provider probe operation identities, catalog sync operation identities, child attempt records, uniqueness, and lookup indexes without destructive rewrites in `/Users/scottcornell/src/my-projects/multi-agent/alembic/versions/0013_prompt_runtime_profiles_v2_gateway_operations.py`
- [ ] T122 Implement V2 gateway operation, physical attempt, provider probe operation, catalog sync operation, and safe provenance model fields in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/db/models/model_providers.py`
- [ ] T123 Implement V2 operation identity, physical attempt, duplicate suppression, and recovery repository methods in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/db/repositories/model_providers.py`
- [ ] T124 Implement gateway invocation context, operation identity, retry decision summary, breaker decision summary, provider provenance, and safe audit value objects in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/models.py`
- [ ] T125 Implement container-managed factories for `ModelGateway`, `ProviderAdapterRegistry`, `ModelProviderService`, provider repository, provider secret resolver, metrics hooks, tracing hooks, retry helper, breaker helper, and audit hooks in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/bootstrap/container.py`
- [ ] T126 Implement adapter registry lifecycle cleanup and managed provider client ownership so adapters, not request handlers or workers, own provider HTTP clients in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/adapters.py`
- [ ] T127 Implement worker bootstrap gateway dependency status, gateway factory exposure, provider service factory exposure, retry helper exposure, and breaker helper exposure in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/bootstrap/worker.py`
- [ ] T128 Wire worker startup and leasing loops to check gateway readiness before accepting model-backed work while preserving non-model-backed maintenance behavior in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/workers/main.py` and `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/workers/loops.py`

**Checkpoint**: Application and worker dependency graphs can construct gateway-ready services from the container, and V2 operation identity persistence is available without rewriting historical Spec 012 or Spec 011 records.

---

## Phase 9: User Story 6 V2 - Profile-Governed Runtime Execution Through ModelGateway (Priority: P1)

**Goal**: Every model-backed runtime action, profile test bench execution, and model-backed workflow validation path uses `ModelGateway` with prompt/profile pins, tenant/run/step/trace context, routing provenance, idempotency, and safe context before side effects.

**Independent Test**: A representative workflow run, a profile test bench execution, and a model-backed workflow validation path all invoke `ModelGateway` and persist equivalent safe context containing tenant id, workflow run id, run step id where available, trace id, idempotency key, selected prompt version ids, selected profile version id, model routing provenance, and safe policy summaries.

### Tests for User Story 6 V2

- [ ] T129 [P] [US6] Write integration tests proving run acceptance resolves and pins workflow-declared prompt/profile versions before model-backed work, with dynamic first-use pinning persisted before side effects in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/runtime/test_prompt_profile_gateway_pinning.py`
- [ ] T130 [P] [US6] Write unit tests proving runtime orchestration calls `ModelGateway` with tenant id, workflow run id, run step id where available, trace id, idempotency key, prompt version ids, profile version id, model routing provenance, and safe context in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/runtime/orchestration/test_model_gateway_invocation.py`
- [ ] T131 [P] [US6] Write integration tests proving profile test bench execution and model-backed profile validation use the same gateway path and record equivalent safe metadata in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/runtime/test_profile_test_bench_gateway.py`
- [ ] T132 [P] [US6] Write unit tests proving runtime profile model routing hints do not bypass `model_skill_config` authorization or tenant-over-platform profile precedence in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/agents/test_profile_gateway_routing_context.py`
- [ ] T133 [P] [US6] Write contract tests for the runtime gateway execution contract, including invocation ordering, side-effect boundary, test bench identity, workflow validation identity, and safe context shape in `/Users/scottcornell/src/my-projects/multi-agent/tests/contract/test_runtime_gateway_execution_contract.py`

### Implementation for User Story 6 V2

- [ ] T134 [US6] Implement prompt/profile run acceptance and dynamic first-use pin accessors used by gateway invocation context in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/runtime/versioning.py`
- [ ] T135 [US6] Implement runtime orchestration `GatewayInvocationContext` construction and `ModelGateway` invocation before model, tool, memory, approval, handoff, artifact, or other side-effectful work in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/runtime/orchestration/service.py`
- [ ] T136 [US6] Propagate workflow run step id, trace id, idempotency key, and side-effect boundary metadata through orchestration side-effect handling in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/runtime/orchestration/side_effects.py`
- [ ] T137 [US6] Implement profile-to-gateway routing context integration for model routing hints, prompt/profile provenance, memory policy context, tool policy expectations, and output contract metadata in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/agents/model_skill_integration.py`
- [ ] T138 [US6] Enforce `model_skill_config` route authorization and tenant/provider visibility when applying runtime profile hints to gateway routing context in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/config/resolver.py`
- [ ] T139 [US6] Implement profile test bench model-backed execution through `ModelGateway` with test bench identity and equivalent safe metadata in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/agents/test_bench.py`
- [ ] T140 [US6] Implement model-backed workflow validation execution through `ModelGateway` while preserving non-model-backed validation behavior in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/admin/workflow_registry/validation.py`
- [ ] T141 [US6] Persist equivalent safe gateway metadata for runtime, test bench, and workflow validation invocations in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/gateway.py`

**Checkpoint**: Profile-governed production runtime, test bench, and model-backed validation all use `ModelGateway` end to end without bypassing existing routing authorization.

---

## Phase 10: User Story 7 V2 - Durable Gateway, Probe, And Catalog Recovery (Priority: P2)

**Goal**: Gateway invocations, provider test probes, and provider catalog synchronization actions are idempotent and recoverable across retries, duplicate submits, worker restarts, and partial failures.

**Independent Test**: Gateway invocation, provider probe, and catalog sync acceptance tests can be interrupted and retried with the same logical operation identity, then prove one authoritative outcome is preserved while child physical attempts and safe recovery summaries remain visible.

### Tests for User Story 7 V2

- [ ] T142 [P] [US7] Write unit tests mapping provider normalized error categories to reliability failure categories, retry budgets, retry decision categories, and retry decision summaries in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/reliability/test_gateway_retry_decisions.py`
- [ ] T143 [P] [US7] Write unit tests for circuit breaker scope keys and breaker decision summaries scoped by provider connection and model/catalog identity with tenant/run context stored as evidence only in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/reliability/test_gateway_breaker_decisions.py`
- [ ] T144 [P] [US7] Write integration tests for persisted gateway invocation idempotency, duplicate suppression, authoritative outcome reuse, ambiguous recovery, and worker restart recovery in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/runtime/test_gateway_operation_recovery.py`
- [ ] T145 [P] [US7] Write integration tests for provider probe idempotency, admin resubmit recovery, duplicate suppression, and safe prior-result return in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_provider_probe_recovery.py`
- [ ] T146 [P] [US7] Write integration tests for provider catalog sync checkpoints, restart recovery, duplicate authoritative catalog suppression, and safe partial failure handling in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/model_providers/test_catalog_sync_recovery.py`

### Implementation for User Story 7 V2

- [ ] T147 [US7] Implement provider normalized error to retry failure-category mapping, retry decision category normalization, and retry budget summaries in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/reliability/retries.py`
- [ ] T148 [US7] Implement gateway circuit breaker scope keys and breaker decision summary helpers for provider connection plus model/catalog identity in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/reliability/breakers.py`
- [ ] T149 [US7] Integrate retry decision and circuit breaker decision evaluation into the gateway invocation flow before provider adapter calls and after physical attempts in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/gateway.py`
- [ ] T150 [US7] Implement logical gateway operation recovery, duplicate suppression, physical attempt child recording, and authoritative outcome reuse in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/db/repositories/model_providers.py`
- [ ] T151 [US7] Implement provider probe operation identity, recovery, duplicate suppression, and authoritative safe result reuse in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/service.py` and `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/probes.py`
- [ ] T152 [US7] Implement catalog sync operation identity, safe checkpoints, recovery, duplicate authoritative catalog suppression, and partial failure handling in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/catalog_sync.py`

**Checkpoint**: Provider operations can retry, recover, and suppress duplicates using logical operation identities without creating duplicate authoritative provider effects or rewriting historical records.

---

## Phase 11: User Story 8 V2 - Provider Operation Limits, Retry, Breaker, And Safe Audit Hardening (Priority: P3)

**Goal**: Provider operations enforce bounded execution, existing rate limits, retry decisions, breaker decisions, normalized errors, direct-call guardrails, and safe audit/telemetry summaries without leaking sensitive provider or prompt content.

**Independent Test**: Successful, throttled, denied, retried, circuit-open, provider-error, and direct-call-bypass attempts all produce safe normalized evidence while records, logs, telemetry, and audits exclude prompts, completions, credentials, provider tokens, API keys, local endpoint secrets, unsafe previews, and unauthorized run content.

### Tests for User Story 8 V2

- [ ] T153 [P] [US8] Write integration tests proving admin provider test probes enforce existing actor/provider-connection rate limits, tenant/global backstops, and bounded-operation controls before provider activity in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_model_provider_probe_limits.py`
- [ ] T154 [P] [US8] Write unit tests proving denied and throttled provider probe attempts persist safe audit evidence with actor, scope, tenant, provider identity, decision category, recovery identity, and safe summary in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/model_providers/test_provider_probe_audit.py`
- [ ] T155 [P] [US8] Write static guardrail tests scanning runtime, workers, orchestration, test bench, workflow validation, agents, prompts, config, and API paths for direct provider SDK imports or direct provider HTTP usage outside allowed `ModelGateway` adapter modules in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/guardrails/test_model_gateway_only_provider_calls.py`
- [ ] T156 [P] [US8] Write behavioral tests proving model-backed runtime, test bench, and workflow validation execution fails or routes through `ModelGateway` when direct provider calls are attempted in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/runtime/test_model_gateway_guardrails.py`
- [ ] T157 [P] [US8] Write safety tests proving raw prompts, completions, credentials, provider tokens, API keys, local endpoint secrets, unsafe rendered previews, and unauthorized run content never appear in gateway records, logs, telemetry, or audits in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/model_providers/test_gateway_safe_observability.py`
- [ ] T158 [P] [US8] Write integration tests proving gateway attempts include prompt/profile provenance, provider provenance, retry summaries, breaker summaries, latency, usage availability, normalized errors, and safe audit summaries in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/model_providers/test_gateway_attempt_evidence.py`

### Implementation for User Story 8 V2

- [ ] T159 [US8] Implement existing rate-limit, tenant/global backstop, and bounded-operation enforcement for admin provider probe routes before provider activity in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/routers/admin_model_providers.py`
- [ ] T160 [US8] Implement denied and throttled provider probe safe audit capture in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/service.py` and `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/audit/capture.py`
- [ ] T161 [US8] Implement direct provider call guardrail allowlist and scanning helpers for runtime/test bench enforcement in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/guardrails.py`
- [ ] T162 [US8] Refactor any remaining model-backed runtime, test bench, and workflow validation provider calls to `ModelGateway` in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/runtime/orchestration/service.py`, `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/agents/test_bench.py`, and `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/admin/workflow_registry/validation.py`
- [ ] T163 [US8] Implement provider operation safe audit classifications, capture builders, metrics correlation, and tracing correlation without sensitive payloads in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/audit/classification.py`, `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/audit/capture.py`, `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/observability/metrics.py`, and `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/observability/tracing.py`
- [ ] T164 [US8] Add gateway/probe/catalog operation metrics and trace hooks for latency, usage availability, normalized outcome, retry category, breaker decision, duplicate suppression, and recovery outcome in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/gateway.py` and `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/service.py`

**Checkpoint**: Provider operation limits, retry/breaker evidence, guardrails, and safe observability protect all covered model-backed execution paths.

---

## Phase 12: User Story 9 V2 - Combined Prompt/Profile And Provider Provenance Evidence (Priority: P4)

**Goal**: Reviewers and incident responders can see Spec 012 prompt/profile pins together with Spec 011 provider gateway metadata for newly accepted runs and dynamic first-use selections, while historical runs remain immutable.

**Independent Test**: Runtime provenance review for new V2 runs shows prompt/profile pins, provider route metadata, gateway operation identity, retry/breaker summaries, latency, usage availability, and safe summaries together; pre-V2 records show metadata unavailable without backfill rewrites.

### Tests for User Story 9 V2

- [ ] T165 [P] [US9] Write integration tests proving runtime provenance shows prompt/profile pins with provider gateway metadata for newly accepted runs and dynamic first-use selections without rewriting historical runs in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/model_skill_config/test_prompt_profile_gateway_provenance.py`
- [ ] T166 [P] [US9] Write docs tests covering Spec 012 V2 reviewer docs, testing instructions, PR notes, README links, exact verification commands, and no-destructive-migration guidance in `/Users/scottcornell/src/my-projects/multi-agent/tests/docs/test_prompt_runtime_profiles_v2_docs.py`
- [ ] T167 [P] [US9] Write browser/admin regression tests proving existing Spec 012 prompt/profile workflows still pass with V2 provenance available for new runs and metadata-unavailable states for historical runs in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_prompt_runtime_v2_browser_regression.py`

### Implementation for User Story 9 V2

- [ ] T168 [US9] Implement runtime provenance projection that links immutable prompt/profile pins with gateway operation and provider attempt metadata without historical backfill rewrites in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/runtime/versioning.py` and `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/config/provenance.py`
- [ ] T169 [US9] Implement admin run inspection display for combined prompt/profile/provider provenance, retry/breaker summaries, usage availability, normalized outcomes, and pre-V2 metadata-unavailable states in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/routers/admin_run_inspection.py` and `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/runs/detail.html`
- [ ] T170 [US9] Update feature documentation with V2 ModelGateway runtime execution, worker bootstrap wiring, idempotency/recovery, retry/breaker behavior, probe limits, guardrails, safe audit, and provenance review in `/Users/scottcornell/src/my-projects/multi-agent/docs/prompt-runtime-profiles.md`
- [ ] T171 [US9] Update reviewer testing instructions with exact V2 verification steps for runtime gateway execution, test bench parity, provider probe throttling, catalog recovery, direct-call guardrails, browser regressions, Alembic validation, and coverage in `/Users/scottcornell/src/my-projects/multi-agent/docs/prompt-runtime-profiles-testing.md`
- [ ] T172 [US9] Update PR notes with V2 scope, preservation of completed Spec 012 behavior, additive migration/index rationale, ModelGateway-only runtime proof, safe audit proof, known risks, and rollback/retirement guidance in `/Users/scottcornell/src/my-projects/multi-agent/docs/prompt-runtime-profiles-pr-notes.md`
- [ ] T173 [US9] Update README sections with Spec 012 V2 runtime gateway verification links and reviewer entry points in `/Users/scottcornell/src/my-projects/multi-agent/README.md`

**Checkpoint**: V2 reviewer evidence ties prompt/profile governance to provider gateway execution without rewriting old provenance or weakening completed Spec 012 flows.

---

## Final Phase V2: Validation & Regression Evidence

**Purpose**: Validate both completed Spec 012 behavior and V2 gateway hardening end to end.

- [ ] T174 [P] Run `uv run ruff check .`, resolve V2 lint issues, and record gateway-hardening evidence in `/Users/scottcornell/src/my-projects/multi-agent/docs/prompt-runtime-profiles-testing.md`
- [ ] T175 [P] Run `uv run ruff format --check .`, resolve V2 formatting drift, and record evidence in `/Users/scottcornell/src/my-projects/multi-agent/docs/prompt-runtime-profiles-testing.md`
- [ ] T176 [P] Run `uv run mypy src`, resolve V2 typing issues, and record evidence in `/Users/scottcornell/src/my-projects/multi-agent/docs/prompt-runtime-profiles-testing.md`
- [ ] T177 Run Alembic upgrade and downgrade validation for Spec 012 V1 and additive V2 gateway migrations, confirming no destructive rewrites or historical provenance backfills, and record evidence in `/Users/scottcornell/src/my-projects/multi-agent/docs/prompt-runtime-profiles-testing.md`
- [ ] T178 Run full pytest with coverage >=90 percent, including V1 Spec 012 regression tests and V2 gateway acceptance tests, and record evidence in `/Users/scottcornell/src/my-projects/multi-agent/docs/prompt-runtime-profiles-testing.md`
- [ ] T179 Run browser/admin regression flows for existing Spec 012 prompt library, runtime profile, workflow validation, model-skill prompt reference, tenant grant, immutable versioning, retirement, audit, and docs workflows, then record evidence in `/Users/scottcornell/src/my-projects/multi-agent/docs/prompt-runtime-profiles-pr-notes.md`
- [ ] T180 Run V2 acceptance proving profile-governed runtime execution and profile test bench model calls use `ModelGateway` end to end with prompt/profile pins, provider provenance, retry/breaker summaries, idempotency, and safe audit evidence in `/Users/scottcornell/src/my-projects/multi-agent/docs/prompt-runtime-profiles-pr-notes.md`

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
- **Polish**: Depends on all desired V1 user stories being complete.
- **V2 Foundational Gateway Wiring (Phase 8)**: Depends on Spec 011 gateway primitives, existing Spec 012 prompt/profile persistence, and the current V1 task state; it is additive and must not rewrite completed V1 behavior.
- **User Story 6 V2 (Phase 9)**: Depends on Phase 8 plus run acceptance/profile pinning integration points from US2/US3, especially T051 and T072.
- **User Story 7 V2 (Phase 10)**: Depends on Phase 8; gateway invocation recovery depends on US6 context propagation, while probe and catalog recovery can proceed after V2 operation persistence exists.
- **User Story 8 V2 (Phase 11)**: Depends on Phase 8 and can proceed in parallel with late US7 work where files do not overlap; direct-call guardrails depend on the US6 gateway path being defined.
- **User Story 9 V2 (Phase 12)**: Depends on US6-US8 V2 behavior and preserves historical run provenance without backfill rewrites.
- **V2 Validation**: Depends on completed desired V1 tasks and all V2 phases being complete.

### User Story Dependencies

- **US1 (P1)**: Starts after Foundational; no dependency on other user stories.
- **US2 (P2)**: Starts after US1 prompt publication exists.
- **US3 (P3)**: Starts after US1 prompt publication exists; workflow/runtime pinning tasks depend on active prompt/profile service contracts.
- **US4 (P4)**: Starts after API/service contracts for US1-US3 are available; template work can begin from view model contracts.
- **US5 (P5)**: Starts after audit actions and UI/API flows exist; docs placeholders can be drafted earlier but final evidence depends on implementation.
- **US6 V2 (P1)**: Starts after V2 foundational gateway wiring and required prompt/profile pinning contracts; delivers ModelGateway-only runtime/test bench/model-backed validation execution.
- **US7 V2 (P2)**: Starts after V2 operation identity persistence; gateway invocation recovery follows US6, while provider probe and catalog sync recovery can be implemented independently.
- **US8 V2 (P3)**: Starts after V2 foundational wiring; rate-limit/audit work can proceed independently from guardrail refactors until final integration.
- **US9 V2 (P4)**: Starts after gateway attempts and safe summaries are available; docs can draft earlier but final evidence depends on V2 acceptance behavior.

### Within Each User Story

- Write tests first and confirm they fail before implementation.
- Implement domain models/helpers before services.
- Implement repositories before services that persist state.
- Implement services before routers and UI handlers.
- Implement API schemas before routers.
- Implement UI view models before templates.
- Complete each checkpoint before using the story as a dependency for later stories.
- For V2, add or update only additive migrations, nullable/companion provenance fields, and new indexes; do not rewrite historical prompt/profile/run/provider provenance.
- Preserve completed Spec 012 prompt authoring, lifecycle, tenant grant, immutable versioning, retirement, browser UI, workflow validation, model-skill prompt reference, docs, and coverage behavior unless a failing V2 regression test identifies a necessary targeted fix.

---

## Parallel Opportunities

- Phase 1 placeholder files T003-T007 can run in parallel.
- Phase 2 test tasks T008-T014 can run in parallel, then implementation tasks T015-T024 should proceed by dependency order.
- US1 tests T025-T032 can run in parallel; parser, fixture safety, and domain models T033-T035 can run in parallel before validation and service work.
- US2 tests T042-T046 can run in parallel once US1 contracts exist.
- US3 tests T053-T061 can run in parallel; models, validation, and resolution T062-T064 can run in parallel before service and integration tasks.
- US4 tests T074-T079 can run in parallel; prompt and profile template tasks T084-T085 can run in parallel with JavaScript/CSS tasks T087-T088 after view model contracts are known.
- US5 tests T090-T096 can run in parallel; docs and review-note tasks T104-T108 can run in parallel after implementation behavior is stable.
- V2 foundational tests T116-T120 can run in parallel; migration/model/repository tasks T121-T123 should complete before gateway invocation recovery work.
- US6 V2 tests T129-T133 can run in parallel after V2 foundational wiring; implementation tasks T134-T141 should proceed in dependency order from pin accessors to gateway invocation to test bench and validation parity.
- US7 V2 tests T142-T146 can run in parallel; provider probe and catalog sync implementation T151-T152 can proceed after operation persistence while gateway retry/recovery tasks T147-T150 follow US6 context propagation.
- US8 V2 tests T153-T158 can run in parallel; admin probe limit work T159-T160 can proceed independently from direct-call guardrail work T161-T162 after V2 foundational wiring.
- US9 V2 docs tests T166 can start while provenance tests T165 and browser regression tests T167 wait for US6-US8 evidence; documentation tasks T170-T173 can draft early and finalize after acceptance.
- V2 validation tasks T174-T176 can run in parallel after implementation settles; T177-T180 should run in sequence because migration, full coverage, browser regression, and V2 acceptance evidence build on each other.

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

## Parallel Example: V2 Foundational Wiring

```bash
Task: "Write unit tests proving Container exposes gateway dependency factories in /Users/scottcornell/src/my-projects/multi-agent/tests/unit/bootstrap/test_container_model_gateway_factories.py"
Task: "Write unit tests proving WorkerBootstrap exposes gateway-ready dependencies in /Users/scottcornell/src/my-projects/multi-agent/tests/unit/bootstrap/test_worker_gateway_bootstrap.py"
Task: "Write migration tests for additive V2 gateway operation identities in /Users/scottcornell/src/my-projects/multi-agent/tests/integration/db/test_prompt_runtime_profiles_v2_gateway_migration.py"
Task: "Write repository tests for gateway/probe/catalog duplicate suppression and recovery queries in /Users/scottcornell/src/my-projects/multi-agent/tests/unit/db/test_model_provider_operation_repository.py"
```

## Parallel Example: User Story 6 V2

```bash
Task: "Write integration tests proving run acceptance pins prompt/profile versions before model-backed work in /Users/scottcornell/src/my-projects/multi-agent/tests/integration/runtime/test_prompt_profile_gateway_pinning.py"
Task: "Write unit tests proving runtime orchestration calls ModelGateway with complete context in /Users/scottcornell/src/my-projects/multi-agent/tests/unit/runtime/orchestration/test_model_gateway_invocation.py"
Task: "Write integration tests proving profile test bench execution uses the same gateway path in /Users/scottcornell/src/my-projects/multi-agent/tests/integration/runtime/test_profile_test_bench_gateway.py"
Task: "Write contract tests for runtime gateway execution ordering and context in /Users/scottcornell/src/my-projects/multi-agent/tests/contract/test_runtime_gateway_execution_contract.py"
```

## Parallel Example: User Story 8 V2

```bash
Task: "Write admin provider probe limit tests in /Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_model_provider_probe_limits.py"
Task: "Write static ModelGateway-only provider call guardrail tests in /Users/scottcornell/src/my-projects/multi-agent/tests/unit/guardrails/test_model_gateway_only_provider_calls.py"
Task: "Write behavioral ModelGateway guardrail tests in /Users/scottcornell/src/my-projects/multi-agent/tests/integration/runtime/test_model_gateway_guardrails.py"
Task: "Write gateway safe observability leak tests in /Users/scottcornell/src/my-projects/multi-agent/tests/unit/model_providers/test_gateway_safe_observability.py"
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
6. Add V2 foundational container, worker, and additive operation identity persistence.
7. Add US6 V2 ModelGateway-only runtime, test bench, and model-backed validation execution.
8. Add US7 V2 durable gateway/probe/catalog idempotency and recovery.
9. Add US8 V2 provider limits, retry/breaker evidence, safe audit, and direct-call guardrails.
10. Add US9 V2 combined prompt/profile/provider provenance and reviewer documentation.

### Final Validation Commands

```bash
uv sync
uv run alembic upgrade head
uv run alembic downgrade -1
uv run alembic upgrade head
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest tests/unit/model_providers tests/unit/bootstrap tests/unit/runtime tests/unit/reliability
uv run pytest tests/contract
uv run pytest tests/integration/workers tests/integration/runtime tests/integration/api
uv run pytest tests/docs
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
uv run uvicorn multi_agent_platform.api.main:app --reload
uv run python -m multi_agent_platform.workers.main
```

### Browser Validation URLs

```text
http://127.0.0.1:8000/admin/prompt-runtime/prompts
http://127.0.0.1:8000/admin/prompt-runtime/profiles
http://127.0.0.1:8000/admin/prompt-runtime/profiles/resolve
http://127.0.0.1:8000/admin/runs
http://127.0.0.1:8000/admin/model-providers
```

## Notes

- Every task above follows the required `- [ ] T### [P?] [US?] Description with file path` checklist format.
- `[P]` tasks touch distinct files and can run in parallel after their phase prerequisites are satisfied.
- Browser UI tasks are required acceptance scope, not optional polish.
- Tenant admins must be able to use the browser UI for tenant-scoped prompt/profile work; platform admins must be able to use it for platform-scoped assets and per-version tenant grants.
- Platform prompt/profile versions are tenant-visible only through explicit per-version grants.
- Prompt previews, logs, audit records, and rendered pages must never include raw secrets, credential values, provider tokens, unauthorized run content, protected cross-tenant content, or unsafe rendered prompts.
- V2 migrations must be additive only: no destructive migrations, no historical prompt/profile/run/provider provenance rewrites, and no backfills that mutate completed Spec 012 meaning.
- V2 runtime, worker, test bench, and model-backed validation paths must use `ModelGateway`; direct provider SDK or HTTP usage is allowed only in the explicit adapter modules named by the runtime gateway contract.
