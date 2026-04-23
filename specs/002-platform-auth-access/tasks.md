# Tasks: Platform Authentication And Authorization

**Input**: Design documents from `/specs/002-platform-auth-access/`
**Prerequisites**: `plan.md` (required), `spec.md` (required), `research.md`,
`data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Test-first tasks are REQUIRED for JWT validation, role enforcement,
dev bypass behavior, configuration errors, protected endpoint behavior,
tenant-context extraction, delegated-credential boundaries, and support-override
approval flows.

**Organization**: Tasks are grouped by user story to enable independent
implementation, testing, and review.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no direct dependency)
- **[Story]**: Which user story this task belongs to (e.g., `US1`, `US2`,
  `US3`)
- Include exact file paths in every implementation or documentation task

## Constitution-Driven Task Rules

- Include test-first tasks before implementation tasks where practical.
- Include documentation tasks, `README.md` update tasks, quickstart validation,
  PR review guidance, and test-instruction updates.
- Include explicit tasks for tenant isolation, support-override approval,
  secret/tool policy, delegated-credential boundaries, and observability because
  those concerns are in scope.
- Include operational validation tasks for runtime-affecting changes, including
  config failure behavior, audit evidence, and coverage validation.
- Keep tasks dependency-ordered, file-specific, and safe for small, reviewable
  changes.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the scaffolding and fixture updates needed before shared
auth/access work begins.

- [X] T001 Create auth, admin-access, and test scaffolding in `src/multi_agent_platform/auth/config.py`, `src/multi_agent_platform/auth/claims.py`, `src/multi_agent_platform/auth/dependencies.py`, `src/multi_agent_platform/auth/jwt_validator.py`, `src/multi_agent_platform/auth/local_principals.py`, `src/multi_agent_platform/auth/policy.py`, `src/multi_agent_platform/auth/service.py`, `src/multi_agent_platform/admin/support_overrides.py`, `src/multi_agent_platform/api/routers/auth.py`, `src/multi_agent_platform/api/routers/admin_access.py`, `src/multi_agent_platform/api/schemas/auth.py`, `src/multi_agent_platform/db/models/access_control.py`, `src/multi_agent_platform/db/models/delegated_credential.py`, `src/multi_agent_platform/db/repositories/access_control.py`, `src/multi_agent_platform/db/repositories/delegated_credential.py`, `src/multi_agent_platform/audit/access.py`, `tests/unit/auth/test_jwt_validator.py`, `tests/unit/auth/test_local_principals.py`, `tests/unit/auth/test_policy.py`, `tests/unit/auth/test_service.py`, `tests/unit/api/test_auth_dependencies.py`, `tests/unit/config/test_auth_settings.py`, `tests/unit/db/test_access_control_models.py`, `tests/unit/audit/test_access_audit.py`, `tests/unit/admin/test_support_overrides.py`, `tests/integration/api/test_auth_routes.py`, `tests/integration/api/test_authorization_failures.py`, `tests/integration/api/test_auth_modes.py`, `tests/integration/api/test_readiness_failures.py`, `tests/integration/auth/test_support_overrides.py`, `tests/integration/auth/test_delegated_credentials.py`, `tests/integration/auth/test_platform_secret_boundaries.py`, and `tests/contract/test_access_control_contract.py`
- [X] T002 [P] Extend shared auth fixture scaffolding in `tests/conftest.py`, `tests/fixtures/config.py`, and `tests/fixtures/providers.py`
- [X] T003 [P] Add auth-mode environment placeholders and local example guidance in `.env.example` and `docs/example/fastapi_auth_toggle.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build the shared auth/access foundation that every user story
depends on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T004 Add foundational settings and context tests in `tests/unit/config/test_auth_settings.py`, `tests/unit/auth/test_principal.py`, and `tests/unit/tenancy/test_context.py`
- [X] T005 [P] Add foundational policy and persistence tests in `tests/unit/auth/test_policy.py` and `tests/unit/db/test_access_control_models.py`
- [X] T006 [P] Add foundational audit recorder tests in `tests/unit/audit/test_access_audit.py` and `tests/unit/admin/test_support_overrides.py`
- [X] T007 Implement auth-mode configuration and startup validation in `src/multi_agent_platform/config/settings.py` and `src/multi_agent_platform/auth/config.py`
- [X] T008 [P] Implement principal, claim, and scope-context models in `src/multi_agent_platform/auth/principal.py`, `src/multi_agent_platform/auth/claims.py`, and `src/multi_agent_platform/tenancy/context.py`
- [X] T009 [P] Implement access-control and delegated-credential persistence plus metadata registration in `src/multi_agent_platform/db/models/access_control.py`, `src/multi_agent_platform/db/models/delegated_credential.py`, `src/multi_agent_platform/db/models/__init__.py`, `src/multi_agent_platform/db/repositories/access_control.py`, `src/multi_agent_platform/db/repositories/delegated_credential.py`, `src/multi_agent_platform/db/base.py`, and `alembic/versions/0002_auth_access_control.py`
- [X] T010 [P] Implement shared authorization service and container wiring in `src/multi_agent_platform/auth/service.py`, `src/multi_agent_platform/auth/policy.py`, `src/multi_agent_platform/bootstrap/container.py`, and `src/multi_agent_platform/api/deps.py`
- [X] T011 Implement auth policy versioning and execution-bundle hooks in `src/multi_agent_platform/runtime/versioning.py`, `src/multi_agent_platform/auth/policy.py`, `src/multi_agent_platform/auth/service.py`, and `tests/unit/runtime/test_versioning.py`
- [X] T012 Implement auth dependency readiness checks and `503` propagation in `src/multi_agent_platform/runtime/health/checks.py`, `src/multi_agent_platform/runtime/health/service.py`, `src/multi_agent_platform/api/routers/ops.py`, and `tests/integration/api/test_readiness_failures.py`
- [X] T013 [P] Implement access-decision audit models and recorder wiring in `src/multi_agent_platform/audit/models.py`, `src/multi_agent_platform/audit/service.py`, and `src/multi_agent_platform/audit/access.py`

