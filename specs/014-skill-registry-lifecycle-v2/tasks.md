# Tasks: Skill Registry Lifecycle Browser Workflows

**Input**: Design documents from `/Users/scottcornell/src/my-projects/multi-agent/specs/014-skill-registry-lifecycle-v2/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/admin-skill-registry-browser-ui.md`, `quickstart.md`
**Tests**: Required by the feature specification for browser route, template, authorization, stale conflict, redaction, docs, and screenshot-backed QA verification.

**Organization**: Tasks are grouped by user story so each increment can be implemented and tested independently after the foundational browser contracts are in place.

## Current QA Curl Feature-Action Mapping

Terminal setup and diagnostics remain allowed in `specs/014-skill-registry-lifecycle/qa014_ui.md`: environment copy, tool checks, cleanup, dependency install, PostgreSQL startup/reset, migrations, deterministic tenant seed, schema diagnostics, server startup, shared variables, manifest fixture creation, redaction scan, and automated evidence collection.

| Current `qa014_ui.md` action | Required browser UI workflow |
| --- | --- |
| Step 3 `POST /admin/skill-registry/packages` | Platform-admin `GET /admin/skill-registry/ui/packages/new` and `POST /admin/skill-registry/ui/packages` package creation form |
| Step 5 `POST /admin/skill-registry/packages/{slug}/versions/validate` | Platform-admin manifest candidate entry/upload plus `POST /admin/skill-registry/ui/packages/{slug}/candidate/validate` inline validation findings |
| Step 6 `POST /admin/skill-registry/packages/{slug}/versions` | Platform-admin `POST /admin/skill-registry/ui/packages/{slug}/candidate/publish` gated immutable publication |
| Step 6 `POST /admin/skill-registry/packages/{slug}/versions/{version}/availability` | Platform-admin `GET/POST /admin/skill-registry/ui/packages/{slug}/versions/{version}/grants` tenant grant form |
| Step 10 `GET /admin/skill-registry/tenants/{tenant_id}/available-versions` | Tenant-admin `GET /admin/skill-registry/ui/available-versions?tenant_id=...` discovery page for Acme and empty/absent Globex state |
| Step 11 `POST /admin/skill-registry/installations` | Tenant-admin `POST /admin/skill-registry/ui/installations` install action from available versions |
| Step 13 `POST /admin/skill-registry/installations/{installation_id}/credentials` | Tenant-admin `GET/POST /admin/skill-registry/ui/installations/{installation_id}/credentials` credential picker and delegated metadata form |
| Step 15 `GET /admin/skill-registry/installations/{installation_id}/eligibility` | Tenant-admin `POST /admin/skill-registry/ui/installations/{installation_id}/eligibility-preview` binding eligibility preview form |
| Step 16 stale credential `POST` helper | Two-browser stale revision conflict check on credential, candidate, grant, smoke-test, or eligibility forms |
| Step 19 direct JSON available-versions URL | Tenant-admin browser discovery page showing Globex empty/absent state without JSON helper calls |

## Phase 1: Setup (Shared Audit And Test Scaffolding)

**Purpose**: Establish the browser-first implementation inventory, test scaffolding, and route evidence expectations before changing lifecycle behavior.

- [ ] T001 Audit every current feature-action curl in `specs/014-skill-registry-lifecycle/qa014_ui.md` and add the curl-to-browser mapping to `specs/014-skill-registry-lifecycle-v2/contracts/admin-skill-registry-browser-ui.md`
- [ ] T002 [P] Add docs-test expectations that `specs/014-skill-registry-lifecycle/qa014_ui.md` permits curl/SQL only for setup, diagnostics, and automated evidence collection in `tests/docs/test_skill_registry_docs.py`
- [ ] T003 [P] Create browser route integration test scaffolding for platform-admin and tenant-admin flows in `tests/integration/api/test_admin_skill_registry_ui.py`
- [ ] T004 [P] Create screenshot/evidence helper scaffolding for `output/playwright/qa014_ui` capture expectations in `tests/integration/api/test_skill_registry_browser_flows.py`

