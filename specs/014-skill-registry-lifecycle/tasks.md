# Tasks: Skill Registry And Installation Lifecycle

**Input**: Design documents from `/Users/scottcornell/src/my-projects/multi-agent/specs/014-skill-registry-lifecycle/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md, contracts/

**Tests**: TDD is required by the user request and feature requirements. Write the listed tests first, run the targeted suite, confirm failure, then implement.

**Organization**: Tasks are grouped by user story so each story is independently implementable and testable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel with other tasks in the same phase because it touches different files and has no dependency on incomplete tasks.
- **[Story]**: Maps to a user story from spec.md.
- Every task includes an exact repository path.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare the additive skill lifecycle module, test fixtures, and routing/docs scaffolds.

- [ ] T001 Create the skill registry package directory and module exports in `src/multi_agent_platform/admin/skill_registry/__init__.py`
- [ ] T002 [P] Create reusable valid and invalid skill manifest fixtures in `tests/fixtures/skill_registry.py`
- [ ] T003 [P] Add initial API/schema/router imports for the skill registry surface in `src/multi_agent_platform/api/schemas/skill_registry.py`
- [ ] T004 [P] Add initial admin router module for JSON and UI routes in `src/multi_agent_platform/api/routers/admin_skill_registry.py`
- [ ] T005 [P] Create initial admin template directory scaffold in `src/multi_agent_platform/web_admin/templates/skill_registry/index.html`
- [ ] T006 [P] Create initial documentation scaffolds in `docs/skill-registry.md`, `docs/skill-registry-testing.md`, and `docs/skill-registry-pr-notes.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core database, policies, schemas, storage, durable jobs, observability, audit safety, and route wiring required before user stories.

**Critical**: No user story implementation should begin until this phase is complete.

### Tests for Foundational Infrastructure

- [ ] T007 [P] Add migration tests for skill lifecycle tables, constraints, indexes, and downgrade behavior in `tests/integration/migrations/test_skill_registry_migration.py`
- [ ] T008 [P] Add SQLAlchemy model tests for immutability columns, tenant scope fields, revision tokens, and redacted JSON fields in `tests/unit/db/test_skill_models.py`
- [ ] T009 [P] Add repository tests for tenant-scoped queries, optimistic concurrency rejection, and immutable version writes in `tests/unit/db/test_skill_repository.py`
- [ ] T010 [P] Add API schema tests for redaction, semantic version fields, revision token requests, and safe response models in `tests/unit/api/test_skill_registry_schemas.py`
- [ ] T011 [P] Add skill registry admin UI view-model unit tests for platform and tenant scoping, redacted credential summaries, readiness/actionable findings, quarantine states, and safe empty/error states in `tests/unit/api/test_skill_registry_ui_models.py`
- [ ] T012 [P] Add authorization policy tests for platform skill publishing, tenant installation, cross-tenant denial, and audit access in `tests/unit/auth/test_skill_policy.py`
- [ ] T013 [P] Add artifact storage tests for content-addressed package, manifest, documentation, fixture, and evidence writes in `tests/unit/admin/test_skill_artifact_store.py`
- [ ] T014 [P] Add safe audit helper tests proving raw secrets, credential values, provider tokens, unsafe docs, and cross-tenant data are redacted in `tests/unit/admin/test_skill_audit_redaction.py`
- [ ] T015 [P] Add persisted job durability tests for validation and smoke-test lease expiry, duplicate idempotency keys, retryable failure recovery, and terminal failure blocking in `tests/unit/admin/test_skill_registry_jobs.py`
- [ ] T016 [P] Add observability tests proving metrics, structured logs, traces, and labels exclude raw package payloads, raw credentials, provider tokens, unsafe docs or fixtures, and cross-tenant data in `tests/unit/admin/test_skill_registry_observability.py`
- [ ] T017 [P] Add tenant quota and fair-scheduling tests for validation and smoke-test jobs covering per-tenant concurrency limits, queued-job limits, artifact-throughput throttling, round-robin selection, oldest-created ordering, and safe rejection summaries in `tests/unit/admin/test_skill_registry_fairness.py`

### Implementation for Foundational Infrastructure

