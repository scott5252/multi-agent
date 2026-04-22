# Tasks: Platform Foundation

**Input**: Design documents from `/specs/001-platform-foundation/`
**Prerequisites**: `plan.md` (required), `spec.md` (required), `research.md`,
`data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Test-first tasks are REQUIRED where behavior can be automated.
Documentation-only tasks rely on the approved plan's review-evidence and
operational-validation requirements instead of separate doc-specific tests.

**Organization**: Tasks are grouped by user story to enable independent
implementation, testing, and review.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no direct dependency)
- **[Story]**: Which user story this task belongs to (e.g., `US1`, `US2`,
  `US3`)
- Include exact file paths in every implementation or documentation task

## Constitution-Driven Task Rules

- Include test-first tasks before implementation tasks where practical.
- Include documentation tasks, `README.md` update tasks, and quickstart
  validation tasks.
- Include explicit tasks for tenant isolation, version pinning, secret/tool
  policy, and artifact storage because those concerns are in scope.
- Include operational validation tasks for runtime-affecting changes, including
  observability, recovery, and quota-aware tenant validation where relevant.
- Keep tasks dependency-ordered, file-specific, and safe for small, reviewable
  changes.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the repository scaffolding and shared tooling needed before
any foundation behavior is implemented.

- [X] T001 Create the package skeleton in `src/multi_agent_platform/__init__.py`, `src/multi_agent_platform/api/__init__.py`, `src/multi_agent_platform/admin/__init__.py`, `src/multi_agent_platform/audit/__init__.py`, `src/multi_agent_platform/auth/__init__.py`, `src/multi_agent_platform/bootstrap/__init__.py`, `src/multi_agent_platform/config/__init__.py`, `src/multi_agent_platform/db/__init__.py`, `src/multi_agent_platform/db/models/__init__.py`, `src/multi_agent_platform/db/repositories/__init__.py`, `src/multi_agent_platform/memory/__init__.py`, `src/multi_agent_platform/observability/__init__.py`, `src/multi_agent_platform/runtime/__init__.py`, `src/multi_agent_platform/runtime/health/__init__.py`, `src/multi_agent_platform/runtime/queue/__init__.py`, `src/multi_agent_platform/secrets/__init__.py`, `src/multi_agent_platform/secrets/providers/__init__.py`, `src/multi_agent_platform/storage/__init__.py`, `src/multi_agent_platform/storage/providers/__init__.py`, `src/multi_agent_platform/tenancy/__init__.py`, and `src/multi_agent_platform/workers/__init__.py`
- [X] T002 Configure the Python 3.12 project, dependency groups, Ruff, mypy, pytest, and coverage settings in `pyproject.toml` and `.python-version`
- [X] T003 [P] Create local environment and Docker Compose scaffolding in `.env.example` and `compose.yaml`
- [X] T004 [P] Create Alembic bootstrap scaffolding in `alembic.ini`, `alembic/env.py`, and `alembic/script.py.mako`
- [X] T005 [P] Create shared pytest fixture scaffolding in `tests/conftest.py`, `tests/fixtures/config.py`, `tests/fixtures/db.py`, and `tests/fixtures/providers.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build the shared infrastructure that every story depends on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T006 Add unit tests for settings parsing and container wiring in `tests/unit/config/test_settings.py` and `tests/unit/bootstrap/test_container.py`
- [X] T007 [P] Add unit tests for async database session management and model invariants in `tests/unit/db/test_session.py` and `tests/unit/db/test_models.py`
- [X] T008 [P] Add unit tests for tenant guards, secret providers, artifact providers, and version-bundle boundaries in `tests/unit/tenancy/test_context.py`, `tests/unit/tenancy/test_guards.py`, `tests/unit/secrets/test_providers.py`, `tests/unit/storage/test_providers.py`, and `tests/unit/runtime/test_versioning.py`
- [X] T009 [P] Add integration tests for migration bootstrap and queue repository startup in `tests/integration/db/test_migrations.py` and `tests/integration/runtime/test_queue_repository.py`
- [X] T045 [P] Add unit and integration tests for the production secret-manager adapter in `tests/unit/secrets/test_secret_manager.py` and `tests/integration/secrets/test_secret_manager_adapter.py`
- [X] T047 [P] Add integration tests for Alembic upgrade, downgrade, and rollback validation in `tests/integration/db/test_migration_rollback.py`
- [X] T010 Implement shared settings, process profiles, and principal models in `src/multi_agent_platform/config/settings.py` and `src/multi_agent_platform/auth/principal.py`
- [X] T011 Implement dependency-injection container and worker bootstrap wiring in `src/multi_agent_platform/bootstrap/container.py` and `src/multi_agent_platform/bootstrap/worker.py`
- [X] T012 Implement SQLAlchemy base, async session management, and metadata registration in `src/multi_agent_platform/db/base.py`, `src/multi_agent_platform/db/session.py`, and `src/multi_agent_platform/db/models/__init__.py`
- [X] T013 [P] Implement tenant, queue, artifact, secret-reference, and audit models in `src/multi_agent_platform/db/models/tenant.py`, `src/multi_agent_platform/db/models/queue.py`, `src/multi_agent_platform/db/models/artifact.py`, `src/multi_agent_platform/db/models/secret_reference.py`, and `src/multi_agent_platform/db/models/audit.py`
- [X] T014 [P] Implement fail-closed tenant scope propagation and guards in `src/multi_agent_platform/tenancy/context.py`, `src/multi_agent_platform/tenancy/middleware.py`, `src/multi_agent_platform/tenancy/guards.py`, and `src/multi_agent_platform/api/deps.py`
- [X] T015 [P] Implement the shared secret-provider abstraction and local/test stand-ins in `src/multi_agent_platform/secrets/base.py`, `src/multi_agent_platform/secrets/providers/env.py`, and `src/multi_agent_platform/secrets/providers/static.py`
- [X] T046 [P] Implement the production secret-manager provider and wiring in `src/multi_agent_platform/secrets/providers/secret_manager.py`, `src/multi_agent_platform/config/settings.py`, and `src/multi_agent_platform/bootstrap/container.py`
- [X] T016 [P] Implement the artifact-storage abstraction and filesystem/S3 providers in `src/multi_agent_platform/storage/base.py`, `src/multi_agent_platform/storage/providers/filesystem.py`, and `src/multi_agent_platform/storage/providers/s3.py`
- [X] T017 [P] Implement queue models, queue repository bootstrap, and the version-bundle boundary in `src/multi_agent_platform/runtime/queue/models.py`, `src/multi_agent_platform/db/repositories/queue.py`, and `src/multi_agent_platform/runtime/versioning.py`
- [X] T018 Implement observability and audit baselines in `src/multi_agent_platform/observability/logging.py`, `src/multi_agent_platform/observability/metrics.py`, `src/multi_agent_platform/observability/tracing.py`, `src/multi_agent_platform/audit/models.py`, and `src/multi_agent_platform/audit/service.py`
- [X] T019 Implement metadata wiring and the initial schema revision in `src/multi_agent_platform/db/base.py`, `alembic/env.py`, and `alembic/versions/0001_platform_foundation.py`

