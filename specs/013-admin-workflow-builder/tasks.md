# Tasks: Guided Admin Workflow Builder

**Input**: Design documents from `/Users/scottcornell/src/my-projects/multi-agent/specs/013-admin-workflow-builder/`
**Prerequisites**: `/Users/scottcornell/src/my-projects/multi-agent/specs/013-admin-workflow-builder/plan.md`, `/Users/scottcornell/src/my-projects/multi-agent/specs/013-admin-workflow-builder/spec.md`, `/Users/scottcornell/src/my-projects/multi-agent/specs/013-admin-workflow-builder/research.md`, `/Users/scottcornell/src/my-projects/multi-agent/specs/013-admin-workflow-builder/data-model.md`, `/Users/scottcornell/src/my-projects/multi-agent/specs/013-admin-workflow-builder/contracts/`

**Tests**: Tests are required by the feature specification and by the task request. Write each story's tests first and confirm they fail before implementing that story.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested as an independently reviewable increment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and does not depend on incomplete tasks in the same phase.
- **[Story]**: User story label from `/Users/scottcornell/src/my-projects/multi-agent/specs/013-admin-workflow-builder/spec.md`.
- Every task includes at least one exact file path.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the additive files and documentation anchors used by later tasks.

- [ ] T001 [P] Add graph preview module scaffold with a typed public entry point in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/admin/workflow_registry/graph_preview.py`
- [ ] T002 [P] Add reference readiness module scaffold with adapter protocols for prompts, profiles, model routes, skills, subworkflows, contracts, and tests in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/admin/workflow_registry/reference_validation.py`
- [ ] T003 [P] Add publish gate module scaffold with service inputs, result status constants, and digest helpers in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/admin/workflow_registry/publish_gate.py`
- [ ] T004 [P] Add user guide documentation skeleton in `/Users/scottcornell/src/my-projects/multi-agent/docs/admin-workflow-builder.md`
- [ ] T005 [P] Add reviewer testing guide skeleton in `/Users/scottcornell/src/my-projects/multi-agent/docs/admin-workflow-builder-testing.md`
- [ ] T006 [P] Add PR review notes skeleton in `/Users/scottcornell/src/my-projects/multi-agent/docs/admin-workflow-builder-pr-notes.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared policy, schema, metadata, and route foundations that all user stories depend on.

**Critical**: No user story implementation should start until this phase is complete.

### Tests First

