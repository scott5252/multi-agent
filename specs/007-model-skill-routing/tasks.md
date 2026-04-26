# Tasks: Model Routing And Skill Configuration

**Input**: Design documents from `/Users/scottcornell/src/my-projects/multi-agent/specs/007-model-skill-routing/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `quickstart.md`, `contracts/`

**Tests**: Test-first delivery is required by the feature request and specification. Each user story begins with contract, unit, or integration tests that must be written and observed failing before implementation.

**Organization**: Tasks are grouped by user story so each story can be implemented, tested, and reviewed independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel with other marked tasks in the same phase because it touches different files and does not depend on incomplete tasks
- **[Story]**: User story label for story phases only
- **File paths**: Every task includes exact repository paths

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the feature scaffolding and shared package boundaries used by later test-first work.

- [ ] T001 Create model-skill configuration domain module scaffolding in `src/multi_agent_platform/config/model_skill.py`, `src/multi_agent_platform/config/resolver.py`, `src/multi_agent_platform/config/policy.py`, `src/multi_agent_platform/config/validation.py`, `src/multi_agent_platform/config/provenance.py`, `src/multi_agent_platform/config/rollback.py`, and `src/multi_agent_platform/config/service.py`
- [ ] T002 Create persistence scaffolding in `src/multi_agent_platform/db/models/model_skill_config.py` and `src/multi_agent_platform/db/repositories/model_skill_config.py`
- [ ] T003 Create API and UI scaffolding in `src/multi_agent_platform/api/schemas/model_skill_config.py`, `src/multi_agent_platform/api/routers/admin_model_skill_config.py`, and `src/multi_agent_platform/api/ui/model_skill_config.py`
- [ ] T004 [P] Create admin web asset and template placeholders in `src/multi_agent_platform/web_admin/static/model_skill_config.js`, `src/multi_agent_platform/web_admin/templates/model_skill_config/index.html`, `src/multi_agent_platform/web_admin/templates/model_skill_config/history.html`, and `src/multi_agent_platform/web_admin/templates/model_skill_config/run_provenance.html`
- [ ] T005 [P] Create model-skill test package placeholders in `tests/unit/model_skill_config/__init__.py`, `tests/integration/model_skill_config/__init__.py`, and `tests/contract/test_model_skill_config_contract.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build durable versioning, tenant-safe validation primitives, and dependency wiring required by every user story.

**Critical**: No user story work can begin until this phase is complete.

### Foundational Tests First

- [ ] T006 [P] Add failing ORM tests for immutable configuration version entities, active pointer uniqueness, runtime decision rows, and audit rows in `tests/unit/db/test_model_skill_config_models.py`
- [ ] T007 [P] Add failing migration tests for PostgreSQL tables, indexes, active singleton constraints, and rollback downgrade safety in `tests/integration/db/test_model_skill_config_migration.py`
- [ ] T008 [P] Add failing schema tests for safe request/response models, stable error categories, reason requirements, and secret redaction in `tests/unit/api/test_model_skill_config_schemas.py`
- [ ] T009 [P] Add failing validation tests for tenant scope selectors, raw-secret rejection, unknown model/tool references, and invalid prompt/global scope combinations in `tests/unit/model_skill_config/test_validation.py`
- [ ] T010 [P] Add failing publish-time model-skill validation tests for missing global default, inactive/unauthorized model references, missing prompt references, unbound skills, denied tools, denied outbound domains, unsatisfied credentials, and safe error categories in `tests/unit/admin/test_workflow_registry_model_skill_validation.py` and `tests/integration/api/test_admin_workflow_publish_model_skill_validation.py`
- [ ] T011 [P] Add failing authorization matrix tests for administrator, workflow owner, operator, auditor, maintainer, runtime actor, and cross-tenant fail-closed behavior across create, update, activate, deactivate, preview, history, provenance, rollback, migration, and runtime resolver calls in `tests/integration/api/test_model_skill_config_authorization.py`

### Foundational Implementation