- [ ] T018 Define skill package, package version, tenant grant, installation, credential readiness, smoke test, quarantine, and audit SQLAlchemy models in `src/multi_agent_platform/db/models/skill_registry.py`
- [ ] T019 Register the skill lifecycle models with the model metadata imports in `src/multi_agent_platform/db/models/__init__.py`
- [ ] T020 Create Alembic revision 0014 with skill lifecycle tables, unique constraints, tenant indexes, immutable digest fields, revision token fields, and audit indexes in `alembic/versions/0014_skill_registry_lifecycle.py`
- [ ] T021 Implement scoped repository methods for packages, versions, grants, installations, credentials, smoke tests, quarantine, and audit queries in `src/multi_agent_platform/db/repositories/skill_registry.py`
- [ ] T022 Implement optimistic concurrency helpers and stale-write audit hooks in `src/multi_agent_platform/db/repositories/skill_registry.py`
- [ ] T023 Implement Pydantic request/response schemas for packages, versions, availability, installations, credentials, smoke tests, readiness, quarantine, eligibility, and audits in `src/multi_agent_platform/api/schemas/skill_registry.py`
- [ ] T024 Implement content-addressed object storage integration, checksum verification, and retry-safe digest idempotency for skill artifacts in `src/multi_agent_platform/admin/skill_registry/artifact_store.py`
- [ ] T025 Implement safe lifecycle audit event builder and redaction boundary in `src/multi_agent_platform/admin/skill_registry/audit.py`
- [ ] T026 Implement persisted validation and smoke-test job records, lease ownership and expiry, retry counters, idempotency-key handling, terminal state transitions, and compensation evidence in `src/multi_agent_platform/admin/skill_registry/jobs.py`
- [ ] T027 Implement tenant quota, artifact-throughput, and fair-scheduling admission helpers for validation and smoke-test jobs in `src/multi_agent_platform/admin/skill_registry/fairness.py`
- [ ] T028 Integrate fairness decisions with persisted job records, leases, retries, metrics, and audit summaries in `src/multi_agent_platform/admin/skill_registry/jobs.py`
- [ ] T029 Implement Prometheus metrics for validation attempts and duration, publication outcomes, artifact failures, tenant installs, smoke-test outcomes, readiness promotions, binding denials, quarantine actions, fairness decisions, quota throttles, and workflow publish denials in `src/multi_agent_platform/admin/skill_registry/metrics.py`
- [ ] T030 Implement structured log and trace helpers keyed by `trace_id`, tenant, package slug/version, installation id/version, validation job id, smoke-test run id, and fairness decision reason in `src/multi_agent_platform/admin/skill_registry/observability.py`
- [ ] T031 Add skill registry auth policy entries and permission checks in `src/multi_agent_platform/auth/policy.py`
- [ ] T032 Add local-principal admin test-mode grants for platform and tenant skill registry roles in `src/multi_agent_platform/auth/local_principals.py`
- [ ] T033 Wire the admin skill registry router into the FastAPI app startup in `src/multi_agent_platform/api/main.py`

**Checkpoint**: Database, schemas, storage, durable job records, audit safety, observability helpers, auth policy, and router shell exist; user stories can now proceed.

---

## Phase 3: User Story 1 - Publish Approved Skill Versions (Priority: P1) MVP

**Goal**: A platform admin can create a package, validate a declarative manifest, publish an immutable version with pinned artifact provenance, and grant tenant availability.

**Independent Test**: Submit valid and invalid packages through the API/service; invalid manifests, invalid permissions, unsafe docs, duplicate versions, rejected entrypoints, and bad digests are blocked, while a valid package publishes an immutable version discoverable only by granted tenants.

### Tests for User Story 1