**Checkpoint**: Shared auth/access infrastructure is complete; user story phases
can begin.

---

## Phase 3: User Story 1 - Secure Tenant Access (Priority: P1) 🎯 MVP

**Goal**: Authenticated tenant users can reach only their allowed protected API
surfaces, with tenant context extracted from validated identity claims and
denied access recorded for audit review.

**Independent Test**: With a valid Auth0-style token, a tenant user can call
`GET /auth/me` and a tenant-scoped protected route for their tenant, while
cross-tenant requests, missing `org_id`, invalid issuer/audience, and missing
permissions return the expected deny response and access-decision audit record.

### Tests for User Story 1

> Write these tests first and ensure they fail before implementation.

- [X] T014 [P] [US1] Add unit tests for JWT validation, claim normalization, and tenant-context extraction in `tests/unit/auth/test_jwt_validator.py` and `tests/unit/api/test_auth_dependencies.py`
- [X] T015 [P] [US1] Add contract and integration tests for `/auth/me`, `/auth/tenant-context/{tenant_id}`, and protected endpoint behavior in `tests/contract/test_access_control_contract.py` and `tests/integration/api/test_auth_routes.py`
- [X] T016 [US1] Add failure-path integration tests for invalid JWTs, missing organization claims, and cross-tenant access denials in `tests/integration/api/test_authorization_failures.py`

### Implementation for User Story 1

- [X] T017 [P] [US1] Implement Auth0 JWT validation and claim normalization in `src/multi_agent_platform/auth/jwt_validator.py` and `src/multi_agent_platform/auth/claims.py`
- [X] T018 [P] [US1] Implement dependency-based principal resolution, role enforcement, and protected-surface checks in `src/multi_agent_platform/auth/dependencies.py`, `src/multi_agent_platform/auth/service.py`, `src/multi_agent_platform/auth/policy.py`, and `src/multi_agent_platform/api/deps.py`
- [X] T019 [US1] Implement principal-context schemas, `/auth/me`, `/auth/tenant-context/{tenant_id}`, UI-consumable protected-surface metadata, and protected router wiring in `src/multi_agent_platform/api/schemas/auth.py`, `src/multi_agent_platform/api/routers/auth.py`, and `src/multi_agent_platform/api/main.py`
- [X] T020 [US1] Implement tenant-context propagation and access-decision audit recording for protected routes in `src/multi_agent_platform/tenancy/guards.py`, `src/multi_agent_platform/audit/access.py`, and `src/multi_agent_platform/audit/service.py`

**Checkpoint**: User Story 1 is functional and independently testable.

---