**Checkpoint**: Foundational work is complete; user story phases can begin.

---

## Phase 3: User Story 1 - Bootstrap The Foundation (Priority: P1) 🎯 MVP

**Goal**: Boot the API service, background worker, and migration-backed
operational endpoints from a clean checkout.

**Independent Test**: Starting from a fresh checkout, a contributor can follow
`README.md` and `docs/quickstart.md`, run migrations, launch the API and
worker, and verify `GET /health/live`, `GET /health/ready`, `GET /version`, and
`GET /dependencies`.

### Tests for User Story 1

> Write these tests first and ensure they fail before implementation.

- [X] T020 [P] [US1] Add unit tests for readiness aggregation and health checks in `tests/unit/runtime/health/test_service.py` and `tests/unit/runtime/health/test_checks.py`
- [X] T021 [P] [US1] Add contract and integration tests for the operational API in `tests/contract/test_ops_api_contract.py` and `tests/integration/api/test_ops_endpoints.py`
- [X] T022 [US1] Add failure-recovery tests for missing configuration, stale migrations, and worker dependency outages in `tests/integration/api/test_readiness_failures.py` and `tests/integration/workers/test_worker_bootstrap.py`

### Implementation for User Story 1

- [X] T023 [P] [US1] Implement operational response schemas and health models in `src/multi_agent_platform/api/schemas/ops.py` and `src/multi_agent_platform/runtime/health/models.py`
- [X] T024 [P] [US1] Implement dependency checks and readiness services in `src/multi_agent_platform/runtime/health/checks.py` and `src/multi_agent_platform/runtime/health/service.py`
- [X] T025 [US1] Implement API lifespan, router registration, and operational endpoints in `src/multi_agent_platform/api/lifespan.py`, `src/multi_agent_platform/api/routers/ops.py`, and `src/multi_agent_platform/api/main.py`
- [X] T026 [US1] Implement the worker entrypoint and queue polling loop in `src/multi_agent_platform/workers/main.py` and `src/multi_agent_platform/workers/loops.py`
- [X] T027 [US1] Wire trace IDs, scope metadata, and audit events into API and worker startup flows in `src/multi_agent_platform/api/main.py`, `src/multi_agent_platform/workers/main.py`, and `src/multi_agent_platform/audit/service.py`