- [ ] T034 [P] [US1] Add manifest validation unit tests for required fields, canonical digest, malformed semantic versions, rejected executable or HTTP entrypoints, and missing safe docs in `tests/unit/admin/test_skill_manifest.py`
- [ ] T035 [P] [US1] Add invalid permission tests for undeclared network domains, unknown action categories, disallowed runtime permissions, and unapproved tool/MCP refs in `tests/unit/admin/test_skill_manifest_permissions.py`
- [ ] T036 [P] [US1] Add package validation service tests for safe documentation, fixture safety, compatibility metadata, artifact digest mismatch, and blocking findings in `tests/unit/admin/test_skill_package_validation.py`
- [ ] T037 [P] [US1] Add isolated package validation runner tests for undeclared network access, cross-tenant data access, raw credential exposure, unapproved tool/MCP references, and side-effect rejection in `tests/integration/skill_registry/test_skill_validation_runner.py`
- [ ] T038 [P] [US1] Add platform publication API contract tests for create package, validate version, publish version, duplicate semantic version conflict, and tenant availability grants in `tests/contract/test_skill_registry_contract.py`
- [ ] T039 [P] [US1] Add platform admin API integration tests for publication, package artifact storage, immutable version records, and authorized tenant discovery in `tests/integration/api/test_admin_skill_registry_api.py`
- [ ] T040 [P] [US1] Add platform admin UI integration tests for package list, candidate form, validation findings, version detail, and availability grants in `tests/integration/api/test_admin_skill_registry_ui.py`

### Implementation for User Story 1

- [ ] T041 [P] [US1] Implement the Pydantic skill manifest schema, canonical JSON digesting, SemVer validation, and secret-material rejection in `src/multi_agent_platform/admin/skill_registry/manifest.py`
- [ ] T042 [P] [US1] Implement runtime permission, network requirement, approved integration, action category, credential requirement, fixture, compatibility, and safe documentation validation in `src/multi_agent_platform/admin/skill_registry/validation.py`
- [ ] T043 [US1] Implement the isolated package validation runner and blocking-finding translation in `src/multi_agent_platform/admin/skill_registry/validation_runner.py`
- [ ] T044 [US1] Implement platform package creation, candidate validation runner integration, validation job outcome gating, version publication, duplicate version blocking, and immutable digest persistence in `src/multi_agent_platform/admin/skill_registry/service.py`
- [ ] T045 [US1] Implement package artifact, safe documentation, fixture bundle, and validation evidence storage calls during publication in `src/multi_agent_platform/admin/skill_registry/service.py`
- [ ] T046 [US1] Implement tenant availability grant, revoke, and tenant-visible discovery logic in `src/multi_agent_platform/admin/skill_registry/service.py`
- [ ] T047 [US1] Implement platform package, version validation, publication, version detail, availability, withdraw, and quarantine JSON endpoints in `src/multi_agent_platform/api/routers/admin_skill_registry.py`
- [ ] T048 [US1] Implement platform package list, package detail, version detail, and candidate publication view models in `src/multi_agent_platform/api/ui/skill_registry.py`
- [ ] T049 [US1] Implement platform package list template with filters and safe state indicators in `src/multi_agent_platform/web_admin/templates/skill_registry/package_list.html`
- [ ] T050 [US1] Implement package detail and package version detail templates with provenance, validation findings, availability, and redacted artifact summaries in `src/multi_agent_platform/web_admin/templates/skill_registry/package_detail.html` and `src/multi_agent_platform/web_admin/templates/skill_registry/package_version_detail.html`
- [ ] T051 [US1] Implement candidate validation and publication form template with duplicate-version and blocking-finding states in `src/multi_agent_platform/web_admin/templates/skill_registry/package_candidate_form.html`
- [ ] T052 [US1] Register skill registry navigation entries and platform-only controls in `src/multi_agent_platform/web_admin/templates/admin_shell/navigation.html`

**Checkpoint**: User Story 1 is fully functional and independently testable as the MVP.

---

## Phase 4: User Story 2 - Install And Validate Tenant Skills (Priority: P2)

**Goal**: A tenant admin can install an authorized immutable package version, configure required secret references or delegated credentials, run smoke tests, and reach ready only when checks pass.

**Independent Test**: Install an authorized package version for one tenant; unauthorized cross-tenant installs fail; missing or wrong-scope credentials block readiness; smoke tests record pass/fail evidence without secrets; installation records remain immutable.

### Tests for User Story 2

