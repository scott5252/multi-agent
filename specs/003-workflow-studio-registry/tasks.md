# Tasks: Admin Workflow Studio And Registry

**Input**: Design documents from `/specs/003-workflow-studio-registry/`
**Prerequisites**: `plan.md` (required), `spec.md` (required), `research.md`,
`data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Test-first tasks are REQUIRED for authoring schemas, optimistic
concurrency, contract compatibility, subworkflow validation, join-policy and
approval-gate validation, publish compilation, version immutability, sharing
grants, admin APIs, and the Web UI field-help modal behavior.

**Organization**: Tasks are grouped by user story to enable independent
implementation, testing, and review.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no direct dependency)
- **[Story]**: Which user story this task belongs to (e.g., `US1`, `US2`,
  `US3`)
- Include exact file paths in every implementation or documentation task

## Constitution-Driven Task Rules

- Include test-first tasks before implementation tasks where practical.
- Include documentation tasks, `README.md` update tasks, quickstart
  validation, PR review guidance, and testing-instruction updates.
- Include explicit tasks for tenant isolation, version pinning, secrets/tool-
  policy hygiene, artifact storage, approval-gate durability metadata,
  contract compatibility, and field-help modal UX because those concerns are
  in scope.
- Include operational validation tasks for observability, publish recovery, and
  coverage evidence because the feature changes admin control-plane behavior.
- Keep tasks dependency-ordered, file-specific, and safe for small, reviewable
  changes.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the workflow-registry scaffolding, dependency updates, and
test fixtures needed before shared implementation begins.

- [X] T001 Create workflow-registry, admin UI, and test scaffolding in `src/multi_agent_platform/admin/workflow_registry/__init__.py`, `src/multi_agent_platform/admin/workflow_registry/service.py`, `src/multi_agent_platform/admin/workflow_registry/validation.py`, `src/multi_agent_platform/admin/workflow_registry/compiler.py`, `src/multi_agent_platform/admin/workflow_registry/sharing.py`, `src/multi_agent_platform/admin/workflow_registry/field_help.py`, `src/multi_agent_platform/api/routers/admin_workflows.py`, `src/multi_agent_platform/api/routers/admin_workflow_ui.py`, `src/multi_agent_platform/api/schemas/workflow_registry.py`, `src/multi_agent_platform/api/schemas/workflow_editor.py`, `src/multi_agent_platform/api/ui/admin_workflows.py`, `src/multi_agent_platform/db/models/workflow_registry.py`, `src/multi_agent_platform/db/repositories/workflow_registry.py`, `src/multi_agent_platform/runtime/workflow_bundle.py`, `src/multi_agent_platform/web_admin/templates/workflows/index.html`, `src/multi_agent_platform/web_admin/templates/workflows/draft_editor.html`, `src/multi_agent_platform/web_admin/templates/workflows/version_detail.html`, `src/multi_agent_platform/web_admin/templates/workflows/components/field_help_modal.html`, `src/multi_agent_platform/web_admin/templates/workflows/components/validation_panel.html`, `src/multi_agent_platform/web_admin/static/workflow_studio.js`, `src/multi_agent_platform/web_admin/static/workflow_studio.css`, `tests/unit/admin/test_workflow_registry_service.py`, `tests/unit/admin/test_validation.py`, `tests/unit/admin/test_compiler.py`, `tests/unit/admin/test_field_help.py`, `tests/unit/api/test_workflow_registry_schemas.py`, `tests/unit/api/test_admin_workflow_ui_models.py`, `tests/unit/db/test_workflow_registry_models.py`, `tests/integration/api/test_admin_workflows_api.py`, `tests/integration/api/test_admin_workflow_ui.py`, `tests/integration/admin/test_publish_compilation.py`, and `tests/contract/test_workflow_registry_contract.py`
- [X] T002 [P] Add embedded admin UI and schema dependency updates in `pyproject.toml` and `uv.lock`
- [X] T003 [P] Extend workflow-registry fixtures and seeded admin contexts in `tests/conftest.py`, `tests/fixtures/config.py`, `tests/fixtures/db.py`, and `tests/fixtures/providers.py`
- [X] T004 [P] Draft admin workflow studio documentation placeholders in `docs/admin-workflow-studio.md`, `README.md`, and `docs/quickstart.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build the shared persistence, container, schema, policy, and
observability foundations that MUST be complete before any user story work
begins.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T005 Add foundational container, settings, and template-serving tests in `tests/unit/bootstrap/test_container.py`, `tests/unit/config/test_settings.py`, and `tests/unit/api/test_dependency_helpers.py`
- [X] T006 [P] Add foundational persistence and editor-schema tests in `tests/unit/db/test_workflow_registry_models.py`, `tests/unit/api/test_workflow_registry_schemas.py`, and `tests/unit/api/test_admin_workflow_ui_models.py`
- [X] T007 Implement workflow-registry persistence models, metadata registration, and Alembic migration in `src/multi_agent_platform/db/models/workflow_registry.py`, `src/multi_agent_platform/db/models/__init__.py`, and `alembic/versions/0003_workflow_registry.py`
- [X] T008 [P] Implement workflow-registry repositories and bundle/artifact helpers in `src/multi_agent_platform/db/repositories/workflow_registry.py`, `src/multi_agent_platform/runtime/workflow_bundle.py`, `src/multi_agent_platform/runtime/versioning.py`, and `src/multi_agent_platform/storage/base.py`
- [X] T009 [P] Implement shared workflow-registry schemas and field-help metadata foundations in `src/multi_agent_platform/api/schemas/workflow_registry.py`, `src/multi_agent_platform/api/schemas/workflow_editor.py`, and `src/multi_agent_platform/admin/workflow_registry/field_help.py`
- [X] T010 [P] Implement container, settings, and admin UI route wiring in `src/multi_agent_platform/config/settings.py`, `src/multi_agent_platform/bootstrap/container.py`, `src/multi_agent_platform/api/main.py`, and `src/multi_agent_platform/api/lifespan.py`
- [X] T011 Implement policy classification, audit scaffolding, and observability baselines for admin workflow routes in `src/multi_agent_platform/auth/policy.py`, `src/multi_agent_platform/audit/models.py`, `src/multi_agent_platform/audit/service.py`, `src/multi_agent_platform/observability/logging.py`, `src/multi_agent_platform/observability/metrics.py`, and `src/multi_agent_platform/observability/tracing.py`