- [ ] T007 [P] Add failing auth surface policy tests for editor metadata, lookups, graph preview, revisions, restore, copy, publish gate, UI pages, and publish actions in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/auth/test_policy.py`
- [ ] T008 [P] Add failing shared editor metadata schema tests for section order, field definitions, lookup sources, capabilities, action URLs, and validation code mapping in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/api/test_workflow_builder_schemas.py`
- [ ] T009 [P] Add failing UI view model tests for builder breadcrumbs, action URLs, conflict state, validation summaries, publish readiness, and authorized links in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/api/test_admin_workflow_builder_ui_models.py`
- [ ] T089 [P] Add failing observability tests for save, validation, publish gate, publish, conflict, denial, and reference lookup denial metrics/log fields in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/admin/test_workflow_builder_observability.py`
- [ ] T090 [P] Add failing tenant fairness and bounded-work tests for editor lookups, validation, graph preview, and publish gate requests in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_workflow_builder_api.py`

### Implementation

- [ ] T010 Add workflow builder auth policy entries for every new JSON and server-rendered surface in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/auth/policy.py`
- [ ] T011 Define shared editor metadata, lookup option, capability, action URL, validation mapping, and UI summary schemas in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/schemas/workflow_editor.py`
- [ ] T012 Extend workflow registry response schemas with builder status summaries, revision ids, validation ids, and publish readiness fields in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/schemas/workflow_registry.py`
- [ ] T013 Expand metadata-driven field help and section definitions for the guided builder in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/admin/workflow_registry/field_help.py`
- [ ] T014 Wire shared editor metadata and lookup dependencies through the JSON admin workflow router in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/routers/admin_workflows.py`
- [ ] T015 Wire shared builder page state, scope resolution, and safe error handling through the server-rendered workflow UI router in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/routers/admin_workflow_ui.py`
- [ ] T016 Expand workflow admin UI page models with builder metadata, lookup groups, graph preview summaries, validation groups, and publish gate placeholders in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/ui/admin_workflows.py`
- [ ] T091 Add builder observability helpers for structured log fields, metrics names, and trace/request id propagation in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/admin/workflow_registry/observability.py`
- [ ] T092 Enforce bounded request sizes, reused reliability admission/backpressure guards when available, and local per-tenant in-flight fallback limits with deterministic 429/413 responses for builder validation and publish gate flows in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/routers/admin_workflows.py`
- [ ] T093 Wire builder metrics and structured logging into draft save, validation, publish gate, publish, conflict, denial, and reference lookup denial flows in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/admin/workflow_registry/service.py`

**Checkpoint**: Foundation ready. User story implementation can proceed with consistent policy, schema, metadata, and UI model contracts.

---

## Phase 3: User Story 1 - Create Workflow Drafts Without Raw JSON (Priority: P1) MVP

**Goal**: Authorized platform and tenant admins can create, edit, save, and reload guided workflow drafts through forms and graph-oriented views without editing raw JSON.

**Independent Test**: An authorized admin creates a draft with metadata, roles, sub-agent roles, prompt/profile references, model routing preview links, skill installation references, contracts, graph nodes and edges, a join policy, an approval gate, and a reusable subworkflow reference; after saving and reloading, the authored structure round-trips without using a raw JSON editor.

### Tests for User Story 1

- [ ] T017 [P] [US1] Add failing form schema round-trip tests for `WorkflowBuilderDocument`, nested builder sections, safe JSON serialization, and form payload normalization in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/api/test_workflow_builder_schemas.py`
- [ ] T018 [P] [US1] Add failing reference lookup tests for prompt/profile refs, model routing preview links, skill installation refs, subworkflow choices, and tenant-filtered options in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/admin/test_workflow_builder_references.py`
- [ ] T019 [P] [US1] Add failing graph preview data tests for server-derived nodes, edges, entry node, terminal nodes, field paths, and stable graph element ids in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/admin/test_graph_preview.py`
- [ ] T020 [US1] Add failing optimistic concurrency and unauthorized tenant/platform draft access tests for create, get, save, and stale 409 flows in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_workflow_builder_api.py`
- [ ] T021 [P] [US1] Add failing template rendering tests for registry list, create form, editor sections, graph preview component, read-only JSON inspector, and no-JS save controls in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_workflow_builder_ui.py`
- [ ] T022 [US1] Add failing OpenAPI contract tests for editor metadata, editor lookups, graph preview, draft create, and draft save payloads in `/Users/scottcornell/src/my-projects/multi-agent/tests/contract/test_workflow_builder_contract.py`
- [ ] T094 [P] [US1] Add failing regression tests proving workflow registry entries and published bundles created before the builder remain listable, viewable, copyable where authorized, and publishable through existing lineage behavior in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_workflow_builder_api.py`

### Implementation for User Story 1

- [ ] T023 [US1] Extend the existing draft document schemas with additive guided builder document models, legacy draft coercion, and backward-compatible serialization for metadata, roles, prompt/profile references, skills, contracts, graph, joins, approvals, subworkflows, tests, and editor annotations in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/schemas/workflow_registry.py`
- [ ] T024 [US1] Add graph preview, lookup response, editor section, field definition, and conflict response schemas for builder forms in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/schemas/workflow_editor.py`
- [ ] T025 [P] [US1] Implement server-derived graph projection from the saved builder document in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/admin/workflow_registry/graph_preview.py`
- [ ] T026 [US1] Extend draft create, draft get, and draft save flows to validate guided builder documents and reject stale `base_revision_number` saves without creating revisions in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/admin/workflow_registry/service.py`
- [ ] T027 [US1] Add editor metadata, editor lookup, graph preview, draft create, and draft save handlers that return typed builder schemas in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/routers/admin_workflows.py`
- [ ] T028 [US1] Build registry, create draft, and editor view models that expose guided section data, graph preview data, reference lookup groups, conflict banners, and read-only JSON inspector data in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/ui/admin_workflows.py`
- [ ] T029 [US1] Add server-rendered create and editor routes with tenant/platform scope checks, conflict query handling, and safe 403/404 responses in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/routers/admin_workflow_ui.py`
- [ ] T030 [P] [US1] Update the workflow registry list with create action, scope/status filters, validation badges, publish readiness, and authorized action links in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/workflows/index.html`
- [ ] T031 [P] [US1] Update the guided draft editor sections and make the advanced JSON inspector read-only in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/workflows/draft_editor.html`
- [ ] T032 [P] [US1] Add graph preview and reference picker components for server-rendered fallback markup in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/workflows/components/graph_preview.html` and `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/workflows/components/reference_picker.html`
- [ ] T033 [P] [US1] Add dynamic repeated-section editing, graph preview refresh, unsaved-change warnings, and conflict preservation behavior in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/static/workflow_studio.js`
- [ ] T034 [P] [US1] Add responsive builder layout, graph preview, reference picker, and read-only inspector styling in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/static/workflow_studio.css`
- [ ] T035 [US1] Record safe draft creation, draft update, and stale-save conflict audit events without raw prompts, secrets, credentials, provider payloads, or unauthorized tenant data in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/admin/workflow_registry/service.py`