- [ ] T012 Implement SQLAlchemy models for model provider catalog entries, routing versions, prompt references, skill bindings, tool policies, outbound policies, secret references, credential requirements, active pointers, resolved execution configurations, runtime decisions, audit records, rollback records, and run migration records in `src/multi_agent_platform/db/models/model_skill_config.py`
- [ ] T013 Register model-skill ORM metadata exports in `src/multi_agent_platform/db/models/__init__.py`
- [ ] T014 Implement Alembic migration with PostgreSQL tables, foreign keys, JSONB columns, active singleton partial indexes, scope hash indexes, and downgrade behavior in `alembic/versions/0007_model_skill_routing.py`
- [ ] T015 Implement repository primitives for immutable version insert, active pointer activation, expected-version conflict checks, audit writes, history reads, and runtime decision persistence in `src/multi_agent_platform/db/repositories/model_skill_config.py`
- [ ] T016 Implement Pydantic domain value objects, enums, scope selectors, safe summaries, and stable error categories in `src/multi_agent_platform/config/model_skill.py`
- [ ] T017 Implement API schemas for create, activate, preview, history, rollback, provenance, and error responses in `src/multi_agent_platform/api/schemas/model_skill_config.py`
- [ ] T018 Implement shared validation helpers for tenant scope shape, required reasons, provider/model availability, prompt scope rules, publish/start validation, skill/tool identifiers, raw-secret detection, and redacted summaries in `src/multi_agent_platform/config/validation.py`
- [ ] T019 Wire configuration service and repository dependencies into `src/multi_agent_platform/bootstrap/container.py`
- [ ] T020 Implement publish-time model-skill validation integration in `src/multi_agent_platform/admin/workflow_registry/service.py`, using `src/multi_agent_platform/config/validation.py` before `WorkflowVersionBundle` creation so invalid model-backed workflow definitions cannot publish
- [ ] T021 Implement model-skill tenant and role authorization guard helpers in `src/multi_agent_platform/config/service.py` and `src/multi_agent_platform/api/routers/admin_model_skill_config.py`, reusing existing principal, AuthService, and tenancy guard patterns for every mutation, preview, history, provenance, rollback, migration, and runtime-resolution surface
- [ ] T022 Wire model-skill policy evaluation to the existing secret provider and delegated credential authorization services in `src/multi_agent_platform/bootstrap/container.py`, `src/multi_agent_platform/auth/service.py`, and `src/multi_agent_platform/config/service.py`, ensuring only reference metadata and safe summaries cross persistence/audit boundaries

**Checkpoint**: Foundation ready. Versioned storage, schemas, validation, and dependency wiring are available for story work.

---

## Phase 3: User Story 1 - Configure Model Defaults And Overrides (Priority: P1)

**Goal**: Administrators can set one active tenant default LLM, add workflow/agent/step model overrides, preview deterministic model and prompt resolution, and preserve version history.

**Independent Test**: Set a tenant global default and workflow/agent/step overrides through the API, preview each scope through API and admin web views, and confirm step > agent > workflow > tenant default resolution with version history intact.

### Tests for User Story 1

- [ ] T023 [P] [US1] Add failing table-driven resolver tests for model precedence step > agent > workflow > tenant default, missing global default, inactive model reference, equal-specificity conflict, and stable candidate ordering in `tests/unit/model_skill_config/test_model_resolution.py`
- [ ] T024 [P] [US1] Add failing prompt resolution tests for step > agent > workflow precedence, rejection of tenant-global prompt references, and missing prompt failure in `tests/unit/model_skill_config/test_prompt_resolution.py`
- [ ] T025 [P] [US1] Add failing invalid-configuration tests for unavailable models, unauthorized tenant model references, stale expected active version ids, and missing activation reasons in `tests/unit/model_skill_config/test_model_validation.py`
- [ ] T026 [P] [US1] Add failing contract tests for model routing create, activate, prompt reference create, model preview, history, and safe error categories from `specs/007-model-skill-routing/contracts/model-skill-routing.openapi.yaml` in `tests/contract/test_model_skill_config_contract.py`
- [ ] T027 [P] [US1] Add failing integration API tests for configuring tenant defaults and workflow/agent/step overrides in `tests/integration/api/test_admin_model_skill_config_api.py`
- [ ] T028 [P] [US1] Add failing admin web view tests for model routing list, missing default blocking state, preview, history link, and unauthorized scope behavior in `tests/integration/api/test_admin_model_skill_config_ui.py`

### Implementation for User Story 1