**Checkpoint**: Shared workflow-registry infrastructure is complete; user story
phases can begin.

---

## Phase 3: User Story 1 - Author Workflow Drafts (Priority: P1) 🎯 MVP

**Goal**: Admins can create, edit, review, and safely save workflow drafts
through APIs and an embedded Web UI that explains every input field with
icon-triggered help modals.

**Independent Test**: An authorized admin can create a draft, edit roles,
skills, contracts, join policies, approval gates, and subworkflow references,
save a new revision, reload the draft, open help modals beside each editable
field, and receive a conflict response when attempting a stale save from an
older revision.

### Tests for User Story 1

> Write these tests first and ensure they fail before implementation.

- [X] T012 [P] [US1] Add unit tests for draft document models, field-help metadata, and optimistic concurrency behavior in `tests/unit/admin/test_workflow_registry_service.py`, `tests/unit/admin/test_field_help.py`, `tests/unit/api/test_workflow_registry_schemas.py`, and `tests/unit/api/test_admin_workflow_ui_models.py`
- [X] T013 [P] [US1] Add contract and integration tests for draft create, fetch, save, and registry list APIs in `tests/contract/test_workflow_registry_contract.py` and `tests/integration/api/test_admin_workflows_api.py`
- [X] T014 [US1] Add integration tests for registry rendering, draft editor flows, field-help modal popups, and stale-save conflict UX in `tests/integration/api/test_admin_workflow_ui.py`

### Implementation for User Story 1