**Checkpoint**: User Story 1 is independently functional and testable through API round trips and server-rendered pages.

---

## Phase 4: User Story 2 - Validate Readiness Before Publication (Priority: P2)

**Goal**: Admins can run validation and see field-level findings for structural issues, graph issues, prompt/profile readiness, model routing readiness, skill readiness, contract compatibility, approvals, subworkflows, and required tests.

**Independent Test**: A draft with missing prompt versions, an unresolved model route, a missing skill installation, an invalid join policy, a graph cycle without bounds, and a failing required test produces blocking validation findings with stable form and graph locations.

### Tests for User Story 2

- [ ] T036 [P] [US2] Add failing field-level validation finding tests for canonical field paths, section keys, graph element ids, remediation text, blocking flags, and safe links in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/admin/test_workflow_builder_validation.py`
- [ ] T037 [US2] Add failing prompt/profile, model routing preview, provider catalog, skill installation, subworkflow, contract, approval role, and required test readiness validation tests in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/admin/test_workflow_builder_references.py`
- [ ] T038 [P] [US2] Add failing graph policy tests for disconnected nodes, incompatible edge contracts, invalid joins, arbitrary cycles, bounded retry loops, and approval-resume loops in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/admin/test_graph_preview.py`
- [ ] T039 [P] [US2] Add failing validation route integration tests for blocked findings, persisted validation results, superseded validation, and scope-filtered reference evidence in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_workflow_builder_api.py`
- [ ] T040 [P] [US2] Add failing validation panel template rendering tests for grouped findings, field anchors, graph highlights, authorized external links, and no-JS display in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_workflow_builder_ui.py`
- [ ] T041 [US2] Add failing OpenAPI contract tests for validation response fields, reference readiness snapshots, finding locations, and blocked categories in `/Users/scottcornell/src/my-projects/multi-agent/tests/contract/test_workflow_builder_contract.py`

### Implementation for User Story 2

- [ ] T042 [US2] Implement canonical field-path validation for metadata, roles, prompt/profile references, skills, contracts, graph nodes, graph edges, joins, approvals, subworkflows, and tests in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/admin/workflow_registry/validation.py`
- [ ] T043 [US2] Implement scoped reference readiness adapters for prompts, profiles, model routing previews, provider catalog entries, skill installations, subworkflows, contracts, approval roles, and required test evidence in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/admin/workflow_registry/reference_validation.py`
- [ ] T044 [US2] Integrate reference readiness, graph policy, required test status, and finding mapping into validation result creation in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/admin/workflow_registry/validation.py`
- [ ] T045 [P] [US2] Extend graph preview projection with validation badges, cycle summaries, join summaries, approval loop metadata, and graph-to-field mapping in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/admin/workflow_registry/graph_preview.py`
- [ ] T046 [US2] Add validation result, validation finding, reference readiness, required test summary, and graph badge schemas in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/schemas/workflow_editor.py`
- [ ] T047 [US2] Add validation endpoint behavior, editor lookup filtering, reference evidence serialization, and safe 403 handling in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/routers/admin_workflows.py`
- [ ] T048 [US2] Update validation panel grouping, field anchors, graph highlights, severity order, remediation display, and authorized deep links in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/workflows/components/validation_panel.html`
- [ ] T049 [P] [US2] Add inline validation refresh, finding-to-field focus, and graph highlight behavior in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/static/workflow_studio.js`
- [ ] T050 [P] [US2] Add validation badge, blocking/advisory grouping, graph highlight, and reference readiness styles in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/static/workflow_studio.css`
- [ ] T051 [US2] Persist validation request and outcome audit events, supersede stale validation results, and avoid unsafe payloads in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/admin/workflow_registry/service.py`

**Checkpoint**: User Story 2 is independently functional and testable by validating bad drafts and confirming stable, actionable findings.

---

## Phase 5: User Story 3 - Publish Versioned Workflow Bundles Safely (Priority: P3)

**Goal**: Authorized admins can publish validated drafts into the existing immutable bundle lineage, while blocked publish attempts leave the active bundle unchanged and explain every blocking reason.

**Independent Test**: A valid draft publishes as an immutable workflow bundle and becomes active for the selected scope; a draft with any blocking gate condition cannot publish and records safe audit evidence without changing the active published bundle.

### Tests for User Story 3

- [ ] T052 [P] [US3] Add failing publish gate blocking tests for stale validation, missing prompt/profile readiness, failing provider routing, missing skill installation, incompatible subworkflow, missing test evidence, graph policy failure, and authorization denial in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/admin/test_publish_gate.py`
- [ ] T053 [US3] Add failing successful publish and active-bundle-unchanged-on-block tests for immutable bundle creation, active pointer update, idempotency, artifact failure recovery, and pin summaries in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/workflows/test_workflow_builder_publish_gate.py`
- [ ] T054 [P] [US3] Add failing unauthorized tenant/platform publish tests for publish gate and publish confirmation routes in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_workflow_builder_api.py`
- [ ] T055 [US3] Add failing OpenAPI contract tests for publish gate request, publish gate response, publish request, conflict response, and workflow version response pin fields in `/Users/scottcornell/src/my-projects/multi-agent/tests/contract/test_workflow_builder_contract.py`
- [ ] T056 [P] [US3] Add failing publish gate and version detail template tests for blocking reasons, disabled confirmation, ready confirmation, prompt/profile pins, routing provenance, skill pins, subworkflow pins, and test evidence in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_workflow_builder_ui.py`

### Implementation for User Story 3

- [ ] T057 [US3] Add publish gate request, publish gate response, pin summary, required test summary, and publish conflict schemas in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/schemas/workflow_editor.py`
- [ ] T058 [US3] Implement publish gate readiness checks, digest generation, status calculation, idempotent gate ids, and safe audit payload preparation in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/admin/workflow_registry/publish_gate.py`
- [ ] T059 [US3] Require a current ready publish gate or re-run gate checks before publishing a draft in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/admin/workflow_registry/service.py`
- [ ] T060 [P] [US3] Extend workflow bundle compilation with source draft revision, prompt/profile pins, provider routing provenance, skill pins, subworkflow pins, contract compatibility, approval summary, graph summary, test evidence, and publish gate digest in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/admin/workflow_registry/compiler.py`
- [ ] T061 [P] [US3] Extend runtime workflow bundle summary types with builder pin and provenance fields in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/runtime/workflow_bundle.py`
- [ ] T062 [US3] Add publish gate and publish confirmation JSON route behavior with 409 handling for stale, blocked, failed, or mismatched gates in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/routers/admin_workflows.py`
- [ ] T063 [US3] Add server-rendered publish gate review route with scope checks, ready/blocked states, confirmation form, and safe errors in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/routers/admin_workflow_ui.py`
- [ ] T064 [P] [US3] Create publish gate review template with blocking findings, readiness tables, pin summaries, validation freshness, and disabled confirmation behavior in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/workflows/publish_gate.html`
- [ ] T065 [P] [US3] Update published version detail template with source revision, publish gate digest, prompt/profile pins, routing provenance, skill installations, subworkflow pins, contract compatibility, approval summary, graph summary, and test evidence in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/workflows/version_detail.html`
- [ ] T066 [US3] Record publish gate request/outcome, blocked publish, successful publish, and publish authorization denial audit events in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/admin/workflow_registry/service.py`

**Checkpoint**: User Story 3 is independently functional and testable through blocked and successful publish flows.

---

## Phase 6: User Story 4 - Review Revisions And Audit Trail (Priority: P4)

**Goal**: Platform and tenant admins can review draft revisions, validation history, publication attempts, safe audit details, and published lineage without exposing secrets or unauthorized content.

**Independent Test**: After multiple edits, validation runs, a blocked publish attempt, and a successful publish, an authorized admin reviews revision history and audit records showing actors, timestamps, scopes, changed sections, validation outcomes, publish outcomes, and source bundle lineage.

### Tests for User Story 4

- [ ] T067 [P] [US4] Add failing revision history, restore, copy, and stale restore API tests with changed-section summaries in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_workflow_builder_api.py`
- [ ] T068 [P] [US4] Add failing audit trail tests for draft create, save, conflict, validate, publish gate, blocked publish, successful publish, authorization denial, restore, copy, and reference lookup denial safe summaries in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_workflow_builder_audit.py`
- [ ] T069 [P] [US4] Add failing revision history, restore/copy controls, audit link, and published lineage template tests in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_workflow_builder_ui.py`
- [ ] T070 [US4] Add failing OpenAPI contract tests for revision list, copy draft, restore revision, and version detail lineage fields in `/Users/scottcornell/src/my-projects/multi-agent/tests/contract/test_workflow_builder_contract.py`

