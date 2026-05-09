# Tasks: Design Review Domain Foundation

**Input**: Design documents from `specs/060-design-review-domain-foundation/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Required. This backend foundation touches database schema, tenant
authorization, idempotency, immutable evidence, and public admin JSON contracts.

**Organization**: Tasks are grouped by independently testable user stories.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish feature scaffolding, migration slot, and docs placeholders.

- [X] T001 Create design review package files in `src/multi_agent_platform/admin/design_review/__init__.py`, `src/multi_agent_platform/admin/design_review/models.py`, `src/multi_agent_platform/admin/design_review/redaction.py`, and `src/multi_agent_platform/admin/design_review/service.py`
- [X] T002 Create database model and repository placeholders in `src/multi_agent_platform/db/models/design_review.py` and `src/multi_agent_platform/db/repositories/design_review.py`
- [X] T003 Create API schema and router placeholders in `src/multi_agent_platform/api/schemas/design_review.py` and `src/multi_agent_platform/api/routers/admin_design_review.py`
- [X] T004 Create test directories in `tests/unit/admin/design_review/`, `tests/unit/db/`, `tests/contract/`, and `tests/integration/api/`
- [X] T005 Add QA placeholder files `specs/060-design-review-domain-foundation/qa060.md`, `specs/060-design-review-domain-foundation/qa060_ui.md`, `specs/060-design-review-domain-foundation/.env.qa060`, `specs/060-design-review-domain-foundation/qa060_user_guide.md`, and `specs/060-design-review-domain-foundation/pr_notes.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Durable schema, enums, redaction helpers, and app wiring required by all stories.

- [X] T006 Add SQLAlchemy design review models and relationships in `src/multi_agent_platform/db/models/design_review.py`
- [X] T007 Register design review models in `src/multi_agent_platform/db/models/__init__.py`
- [X] T008 Add Alembic migration `alembic/versions/0021_design_review_domain.py` for design review sessions, revisions, rounds, assignments, verdicts, quorum decisions, manual decisions, and handoffs
- [X] T009 Add design review domain enums and dataclasses in `src/multi_agent_platform/admin/design_review/models.py`
- [X] T010 Add redaction and safe-summary validators in `src/multi_agent_platform/admin/design_review/redaction.py`
- [X] T011 Add repository create/get/list scaffolding with tenant filters in `src/multi_agent_platform/db/repositories/design_review.py`
- [X] T012 Add service authorization/idempotency scaffolding in `src/multi_agent_platform/admin/design_review/service.py`
- [X] T013 Wire `admin_design_review_router` into `src/multi_agent_platform/api/main.py`
- [X] T014 [P] Add foundational model and redaction tests in `tests/unit/admin/design_review/test_design_review_models.py` and `tests/unit/admin/design_review/test_design_review_redaction.py`
- [X] T015 [P] Add Alembic upgrade/schema smoke test in `tests/integration/api/test_admin_design_review_api.py`

**Checkpoint**: Foundation ready for independently testable session and evidence stories.

---

## Phase 3: User Story 1 - Create Durable Design Review Sessions (Priority: P1) MVP

**Goal**: Authorized tenant admins can create idempotent sessions with revision 1.

**Independent Test**: API and repository tests create a session, replay the same idempotency key, and verify one session plus one revision exists for the tenant.

### Tests for User Story 1

- [X] T016 [P] [US1] Add contract tests for `DesignReviewSessionCreateRequest` and `DesignReviewSessionResponse` in `tests/contract/test_design_review_contracts.py`
- [X] T017 [P] [US1] Add repository idempotent create-session tests in `tests/unit/db/test_design_review_repository.py`
- [X] T018 [P] [US1] Add service create-session authorization and redaction tests in `tests/unit/admin/design_review/test_design_review_service.py`
- [X] T019 [US1] Add integration tests for `POST /admin/design-reviews/sessions` success, replay, validation, unauthorized, and cross-tenant denial in `tests/integration/api/test_admin_design_review_api.py`

### Implementation for User Story 1

- [X] T020 [US1] Implement session/revision create and replay repository methods in `src/multi_agent_platform/db/repositories/design_review.py`
- [X] T021 [US1] Implement create-session service behavior in `src/multi_agent_platform/admin/design_review/service.py`
- [X] T022 [US1] Implement create-session Pydantic schemas in `src/multi_agent_platform/api/schemas/design_review.py`
- [X] T023 [US1] Implement `POST /admin/design-reviews/sessions` in `src/multi_agent_platform/api/routers/admin_design_review.py`

**Checkpoint**: User Story 1 is fully functional and independently testable.

---

## Phase 4: User Story 2 - Inspect Session, Revision, And Round Evidence (Priority: P2)

**Goal**: Authorized callers can list and inspect safe design review metadata with truthful empty and denied states.

**Independent Test**: Seed sessions and empty tenants, then verify list/detail/revision/round routes return safe live metadata or truthful empty states and fail closed cross-tenant.

### Tests for User Story 2

- [X] T024 [P] [US2] Add contract tests for list/detail/revision/round state schemas in `tests/contract/test_design_review_contracts.py`
- [X] T025 [P] [US2] Add repository tenant-filter and relationship-loading tests in `tests/unit/db/test_design_review_repository.py`
- [X] T026 [P] [US2] Add service list/detail safe projection tests in `tests/unit/admin/design_review/test_design_review_service.py`
- [X] T027 [US2] Add integration tests for `GET /admin/design-reviews/sessions`, `GET /admin/design-reviews/sessions/{session_id}`, `GET /admin/design-reviews/sessions/{session_id}/revisions`, `GET /admin/design-reviews/sessions/{session_id}/rounds`, `GET /admin/design-reviews/sessions/{session_id}/manual-decisions`, and `GET /admin/design-reviews/rounds/{round_id}` in `tests/integration/api/test_admin_design_review_api.py`