- [X] T015 [P] [US1] Implement workflow lineage, draft-head, and immutable revision save services with optimistic concurrency in `src/multi_agent_platform/admin/service.py`, `src/multi_agent_platform/admin/workflow_registry/service.py`, and `src/multi_agent_platform/db/repositories/workflow_registry.py`
- [X] T016 [P] [US1] Implement draft CRUD and editor-metadata APIs plus route authorization in `src/multi_agent_platform/api/routers/admin_workflows.py`, `src/multi_agent_platform/api/schemas/workflow_registry.py`, `src/multi_agent_platform/api/schemas/workflow_editor.py`, `src/multi_agent_platform/auth/policy.py`, and `src/multi_agent_platform/api/main.py`
- [X] T017 [US1] Implement registry list and draft editor UI with field-help modal components in `src/multi_agent_platform/api/routers/admin_workflow_ui.py`, `src/multi_agent_platform/api/ui/admin_workflows.py`, `src/multi_agent_platform/web_admin/templates/workflows/index.html`, `src/multi_agent_platform/web_admin/templates/workflows/draft_editor.html`, `src/multi_agent_platform/web_admin/templates/workflows/components/field_help_modal.html`, `src/multi_agent_platform/web_admin/static/workflow_studio.js`, and `src/multi_agent_platform/web_admin/static/workflow_studio.css`
- [X] T018 [US1] Add tenant-scope guards, draft audit events, and request tracing for authoring flows in `src/multi_agent_platform/tenancy/guards.py`, `src/multi_agent_platform/admin/workflow_registry/service.py`, `src/multi_agent_platform/audit/service.py`, and `src/multi_agent_platform/observability/logging.py`

**Checkpoint**: User Story 1 is functional and independently testable.

---

## Phase 4: User Story 2 - Validate Workflow Designs (Priority: P2)

**Goal**: Admins can validate workflow drafts and receive actionable blocking
and advisory findings for contracts, skills, subworkflow references, join
policies, approval gates, and publish-readiness rules.

**Independent Test**: An admin can run validation on an invalid draft and see
grouped blocking findings for missing or incompatible design elements, then run
validation on a corrected draft and receive a publish-eligible result tied to
the latest revision.

### Tests for User Story 2

> Write these tests first and ensure they fail before implementation.

- [X] T019 [P] [US2] Add unit tests for contract compatibility, exact skill-version checks, subworkflow reference rules, join-policy rules, and approval-gate validation in `tests/unit/admin/test_validation.py`
- [X] T039 [P] [US2] Add unit and contract tests proving workflow drafts and published bundles reject embedded secret values, delegated credential identifiers, and non-reference tool or credential payloads in `tests/unit/admin/test_validation.py`, `tests/unit/api/test_workflow_registry_schemas.py`, `tests/contract/test_workflow_registry_contract.py`, and `tests/integration/api/test_admin_workflows_api.py`
- [X] T020 [P] [US2] Add contract and integration tests for validation endpoint responses and blocking-versus-advisory findings in `tests/contract/test_workflow_registry_contract.py` and `tests/integration/api/test_admin_workflows_api.py`
- [X] T021 [US2] Add integration tests for validation panel rendering, field-level findings, and invalid-draft UX in `tests/integration/api/test_admin_workflow_ui.py`

### Implementation for User Story 2

- [X] T022 [P] [US2] Implement structural and compatibility validation for contracts, roles, and exact skill bindings in `src/multi_agent_platform/admin/workflow_registry/validation.py`, `src/multi_agent_platform/admin/workflow_registry/service.py`, and `src/multi_agent_platform/api/schemas/workflow_registry.py`
- [X] T023 [P] [US2] Implement subworkflow, join-policy, approval-gate, and sharing-grant validation rules in `src/multi_agent_platform/admin/workflow_registry/validation.py`, `src/multi_agent_platform/admin/workflow_registry/sharing.py`, and `src/multi_agent_platform/db/repositories/workflow_registry.py`
- [X] T040 [P] [US2] Implement schema, validation, and publish-compilation guards that allow only approved skill-version and tool-policy references and reject secret-like fields or delegated credential references in `src/multi_agent_platform/api/schemas/workflow_registry.py`, `src/multi_agent_platform/admin/workflow_registry/validation.py`, `src/multi_agent_platform/admin/workflow_registry/compiler.py`, and `src/multi_agent_platform/api/routers/admin_workflows.py`
- [X] T024 [US2] Implement validation APIs and UI feedback surfaces in `src/multi_agent_platform/api/routers/admin_workflows.py`, `src/multi_agent_platform/api/ui/admin_workflows.py`, `src/multi_agent_platform/web_admin/templates/workflows/components/validation_panel.html`, and `src/multi_agent_platform/web_admin/static/workflow_studio.js`
- [X] T025 [US2] Persist validation results and add audit and metrics for validation runs in `src/multi_agent_platform/db/models/workflow_registry.py`, `src/multi_agent_platform/db/repositories/workflow_registry.py`, `src/multi_agent_platform/audit/service.py`, and `src/multi_agent_platform/observability/metrics.py`
- [X] T026 [US2] Enforce publish-readiness guards against stale revisions and superseded validation results in `src/multi_agent_platform/admin/workflow_registry/service.py`, `src/multi_agent_platform/api/routers/admin_workflows.py`, and `src/multi_agent_platform/auth/policy.py`