---

## Phase 2: Foundational (Blocking Browser Infrastructure)

**Purpose**: Shared route policy, form parsing, safe page context, and template primitives required by every browser workflow.

**Critical**: No user story implementation should start until these tasks are complete.

- [ ] T005 Add failing protected surface policy tests for all new UI GET/POST routes in `tests/unit/auth/test_skill_policy.py`
- [ ] T006 Add protected surface policies for package creation, candidate entry, candidate validation, publish, grants, available versions, install, credentials, smoke-tests, and eligibility preview in `src/multi_agent_platform/auth/policy.py`
- [ ] T007 Adjust local-principal platform-admin and tenant-admin permission grants for new UI actions in `src/multi_agent_platform/auth/local_principals.py`
- [ ] T008 Add unit tests for browser form parsing, YAML/JSON upload precedence, idempotency keys, revision tokens, and safe error mapping in `tests/unit/api/test_skill_registry_ui_models.py`
- [ ] T009 Implement shared browser form and safe view models for `SkillPackageCreateForm`, `ManifestCandidateForm`, `TenantGrantForm`, `InstallSkillForm`, `CredentialReferenceConfigForm`, `SmokeTestActionForm`, `BindingEligibilityPreviewForm`, `RevisionConflictView`, and `RedactionSafePageContext` in `src/multi_agent_platform/api/ui/skill_registry.py`
- [ ] T010 Extend shared API schemas only where router form adapters need typed request mapping in `src/multi_agent_platform/api/schemas/skill_registry.py`
- [ ] T011 Add shared form, validation, stale conflict, empty, denied, readiness, smoke-test, policy, and audit partial coverage in `tests/integration/api/test_admin_console_templates.py`
- [ ] T012 Implement shared skill registry template partials for form errors, stale conflicts, validation findings, readiness, smoke-test history, policy eligibility, and audit timeline in `src/multi_agent_platform/web_admin/templates/skill_registry/components/form_errors.html`
- [ ] T013 Implement the shared stale conflict template partial in `src/multi_agent_platform/web_admin/templates/skill_registry/components/stale_conflict.html`
- [ ] T014 Wire common form parsing, redirect/flash handling, safe template rendering, and service error translation helpers in `src/multi_agent_platform/api/routers/admin_skill_registry.py`

**Checkpoint**: Browser route policies, form models, template components, and router helpers are ready for user-story work.

---

## Phase 3: User Story 1 - Publish Skill Versions From The Browser (Priority: P1) - MVP

**Goal**: A platform admin can create a skill package, enter/upload a manifest candidate, validate it, publish an immutable version, and grant tenants entirely from browser pages.

**Independent Test**: Starting from an empty local QA environment, log in as platform admin, create `calendar-assistant`, submit a YAML or JSON manifest candidate, validate inline findings, prove blocked publication while findings are blocking, publish after passing validation, grant Acme, and capture browser screenshots without feature-action curl.

### Tests for User Story 1

- [ ] T015 [P] [US1] Add platform-admin route tests for package list, package create GET/POST, field errors, duplicate package conflict, and package detail redirects in `tests/integration/api/test_admin_skill_registry_ui.py`
- [ ] T016 [P] [US1] Add platform-admin route tests for manifest paste/upload, parse errors, schema errors, safe summary rendering, and raw manifest omission in `tests/integration/api/test_admin_skill_registry_ui.py`
- [ ] T017 [P] [US1] Add platform-admin route tests for candidate validation findings, blocked publish, successful publish, immutable version detail, and grant form save in `tests/integration/api/test_admin_skill_registry_ui.py`
- [ ] T018 [P] [US1] Add page model tests for package creation, candidate summary, grouped validation findings, publish gate state, version provenance, and grant summary in `tests/unit/api/test_skill_registry_ui_models.py`

### Implementation for User Story 1