- [ ] T053 [P] [US2] Add tenant installation lifecycle tests for authorized install, unauthorized cross-tenant install denial, immutable installation version fields, and upgrade lineage seed data in `tests/integration/skill_registry/test_skill_installation_lifecycle.py`
- [ ] T054 [P] [US2] Add credential readiness tests for required secret refs, revoked refs, wrong-scope refs, missing refs, and delegated credential requirements in `tests/unit/admin/test_skill_readiness.py`
- [ ] T055 [P] [US2] Add smoke runner tests for pass, fail, skipped, errored, idempotency, fixture safety, policy summaries, and evidence redaction in `tests/integration/skill_registry/test_skill_smoke_runner.py`
- [ ] T056 [P] [US2] Add installation API contract tests for available versions, create install, configure credentials, run smoke tests, promote readiness, and stale revision token conflicts in `tests/contract/test_skill_installation_contract.py`
- [ ] T057 [P] [US2] Add tenant admin UI tests for installation list, configure form, smoke-test history, readiness findings, and no raw credential fields in `tests/integration/api/test_admin_skill_registry_ui.py`
- [ ] T058 [P] [US2] Add object storage failure tests for smoke-test evidence artifact retries, checksum mismatch, and safe failure summaries in `tests/unit/admin/test_skill_artifact_store.py`

### Implementation for User Story 2

- [ ] T059 [US2] Implement tenant authorized package discovery, install authorization checks, and cross-tenant denial audit events in `src/multi_agent_platform/admin/skill_registry/service.py`
- [ ] T060 [US2] Implement immutable tenant installation version creation with package slug/version, manifest summary, artifact digest, readiness projection, and revision token in `src/multi_agent_platform/admin/skill_registry/service.py`
- [ ] T061 [US2] Implement credential readiness evaluation for secret references, secret reference versions, delegated credential links, revoked or expired credentials, and wrong-scope credentials in `src/multi_agent_platform/admin/skill_registry/readiness.py`
- [ ] T062 [US2] Implement readiness promotion rules for credential status, compatibility, permission checks, smoke-test status, quarantine state, and actionable findings in `src/multi_agent_platform/admin/skill_registry/readiness.py`
- [ ] T063 [US2] Implement tenant-scoped smoke-test runner input/output models, persisted job lease integration, idempotent run recording, pass/fail/skipped/errored transitions, and safe evidence summaries in `src/multi_agent_platform/admin/skill_registry/smoke_runner.py`
- [ ] T064 [US2] Integrate smoke-test artifact evidence writes, retryable failure summaries, and compensation evidence with object storage in `src/multi_agent_platform/admin/skill_registry/smoke_runner.py`
- [ ] T065 [US2] Implement available versions, installation list, create installation, configure credentials, run smoke tests, promote readiness, and stale-token 409 endpoints in `src/multi_agent_platform/api/routers/admin_skill_registry.py`
- [ ] T066 [US2] Implement tenant installation list, installation detail, and configure-form view models with redacted credential summaries in `src/multi_agent_platform/api/ui/skill_registry.py`
- [ ] T067 [US2] Implement tenant installation list and detail templates with readiness, credential, smoke-test, upgrade, and audit sections in `src/multi_agent_platform/web_admin/templates/skill_registry/installation_list.html` and `src/multi_agent_platform/web_admin/templates/skill_registry/installation_detail.html`
- [ ] T068 [US2] Implement credential configuration and smoke-test form template without raw credential entry fields in `src/multi_agent_platform/web_admin/templates/skill_registry/installation_configure.html`
- [ ] T069 [US2] Implement reusable readiness and smoke-test template components in `src/multi_agent_platform/web_admin/templates/skill_registry/components/readiness_panel.html` and `src/multi_agent_platform/web_admin/templates/skill_registry/components/smoke_test_history.html`

**Checkpoint**: User Story 2 is independently functional with tenant install, credential readiness, smoke tests, immutable installation records, and readiness promotion.

---

## Phase 5: User Story 3 - Bind Installed Skills To Runtime Use (Priority: P3)

**Goal**: Ready installations can be bound through existing skill-binding policies; upgrades create new installation versions and never move existing bindings automatically.

**Independent Test**: Bind a ready installation to an eligible agent profile or workflow role; deny non-ready, unauthorized, incompatible, or quarantined installations; install an upgrade and confirm existing bindings remain pinned until explicit rebinding or workflow publish.