- [ ] T029 [US1] Implement deterministic model and prompt resolution, candidate ordering, source scope reporting, and conflict detection in `src/multi_agent_platform/config/resolver.py`
- [ ] T030 [US1] Implement admin service methods for model routing versions, prompt reference versions, activation, preview, history, and tenant/role authorization enforcement in `src/multi_agent_platform/config/service.py`
- [ ] T031 [US1] Implement model routing, prompt reference, activation, preview, and history endpoints in `src/multi_agent_platform/api/routers/admin_model_skill_config.py`
- [ ] T032 [US1] Register the admin model-skill router in `src/multi_agent_platform/api/main.py`
- [ ] T033 [US1] Implement admin UI view models for model routing preview and history in `src/multi_agent_platform/api/ui/model_skill_config.py`
- [ ] T034 [US1] Implement server-rendered model routing and history templates in `src/multi_agent_platform/web_admin/templates/model_skill_config/index.html` and `src/multi_agent_platform/web_admin/templates/model_skill_config/history.html`
- [ ] T035 [US1] Implement preview form behavior without model calls, DNS lookups, HTTP calls, or external tool calls in `src/multi_agent_platform/web_admin/static/model_skill_config.js`
- [ ] T036 [US1] Add safe structured audit records for model routing and prompt reference create, activate, preview denial, and history reads in `src/multi_agent_platform/config/service.py`

**Checkpoint**: User Story 1 is independently testable and delivers the MVP for model routing and prompt preview.

---

## Phase 4: User Story 2 - Bind Skills And Tool Policies To Agents (Priority: P2)

**Goal**: Agents can only use explicitly bound skills and allowed tools, with cumulative skill/tool/outbound/credential policies enforced deny-by-default.

**Independent Test**: Configure skill bindings, allowed tools, outbound domains, secret references, and credential requirements through API/UI, then verify allowed requests succeed and disallowed skill, tool, domain, secret, or credential requests are blocked and audited.

### Tests for User Story 2

- [ ] T037 [P] [US2] Add failing allowed-skill enforcement tests for missing binding denial, exact skill version match, allowed context constraints, and evaluated binding versions in `tests/unit/model_skill_config/test_skill_policy.py`
- [ ] T038 [P] [US2] Add failing tool policy intersection tests for deny-by-default, allowed action categories, overlapping applicable policies, and broader policy constraints in `tests/unit/model_skill_config/test_tool_policy.py`
- [ ] T039 [P] [US2] Add failing outbound policy tests for lowercase and IDNA normalization, wildcard matching, scheme and port checks, embedded credential rejection, malformed destinations, and domain denial reasons in `tests/unit/model_skill_config/test_outbound_policy.py`
- [ ] T040 [P] [US2] Add failing secret-reference and credential-provider boundary tests for raw secret rejection, inactive/revoked/expired/cross-tenant references, delegated credential authorization, SecretProvider resolution through `src/multi_agent_platform/secrets/base.py`, safe redacted summaries, and proof that persisted decisions never store `SecretValue.value` in `tests/unit/model_skill_config/test_secret_reference_policy.py`
- [ ] T041 [P] [US2] Add failing contract tests for skill bindings, tool policies, outbound policies, secret references, credential requirements, and tool preview endpoints in `tests/contract/test_model_skill_config_contract.py`
- [ ] T042 [P] [US2] Add failing integration tests proving disallowed skill, tool, outbound domain, and credential attempts are denied before side effects and persisted as safe audit records in `tests/integration/model_skill_config/test_policy_enforcement.py`
- [ ] T043 [P] [US2] Add failing admin web view tests for skills-tools filters, policy create forms, tool preview allow/deny states, and secret-value redaction in `tests/integration/api/test_admin_model_skill_config_ui.py`

### Implementation for User Story 2