- [ ] T019 [US1] Implement platform-admin `GET /admin/skill-registry/ui/packages/new` and `POST /admin/skill-registry/ui/packages` in `src/multi_agent_platform/api/routers/admin_skill_registry.py`
- [ ] T020 [US1] Implement platform-admin package creation template with slug, display name, description, owner/steward, lifecycle intent, safe docs summary, field errors, and success redirect in `src/multi_agent_platform/web_admin/templates/skill_registry/package_create.html`
- [ ] T021 [US1] Update platform-admin package list actions, filters, empty state, and create-package entry point in `src/multi_agent_platform/web_admin/templates/skill_registry/package_list.html`
- [ ] T022 [US1] Implement platform-admin `GET/POST /admin/skill-registry/ui/packages/{slug}/candidate` with structured YAML/JSON parsing, upload precedence, v1 schema validation, candidate revision, digests, safe summary, and raw payload omission in `src/multi_agent_platform/api/routers/admin_skill_registry.py`
- [ ] T023 [US1] Implement platform-admin manifest candidate form with paste/upload controls, artifact digest/reference, approved integration refs, validation reason, candidate revision, parse/schema errors, and safe summary in `src/multi_agent_platform/web_admin/templates/skill_registry/package_candidate_form.html`
- [ ] T024 [US1] Implement platform-admin `POST /admin/skill-registry/ui/packages/{slug}/candidate/validate` with current candidate revision checks and grouped inline findings in `src/multi_agent_platform/api/routers/admin_skill_registry.py`
- [ ] T025 [US1] Update validation finding grouping and safe remediation rendering in `src/multi_agent_platform/web_admin/templates/skill_registry/components/validation_findings.html`
- [ ] T026 [US1] Implement platform-admin `POST /admin/skill-registry/ui/packages/{slug}/candidate/publish` gated by current passing validation, duplicate semantic version checks, lifecycle state, and stale revision handling in `src/multi_agent_platform/api/routers/admin_skill_registry.py`
- [ ] T027 [US1] Update package detail with candidate status, validation action, publish action, stale conflict banner, version lineage, grant summary, and audit timeline in `src/multi_agent_platform/web_admin/templates/skill_registry/package_detail.html`
- [ ] T028 [US1] Update immutable version detail with pinned version, manifest/artifact digests, validation evidence, safe manifest summary, provenance, smoke-test expectations, grant action, and redaction notice in `src/multi_agent_platform/web_admin/templates/skill_registry/package_version_detail.html`
- [ ] T029 [US1] Implement platform-admin `GET/POST /admin/skill-registry/ui/packages/{slug}/versions/{semantic_version}/grants` for one-or-many tenant grants, removals affecting future discovery only, grant revision checks, and safe confirmation in `src/multi_agent_platform/api/routers/admin_skill_registry.py`
- [ ] T030 [US1] Implement platform-admin tenant availability grant form with selected tenants, current availability list, grant reason, grant revision, empty state, stale conflict, and safe cross-tenant summaries in `src/multi_agent_platform/web_admin/templates/skill_registry/tenant_grant_form.html`

**Checkpoint**: User Story 1 is fully functional and independently testable as the platform-admin MVP.

---

## Phase 4: User Story 2 - Install And Configure Granted Skills From The Browser (Priority: P2)

**Goal**: A tenant admin can discover granted versions, install one, configure credential references without raw secrets, run or refresh smoke-test evidence, and understand readiness from browser pages.

**Independent Test**: Log in as Acme tenant admin after US1 grants Acme, discover the granted version, install it, configure credentials using picker/delegated metadata controls, enqueue or refresh smoke tests, and confirm readiness state without feature-action curl.

### Tests for User Story 2