### Implementation for User Story 4

- [ ] T071 [US4] Implement revision list, safe changed-section summary, copy, restore, and base revision conflict repository helpers in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/db/repositories/workflow_registry.py`
- [ ] T072 [US4] Implement revision history, restore, copy, conflict handling, safe changed-section summaries, and lineage trace service methods in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/admin/workflow_registry/service.py`
- [ ] T073 [US4] Add revision list, copy draft, and restore revision JSON routes with scoped authorization and 409 handling in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/routers/admin_workflows.py`
- [ ] T074 [US4] Add revision history, audit summary, restore/copy capability, and published lineage view models in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/ui/admin_workflows.py`
- [ ] T075 [US4] Add revision history server-rendered route and version detail lineage route wiring in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/routers/admin_workflow_ui.py`
- [ ] T076 [P] [US4] Create revision history template with safe diffs, actors, timestamps, changed sections, validation status, restore/copy controls, and conflict-safe forms in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/workflows/revision_history.html`
- [ ] T077 [US4] Add revision history, publish gate, audit summary, and version lineage links to the draft editor template in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/workflows/draft_editor.html`
- [ ] T078 [US4] Record restore, copy, revision view, audit detail view, and hidden reference denial events with safe summaries in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/admin/workflow_registry/service.py`

**Checkpoint**: User Story 4 is independently functional and testable through revision/audit review flows.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, reviewer evidence, contract cleanup, and final quality checks.