## Phase 4: User Story 2 - Control Administrative Access (Priority: P2)

**Goal**: Tenant admins and platform admins have clearly separated powers,
tenant-specific support access requires approval, and role changes take effect
on the next protected action.

**Independent Test**: A tenant admin can list tenant-scoped role assignments
for their own tenant without gaining platform-wide access, a platform admin can
manage role grants, tenant-specific support access stays denied until a second
approver approves it, and revoked or changed roles are enforced on the next
protected action.

### Tests for User Story 2

> Write these tests first and ensure they fail before implementation.

- [X] T021 [P] [US2] Add unit tests for role-assignment (role-grant) administration, support-override approval, and revocation timing in `tests/unit/admin/test_support_overrides.py` and `tests/unit/auth/test_service.py`
- [X] T022 [P] [US2] Expand contract and integration tests for tenant-admin role-assignment access, platform-admin role-grant endpoints, and support-override endpoints in `tests/contract/test_access_control_contract.py` and `tests/integration/auth/test_support_overrides.py`
- [X] T023 [US2] Add protected endpoint tests for tenant-admin versus platform-admin behavior and stale-role denial cases in `tests/integration/api/test_authorization_failures.py`

### Implementation for User Story 2

- [X] T024 [P] [US2] Implement role-assignment (role-grant) and support-override persistence helpers in `src/multi_agent_platform/db/models/access_control.py`, `src/multi_agent_platform/db/repositories/access_control.py`, and `src/multi_agent_platform/admin/support_overrides.py`
- [X] T025 [P] [US2] Implement admin authorization services for role assignment, support-override approval, and next-request revocation checks in `src/multi_agent_platform/admin/service.py`, `src/multi_agent_platform/auth/service.py`, and `src/multi_agent_platform/auth/policy.py`
- [X] T026 [US2] Implement admin API schemas and endpoints for tenant-admin role-assignment access, platform-admin role grants, and support overrides in `src/multi_agent_platform/api/schemas/auth.py`, `src/multi_agent_platform/api/routers/admin_access.py`, and `src/multi_agent_platform/api/main.py`
- [X] T027 [US2] Record role-grant and support-override audit events in `src/multi_agent_platform/audit/access.py`, `src/multi_agent_platform/audit/models.py`, and `src/multi_agent_platform/audit/service.py`

**Checkpoint**: User Stories 1 and 2 are both independently functional.

---

## Phase 5: User Story 3 - Audit And Test Access Decisions (Priority: P3)

**Goal**: Developers and operators can exercise authorization logic in
non-production with deterministic local principals, validate delegated-credential
boundaries, and inspect durable audit evidence for allow and deny decisions.

**Independent Test**: In `local` or `test`, a configured local principal can
exercise the same protected endpoint and denial paths as Auth0 mode, production
rejects local-principal mode at startup, and delegated credentials are usable
only by approved tools within the owning tenant while audit records remain
secret-free.

### Tests for User Story 3

> Write these tests first and ensure they fail before implementation.

- [X] T028 [P] [US3] Add unit tests for deterministic local principals, auth-mode config errors, and production guardrails in `tests/unit/auth/test_local_principals.py` and `tests/unit/config/test_auth_settings.py`
- [X] T029 [P] [US3] Add unit and integration tests for delegated-credential boundary handling in `tests/unit/auth/test_service.py` and `tests/integration/auth/test_delegated_credentials.py`
- [X] T030 [P] [US3] Add unit and integration tests for platform-managed secret authorization boundaries in `tests/unit/auth/test_policy.py` and `tests/integration/auth/test_platform_secret_boundaries.py`
- [X] T031 [US3] Add integration tests for local-principal protected endpoint behavior and audit evidence generation in `tests/integration/api/test_auth_modes.py` and `tests/integration/api/test_authorization_failures.py`

### Implementation for User Story 3