- [ ] T031 [P] [US2] Add tenant-admin route tests for available versions, Acme authorized discovery, Globex empty discovery, safe summaries, and install action visibility in `tests/integration/api/test_admin_skill_registry_ui.py`
- [ ] T032 [P] [US2] Add tenant-admin route tests for install POST, installation list, installation detail, exact pinned version, readiness state, and no raw payload rendering in `tests/integration/api/test_admin_skill_registry_ui.py`
- [ ] T033 [P] [US2] Add tenant-admin route tests for credential picker options, delegated metadata fields, forbidden raw secret fields, no arbitrary reference identifier entry, wrong-scope/revoked/missing findings, and readiness recompute in `tests/integration/api/test_admin_skill_registry_ui.py`
- [ ] T034 [P] [US2] Add tenant-admin route tests for smoke-test enqueue, queued/running immediate response, final status refresh, safe fixture summaries, and blocked-by-policy states in `tests/integration/api/test_admin_skill_registry_ui.py`
- [ ] T035 [P] [US2] Add page model tests for available versions, install action state, credential readiness, smoke-test evidence, readiness findings, and pinned-version messaging in `tests/unit/api/test_skill_registry_ui_models.py`

### Implementation for User Story 2

- [ ] T036 [US2] Implement tenant-admin `GET /admin/skill-registry/ui/available-versions?tenant_id=...` with authorized granted versions, credential requirements, smoke-test expectations, compatibility, install actions, and empty state in `src/multi_agent_platform/api/routers/admin_skill_registry.py`
- [ ] T037 [US2] Implement tenant-admin available versions template with safe package summaries, grant status, install controls, withdrawal/quarantine indicators, and Globex empty state in `src/multi_agent_platform/web_admin/templates/skill_registry/available_versions.html`
- [ ] T038 [US2] Implement tenant-admin `POST /admin/skill-registry/ui/installations` with granted-version checks, tenant-scope checks, exact version pinning, idempotency, safe failures, and redirect to detail in `src/multi_agent_platform/api/routers/admin_skill_registry.py`
- [ ] T039 [US2] Update tenant-admin installation list with ready/blocked/smoke failed/quarantined/withdrawn states, exact package versions, credential status, smoke status, binding status, and empty state in `src/multi_agent_platform/web_admin/templates/skill_registry/installation_list.html`
- [ ] T040 [US2] Update tenant-admin installation detail with exact package version, installation version, revision token, readiness findings, credential status, smoke-test status/history, compatibility, quarantine/runtime blocks, audit, and pinned-version note in `src/multi_agent_platform/web_admin/templates/skill_registry/installation_detail.html`
- [ ] T041 [US2] Implement tenant-admin `GET/POST /admin/skill-registry/ui/installations/{installation_id}/credentials` with tenant-authorized picker options, predefined delegated metadata fields, revision token checks, readiness recompute, and safe failure mapping in `src/multi_agent_platform/api/routers/admin_skill_registry.py`
- [ ] T042 [US2] Implement tenant-admin credential configuration template with one row per requirement, picker controls, delegated metadata controls, no raw secret fields, per-requirement readiness findings, and stale conflict rendering in `src/multi_agent_platform/web_admin/templates/skill_registry/installation_configure.html`
- [ ] T043 [US2] Update readiness component with satisfied, missing, revoked, unauthorized, wrong-scope, incompatible, blocked, ready, quarantined, withdrawn, and corrective guidance states in `src/multi_agent_platform/web_admin/templates/skill_registry/components/readiness_panel.html`
- [ ] T044 [US2] Implement tenant-admin `POST /admin/skill-registry/ui/installations/{installation_id}/smoke-tests` with revision token checks, policy checks, queued job enqueue, duplicate handling, refresh URL, and safe evidence state in `src/multi_agent_platform/api/routers/admin_skill_registry.py`
- [ ] T045 [US2] Update smoke-test history component with queued, running, passed, failed, skipped, blocked, timeout, last-run time, safe fixture identity, safe evidence summary, and redacted failure reasons in `src/multi_agent_platform/web_admin/templates/skill_registry/components/smoke_test_history.html`

**Checkpoint**: User Story 2 is fully functional and independently testable for tenant-admin install, credential, smoke-test, and readiness workflows.

