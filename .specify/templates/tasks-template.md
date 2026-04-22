---

description: "Task list template for feature implementation"
---

# Tasks: [FEATURE NAME]

**Input**: Design documents from `/specs/[###-feature-name]/`
**Prerequisites**: plan.md (required), spec.md (required), research.md,
data-model.md, contracts/, quickstart.md

**Tests**: Test-first tasks are REQUIRED where behavior can be automated. If a
test is intentionally omitted, the task list MUST reference the approved plan
justification.

**Organization**: Tasks are grouped by user story to enable independent
implementation, testing, and review.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no direct dependency)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in every implementation or documentation task

## Constitution-Driven Task Rules

- Include test-first tasks before implementation tasks where practical.
- Include documentation tasks, `README.md` update tasks, and quickstart
  validation tasks.
- Include explicit tasks for tenant isolation, version pinning, secret/tool
  policy, artifact storage, and approval/resume behavior when those concerns are
  in scope.
- Include operational validation tasks for runtime-affecting changes, including
  observability, replay, quota, or recovery validation where relevant.
- Keep tasks dependency-ordered, file-specific, and safe for small, reviewable
  changes.

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Platform services**: `apps/`, `services/`, `workers/`, `packages/`
- Adjust the examples below to match `plan.md`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and workflow scaffolding

- [ ] T001 Create feature directories and stub files per plan in [exact paths]
- [ ] T002 Configure or extend test tooling in [exact paths]
- [ ] T003 [P] Add or update linting, typing, and coverage configuration in [exact paths]
- [ ] T004 [P] Draft documentation stubs for spec-required README or quickstart changes in [exact paths]

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before any user story
implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Implement tenant context propagation or validation in [exact paths]
- [ ] T006 [P] Implement auth, authorization, or policy plumbing in [exact paths]
- [ ] T007 [P] Implement version-bundle, contract, or schema foundations in [exact paths]
- [ ] T008 [P] Implement secret-management, tool-policy, or egress controls in [exact paths]
- [ ] T009 [P] Implement artifact metadata or storage abstractions in [exact paths]
- [ ] T010 Implement observability baselines in [exact paths]
- [ ] T011 Implement workflow wait-state, recovery, or approval primitives in [exact paths] if in scope

**Checkpoint**: Foundational work complete; user story phases can now proceed

---

## Phase 3: User Story 1 - [Title] (Priority: P1) 🎯 MVP

**Goal**: [Brief description of the outcome]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 1 (REQUIRED where practical)

> Write these tests first and ensure they fail before implementation.

- [ ] T012 [P] [US1] Add unit tests for [behavior] in [exact path]
- [ ] T013 [P] [US1] Add contract or integration tests for [flow] in [exact path]
- [ ] T014 [US1] Add failure-recovery, tenant, or auth edge-case tests for [flow] in [exact path] when relevant

### Implementation for User Story 1

- [ ] T015 [P] [US1] Create or update data models in [exact path]
- [ ] T016 [P] [US1] Create or update services in [exact path]
- [ ] T017 [US1] Implement API, worker, or UI flow in [exact path]
- [ ] T018 [US1] Add observability, audit, or lineage handling in [exact path]
- [ ] T019 [US1] Validate documentation or user-facing behavior in [exact path]

**Checkpoint**: User Story 1 is functional and independently testable

---

## Phase 4: User Story 2 - [Title] (Priority: P2)

**Goal**: [Brief description of the outcome]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 2 (REQUIRED where practical)

- [ ] T020 [P] [US2] Add unit tests for [behavior] in [exact path]
- [ ] T021 [P] [US2] Add contract or integration tests for [flow] in [exact path]

### Implementation for User Story 2

- [ ] T022 [P] [US2] Create or update data models in [exact path]
- [ ] T023 [P] [US2] Create or update services in [exact path]
- [ ] T024 [US2] Implement API, worker, or UI flow in [exact path]
- [ ] T025 [US2] Add observability, audit, or lineage handling in [exact path]

**Checkpoint**: User Stories 1 and 2 both work independently

---

## Phase 5: User Story 3 - [Title] (Priority: P3)

**Goal**: [Brief description of the outcome]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 3 (REQUIRED where practical)

- [ ] T026 [P] [US3] Add unit tests for [behavior] in [exact path]
- [ ] T027 [P] [US3] Add contract or integration tests for [flow] in [exact path]

### Implementation for User Story 3

- [ ] T028 [P] [US3] Create or update data models in [exact path]
- [ ] T029 [P] [US3] Create or update services in [exact path]
- [ ] T030 [US3] Implement API, worker, or UI flow in [exact path]

**Checkpoint**: All user stories are independently functional

---

[Add more user story phases as needed, following the same pattern]

---

## Final Phase: Polish & Cross-Cutting Concerns

**Purpose**: Finish quality gates that affect multiple stories

- [ ] TXXX [P] Update repository docs in [exact paths]
- [ ] TXXX Update `README.md` in [exact path]
- [ ] TXXX Validate or update quickstart instructions in [exact path]
- [ ] TXXX Run coverage validation and record evidence for the >= 90% target
- [ ] TXXX Run operational validation for observability, recovery, quotas, or replay behavior
- [ ] TXXX Close security review or threat-model follow-ups in [exact paths]

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user
  stories
- **User Stories (Phase 3+)**: Depend on Foundational completion
- **Final Phase**: Depends on all targeted user stories being complete

### Within Each User Story

- Tests MUST be written and failing before implementation where practical
- Data and contracts before services
- Services before endpoints, workers, or UI integrations
- Core implementation before cross-system integration
- Story-specific docs and observability updates before story completion

### Parallel Opportunities

- Only tasks marked `[P]` may run in parallel
- Parallel tasks MUST touch different files or isolated modules
- User stories may run in parallel only after Foundational work is complete and
  only when the plan identifies the file ownership boundaries

---

## Implementation Strategy

### MVP First

1. Complete Setup
2. Complete Foundational work
3. Complete User Story 1
4. Validate User Story 1 independently
5. Stop and demo before expanding scope

### Incremental Delivery

1. Finish Setup + Foundational work
2. Deliver User Story 1 and validate it
3. Deliver User Story 2 and validate it
4. Deliver User Story 3 and validate it
5. Finish documentation, coverage, security, and operational validation

## Notes

- `[P]` tasks must be safe to parallelize
- `[Story]` labels maintain traceability from task to spec
- Every task list must be immediately actionable without extra interpretation
- Avoid vague tasks, overlapping file ownership, and undocumented scope changes