- [X] T032 [P] [US3] Implement deterministic local-principal catalog resolution and production-disable guardrails in `src/multi_agent_platform/auth/local_principals.py`, `src/multi_agent_platform/config/settings.py`, and `src/multi_agent_platform/bootstrap/container.py`
- [X] T033 [P] [US3] Implement delegated-credential linkage and approved-tool authorization checks in `src/multi_agent_platform/db/models/delegated_credential.py`, `src/multi_agent_platform/db/repositories/delegated_credential.py`, and `src/multi_agent_platform/auth/service.py`
- [X] T034 [US3] Implement platform-managed secret action authorization in `src/multi_agent_platform/auth/policy.py`, `src/multi_agent_platform/auth/service.py`, `src/multi_agent_platform/secrets/base.py`, and `src/multi_agent_platform/audit/access.py`
- [X] T035 [US3] Implement auth-mode-aware dependency wiring and deny reason mapping for local principals and delegated credentials in `src/multi_agent_platform/auth/dependencies.py`, `src/multi_agent_platform/api/deps.py`, and `src/multi_agent_platform/audit/access.py`
- [X] T036 [US3] Add auth observability for access decisions, JWKS failures, and local-principal activation in `src/multi_agent_platform/observability/logging.py`, `src/multi_agent_platform/observability/metrics.py`, and `src/multi_agent_platform/observability/tracing.py`

**Checkpoint**: All user stories are independently functional and auditable.

---

## Final Phase: Polish & Cross-Cutting Concerns

**Purpose**: Finish review guidance, documentation, and validation work that
spans multiple stories.

- [X] T037 [P] Update repository and operator docs for auth modes, protected surfaces, support overrides, and delegated credentials in `README.md`, `docs/quickstart.md`, and `docs/foundation-runbook.md`
- [X] T038 Update PR review guidance and feature test instructions in `.github/pull_request_template.md` and `specs/002-platform-auth-access/quickstart.md`
- [X] T039 Update CI and validation guidance for auth/access coverage and contract checks in `.github/workflows/ci.yml` and `specs/002-platform-auth-access/contracts/access-control.openapi.yaml`
- [X] T040 Close cross-cutting security and operational review notes for Auth0, JWKS failure handling, and delegated-credential redaction in `docs/foundation-runbook.md` and `README.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1: Setup**: No dependencies
- **Phase 2: Foundational**: Depends on Phase 1 and blocks all user stories
- **Phase 3: US1**: Depends on Phase 2
- **Phase 4: US2**: Depends on US1 because `src/multi_agent_platform/auth/service.py`, `src/multi_agent_platform/auth/policy.py`, `src/multi_agent_platform/api/main.py`, and `src/multi_agent_platform/audit/access.py` are extended by both stories
- **Phase 5: US3**: Depends on US2 because it extends the same auth service, dependency, audit, and configuration files with local-principal and delegated-credential behavior
- **Final Phase**: Depends on all targeted user stories being complete

### Within Each User Story

- Tests MUST be written and failing before implementation where practical
- JWT/config parsing and persistence models come before services
- Services and policy checks come before route wiring
- Route wiring comes before audit and observability completion
- Story-specific docs and validation evidence are required before story completion

### Parallel Opportunities

- **Setup**: `T002` and `T003` can run in parallel after `T001`
- **Foundational**: `T005` and `T006` can run in parallel; after `T007`, `T008`, `T009`, and `T010` can proceed in parallel where their write scopes remain isolated; `T011` follows `T010` because both extend `src/multi_agent_platform/auth/policy.py` and `src/multi_agent_platform/auth/service.py`
- **US1**: `T014` and `T015` can run in parallel; `T017` and `T018` can run in parallel before `T019`
- **US2**: `T021` and `T022` can run in parallel; `T024` and `T025` can run in parallel before `T026`
- **US3**: `T028`, `T029`, and `T030` can run in parallel; `T032` and `T033` can run in parallel before `T035`
- **Final Phase**: `T037` and `T039` can run in parallel before `T038` and `T040`

---

## Implementation Strategy

### MVP First

1. Complete Phase 1
2. Complete Phase 2
3. Complete User Story 1
4. Validate tenant-user access, JWT validation, tenant extraction, and deny-path auditing
5. Stop and demo before expanding into admin overrides and non-production auth modes

### Incremental Delivery

1. Finish Setup and Foundational work
2. Deliver User Story 1 and validate protected tenant access
3. Deliver User Story 2 and validate admin separation and support overrides
4. Deliver User Story 3 and validate local principals, delegated credentials, and observability
5. Finish documentation, PR guidance, and validation updates

## Notes

- `[P]` markers are used only where the tasks touch different files and do not
  rely on incomplete work in the same area.
- The story phases are intentionally sequential because the auth service,
  policy, audit, config, and API wiring files are shared across stories.
- Documentation and review tasks are deferred to the final phase so they can
  reflect the completed behavior across all three stories.