---

## Phase 5: User Story 3 - Preview Binding Eligibility From The Browser (Priority: P3)

**Goal**: A tenant admin can choose an authorized profile or workflow-role context and preview whether an installed skill version may be bound under existing policy.

**Independent Test**: From a tenant installation detail page, choose an authorized context, submit preview, and see allowed or denied results with pinned versions and redacted policy/readiness reasons.

### Tests for User Story 3

- [ ] T046 [P] [US3] Add tenant-admin route tests for eligibility context option filtering, allowed result rendering, denied result rendering, redacted policy reasons, and pinned version evidence in `tests/integration/api/test_admin_skill_registry_ui.py`
- [ ] T047 [P] [US3] Add page model tests for binding eligibility preview form options, allow/deny summaries, remediation guidance, and existing binding pinning language in `tests/unit/api/test_skill_registry_ui_models.py`

### Implementation for User Story 3

- [ ] T048 [US3] Implement tenant-admin authorized profile and workflow-role context loading for eligibility preview in `src/multi_agent_platform/api/ui/skill_registry.py`
- [ ] T049 [US3] Implement tenant-admin `POST /admin/skill-registry/ui/installations/{installation_id}/eligibility-preview` with revision token checks, tenant access, policy preview delegation, and safe allow/deny result mapping in `src/multi_agent_platform/api/routers/admin_skill_registry.py`
- [ ] T050 [US3] Update binding eligibility component with context selector, allowed/denied status, exact installation version, package version, readiness, credential, policy, compatibility, quarantine reasons, remediation, and pinned binding note in `src/multi_agent_platform/web_admin/templates/skill_registry/components/policy_eligibility.html`
- [ ] T051 [US3] Integrate the eligibility preview panel and result state into tenant-admin installation detail in `src/multi_agent_platform/web_admin/templates/skill_registry/installation_detail.html`

**Checkpoint**: User Story 3 is fully functional and independently testable from the tenant installation detail page.

---

## Phase 6: User Story 4 - Recover From Browser Stale Revision Conflicts (Priority: P4)

**Goal**: Platform and tenant admins see clear browser conflict messages when stale candidate, grant, credential, readiness, smoke-test, or binding-related submissions are rejected without state changes.

**Independent Test**: Open the same mutable workflow in two browser sessions, submit in one, submit stale data in the other, confirm no stale change applies, safe audit evidence exists, and the second session can reload latest state and retry.

### Tests for User Story 4

- [ ] T052 [P] [US4] Add two-session platform-admin stale conflict tests for candidate validation, candidate publish, and tenant grant revision submissions in `tests/integration/api/test_admin_skill_registry_ui.py`
- [ ] T053 [P] [US4] Add two-session tenant-admin stale conflict tests for credential configuration, smoke-test action, and eligibility preview revision submissions in `tests/integration/api/test_admin_skill_registry_ui.py`
- [ ] T054 [P] [US4] Add safe audit tests for rejected stale browser actions without raw submitted payloads in `tests/unit/admin/test_skill_audit_redaction.py`

### Implementation for User Story 4

- [ ] T055 [US4] Map service stale revision errors into `RevisionConflictView` reload/retry contexts for platform-admin and tenant-admin forms in `src/multi_agent_platform/api/ui/skill_registry.py`
- [ ] T056 [US4] Add hidden revision tokens and stale conflict handling to platform-admin candidate, validate, publish, and grant POST handlers in `src/multi_agent_platform/api/routers/admin_skill_registry.py`
- [ ] T057 [US4] Add hidden revision tokens and stale conflict handling to tenant-admin credential, smoke-test, and eligibility POST handlers in `src/multi_agent_platform/api/routers/admin_skill_registry.py`
- [ ] T058 [US4] Render stale conflict messages with no applied state, no raw submitted payloads, reload-latest action, retry path, and audit evidence reference in `src/multi_agent_platform/web_admin/templates/skill_registry/components/stale_conflict.html`