### Tests for User Story 3

- [ ] T070 [P] [US3] Add skill binding eligibility unit tests for ready, non-ready, unauthorized, missing credential, incompatible action category, and quarantined installations in `tests/unit/admin/test_skill_eligibility.py`
- [ ] T071 [P] [US3] Add model skill config integration tests proving existing policy preview and binding creation consume exact installation evidence in `tests/integration/skill_registry/test_skill_policy_integration.py`
- [ ] T072 [P] [US3] Add workflow publish validation tests for missing, stale, not-ready, quarantined, policy-incompatible, and eligible installed skill references in `tests/integration/skill_registry/test_skill_workflow_publish_validation.py`
- [ ] T073 [P] [US3] Add upgrade path tests proving new installation versions are created and existing bindings remain pinned until explicit rebinding in `tests/integration/skill_registry/test_skill_upgrade_path.py`
- [ ] T074 [P] [US3] Add runtime eligibility tests for quarantine and runtime-blocked installations in `tests/unit/admin/test_skill_runtime_eligibility.py`

### Implementation for User Story 3

- [ ] T075 [US3] Implement the Spec 007 skill-binding eligibility adapter with exact installation id, installation version, package slug/version, manifest digest, policy matches, and denial reasons in `src/multi_agent_platform/admin/skill_registry/eligibility.py`
- [ ] T076 [US3] Integrate installed skill eligibility with existing model skill config preview and binding policy flows in `src/multi_agent_platform/config/model_skill.py`
- [ ] T077 [US3] Integrate installed skill eligibility with workflow publish validation and bundle pinning in `src/multi_agent_platform/admin/workflow_registry/publish_gate.py`
- [ ] T078 [US3] Implement runtime eligibility and quarantine checks for installed skills in `src/multi_agent_platform/runtime/skill_registry.py`
- [ ] T079 [US3] Implement upgrade installation creation, previous-installation lineage, and explicit rebinding support in `src/multi_agent_platform/admin/skill_registry/service.py`
- [ ] T080 [US3] Implement binding eligibility, workflow publish validation, and upgrade endpoints in `src/multi_agent_platform/api/routers/admin_skill_registry.py`
- [ ] T081 [US3] Implement policy eligibility UI component and denied-reason display in `src/multi_agent_platform/web_admin/templates/skill_registry/components/policy_eligibility.html`

**Checkpoint**: User Story 3 is independently functional with governed binding eligibility and explicit upgrade semantics.

---

## Phase 6: User Story 4 - Review Lifecycle Evidence And Audit Trail (Priority: P4)

**Goal**: Platform and tenant admins can review safe package history, installation history, smoke-test evidence, credential readiness, bindings, upgrade lineage, quarantine, and audit records without secrets or cross-tenant data.

**Independent Test**: After a full lifecycle flow, authorized admins see safe history and audit summaries; unauthorized users and other tenants are denied and audited; views and exports redact secrets, credential values, unsafe package content, and cross-tenant data.

### Tests for User Story 4

- [ ] T082 [P] [US4] Add audit timeline tests for package creation, validation, publication, availability, installation, credential configuration, smoke tests, readiness, binding attempts, upgrades, denials, quarantine, and redactions in `tests/integration/skill_registry/test_skill_audit_lifecycle.py`
- [ ] T083 [P] [US4] Add lifecycle evidence API tests for platform package lineage, tenant installation history, smoke-test evidence, upgrade lineage, quarantine decisions, and tenant isolation in `tests/integration/api/test_admin_skill_registry_api.py`
- [ ] T084 [P] [US4] Add admin audit/export redaction tests proving no raw secrets, credential values, provider tokens, unsafe docs, fixtures, or cross-tenant data render or export in `tests/unit/admin/test_skill_audit_redaction.py`
- [ ] T085 [P] [US4] Add quarantine tests for package versions and installations blocking new installs, readiness promotion, new bindings, workflow publish, and runtime use while preserving immutable history in `tests/unit/admin/test_skill_quarantine.py`
- [ ] T086 [P] [US4] Add rendered admin view tests for package history, installation audit timeline, redaction notices, quarantine states, and safe empty/error states in `tests/integration/api/test_admin_skill_registry_ui.py`