**Checkpoint**: User Story 1 is functional and independently testable.

---

## Phase 4: User Story 2 - Build Safely On Shared Platform Primitives (Priority: P2)

**Goal**: Provide reusable tenant-aware primitives for configuration, queues,
secrets, artifacts, and test harness usage.

**Independent Test**: A feature team can add a small tenant-aware component
using the shared container, tenant guards, provider abstractions, and fixtures
without introducing new bootstrap or storage patterns.

### Tests for User Story 2

> Write these tests first and ensure they fail before implementation.

- [X] T028 [P] [US2] Add unit tests for tenant-aware queue services and tenant-limit policy behavior in `tests/unit/runtime/queue/test_service.py` and `tests/unit/admin/test_tenant_policies.py`
- [X] T029 [P] [US2] Add unit tests for dependency overrides and provider selection behavior in `tests/unit/api/test_dependencies.py` and `tests/unit/bootstrap/test_provider_selection.py`
- [X] T030 [US2] Add integration tests for tenant-scoped queue, artifact, and provider-backed fixture flows in `tests/integration/runtime/test_tenant_scope_flows.py` and `tests/integration/runtime/test_artifact_storage.py`

### Implementation for User Story 2

- [X] T031 [P] [US2] Implement the tenant-limit policy repository and admin service boundary in `src/multi_agent_platform/db/repositories/tenant_limits.py` and `src/multi_agent_platform/admin/service.py`
- [X] T032 [P] [US2] Implement queue-service orchestration and lease lifecycle helpers in `src/multi_agent_platform/runtime/queue/service.py` and `src/multi_agent_platform/db/repositories/queue.py`
- [X] T033 [P] [US2] Implement artifact and audit repositories with tenant-aware metadata handling in `src/multi_agent_platform/db/repositories/artifact.py`, `src/multi_agent_platform/db/repositories/audit.py`, and `src/multi_agent_platform/audit/models.py`
- [X] T034 [P] [US2] Implement provider selection and dependency wiring for secrets, storage, and explicit system scope in `src/multi_agent_platform/bootstrap/container.py`, `src/multi_agent_platform/bootstrap/worker.py`, and `src/multi_agent_platform/api/deps.py`
- [X] T035 [US2] Expand the shared pytest fixtures for tenant context, providers, and database setup in `tests/conftest.py`, `tests/fixtures/config.py`, `tests/fixtures/db.py`, and `tests/fixtures/providers.py`

**Checkpoint**: User Stories 1 and 2 work independently and share the same
tenant, secret, artifact, and queueing primitives.

---

## Phase 5: User Story 3 - Operate And Review The Foundation With Confidence (Priority: P3)

**Goal**: Give operators and reviewers clear quality gates, smoke workflows,
testing instructions, and review evidence.

**Independent Test**: A reviewer can run the documented validation workflow,
inspect CI outputs, and use the runbook and PR checklist to determine whether
the foundation is ready for follow-on work.

### Tests for User Story 3

> Write these tests first and ensure they fail before implementation.

- [X] T036 [P] [US3] Add unit tests for redacted logging and dependency-status rendering in `tests/unit/observability/test_logging.py` and `tests/unit/runtime/health/test_dependency_status.py`
- [X] T037 [P] [US3] Add integration tests for the shared validation workflow and CI entrypoints in `tests/integration/ops/test_quality_workflow.py` and `tests/integration/ops/test_local_bootstrap.py`
- [X] T049 [P] [US3] Add operational performance smoke tests for endpoint latency and readiness timing in `tests/integration/ops/test_operational_performance.py`