**Checkpoint**: User Story 4 stale conflict protection is testable across platform-admin and tenant-admin browser sessions.

---

## Phase 7: User Story 5 - Preserve Tenant Isolation And Redaction In Every UI Page (Priority: P5)

**Goal**: Every browser page enforces tenant isolation, role-aware denials, safe empty states, and redaction of raw package, credential, fixture, validation, smoke-test, audit, and cross-tenant data.

**Independent Test**: Acme can discover and inspect its granted package and installation, Globex cannot discover or inspect Acme-only resources or direct links, same-tenant role failures render denied, and screenshots omit protected content.

### Tests for User Story 5

- [ ] T059 [P] [US5] Add cross-tenant route tests for Globex unavailable versions, direct version links, installation links, credential pages, smoke-test actions, eligibility previews, and audit evidence absence in `tests/integration/api/test_admin_skill_registry_ui.py`
- [ ] T060 [P] [US5] Add same-tenant unauthorized role denial tests for protected skill lifecycle pages and POST actions in `tests/integration/api/test_admin_skill_registry_ui.py`
- [ ] T061 [P] [US5] Add template redaction tests covering raw package payloads, raw manifest input, raw credential values, provider tokens, unsafe docs, unsafe fixtures, raw smoke logs, and cross-tenant data in `tests/integration/api/test_admin_skill_registry_ui.py`
- [ ] T062 [P] [US5] Add page model tests for denied, not found, empty, blocked, validation-failed, smoke-test-failed, quarantined, withdrawn, stale-conflict, and success states in `tests/unit/api/test_skill_registry_ui_models.py`

### Implementation for User Story 5

- [ ] T063 [US5] Centralize tenant access checks for UI GET/POST handlers so cross-tenant links render absent/not found and same-tenant role failures render denied in `src/multi_agent_platform/api/routers/admin_skill_registry.py`
- [ ] T064 [US5] Enforce redaction-safe page context and screenshot-safe summaries for every skill registry page model in `src/multi_agent_platform/api/ui/skill_registry.py`
- [ ] T065 [US5] Update package, version, available-version, installation, credential, readiness, smoke-test, eligibility, and audit templates to render safe empty/blocked/denied/not-found states without protected detail in `src/multi_agent_platform/web_admin/templates/skill_registry/index.html`
- [ ] T066 [US5] Update audit timeline component to show safe lifecycle evidence for browser actions, denials, stale conflicts, redactions, and tenant-scoped events without raw payloads in `src/multi_agent_platform/web_admin/templates/skill_registry/components/audit_timeline.html`

**Checkpoint**: User Story 5 isolation and redaction guarantees are independently testable across all browser pages.

---

## Phase 8: User Story 6 - Complete QA Walkthrough With Browser Actions (Priority: P6)

**Goal**: The QA UI guide and screenshot evidence prove that all primary lifecycle actions are performed through browser pages, with terminal commands limited to setup, diagnostics, server startup, and automated evidence collection.

**Independent Test**: `qa014_ui.md` contains no curl, SQL, or direct API commands for primary lifecycle actions; screenshots exist for package creation, manifest entry/upload, validation, publication, grants, discovery, install, credentials, readiness/smoke, eligibility, conflict, Acme visibility, Globex absence/denial, and redaction checks.

### Tests for User Story 6

- [ ] T067 [P] [US6] Add docs tests that fail if `specs/014-skill-registry-lifecycle/qa014_ui.md` includes curl, SQL, or direct API commands for feature actions outside setup, diagnostics, server startup, or automated evidence collection in `tests/docs/test_skill_registry_docs.py`
- [ ] T068 [P] [US6] Add browser-flow integration tests for the complete platform-admin package-to-grant walkthrough in `tests/integration/api/test_skill_registry_browser_flows.py`
- [ ] T069 [P] [US6] Add browser-flow integration tests for the complete tenant-admin discovery-to-readiness-to-eligibility walkthrough in `tests/integration/api/test_skill_registry_browser_flows.py`
- [ ] T070 [P] [US6] Add browser-flow integration tests for stale conflict recovery, Acme visibility, Globex absence/denial, and redaction evidence in `tests/integration/api/test_skill_registry_browser_flows.py`