- [ ] T044 [US2] Implement skill binding evaluation, exact version checks, allowed context checks, and deny-by-default decisions in `src/multi_agent_platform/config/policy.py`
- [ ] T045 [US2] Implement allowed tool policy cumulative intersection for tool id and action category decisions in `src/multi_agent_platform/config/policy.py`
- [ ] T046 [US2] Implement outbound destination normalization and domain, scheme, port, wildcard, and malformed URL policy evaluation in `src/multi_agent_platform/config/policy.py`
- [ ] T047 [US2] Implement secret-reference and credential requirement validation for active status, expiry, revocation, tenant authorization, delegated credential links, allowed scope, SecretProvider-backed reference resolution through existing secret abstractions, and safe summaries in `src/multi_agent_platform/config/policy.py`
- [ ] T048 [US2] Implement admin service methods for skill bindings, tool policies, outbound domain policies, secret-reference versions, credential requirements, tool preview, and tenant/role authorization enforcement in `src/multi_agent_platform/config/service.py`
- [ ] T049 [US2] Implement skill binding, tool policy, outbound policy, secret reference, credential requirement, and preview tool endpoints in `src/multi_agent_platform/api/routers/admin_model_skill_config.py`
- [ ] T050 [US2] Implement skills-tools admin UI view models in `src/multi_agent_platform/api/ui/model_skill_config.py`
- [ ] T051 [US2] Implement skills-tools admin template states in `src/multi_agent_platform/web_admin/templates/model_skill_config/index.html`
- [ ] T052 [US2] Persist safe allow and deny runtime policy decision records for skill, tool, outbound, secret-reference, and credential outcomes in `src/multi_agent_platform/config/provenance.py`
- [ ] T053 [US2] Add safe metrics and structured log helpers for policy allow/deny outcomes in `src/multi_agent_platform/observability/metrics.py` and `src/multi_agent_platform/observability/logging.py`

**Checkpoint**: User Story 2 is independently testable with explicit skill and tool policy enforcement.

---

## Phase 5: User Story 3 - Run With Pinned Model, Prompt, And Policy Provenance (Priority: P3)

**Goal**: Accepted runs record run-level resolvable versions at acceptance, first-use decisions before side effects, and resume with pinned configuration unless explicitly migrated.

**Independent Test**: Start a run, mutate active configuration while queued/running/waiting/resuming, and confirm run-level pins and first-use model, prompt, skill, tool, outbound, secret, and credential decisions remain stable and reviewable.

### Tests for User Story 3

- [ ] T054 [P] [US3] Add failing provenance unit tests for stable resolved execution configuration digests, safe decision serialization, idempotency-key reuse, and redaction in `tests/unit/model_skill_config/test_provenance.py`
- [ ] T055 [P] [US3] Add failing runtime protocol tests for `pin_run_configuration`, `resolve_model_step`, `evaluate_skill_access`, and `evaluate_tool_use` response fields in `tests/unit/model_skill_config/test_runtime_resolution_protocol.py`
- [ ] T056 [P] [US3] Add failing runtime integration tests for acceptance pinning, first-use model/prompt pinning, first-use policy pinning, denied decision persistence before side effects, and resumed-run stability in `tests/integration/runtime/test_config_pinning_runtime.py`
- [ ] T057 [P] [US3] Add failing repository integration tests for immutable run provenance, runtime policy decision idempotency, and no raw secret values in persisted JSON columns in `tests/integration/model_skill_config/test_run_provenance_repository.py`
- [ ] T058 [P] [US3] Add failing contract tests for run provenance and rollback responses from `specs/007-model-skill-routing/contracts/runtime-resolution-protocol.md` in `tests/contract/test_model_skill_config_contract.py`
- [ ] T059 [P] [US3] Add failing admin web view tests for run provenance digest, first-use decision lists, denial reason display, migration records, and secret redaction in `tests/integration/api/test_admin_model_skill_config_ui.py`
- [ ] T060 [P] [US3] Add failing recovery tests for model/tool idempotency, lease retry, persisted decision reuse, and compensation state in `tests/integration/runtime/test_config_pinning_runtime.py`

### Implementation for User Story 3