- [ ] T079 [P] Update the user-facing workflow builder guide with authoring, validation, publication, revision, and audit flows in `/Users/scottcornell/src/my-projects/multi-agent/docs/admin-workflow-builder.md`
- [ ] T080 [P] Update reviewer testing instructions with local-principal setup, blocked publish categories, successful publish, stale save conflict, tenant/platform isolation, graph cycle policy, audit evidence, timed authoring under 25 minutes, blocked-reason identification under 2 minutes, scoped endpoint p95 checks, and publish outcome within 2 minutes in `/Users/scottcornell/src/my-projects/multi-agent/docs/admin-workflow-builder-testing.md`
- [ ] T081 [P] Update PR review notes with implementation summary, risk notes, QA evidence checklist, timed acceptance results, p95/publish latency evidence, coverage result placeholder, docs confirmation, and rollback considerations in `/Users/scottcornell/src/my-projects/multi-agent/docs/admin-workflow-builder-pr-notes.md`
- [ ] T082 [P] Add docs tests that verify README links, user guide, testing instructions, PR notes, quickstart commands, and required evidence sections in `/Users/scottcornell/src/my-projects/multi-agent/tests/docs/test_workflow_builder_docs.py`
- [ ] T083 Update the project README with guided workflow builder usage, admin URLs, required validation/publish evidence, and test commands in `/Users/scottcornell/src/my-projects/multi-agent/README.md`
- [ ] T084 Sync reviewer quickstart steps with the implemented routes, local-principal commands, and expected outcomes in `/Users/scottcornell/src/my-projects/multi-agent/specs/013-admin-workflow-builder/quickstart.md`
- [ ] T085 Update the OpenAPI contract with final request/response schema names, publish gate fields, revision endpoints, and backward compatibility notes in `/Users/scottcornell/src/my-projects/multi-agent/specs/013-admin-workflow-builder/contracts/workflow-builder.openapi.yaml`
- [ ] T086 Run `uv run ruff check .` and record the result in `/Users/scottcornell/src/my-projects/multi-agent/docs/admin-workflow-builder-pr-notes.md`
- [ ] T087 Run `uv run ruff format --check .` and `uv run mypy src` and record the results in `/Users/scottcornell/src/my-projects/multi-agent/docs/admin-workflow-builder-pr-notes.md`
- [ ] T088 Run `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90` and record the coverage result in `/Users/scottcornell/src/my-projects/multi-agent/docs/admin-workflow-builder-pr-notes.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational completion and is the MVP.
- **User Story 2 (Phase 4)**: Depends on Foundational completion; it can use fixtures before US1 UI work is complete, but final UI validation anchors depend on US1 editor surfaces.
- **User Story 3 (Phase 5)**: Depends on User Story 2 validation and reference readiness behavior.
- **User Story 4 (Phase 6)**: Depends on Foundational completion for revision review; complete publish audit coverage depends on User Story 3.
- **Polish (Phase 7)**: Depends on the desired story scope being complete.

### User Story Dependencies

- **User Story 1 (P1)**: No dependencies after Foundational.
- **User Story 2 (P2)**: Depends on shared builder document and metadata contracts from Foundational; integrates most naturally after User Story 1.
- **User Story 3 (P3)**: Depends on validation and reference readiness from User Story 2.
- **User Story 4 (P4)**: Can start after Foundational for revision history, then completes after publish audit flows from User Story 3.

### Within Each User Story

- Write the listed tests first and confirm they fail before implementation.
- Implement schemas before services where a service depends on new typed inputs.
- Implement services before API routes.
- Implement UI view models before templates.
- Complete each story checkpoint before moving to the next priority when delivering sequentially.

### Parallel Opportunities

- Setup tasks T001 through T006 can run in parallel.
- Foundational tests T007 through T009 plus T089 and T090 can run in parallel.
- User Story 1 test tasks T017, T018, T019, T021, and T094 can run in parallel; implementation tasks T025, T030, T031, T032, T033, and T034 can run in parallel after their dependencies are clear.
- User Story 2 test tasks T036, T038, T039, and T040 can run in parallel; implementation tasks T045, T049, and T050 can run in parallel after validation schemas exist.
- User Story 3 test tasks T052, T054, and T056 can run in parallel; implementation tasks T060, T061, T064, and T065 can run in parallel after publish gate schemas exist.
- User Story 4 test tasks T067, T068, and T069 can run in parallel; implementation task T076 can run in parallel after UI view models define its context.
- Polish tasks T079, T080, T081, and T082 can run in parallel after story behavior stabilizes.

---

## Parallel Example: User Story 1

```bash
Task T017: Add failing form schema round-trip tests in /Users/scottcornell/src/my-projects/multi-agent/tests/unit/api/test_workflow_builder_schemas.py
Task T018: Add failing reference lookup tests in /Users/scottcornell/src/my-projects/multi-agent/tests/unit/admin/test_workflow_builder_references.py
Task T019: Add failing graph preview data tests in /Users/scottcornell/src/my-projects/multi-agent/tests/unit/admin/test_graph_preview.py
Task T021: Add failing template rendering tests in /Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_workflow_builder_ui.py
```

## Parallel Example: User Story 2

```bash
Task T036: Add failing field-level validation finding tests in /Users/scottcornell/src/my-projects/multi-agent/tests/unit/admin/test_workflow_builder_validation.py
Task T038: Add failing graph policy tests in /Users/scottcornell/src/my-projects/multi-agent/tests/unit/admin/test_graph_preview.py
Task T039: Add failing validation route integration tests in /Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_workflow_builder_api.py
Task T040: Add failing validation panel template rendering tests in /Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_workflow_builder_ui.py
```

## Parallel Example: User Story 3

```bash
Task T052: Add failing publish gate blocking tests in /Users/scottcornell/src/my-projects/multi-agent/tests/unit/admin/test_publish_gate.py
Task T054: Add failing unauthorized publish tests in /Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_workflow_builder_api.py
Task T056: Add failing publish gate and version detail template tests in /Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_workflow_builder_ui.py
```

## Parallel Example: User Story 4

```bash
Task T067: Add failing revision history API tests in /Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_workflow_builder_api.py
Task T068: Add failing audit trail tests in /Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_workflow_builder_audit.py
Task T069: Add failing revision history template tests in /Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_workflow_builder_ui.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1.
4. Stop and validate the independent User Story 1 round-trip test: create, save, reload, render, and conflict-check a guided draft without raw JSON editing.

### Incremental Delivery

1. Deliver Setup and Foundational work.
2. Deliver User Story 1 as the MVP guided authoring experience.
3. Deliver User Story 2 validation findings and readiness checks.
4. Deliver User Story 3 publish gate and immutable publication.
5. Deliver User Story 4 revision and audit review.
6. Finish Polish tasks and record reviewer evidence.

### Parallel Team Strategy

1. One engineer can own schemas and policy from Phase 2.
2. One engineer can own admin workflow registry services in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/admin/workflow_registry/`.
3. One engineer can own JSON/UI routes and view models in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/`.
4. One engineer can own templates and static assets in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/`.
5. One engineer can own docs, reviewer notes, and final QA evidence in `/Users/scottcornell/src/my-projects/multi-agent/docs/`.

---

## Notes

- [P] tasks are parallelizable only when they touch different files and have no same-phase dependency on incomplete work.
- Tests in each story are intentionally first and should fail before implementation begins.
- Keep all builder storage additive to existing workflow registry drafts, revisions, validation results, and published bundles.
- Do not store or render raw secrets, provider tokens, credentials, rendered unsafe prompts, provider responses, or unauthorized tenant data.
- Preserve existing registry behavior for workflows and bundles created before this feature.