### Implementation for User Story 2

- [X] T028 [US2] Implement list/detail/revision/round repository methods in `src/multi_agent_platform/db/repositories/design_review.py`
- [X] T029 [US2] Implement safe projection builders in `src/multi_agent_platform/admin/design_review/service.py`
- [X] T030 [US2] Implement list/detail/revision/round response schemas in `src/multi_agent_platform/api/schemas/design_review.py`
- [X] T031 [US2] Implement list/detail/revision/round/manual-decision GET routes in `src/multi_agent_platform/api/routers/admin_design_review.py`

**Checkpoint**: User Stories 1 and 2 are functional and tenant-safe.

---

## Phase 5: User Story 3 - Record Immutable Review Evidence (Priority: P3)

**Goal**: Services can record assignments, verdicts, quorum decisions, manual decisions, and handoff metadata as safe immutable or append-only evidence.

**Independent Test**: Repository/service tests record evidence and verify immutability, idempotency, tenant filters, safe summaries, digests, and artifact references.

### Tests for User Story 3

- [X] T032 [P] [US3] Add repository tests for assignment, verdict, quorum decision, manual decision, and handoff creation in `tests/unit/db/test_design_review_repository.py`
- [X] T033 [P] [US3] Add service tests for evidence immutability, idempotency, and unsafe-content rejection in `tests/unit/admin/design_review/test_design_review_service.py`
- [X] T034 [P] [US3] Add contract tests for quorum, manual decision, and handoff schemas in `tests/contract/test_design_review_contracts.py`
- [X] T035 [US3] Add integration tests for `POST /admin/design-reviews/sessions/{session_id}/manual-decisions`, `GET /admin/design-reviews/rounds/{round_id}/quorum-decision`, and `GET /admin/design-reviews/sessions/{session_id}/handoff` in `tests/integration/api/test_admin_design_review_api.py`

### Implementation for User Story 3

- [X] T036 [US3] Implement assignment, verdict, quorum decision, manual decision, and handoff repository methods in `src/multi_agent_platform/db/repositories/design_review.py`
- [X] T037 [US3] Implement evidence recording service methods in `src/multi_agent_platform/admin/design_review/service.py`
- [X] T038 [US3] Implement quorum, manual decision, and handoff schemas in `src/multi_agent_platform/api/schemas/design_review.py`
- [X] T039 [US3] Implement manual-decision, quorum-decision, and handoff routes in `src/multi_agent_platform/api/routers/admin_design_review.py`

**Checkpoint**: All backend design review foundation stories are functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: QA, docs, curl coverage, generated evidence, and validation readiness.

- [X] T040 Add QA seed and verifier scripts in `scripts/qa/seed_design_review_qa060.py` and `scripts/qa/verify_design_review_qa060.py`
- [X] T041 Update `curl_testing.md` with design review setup, create-session success, idempotent replay, list/detail, empty state, manual-decision, and cross-tenant denial commands
- [X] T042 Update `specs/_autopilot/scenario-enhancement-roadmap/060-design-review-domain-foundation/validation.yml` if actual routes or QA commands differ from the generated smoke manifest
- [X] T043 Complete QA docs in `specs/060-design-review-domain-foundation/qa060.md`, `specs/060-design-review-domain-foundation/qa060_ui.md`, `specs/060-design-review-domain-foundation/.env.qa060`, `specs/060-design-review-domain-foundation/qa060_user_guide.md`, and `specs/060-design-review-domain-foundation/pr_notes.md`
- [X] T044 Run focused backend validation for design review modules and tests, then fix failures in touched files
- [X] T045 Run QA document validation for `specs/060-design-review-domain-foundation`
- [X] T046 Run `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/scenario-enhancement-roadmap/060-design-review-domain-foundation/validation.yml`
- [X] T047 Run `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/scenario-enhancement-roadmap/060-design-review-domain-foundation/validation.yml --start-processes`
- [X] T048 Run `uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa060-after-spec`

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 has no dependencies.
- Phase 2 depends on Phase 1 and blocks all user stories.
- User Story 1 depends on Phase 2 and is the MVP.
- User Story 2 depends on User Story 1 for persisted session fixtures.
- User Story 3 depends on User Story 1 and can reuse User Story 2 projections.
- Phase 6 depends on all selected user stories.

### Parallel Opportunities

- T014 and T015 can run in parallel after model/migration scaffolding exists.
- T016, T017, and T018 can run in parallel before T020-T023.
- T024, T025, and T026 can run in parallel before T028-T031.
- T032, T033, and T034 can run in parallel before T036-T039.
- QA doc drafting can proceed alongside validation fixes after route contracts stabilize.

## Implementation Strategy

1. Land durable schema and redaction-safe domain primitives.
2. Implement and validate idempotent session creation as the MVP.
3. Add read projections for live session, revision, and round metadata.
4. Add immutable evidence writes for verdict/quorum/manual/handoff paths.
5. Update curl coverage, QA docs, validation manifests, and run all required validation before Spec 061.