### Implementation for User Story 6

- [ ] T071 [US6] Rewrite `specs/014-skill-registry-lifecycle/qa014_ui.md` so package creation, manifest entry/upload, validation, publication, tenant grants, discovery, installation, credentials, smoke tests, readiness, eligibility, stale conflict, tenant isolation, and redaction are browser steps with screenshots and no feature-action curl
- [ ] T072 [US6] Regenerate platform-admin browser screenshots for login, empty packages, package create, manifest candidate, validation findings, blocked publish, successful publish, version detail, and tenant grant under `output/playwright/qa014_ui`
- [ ] T073 [US6] Regenerate tenant-admin browser screenshots for Acme login, available versions, install, blocked detail, credential picker, readiness/smoke status, ready detail, and binding eligibility under `output/playwright/qa014_ui`
- [ ] T074 [US6] Regenerate isolation and conflict browser screenshots for stale revision recovery, Acme visibility, Globex empty discovery, Globex direct-link absence/denial, same-tenant denied state, and redaction scan under `output/playwright/qa014_ui`

**Checkpoint**: User Story 6 documentation and evidence are independently reviewable and prove browser-first QA.

---

## Final Phase: Polish And Cross-Cutting Verification

**Purpose**: Validate focused Spec 014 behavior, docs, formatting, and browser evidence after all selected user stories are complete.

- [ ] T075 [P] Run focused UI model and router tests with `uv run pytest tests/unit/api/test_skill_registry_ui_models.py tests/unit/api/test_admin_skill_registry_router.py tests/unit/auth/test_skill_policy.py` and fix failures in `src/multi_agent_platform/api/ui/skill_registry.py`
- [ ] T076 [P] Run focused Spec 014 integration tests with `uv run pytest tests/integration/api/test_admin_skill_registry_ui.py tests/integration/api/test_skill_registry_browser_flows.py tests/integration/skill_registry` and fix failures in `src/multi_agent_platform/api/routers/admin_skill_registry.py`
- [ ] T077 [P] Run docs tests with `uv run pytest tests/docs/test_skill_registry_docs.py` and fix failures in `specs/014-skill-registry-lifecycle/qa014_ui.md`
- [ ] T078 [P] Run `uv run ruff check .` and fix lint failures in `src/multi_agent_platform/api/routers/admin_skill_registry.py`
- [ ] T079 [P] Run `uv run ruff format --check .` and format changed Python files in `src/multi_agent_platform/api/ui/skill_registry.py`
- [ ] T080 [P] Run `uv run mypy src` and fix typing failures in `src/multi_agent_platform/api/schemas/skill_registry.py`
- [ ] T081 Run relevant browser verification against `http://127.0.0.1:8000/admin/skill-registry/ui/packages` and update screenshot evidence under `output/playwright/qa014_ui`
- [ ] T082 Run coverage gate with `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90` and fix remaining Spec 014 regressions in `tests/integration/api/test_admin_skill_registry_ui.py`

---

## Dependencies And Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion; blocks all browser story implementation.
- **User Story 1 (Phase 3)**: Depends on Foundational; MVP platform-admin path.
- **User Story 2 (Phase 4)**: Depends on Foundational and needs a published/granted version from US1 for full end-to-end validation.
- **User Story 3 (Phase 5)**: Depends on Foundational and needs an installation from US2 for full end-to-end validation.
- **User Story 4 (Phase 6)**: Depends on Foundational and can be applied incrementally to US1-US3 mutable forms.
- **User Story 5 (Phase 7)**: Depends on Foundational and should harden each page as it lands; complete after US1-US4 routes exist.
- **User Story 6 (Phase 8)**: Depends on implemented US1-US5 browser surfaces.
- **Polish**: Depends on all selected stories being complete.