### Implementation for User Story 3

- [X] T038 [P] [US3] Implement local validation scripts for lint, typing, tests, migrations, and health checks in `scripts/check.sh` and `scripts/smoke_foundation.sh`
- [X] T039 [P] [US3] Implement CI quality gates and >=90 percent coverage enforcement in `.github/workflows/ci.yml` and `pyproject.toml`
- [X] T040 [P] [US3] Add the PR review checklist and foundation runbook in `.github/pull_request_template.md` and `docs/foundation-runbook.md`
- [X] T041 [US3] Update repository setup, testing instructions, and troubleshooting guidance in `README.md` and `docs/quickstart.md`
- [X] T050 [US3] Capture readiness and operational endpoint timing evidence in `scripts/smoke_foundation.sh` and `.github/workflows/ci.yml`
- [X] T048 [US3] Document controlled recovery expectations for shared and production environments in `docs/foundation-runbook.md` and `docs/quickstart.md`

**Checkpoint**: All three user stories are independently functional and
review-ready.

---

## Final Phase: Polish & Cross-Cutting Concerns

**Purpose**: Finish validation, documentation sync, and security review work
that spans multiple stories.

- [X] T042 [P] Reconcile implementation docs with the feature contract and quickstart in `README.md`, `docs/quickstart.md`, `docs/foundation-runbook.md`, and `specs/001-platform-foundation/contracts/ops-api.openapi.yaml`
- [X] T043 Run the full operational validation workflow against `compose.yaml`, `scripts/check.sh`, `scripts/smoke_foundation.sh`, and `.github/workflows/ci.yml`
- [X] T044 Close the tenant-isolation, secret-redaction, and migration-recovery review notes in `docs/foundation-runbook.md` and `.github/pull_request_template.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1: Setup**: No dependencies
- **Phase 2: Foundational**: Depends on Phase 1 and blocks all user stories
- **Phase 3: US1**: Depends on Phase 2
- **Phase 4: US2**: Depends on Phase 2 and can run in parallel with US1 after foundational completion
- **Phase 5: US3**: Depends on US1 for runnable operational flows and should finish after US2 so docs and review guidance reflect the shared primitives
- **Final Phase**: Depends on all targeted user stories being complete

### Within Each User Story

- Tests MUST be written and failing before implementation where practical
- Schemas, models, and contracts come before services
- Services and repositories come before API or worker wiring
- Observability and audit hooks are required before a story is considered done
- Story-specific docs and validation evidence are required before completion

### Parallel Opportunities

- **Setup**: `T003`, `T004`, and `T005` can run in parallel after `T001` and `T002`
- **Foundational**: `T007`, `T008`, `T009`, `T045`, and `T047` can run in parallel; after `T012`, `T013` through `T017` plus `T046` can be split by module ownership
- **US1**: `T020` and `T021` can run in parallel, then `T023` and `T024` can run in parallel before `T025`
- **US2**: `T028` and `T029` can run in parallel, then `T031` through `T034` can be split across admin, queue, repository, and DI boundaries
- **US3**: `T036`, `T037`, and `T049` can run in parallel, then `T038`, `T039`, and `T040` can proceed independently before `T041`, `T048`, and `T050`

---

## Implementation Strategy

### MVP First

1. Complete Phase 1
2. Complete Phase 2
3. Complete User Story 1
4. Validate the API, worker, migration flow, and operational endpoints
5. Stop and demo before expanding to shared primitive hardening and reviewer tooling

### Incremental Delivery

1. Finish Setup and Foundational work
2. Deliver User Story 1 and validate the baseline platform bootstrap
3. Deliver User Story 2 and validate shared tenant, secret, artifact, and queue primitives
4. Deliver User Story 3 and validate CI, docs, and operator review flows
5. Finish the final validation and security-review tasks

## Notes

- No explicit approval or pause-resume implementation tasks are included because the approved plan marks those behaviors as out of scope for this foundation feature.
- Version-pinning work in this feature is limited to the `src/multi_agent_platform/runtime/versioning.py` boundary and related tests so later workflow execution can pin immutable bundles without reshaping the foundation.
- Documentation-only tasks are verified through `T037`, `T041`, `T042`, and `T043` rather than separate doc-specific automated tests.