### Implementation for User Story 4

- [ ] T087 [US4] Implement lifecycle audit query, safe export, and redaction metadata helpers in `src/multi_agent_platform/admin/skill_registry/audit.py`
- [ ] T088 [US4] Implement package and installation quarantine decisions, resolution flow, runtime block projection, and audit events in `src/multi_agent_platform/admin/skill_registry/quarantine.py`
- [ ] T089 [US4] Implement package lineage, installation history, smoke-test evidence, upgrade lineage, quarantine, and audit review endpoints in `src/multi_agent_platform/api/routers/admin_skill_registry.py`
- [ ] T090 [US4] Implement audit and lifecycle evidence view models with platform versus tenant scoping in `src/multi_agent_platform/api/ui/skill_registry.py`
- [ ] T091 [US4] Implement validation findings, audit timeline, quarantine, and redaction template components in `src/multi_agent_platform/web_admin/templates/skill_registry/components/validation_findings.html` and `src/multi_agent_platform/web_admin/templates/skill_registry/components/audit_timeline.html`
- [ ] T092 [US4] Implement safe export links and restricted-content notices in `src/multi_agent_platform/web_admin/templates/skill_registry/package_version_detail.html` and `src/multi_agent_platform/web_admin/templates/skill_registry/installation_detail.html`

**Checkpoint**: User Story 4 is independently functional with safe lifecycle evidence, quarantine review, tenant isolation, and redacted audits.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, reviewer evidence, quality gates, and final consistency checks across all stories.