**Checkpoint**: User Stories 1 and 2 are both independently functional.

---

## Phase 5: User Story 3 - Publish Immutable Version Bundles (Priority: P3)

**Goal**: Admins can publish validated drafts into immutable workflow version
bundles with exact pinned dependencies, inspect version lineage in the registry,
and grant tenant access to platform-scoped reusable assets without mutating the
published bundle.

**Independent Test**: An authorized admin can publish a validated draft, inspect
the immutable version detail and compiled bundle digest, create a successor
draft from the published lineage, and grant a tenant access to a platform-scoped
published version while all stale publish attempts, immutable-edit attempts, and
unauthorized cross-tenant reuse attempts are rejected.

### Tests for User Story 3

> Write these tests first and ensure they fail before implementation.

- [X] T027 [P] [US3] Add unit tests for publish compilation, exact dependency pinning, run-version bundle blueprint generation, and sharing-grant policy in `tests/unit/admin/test_compiler.py`, `tests/unit/admin/test_workflow_registry_service.py`, and `tests/unit/runtime/test_versioning.py`
- [X] T028 [P] [US3] Add contract and integration tests for publish, version detail, sharing-grant, and successor-draft flows in `tests/contract/test_workflow_registry_contract.py`, `tests/integration/api/test_admin_workflows_api.py`, and `tests/integration/admin/test_publish_compilation.py`
- [X] T029 [US3] Add failure-path integration tests for stale validation, immutable version protection, artifact persistence recovery, and cross-tenant reuse rules in `tests/integration/admin/test_publish_compilation.py` and `tests/integration/runtime/test_artifact_storage.py`

### Implementation for User Story 3

- [X] T030 [P] [US3] Implement publish compilation and exact pinning for skills, contracts, subworkflows, join policies, approval metadata, and run-version bundle blueprints in `src/multi_agent_platform/admin/workflow_registry/compiler.py`, `src/multi_agent_platform/runtime/workflow_bundle.py`, and `src/multi_agent_platform/runtime/versioning.py`
- [X] T031 [P] [US3] Implement publish, lineage sequencing, successor-draft creation, and sharing-grant services in `src/multi_agent_platform/admin/service.py`, `src/multi_agent_platform/admin/workflow_registry/service.py`, `src/multi_agent_platform/admin/workflow_registry/sharing.py`, and `src/multi_agent_platform/db/repositories/workflow_registry.py`
- [X] T032 [US3] Implement publish, version-detail, registry-status, and sharing-grant APIs plus version-detail UI in `src/multi_agent_platform/api/routers/admin_workflows.py`, `src/multi_agent_platform/api/routers/admin_workflow_ui.py`, `src/multi_agent_platform/api/ui/admin_workflows.py`, `src/multi_agent_platform/web_admin/templates/workflows/version_detail.html`, `src/multi_agent_platform/web_admin/templates/workflows/index.html`, and `src/multi_agent_platform/web_admin/static/workflow_studio.js`
- [X] T033 [US3] Add publish, registry-status, and sharing audit and observability plus compiled-bundle artifact writes in `src/multi_agent_platform/admin/workflow_registry/service.py`, `src/multi_agent_platform/audit/service.py`, `src/multi_agent_platform/observability/logging.py`, `src/multi_agent_platform/observability/tracing.py`, and `src/multi_agent_platform/storage/base.py`