### User Story Dependencies

- **US1 (P1)**: MVP and prerequisite for granted tenant discovery.
- **US2 (P2)**: Uses US1 grant output but remains independently testable with seeded granted versions.
- **US3 (P3)**: Uses US2 installation output but remains independently testable with seeded installations.
- **US4 (P4)**: Cross-cuts mutable browser forms from US1-US3.
- **US5 (P5)**: Cross-cuts every UI route and template.
- **US6 (P6)**: Documentation and evidence layer over completed browser workflows.

### Parallel Opportunities

- T002, T003, and T004 can run in parallel after T001 starts.
- T005, T008, and T011 can run in parallel before implementation.
- US1 tests T015-T018 can run in parallel, then US1 implementation proceeds T019-T030.
- US2 tests T031-T035 can run in parallel, then US2 implementation proceeds T036-T045.
- US3 tests T046-T047 can run in parallel, then US3 implementation proceeds T048-T051.
- US4 tests T052-T054 can run in parallel, then stale conflict implementation proceeds T055-T058.
- US5 tests T059-T062 can run in parallel, then isolation/redaction implementation proceeds T063-T066.
- US6 tests T067-T070 can run in parallel after browser routes exist; screenshot tasks T072-T074 can be split by platform-admin, tenant-admin, and isolation evidence.
- Polish tasks T075-T080 can run in parallel before T081 and T082.

---

## Parallel Examples

### User Story 1

```bash
Task: "T015 platform-admin package create route tests in tests/integration/api/test_admin_skill_registry_ui.py"
Task: "T016 platform-admin manifest candidate route tests in tests/integration/api/test_admin_skill_registry_ui.py"
Task: "T017 platform-admin validate/publish/grant route tests in tests/integration/api/test_admin_skill_registry_ui.py"
Task: "T018 platform-admin page model tests in tests/unit/api/test_skill_registry_ui_models.py"
```

### User Story 2

```bash
Task: "T031 tenant-admin available versions tests in tests/integration/api/test_admin_skill_registry_ui.py"
Task: "T033 tenant-admin credential picker tests in tests/integration/api/test_admin_skill_registry_ui.py"
Task: "T034 tenant-admin smoke-test route tests in tests/integration/api/test_admin_skill_registry_ui.py"
Task: "T035 tenant-admin page model tests in tests/unit/api/test_skill_registry_ui_models.py"
```

### User Story 6

```bash
Task: "T067 browser-first docs guard in tests/docs/test_skill_registry_docs.py"
Task: "T068 platform-admin browser-flow integration tests in tests/integration/api/test_skill_registry_browser_flows.py"
Task: "T069 tenant-admin browser-flow integration tests in tests/integration/api/test_skill_registry_browser_flows.py"
Task: "T070 conflict/isolation/redaction browser-flow integration tests in tests/integration/api/test_skill_registry_browser_flows.py"
```

---

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 for User Story 1.
3. Validate that platform admins can create, submit, validate, publish, and grant from the browser without feature-action curl.
4. Stop and demo the platform-admin MVP before expanding tenant workflows.

### Incremental Delivery

1. Add US1 platform-admin package-to-grant browser workflow.
2. Add US2 tenant-admin discovery, install, credential, smoke-test, and readiness workflow.
3. Add US3 tenant-admin binding eligibility preview.
4. Add US4 stale conflict recovery across mutable browser forms.
5. Add US5 isolation and redaction hardening across every route/template.
6. Add US6 browser-first QA guide and screenshot evidence.

### Validation Discipline

- Write the route, template, docs, and browser-flow tests before implementation for each story.
- Keep JSON API endpoints available for automation and diagnostics, but remove them from primary QA feature actions.
- Confirm each browser page renders safe summaries only and every screenshot remains redaction-safe.
- Run focused Spec 014 tests, docs tests, Ruff, format, mypy, browser verification, and the coverage gate before marking the feature complete.
