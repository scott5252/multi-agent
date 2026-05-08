# Tasks: Workflow React Live Data

**Input**: Design documents from `/specs/050-workflow-react-live-data/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Required by the spec. Write or update tests before implementation where practical.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm generated design artifacts and active queue state before implementation.

- [X] T001 Verify Spec 050 design artifacts in specs/050-workflow-react-live-data/plan.md, specs/050-workflow-react-live-data/research.md, specs/050-workflow-react-live-data/data-model.md, specs/050-workflow-react-live-data/quickstart.md, and specs/050-workflow-react-live-data/contracts/workflow-react-live-data-contract.md
- [X] T002 Verify active feature context in .specify/feature.json and queue status in specs/_autopilot/remove-mock-data-roadmap/queue.json

---

## Phase 2: Foundational Tests (Blocking Prerequisites)

**Purpose**: Add executable expectations for live workflow projections, empty states, seeded data, tenant isolation, generated contracts, frontend behavior, and scanner guardrails before implementation.

- [X] T003 [P] Update workflow builder schema tests for provenance, empty-state metadata, pagination/filter metadata, safe artifact references, and unsafe workflow text rejection in tests/unit/api/test_admin_workflow_builder_schema.py
- [X] T004 [P] Update workflow builder contract tests for live registry/detail/publish-gate/version/create routes and retired deterministic workflow defaults in tests/contract/test_workflow_builder_contract.py
- [X] T005 [P] Add workflow live-data route tests for empty database behavior, seeded database behavior, Auth0-shaped principal behavior, local-principal behavior, tenant denial, and redaction safety in tests/integration/api/test_admin_workflow_ui.py
- [X] T006 [P] Update workflow registry API integration tests for durable create/save/validate/restore/copy/publish state and stale conflict behavior in tests/integration/api/test_admin_workflows_api.py
- [X] T007 [P] Add workflow projection service tests for live registry rows, latest active draft resolution, published bundle detail, publish-gate evidence, sharing summaries, and unavailable states in tests/unit/admin/test_workflow_builder_service.py
- [X] T008 [P] Add workflow repository/service tests for bounded list filters, search, status, scope, and pagination over durable workflow records in tests/unit/admin/test_workflow_registry_service.py
- [X] T009 [P] Update workflow query performance tests to catch N+1 registry/detail/publish-gate projections in tests/performance/workflows/test_workflow_builder_queries.py
- [X] T010 [P] Update live-data scanner tests for `DEFAULT_DRAFT_ID`, `DEFAULT_LINEAGE_ID`, `draft-rev-qa030`, fake graph nodes, fake publish evidence, fake audit references, generated contracts, and built assets in tests/unit/admin/test_live_data_inventory_scanner.py
- [X] T011 [P] Update frontend workflow registry tests for empty state, seeded live rows, backend pagination/filter metadata, and no production fixture imports in frontend/admin/src/components/workflows/WorkflowBuilderPage.test.tsx
- [X] T012 [P] Update frontend workflow graph/reference/publish tests for live graph preview, unavailable graph state, live references, publish-gate evidence, and stale conflicts in frontend/admin/src/components/workflows/WorkflowGraphPanel.test.tsx, frontend/admin/src/components/workflows/WorkflowReferencePicker.test.tsx, and frontend/admin/src/components/workflows/WorkflowPublishPanel.test.tsx
- [X] T013 [P] Add QA seed helper tests for empty and seeded workflow setup in tests/integration/api/test_admin_workflow_ui.py
- [X] T014 [P] Update generated contract check expectations for workflow live-data schemas in tests/contract/test_admin_react_contract.py

**Checkpoint**: Tests define the expected live workflow contract and fail until implementation is complete.

---

## Phase 3: User Story 1 - Browse Live Workflow Records (Priority: P1) MVP

**Goal**: Replace deterministic workflow registry/create payloads with live workflow list projections, truthful empty states, backend-owned filters, and create actions.

**Independent Test**: With empty and seeded QA databases, request workflow registry/create routes and verify live durable rows or honest empty states with no fixed workflow defaults.

- [X] T015 [US1] Extend workflow React schemas with provenance, empty-state, pagination, filter, and list metadata fields in src/multi_agent_platform/api/schemas/admin_workflow_builder.py
- [X] T016 [US1] Add workflow live projection helper types and safe summary functions for registry/create envelopes in src/multi_agent_platform/admin/workflow_builder.py
- [X] T017 [US1] Implement live workflow registry projection from WorkflowRegistryRepository and WorkflowRegistryService list results in src/multi_agent_platform/admin/workflow_builder.py
- [X] T018 [US1] Implement truthful empty workflow registry and create-state projections with backend-owned provenance and allowed create actions in src/multi_agent_platform/admin/workflow_builder.py
- [X] T019 [US1] Wire /admin/app/workflows/registry.json and /admin/app/workflows/create.json to live workflow projection dependencies in src/multi_agent_platform/api/routers/admin_react.py
- [X] T020 [US1] Add or update QA050 workflow seed helpers for empty and seeded workflow registry states in tests/integration/api/test_admin_workflow_ui.py
- [X] T021 [US1] Update frontend generated contracts for workflow registry/create envelope metadata in scripts/frontend/generate_admin_react_types.py and frontend/admin/src/api/generated/reactAdminApi.ts
- [X] T022 [US1] Update WorkflowRegistryPage to render empty states, backend filters, pagination metadata, and live create actions in frontend/admin/src/components/workflows/WorkflowRegistryPage.tsx
- [X] T023 [US1] Update workflow client helpers for live registry/create query parameters and typed empty-state responses in frontend/admin/src/api/client.ts
- [X] T024 [US1] Update App workflow routing and tests for empty workflow registry behavior and live registry rows in frontend/admin/src/App.tsx and frontend/admin/src/App.test.tsx

**Checkpoint**: Workflow registry/create surfaces are live or truthfully empty and no longer use fixed workflow rows.

---

## Phase 4: User Story 2 - Inspect Live Drafts, Versions, Graphs, And References (Priority: P2)

**Goal**: Replace deterministic builder/detail/version/lookups/publish-gate payloads with live projections from stored workflow documents, validation, publish evidence, references, and sharing.

**Independent Test**: Seed a workflow with a draft, revision history, validation, graph document, published bundle, and sharing evidence, then verify detail routes render live state and unknown/unauthorized IDs fail safely.

- [X] T025 [US2] Implement latest active draft and explicit draft detail projection from durable workflow records in src/multi_agent_platform/admin/workflow_builder.py
- [X] T026 [US2] Implement graph preview projection from stored workflow documents and existing graph/reference validation helpers in src/multi_agent_platform/admin/workflow_builder.py
- [X] T027 [US2] Implement live reference catalog projection from existing prompt/profile/provider/skill/test-suite/subworkflow lookup services in src/multi_agent_platform/admin/workflow_builder.py
- [X] T028 [US2] Implement live validation summary and draft revision history projection from durable validation and revision records in src/multi_agent_platform/admin/workflow_builder.py
- [X] T029 [US2] Implement live publish-gate evidence projection from existing publish-gate and test-bench evidence services in src/multi_agent_platform/admin/workflow_builder.py
- [X] T030 [US2] Implement live published workflow version detail and sharing projection from durable version bundle and sharing records in src/multi_agent_platform/admin/workflow_builder.py
- [X] T031 [US2] Wire /admin/app/workflows/builder.json, draft detail, version detail, publish-gate, lookups, and legacy route projection to live dependencies in src/multi_agent_platform/api/routers/admin_react.py
- [X] T032 [US2] Update workflow builder schemas for live invalid-document findings, unavailable detail states, version detail metadata, and sharing summaries in src/multi_agent_platform/api/schemas/admin_workflow_builder.py
- [X] T033 [US2] Update WorkflowBuilderPage for explicit durable draft/version parameters, live detail loading, and unavailable/not-found states in frontend/admin/src/components/workflows/WorkflowBuilderPage.tsx
- [X] T034 [US2] Update WorkflowGraphPanel and WorkflowJsonInspector to render live graph previews, validation findings, and redacted document previews in frontend/admin/src/components/workflows/WorkflowGraphPanel.tsx and frontend/admin/src/components/workflows/WorkflowJsonInspector.tsx
- [X] T035 [US2] Update WorkflowReferencePicker, WorkflowValidationPanel, WorkflowRevisionPanel, WorkflowPublishPanel, and WorkflowSharingPanel for live references, validation, revision history, publish evidence, and sharing summaries in frontend/admin/src/components/workflows/WorkflowReferencePicker.tsx, frontend/admin/src/components/workflows/WorkflowValidationPanel.tsx, frontend/admin/src/components/workflows/WorkflowRevisionPanel.tsx, frontend/admin/src/components/workflows/WorkflowPublishPanel.tsx, and frontend/admin/src/components/workflows/WorkflowSharingPanel.tsx
- [X] T036 [US2] Update workflow route and contract tests for unknown IDs, denied IDs, invalid stored graph documents, missing references, stale evidence, and published bundle detail in tests/integration/api/test_admin_workflow_ui.py and tests/contract/test_workflow_builder_contract.py

**Checkpoint**: Builder/detail/version/lookups/publish-gate surfaces render live workflow state and fail safely for missing or unauthorized records.

---

## Phase 5: User Story 3 - Persist Workflow Actions Through Durable Services (Priority: P3)

**Goal**: Ensure create, save, validate, restore, copy, and publish actions call durable workflow services and return persisted success, stale conflict, idempotent replay, validation failure, or publish-gate denial results.

**Independent Test**: Execute workflow actions through backend route tests and Playwright, then verify durable draft revisions, validation records, published bundles, audit summaries, and stale conflicts through API or redaction-safe database evidence.

- [X] T037 [US3] Add live workflow create, restore, and copy React action contracts where missing in src/multi_agent_platform/api/schemas/admin_workflow_builder.py
- [X] T038 [US3] Replace deterministic save, validate, and publish mutation results with durable service calls in src/multi_agent_platform/api/routers/admin_react.py
- [X] T039 [US3] Add React create, restore, and copy route handlers that call existing workflow registry services in src/multi_agent_platform/api/routers/admin_react.py
- [X] T040 [US3] Implement action result projection for persisted success, idempotent replay, validation failure, publish denial, and stale conflict responses in src/multi_agent_platform/admin/workflow_builder.py
- [X] T041 [US3] Preserve safe audit/reference summaries for workflow mutations without raw payloads in src/multi_agent_platform/admin/workflow_builder.py
- [X] T042 [US3] Update frontend workflow mutation helpers for create/save/validate/restore/copy/publish using backend action metadata and generated client idempotency in frontend/admin/src/api/client.ts and frontend/admin/src/utils/adminActionMetadata.ts
- [X] T043 [US3] Update WorkflowSectionForm and WorkflowBuilderPage action flows for live save/validate/publish/restore/copy results and stale conflict recovery in frontend/admin/src/components/workflows/WorkflowSectionForm.tsx and frontend/admin/src/components/workflows/WorkflowBuilderPage.tsx
- [X] T044 [US3] Update workflow mutation tests for persisted success, idempotent replay, stale conflict, validation failure, publish-gate denial, and redaction safety in tests/integration/api/test_admin_workflows_api.py and frontend/admin/src/components/workflows/WorkflowSectionForm.test.tsx
- [X] T045 [US3] Update live-data scanner mappings for Spec 050 workflow deterministic markers and replacement ownership in src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py

**Checkpoint**: Workflow React mutations no longer return fake success and can be verified through durable API/database state.

---

## Phase 6: QA Docs And Validation

**Purpose**: Produce required QA artifacts and run the validation gates for Spec 050.

- [X] T046 Create QA environment file specs/050-workflow-react-live-data/.env.qa050
- [X] T047 Create API and quality guide specs/050-workflow-react-live-data/qa050.md
- [X] T048 Create UI walkthrough specs/050-workflow-react-live-data/qa050_ui.md
- [X] T049 Create manual QA user guide specs/050-workflow-react-live-data/qa050_user_guide.md
- [X] T050 Create reviewer notes specs/050-workflow-react-live-data/pr_notes.md
- [X] T051 Reconcile Playwright workflow flow and post-UI API/database evidence in specs/_autopilot/remove-mock-data-roadmap/050-workflow-react-live-data/validation.yml
- [X] T052 Run focused backend tests for Spec 050 schemas, contracts, workflow routes, workflow services, scanner checks, and performance checks
- [X] T053 Run generated TypeScript contract check with uv run python scripts/frontend/generate_admin_react_types.py --check
- [X] T054 Run frontend typecheck, workflow tests, App tests, and build
- [X] T055 Run QA document validation for specs/050-workflow-react-live-data
- [X] T056 Run uv run python scripts/qa/run_spec_qa.py specs/_autopilot/remove-mock-data-roadmap/050-workflow-react-live-data/validation.yml
- [X] T057 Run uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/050-workflow-react-live-data/validation.yml --start-processes
- [X] T058 Run post-UI API/database verification for workflow registry/detail/mutation persistence and save evidence in specs/_autopilot/remove-mock-data-roadmap/050-workflow-react-live-data/status.json
- [X] T059 Run uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa050-after-spec

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 has no dependencies.
- Phase 2 depends on Phase 1 and defines the failing live-data test surface.
- Phase 3 depends on Phase 2 and delivers the MVP workflow registry/create live-data behavior.
- Phase 4 depends on Phase 3 live registry and schema metadata.
- Phase 5 depends on Phase 4 live draft/detail action metadata.
- Phase 6 depends on all implementation phases.

### User Story Dependencies

- **User Story 1 (P1)**: Required MVP; establishes live registry/create projections and empty-state patterns.
- **User Story 2 (P2)**: Depends on live registry state and shared workflow metadata; validates detail, graph, reference, version, sharing, and publish-gate projections.
- **User Story 3 (P3)**: Depends on live draft/detail projections and backend action metadata; validates durable mutations and stale conflicts.

### Parallel Opportunities

- T003 through T014 can be drafted in parallel because they touch distinct test files.
- T016 through T018 can proceed alongside T021 through T024 after schema expectations land.
- T025 through T030 can be split by projection concern after live registry scaffolding lands.
- T042 and T043 can proceed after action contracts in T037 through T040 stabilize.
- T046 through T050 can be drafted in parallel after implementation details settle.

## Implementation Strategy

1. Land test expectations for live workflow registry/detail/mutations, generated contracts, scanner guardrails, frontend states, and query bounds.
2. Implement the smallest MVP: live empty/seeded workflow registry and create-state projections.
3. Add live builder detail, graph, references, validation, publish-gate, version, and sharing projections.
4. Replace fake mutation responses with durable create/save/validate/restore/copy/publish behavior and stale conflict handling.
5. Regenerate contracts and built assets, update scanner mappings, and finish QA docs.
6. Run focused checks, full Spec QA, Playwright, post-UI API/database verification, and curl regression before marking Spec 050 complete.