**Checkpoint**: All user stories are independently functional and publishable.

---

## Final Phase: Polish & Cross-Cutting Concerns

**Purpose**: Finish documentation, review guidance, CI, and validation work
that spans multiple stories.

- [X] T034 [P] Update workflow studio documentation and operator guidance in `docs/admin-workflow-studio.md`, `docs/quickstart.md`, and `docs/foundation-runbook.md`
- [X] T035 Update repository README and feature quickstart usage and testing instructions in `README.md` and `specs/003-workflow-studio-registry/quickstart.md`
- [X] T036 [P] Update PR review guidance and required evidence for workflow-registry changes in `.github/pull_request_template.md` and `docs/admin-workflow-studio.md`
- [X] T037 [P] Update CI and contract-validation guidance for workflow-registry API and UI coverage in `.github/workflows/ci.yml`, `specs/003-workflow-studio-registry/contracts/workflow-registry.openapi.yaml`, and `specs/003-workflow-studio-registry/contracts/admin-workflow-ui.md`
- [X] T038 Record coverage, timed quickstart validation, latency evidence for draft load or list, draft save, validation, publish, and registry detail retrieval, sampled validation-message clarity review for blocked drafts, manual UI verification, and security-review outcomes in `specs/003-workflow-studio-registry/quickstart.md`, `docs/admin-workflow-studio.md`, and `README.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1: Setup**: No dependencies
- **Phase 2: Foundational**: Depends on Phase 1 and blocks all user stories
- **Phase 3: US1**: Depends on Phase 2
- **Phase 4: US2**: Depends on US1 because validation extends the draft
  schemas, repository models, editor UI, and route set created for authoring
- **Phase 5: US3**: Depends on US2 because publish relies on the validation
  result model, exact compatibility checks, and the draft authoring flows from
  US1
- **Final Phase**: Depends on all targeted user stories being complete

### Within Each User Story

- Tests MUST be written and failing before implementation where practical
- Persistence and schemas come before services
- Services come before API and UI route wiring
- API behavior comes before UI feedback and cross-system observability
- Story-specific docs, audit signals, and validation evidence are required
  before story completion

### Parallel Opportunities

- **Setup**: `T002`, `T003`, and `T004` can run in parallel after `T001`
- **Foundational**: `T006`, `T008`, `T009`, and `T010` can run in parallel
  after `T005`; `T011` follows once route wiring and base models exist
- **US1**: `T012` and `T013` can run in parallel before `T014`; `T015` and
  `T016` can run in parallel before `T017`
- **US2**: `T019` and `T020` can run in parallel before `T021`; `T022` and
  `T023` can run in parallel before `T024`
- **US3**: `T027` and `T028` can run in parallel before `T029`; `T030` and
  `T031` can run in parallel before `T032`
- **Final Phase**: `T034`, `T036`, and `T037` can run in parallel before
  `T035` and `T038`

---

## Implementation Strategy

### MVP First

1. Complete Phase 1
2. Complete Phase 2
3. Complete User Story 1
4. Validate draft authoring, optimistic concurrency, and field-help modal UX
5. Stop and demo before expanding into validation and publish flows

### Incremental Delivery

1. Finish Setup and Foundational work
2. Deliver User Story 1 and validate authoring independently
3. Deliver User Story 2 and validate compatibility and publish-readiness checks
4. Deliver User Story 3 and validate immutable publish and sharing behavior
5. Finish documentation, CI, coverage, and security-validation updates

## Notes

- `[P]` markers are used only where tasks touch different files or isolated
  modules and do not depend on incomplete work in the same files.
- User stories remain sequential because each later story extends the same
  workflow-registry document model, repository, service, and route surfaces.
- The admin Web UI is part of the feature scope, so field-help modal behavior
  and rendered-page tests are first-class deliverables rather than polish-only
  extras.