- [ ] T093 [P] Add docs tests covering required user docs, testing instructions, PR notes, README links, and reviewer evidence sections in `tests/docs/test_skill_registry_docs.py`
- [ ] T094 [P] Write user-facing skill registry documentation with platform admin, tenant admin, binding, upgrade, quarantine, and audit flows in `docs/skill-registry.md`
- [ ] T095 [P] Write reviewer testing instructions with local-principal setup, commands, expected evidence, and failure-mode checks in `docs/skill-registry-testing.md`
- [ ] T096 [P] Write PR review notes covering scope, architecture, security, tenant isolation, immutability, coverage, and manual QA in `docs/skill-registry-pr-notes.md`
- [ ] T097 Update README feature index and operator links for skill registry docs and test commands in `README.md`
- [ ] T098 [P] Implement smoke-test worker bootstrap or deferred job wiring and document command references in `src/multi_agent_platform/bootstrap/worker.py`
- [ ] T099 Run `uv run ruff check .` and fix skill registry lint findings in `src/multi_agent_platform/admin/skill_registry`
- [ ] T100 Run `uv run ruff format --check .` and format touched Python files in `src/multi_agent_platform/admin/skill_registry`
- [ ] T101 Run `uv run mypy src` and fix skill registry type errors in `src/multi_agent_platform/admin/skill_registry`
- [ ] T102 Run targeted skill registry tests listed in `docs/skill-registry-testing.md` and record results in `docs/skill-registry-pr-notes.md`
- [ ] T103 Run `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90` and record coverage evidence in `docs/skill-registry-pr-notes.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies; can start immediately.
- **Phase 2 Foundational**: Depends on Phase 1; blocks all user stories.
- **Phase 3 US1**: Depends on Phase 2; MVP.
- **Phase 4 US2**: Depends on Phase 2 and uses published package behavior from US1 for end-to-end tests.
- **Phase 5 US3**: Depends on Phase 2 and uses installation readiness from US2 for binding tests.
- **Phase 6 US4**: Depends on completed lifecycle events from US1, US2, and US3 for full evidence tests, but quarantine/audit helpers can be developed after Phase 2.
- **Phase 7 Polish**: Depends on selected user stories being complete.

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2 and delivers the MVP package publication lifecycle.
- **US2 (P2)**: Starts after Phase 2; fully testable with seeded published package versions, stronger end-to-end validation after US1.
- **US3 (P3)**: Starts after Phase 2; fully testable with seeded ready installations, stronger end-to-end validation after US2.
- **US4 (P4)**: Starts after Phase 2; full audit evidence depends on events generated by US1-US3.

### Within Each User Story

- Write tests first and confirm they fail before implementing.
- Implement schemas/models before services when new fields are needed.
- Implement services before routers and templates.
- Complete route and UI integration before story checkpoint validation.
- Preserve immutable package and installation records; only update lifecycle projection fields that the data model allows.

---

## Parallel Execution Examples

### User Story 1

```bash
Task: "T034 [US1] Add manifest validation unit tests in tests/unit/admin/test_skill_manifest.py"
Task: "T035 [US1] Add invalid permission tests in tests/unit/admin/test_skill_manifest_permissions.py"
Task: "T038 [US1] Add publication API contract tests in tests/contract/test_skill_registry_contract.py"
Task: "T040 [US1] Add platform admin UI integration tests in tests/integration/api/test_admin_skill_registry_ui.py"
```

### User Story 2

```bash
Task: "T053 [US2] Add tenant installation lifecycle tests in tests/integration/skill_registry/test_skill_installation_lifecycle.py"
Task: "T054 [US2] Add credential readiness tests in tests/unit/admin/test_skill_readiness.py"
Task: "T055 [US2] Add smoke runner tests in tests/integration/skill_registry/test_skill_smoke_runner.py"
Task: "T058 [US2] Add object storage failure tests in tests/unit/admin/test_skill_artifact_store.py"
```

### User Story 3

```bash
Task: "T070 [US3] Add skill binding eligibility unit tests in tests/unit/admin/test_skill_eligibility.py"
Task: "T071 [US3] Add model skill config integration tests in tests/integration/skill_registry/test_skill_policy_integration.py"
Task: "T072 [US3] Add workflow publish validation tests in tests/integration/skill_registry/test_skill_workflow_publish_validation.py"
Task: "T073 [US3] Add upgrade path tests in tests/integration/skill_registry/test_skill_upgrade_path.py"
```

### User Story 4

```bash
Task: "T082 [US4] Add audit timeline tests in tests/integration/skill_registry/test_skill_audit_lifecycle.py"
Task: "T083 [US4] Add lifecycle evidence API tests in tests/integration/api/test_admin_skill_registry_api.py"
Task: "T084 [US4] Add admin audit/export redaction tests in tests/unit/admin/test_skill_audit_redaction.py"
Task: "T086 [US4] Add rendered admin view tests in tests/integration/api/test_admin_skill_registry_ui.py"
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1 setup.
2. Complete Phase 2 foundational schema, repository, storage, audit, auth, and router shell.
3. Complete Phase 3 US1 tests and implementation.
4. Validate platform package creation, manifest validation, package artifact storage, immutable publication, and tenant availability.

### Incremental Delivery

1. Deliver US1 package publication as the MVP.
2. Add US2 tenant installation, credential readiness, smoke tests, and readiness promotion.
3. Add US3 binding eligibility, workflow publish validation, runtime checks, and upgrade semantics.
4. Add US4 lifecycle evidence, quarantine, safe audit/export review, and tenant isolation evidence.
5. Complete docs, reviewer notes, README updates, and full quality gates.

### Parallel Team Strategy

1. Complete Phase 1 and Phase 2 together.
2. Assign US1, US2, US3, and US4 tests to separate developers where seeded fixtures unblock independent work.
3. Keep implementation ownership by file family to avoid conflicts: one developer owns `src/multi_agent_platform/admin/skill_registry/*`, one owns API/router/schema paths, one owns DB/migration/repository paths, and one owns admin templates/docs.
4. Integrate by story checkpoint, not by file churn.

---

## Notes

- [P] tasks touch independent files or test scopes and can run in parallel.
- TDD tasks intentionally precede implementation tasks in each phase.
- Existing Spec 007 model skill policies remain the binding authority; the skill registry supplies installation evidence and denial reasons.
- Raw package secrets, credential values, provider tokens, unsafe docs/fixtures, and cross-tenant data must never be stored, rendered, logged, audited, or exported.
- Package versions and tenant installation versions are immutable; upgrades always create a new installation version and require explicit rebinding or workflow publication.