- [ ] T061 [US3] Implement run acceptance pinning and stable resolution digest creation in `src/multi_agent_platform/config/provenance.py`
- [ ] T062 [US3] Implement first-use model step decision persistence with model/prompt winning versions and idempotency reuse in `src/multi_agent_platform/config/provenance.py`
- [ ] T063 [US3] Implement first-use skill and tool decision persistence with evaluated policy versions, safe denial categories, and side-effect boundary guarantees in `src/multi_agent_platform/config/provenance.py`
- [ ] T064 [US3] Expose runtime resolver facade methods `pin_run_configuration`, `resolve_model_step`, `evaluate_skill_access`, and `evaluate_tool_use` with tenant/role authorization enforcement in `src/multi_agent_platform/config/service.py`
- [ ] T065 [US3] Integrate run acceptance pinning into workflow start and acceptance flow in `src/multi_agent_platform/runtime/orchestration/service.py`
- [ ] T066 [US3] Integrate model step, skill access, and tool use first-use checks before external side effects in `src/multi_agent_platform/runtime/orchestration/side_effects.py`
- [ ] T067 [US3] Implement side-effect intent, retry, lease recovery, and compensation handling for model/tool decisions in `src/multi_agent_platform/runtime/orchestration/side_effects.py` and `src/multi_agent_platform/runtime/orchestration/service.py`
- [ ] T068 [US3] Implement resume behavior that reuses `resolved_execution_configuration_id` and evaluates unused decisions against pinned candidates in `src/multi_agent_platform/runtime/orchestration/service.py`
- [ ] T069 [US3] Implement rollback and explicit run migration helpers with audit records and compatibility checks in `src/multi_agent_platform/config/rollback.py`
- [ ] T070 [US3] Implement rollback and run provenance API endpoints with tenant/role authorization enforcement in `src/multi_agent_platform/api/routers/admin_model_skill_config.py`
- [ ] T071 [US3] Implement run provenance UI view model and template in `src/multi_agent_platform/api/ui/model_skill_config.py` and `src/multi_agent_platform/web_admin/templates/model_skill_config/run_provenance.html`

**Checkpoint**: User Story 3 is independently testable with durable run provenance and pinned runtime behavior.

---

## Phase 6: User Story 4 - Audit Configuration History And Review Delivery (Priority: P4)

**Goal**: Auditors, maintainers, and reviewers can inspect complete configuration history, policy decisions, delivery evidence, docs, PR review notes, testing instructions, and README guidance.

**Independent Test**: Review version history, denied policy decisions, provenance views, coverage evidence, PR review notes, testing instructions, and README updates without additional verbal explanation.

### Tests for User Story 4

- [ ] T072 [P] [US4] Add failing audit logging tests for configuration create, activate, deactivate, rollback, migration, validation failure, authorization failure, and denied runtime policy decisions in `tests/unit/model_skill_config/test_audit_logging.py`
- [ ] T073 [P] [US4] Add failing history API integration tests for actor, timestamp, reason, prior version, new version, affected scope, rollback eligibility, tenant authorization, and safe not-found behavior in `tests/integration/api/test_admin_model_skill_config_api.py`
- [ ] T074 [P] [US4] Add failing documentation tests that assert README guidance, model-skill routing docs, testing instructions, and PR review notes mention precedence, skills, tools, secrets, outbound policy, credentials, provenance, coverage commands, and acceptance evidence fields for elapsed time, assistance status, participant count, and aggregate pass/fail calculations in `tests/docs/test_model_skill_routing_docs.py`
- [ ] T075 [P] [US4] Add failing coverage command documentation test for `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90` in `tests/docs/test_model_skill_routing_docs.py`

### Implementation for User Story 4

- [ ] T076 [US4] Implement complete configuration history query responses, redacted diff summaries, tenant/role authorization enforcement, authorization failures, and safe not-found behavior in `src/multi_agent_platform/config/service.py`
- [ ] T077 [US4] Implement configuration history and policy decision audit helpers that forbid raw prompts, raw secrets, credential values, provider tokens, and unauthorized run content in `src/multi_agent_platform/config/provenance.py`
- [ ] T078 [US4] Complete history, provenance, rollback, tenant/role authorization enforcement, and authorization response handling in `src/multi_agent_platform/api/routers/admin_model_skill_config.py`
- [ ] T079 [US4] Add operator and reviewer documentation for routing precedence, prompt precedence, skill/tool/domain/credential setup, secret-reference hygiene, rollback, migration, admin UI, APIs, and provenance in `docs/model-skill-routing.md`
- [ ] T080 [US4] Update local reviewer quickstart with model routing, skill/tool policy, outbound denial, credential failure, secret-reference audit, admin views, provenance APIs, resume stability, and required commands in `docs/quickstart.md`
- [ ] T081 [US4] Update user-facing README guidance for model routing precedence, skill configuration, allowed tool policies, secret references, outbound domain policies, credential requirements, run provenance, admin web views, API endpoints, and review verification in `README.md`
- [ ] T082 [US4] Add PR review notes covering deterministic precedence, prompt provenance, version pinning, migration behavior, skill binding enforcement, tool policies, outbound egress, credentials, secret hygiene, audit completeness, authorization, admin views, and known risks in `specs/007-model-skill-routing/pr-review-notes.md`
- [ ] T083 [US4] Add reviewer testing instructions and evidence checklist for all acceptance paths and required quality commands in `specs/007-model-skill-routing/testing-instructions.md`
- [ ] T084 [US4] Add acceptance evidence checklist for administrator and maintainer history/provenance findability, including tester role, scenario, start/end timestamps, elapsed time, assisted/unassisted result, completion status, and aggregate pass/fail calculations for SC-002 under-5-minute routing verification and SC-008 90 percent unassisted findability in `specs/007-model-skill-routing/testing-instructions.md`

**Checkpoint**: User Story 4 is independently testable with complete audit and review evidence.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, hardening, and release readiness across all user stories.

- [ ] T085 [P] Add performance tests for 3 tenants, 100 workflow/agent/step overrides per tenant, 300 skill/tool/outbound/credential policy versions per tenant, 100 active or paused runs per tenant, and latest-100 history pages: model preview p95 <150ms, policy evaluation p95 <50ms, run acceptance pinning <500ms excluding bundle load, first-use decisions <100ms, and latest-100 history p95 <300ms in `tests/performance/model_skill_config/test_model_skill_config_latency.py`
- [ ] T086 [P] Add tenant quota, bounded pagination, concurrency-budget, and cross-tenant fail-closed tests for model-skill configuration APIs in `tests/integration/api/test_model_skill_config_authorization.py`
- [ ] T087 Implement tenant limit and bounded-query enforcement for preview, history, provenance, and policy evaluation in `src/multi_agent_platform/config/service.py` and `src/multi_agent_platform/db/repositories/model_skill_config.py`
- [ ] T088 [P] Add observability tests for resolver latency metrics, preview metrics, activation/rollback counts, denied skill/tool/domain/credential counts, missing prompt/model counts, first-use decision counts, and cardinality guards in `tests/unit/observability/test_model_skill_config_metrics.py`
- [ ] T089 [P] Add tracing, workflow timeline, lineage visibility, and replay-support tests for routing and policy decisions in `tests/unit/observability/test_model_skill_config_tracing.py` and `tests/integration/runtime/test_config_pinning_runtime.py`
- [ ] T090 Add trace, timeline event, lineage link, and replay metadata emission for model routing and policy decisions in `src/multi_agent_platform/observability/tracing.py`, `src/multi_agent_platform/runtime/orchestration/events.py`, and `src/multi_agent_platform/config/provenance.py`
- [ ] T091 [P] Reconcile public OpenAPI examples with implemented schemas in `specs/007-model-skill-routing/contracts/model-skill-routing.openapi.yaml`
- [ ] T092 Run Ruff checks and fix reported issues in `src/multi_agent_platform/config/`, `src/multi_agent_platform/api/routers/admin_model_skill_config.py`, `src/multi_agent_platform/api/schemas/model_skill_config.py`, and `tests/`
- [ ] T093 Run formatting checks and apply formatting fixes in `src/multi_agent_platform/config/`, `src/multi_agent_platform/db/models/model_skill_config.py`, `src/multi_agent_platform/db/repositories/model_skill_config.py`, and `tests/`
- [ ] T094 Run mypy and fix type errors in `src/multi_agent_platform/config/`, `src/multi_agent_platform/db/repositories/model_skill_config.py`, `src/multi_agent_platform/api/`, and `src/multi_agent_platform/runtime/orchestration/`
- [ ] T095 Run full coverage gate and fix gaps below 90 percent in `src/multi_agent_platform/config/`, `src/multi_agent_platform/api/`, `src/multi_agent_platform/db/`, and `src/multi_agent_platform/runtime/orchestration/`
- [ ] T096 Validate quickstart commands and update any drift in `specs/007-model-skill-routing/quickstart.md`, `docs/quickstart.md`, and `specs/007-model-skill-routing/testing-instructions.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately.
- **Foundational (Phase 2)**: Depends on Phase 1; blocks all user story work.
- **User Story 1 (Phase 3)**: Depends on Phase 2; recommended MVP.
- **User Story 2 (Phase 4)**: Depends on Phase 2; can proceed in parallel with US1 after shared schemas and repositories are stable, but integrates naturally after US1 service/router patterns exist.
- **User Story 3 (Phase 5)**: Depends on Phase 2 and uses resolver/policy behavior from US1 and US2 for full runtime pinning.
- **User Story 4 (Phase 6)**: Depends on Phases 3-5 for complete audit and review evidence.
- **Polish (Phase 7)**: Depends on all desired stories being complete.

### User Story Dependencies

- **US1 Configure Model Defaults And Overrides**: Starts after Phase 2 and is the MVP scope.
- **US2 Bind Skills And Tool Policies To Agents**: Starts after Phase 2; independent policy evaluator work can run while US1 endpoints mature.
- **US3 Run With Pinned Model, Prompt, And Policy Provenance**: Requires US1 model/prompt resolver and US2 policy evaluator for complete end-to-end runtime provenance.
- **US4 Audit Configuration History And Review Delivery**: Requires implemented history/provenance surfaces from US1-US3.

### Within Each User Story

- Write and run the listed tests first; confirm they fail for the expected missing behavior.
- Implement domain models and evaluators before service methods.
- Implement service methods before API endpoints and UI view models.
- Implement UI templates and static behavior after API/view models exist.
- Complete story-level tests before moving to the next priority story.

---

## Parallel Execution Examples

### User Story 1

```bash
# Independent failing tests before implementation:
Task: "T023 [US1] Resolver precedence tests in tests/unit/model_skill_config/test_model_resolution.py"
Task: "T024 [US1] Prompt resolution tests in tests/unit/model_skill_config/test_prompt_resolution.py"
Task: "T026 [US1] Contract tests in tests/contract/test_model_skill_config_contract.py"
Task: "T028 [US1] Admin web view tests in tests/integration/api/test_admin_model_skill_config_ui.py"
```

### User Story 2

```bash
# Policy test work can be split by evaluator:
Task: "T037 [US2] Skill policy tests in tests/unit/model_skill_config/test_skill_policy.py"
Task: "T038 [US2] Tool policy tests in tests/unit/model_skill_config/test_tool_policy.py"
Task: "T039 [US2] Outbound policy tests in tests/unit/model_skill_config/test_outbound_policy.py"
Task: "T040 [US2] Secret-reference tests in tests/unit/model_skill_config/test_secret_reference_policy.py"
```

### User Story 3

```bash
# Runtime provenance tests can run alongside repository tests:
Task: "T054 [US3] Provenance unit tests in tests/unit/model_skill_config/test_provenance.py"
Task: "T056 [US3] Runtime pinning integration tests in tests/integration/runtime/test_config_pinning_runtime.py"
Task: "T057 [US3] Repository provenance tests in tests/integration/model_skill_config/test_run_provenance_repository.py"
```

### User Story 4

```bash
# Review evidence work can be split after audit APIs exist:
Task: "T074 [US4] Documentation tests in tests/docs/test_model_skill_routing_docs.py"
Task: "T079 [US4] Operator guide in docs/model-skill-routing.md"
Task: "T082 [US4] PR review notes in specs/007-model-skill-routing/pr-review-notes.md"
Task: "T083 [US4] Testing instructions in specs/007-model-skill-routing/testing-instructions.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup.
2. Complete Phase 2 foundational schema, validation, repository, and dependency wiring.
3. Complete Phase 3 US1 tests and implementation.
4. Validate US1 independently with resolver unit tests, contract tests, API integration tests, and admin web view tests.
5. Demo tenant default, workflow override, agent override, step override, prompt resolution, history, and preview behavior.

### Incremental Delivery

1. Deliver US1 for deterministic model and prompt routing.
2. Deliver US2 for explicit skill, tool, outbound, secret-reference, and credential policy enforcement.
3. Deliver US3 for runtime pinning, first-use decisions, resumed-run stability, rollback, and provenance.
4. Deliver US4 for audit completeness, docs, PR review notes, testing instructions, README guidance, and reviewer evidence.

### Final Verification Commands

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```
