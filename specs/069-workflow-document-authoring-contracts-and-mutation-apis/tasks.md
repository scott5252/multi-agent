# Tasks: Workflow Document Authoring Contracts And Mutation APIs

**Input**: Design documents from `/specs/069-workflow-document-authoring-contracts-and-mutation-apis/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/workflow-document-authoring.md, quickstart.md  
**Tests**: Required by spec for backend route behavior, contract generation, tenant isolation, stale/idempotency, invalid documents, frontend type/client behavior, QA docs, Playwright smoke, and curl regression.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Capture current behavior and prepare shared artifacts before implementation.

- [x] T001 Audit current React workflow builder save/create behavior and record findings in specs/069-workflow-document-authoring-contracts-and-mutation-apis/implementation_notes.md
- [x] T002 [P] Add PR reviewer notes scaffold for contract, redaction, idempotency, README/docs quickstart impact, and curl coverage in specs/069-workflow-document-authoring-contracts-and-mutation-apis/pr_notes.md
- [x] T003 [P] Verify validation manifest route hints and update specs/_autopilot/workflow-setup-roadmap/069-workflow-document-authoring-contracts-and-mutation-apis/validation.yml if the implementation changes the smoke path

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared durable model, schema, and generated contract groundwork that all stories require.

- [x] T004 Create additive workflow draft revision idempotency migration in alembic/versions/0023_workflow_document_authoring_idempotency.py
- [x] T005 Update WorkflowDraftRevision idempotency fields in src/multi_agent_platform/db/models/workflow_registry.py
- [x] T006 Add repository lookup and save support for React save idempotency fingerprints in src/multi_agent_platform/db/repositories/workflow_registry.py
- [x] T007 Extend canonical and React workflow editor Pydantic contracts for full document editor state, section summaries, save request, mutation result, idempotency metadata, and validation findings in src/multi_agent_platform/api/schemas/admin_workflow_builder.py
- [x] T008 Update generated React type schema export list for new workflow document contracts in scripts/frontend/generate_admin_react_types.py
- [x] T009 Add shared safe document digest, idempotency scope hash, and section summary helpers in src/multi_agent_platform/admin/workflow_builder.py
- [x] T010 Add focused schema and helper tests for safe text, full document request validation, and generated schema inclusion in tests/contract/test_workflow_builder_contract.py

**Checkpoint**: Durable fields, contracts, and shared helpers are ready for story work.

---

## Phase 3: User Story 1 - Save Complete Workflow Documents (Priority: P1)

**Goal**: An authorized admin saves and reloads a complete workflow document through the React-facing workflow route.

**Independent Test**: Create a workflow draft, submit a complete document with every supported section, reload detail JSON, and verify all sections round-trip from durable state.

### Tests for User Story 1

- [x] T011 [P] [US1] Add React Admin OpenAPI assertions for expanded workflow document save/load contracts in tests/contract/test_admin_react_contract.py
- [x] T012 [P] [US1] Add integration test for full React document save and reload in tests/integration/test_admin_react_routes.py
- [x] T013 [P] [US1] Add workflow registry service unit test proving full roles, prompt/profile references, skills, contracts, nodes, edges, joins, approval gates, subworkflows, tests, and annotations persist in tests/unit/admin/test_workflow_registry_service.py
- [x] T014 [P] [US1] Add frontend API client/type test for full workflow document payloads in frontend/admin/src/components/workflows/WorkflowBuilderPage.test.tsx

### Implementation for User Story 1

- [x] T015 [US1] Extend React workflow builder load projection to include the canonical full document and section summaries in src/multi_agent_platform/admin/workflow_builder.py
- [x] T016 [US1] Extend react_admin_workflow_builder and react_admin_workflow_draft_detail responses to return expanded editor state in src/multi_agent_platform/api/routers/admin_react.py
- [x] T017 [US1] Extend react_admin_workflow_builder_save to accept and persist full document payloads in src/multi_agent_platform/api/routers/admin_react.py
- [x] T018 [US1] Reuse WorkflowRegistryService.save_workflow_draft validation, changed-section behavior, and safe audit summaries for React full document saves in src/multi_agent_platform/admin/workflow_registry/service.py
- [x] T019 [US1] Regenerate generated TypeScript contracts in frontend/admin/src/api/generated/reactAdminApi.ts
- [x] T020 [US1] Update workflow API client imports and save helper payload types in frontend/admin/src/api/client.ts
- [x] T021 [US1] Update WorkflowBuilderPage state assembly to send the full document while preserving current minimal UI controls in frontend/admin/src/components/workflows/WorkflowBuilderPage.tsx
- [x] T022 [US1] Update WorkflowSectionForm display of revision, section summaries, and safe mutation result fields in frontend/admin/src/components/workflows/WorkflowSectionForm.tsx
- [x] T023 [US1] Update workflow builder fixture data for full document editor state in frontend/admin/src/test/workflowBuilderTestData.ts

**Checkpoint**: User Story 1 can save and reload full workflow documents without using raw JSON editor UI.

---

## Phase 4: User Story 2 - Recover From Stale Or Conflicting Saves (Priority: P2)

**Goal**: Stale saves are rejected safely and exact duplicate idempotency submissions replay without duplicate revisions.

**Independent Test**: Submit exact duplicate saves with the same key and payload, then submit stale and same-key/different-payload saves and verify replay/rejection without unsafe data exposure.

### Tests for User Story 2

- [x] T024 [P] [US2] Add repository tests for revision idempotency lookup and mismatch behavior in tests/unit/admin/test_workflow_registry_service.py
- [x] T025 [P] [US2] Add React route tests for idempotent replay, idempotency conflict, and stale conflict in tests/integration/test_admin_react_routes.py
- [x] T026 [P] [US2] Add frontend stale conflict rendering test in frontend/admin/src/components/workflows/WorkflowSectionForm.test.tsx

### Implementation for User Story 2

- [x] T027 [US2] Implement idempotency fingerprint persistence and replay in src/multi_agent_platform/admin/workflow_registry/service.py
- [x] T028 [US2] Implement repository lookup by draft, idempotency key, scope hash, and payload hash in src/multi_agent_platform/db/repositories/workflow_registry.py
- [x] T029 [US2] Return safe stale conflict and idempotency conflict mutation results from src/multi_agent_platform/api/routers/admin_react.py
- [x] T030 [US2] Add idempotency replay metadata to BuilderMutationResult handling in src/multi_agent_platform/admin/workflow_builder.py
- [x] T031 [US2] Update frontend save and stale-conflict flow to preserve reload hrefs and safe messages in frontend/admin/src/components/workflows/WorkflowBuilderPage.tsx

**Checkpoint**: User Story 2 prevents overwrite and duplicate revisions with safe recovery behavior.

---

## Phase 5: User Story 3 - Diagnose Invalid Workflow Document Sections (Priority: P3)

**Goal**: Invalid full documents return section and field-path findings that React can show safely.

**Independent Test**: Submit duplicate keys, missing node references, missing entry node, role graph node mismatch, scope mismatch, unsafe strings, and oversized documents and verify mapped findings or safe problem details.

### Tests for User Story 3

- [x] T032 [P] [US3] Add route tests for duplicate role/node/edge keys, missing edge nodes, role graph node mismatch, and missing entry node in tests/integration/test_admin_react_routes.py
- [x] T033 [P] [US3] Add route tests for cross-tenant save, tenant/platform scope mismatch, unsafe strings, and oversized payload rejection in tests/integration/test_admin_react_routes.py
- [x] T034 [P] [US3] Add validation mapping unit tests for section keys, field paths, graph element IDs, and safe remediation in tests/unit/admin/test_workflow_builder_service.py
- [x] T035 [P] [US3] Add frontend validation finding rendering test in frontend/admin/src/components/workflows/WorkflowValidationPanel.test.tsx

### Implementation for User Story 3

- [x] T036 [US3] Normalize Pydantic and workflow validation exceptions into BuilderValidationFinding objects in src/multi_agent_platform/admin/workflow_builder.py
- [x] T037 [US3] Add React save pre-persistence validation flow and section/field error response handling in src/multi_agent_platform/api/routers/admin_react.py
- [x] T038 [US3] Extend validation section mapping for tests, annotations, references, and metadata in src/multi_agent_platform/admin/workflow_registry/validation.py
- [x] T039 [US3] Ensure safe problem detail and audit redaction for invalid save attempts in src/multi_agent_platform/api/routers/admin_react.py
- [x] T040 [US3] Update WorkflowValidationPanel to display field-path findings without raw payloads in frontend/admin/src/components/workflows/WorkflowValidationPanel.tsx

**Checkpoint**: User Story 3 gives safe, actionable validation feedback for invalid documents.

---

## Phase 6: Documentation, Curl Coverage, And QA

**Purpose**: Complete reviewer guidance, local QA, API regression, and required Spec Kit validation artifacts.

- [x] T041 [P] Update curl_testing.md with deterministic React workflow document create/save/reload/stale/invalid route coverage
- [x] T042 [P] Add Spec 069 QA environment file in specs/069-workflow-document-authoring-contracts-and-mutation-apis/.env.qa069
- [x] T043 [P] Add deterministic QA seed script in scripts/qa/seed_workflow_document_authoring_qa069.py
- [x] T044 [P] Add detailed QA guide in specs/069-workflow-document-authoring-contracts-and-mutation-apis/qa069.md
- [x] T045 [P] Add browser-first QA walkthrough in specs/069-workflow-document-authoring-contracts-and-mutation-apis/qa069_ui.md
- [x] T046 [P] Add reviewer user guide with at least 160 lines in specs/069-workflow-document-authoring-contracts-and-mutation-apis/qa069_user_guide.md
- [x] T047 [P] Document README.md and docs/quickstart.md impact, updating those files if shared onboarding commands changed, in specs/069-workflow-document-authoring-contracts-and-mutation-apis/pr_notes.md README.md docs/quickstart.md
- [x] T048 Update specs/_autopilot/workflow-setup-roadmap/069-workflow-document-authoring-contracts-and-mutation-apis/status.json with curl coverage route family and implementation artifact summary
- [x] T049 Run generated TypeScript freshness check with uv run python scripts/frontend/generate_admin_react_types.py --check
- [x] T050 Run focused backend tests for Spec 069 with uv run pytest tests/contract/test_admin_react_contract.py tests/contract/test_workflow_builder_contract.py tests/integration/test_admin_react_routes.py tests/unit/admin/test_workflow_registry_service.py tests/unit/admin/test_workflow_builder_service.py
- [x] T051 Run frontend workflow tests with cd frontend/admin && npm test -- Workflow
- [x] T052 Run QA document validation with bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/069-workflow-document-authoring-contracts-and-mutation-apis

---

## Phase 7: Spec Validation

**Purpose**: Required validation before starting Spec 070.

- [x] T053 Run uv run ruff check .
- [x] T054 Run uv run ruff format --check .
- [x] T055 Run uv run mypy src
- [x] T056 Run uv run python scripts/qa/run_spec_qa.py specs/_autopilot/workflow-setup-roadmap/069-workflow-document-authoring-contracts-and-mutation-apis/validation.yml
- [x] T057 Run uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/workflow-setup-roadmap/069-workflow-document-authoring-contracts-and-mutation-apis/validation.yml --start-processes
- [x] T058 Run uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa069-after-spec
- [x] T059 Update specs/_autopilot/workflow-setup-roadmap/069-workflow-document-authoring-contracts-and-mutation-apis/status.json and specs/_autopilot/workflow-setup-roadmap/queue.json after all validation passes

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 has no dependencies.
- Phase 2 depends on Phase 1 and blocks all user stories.
- User Story 1 depends on Phase 2 and is the MVP.
- User Story 2 depends on User Story 1 save/load behavior.
- User Story 3 depends on User Story 1 contracts and route flow.
- Phase 6 depends on all user stories.
- Phase 7 depends on Phase 6.

### User Story Dependencies

- **US1**: Enables full document persistence and generated contracts.
- **US2**: Builds on US1 mutation path to add durable idempotency and stale recovery.
- **US3**: Builds on US1 validation path and can run after US1 while US2 is being refined if files are coordinated.

### Parallel Opportunities

- T002 and T003 can run with T001.
- T011 through T014 can be drafted in parallel after Phase 2.
- T024 through T026 can be drafted in parallel after US1 route shape is known.
- T032 through T035 can be drafted in parallel after validation contracts exist.
- T041 through T046 can be prepared in parallel once route names and QA seed data are stable.

## Parallel Example: User Story 1

```bash
# Independent test work once foundational contracts are in place:
Task: "Add React Admin OpenAPI assertions in tests/contract/test_admin_react_contract.py"
Task: "Add integration test for full React document save and reload in tests/integration/test_admin_react_routes.py"
Task: "Add frontend API client/type test in frontend/admin/src/components/workflows/WorkflowBuilderPage.test.tsx"
```

## Implementation Strategy

1. Complete setup and foundational durable/schema work.
2. Deliver US1 full document round-trip first and verify it independently.
3. Add US2 stale/idempotency behavior on the same mutation path.
4. Add US3 validation mapping and negative coverage.
5. Finish docs, curl coverage, QA seed, generated types, frontend tests, Playwright smoke, and curl regression.

## Notes

- Do not create commits, stage files, or push branches during the autopilot run.
- Do not expose raw prompts, completions, secrets, credentials, provider payloads, raw tool payloads, raw test transcripts, stack traces, local filesystem paths, or unauthorized tenant labels in UI, tests, docs, screenshots, curl outputs, or audit summaries.
- Keep lower-level `/admin/workflows/...` APIs supported while extending the React-facing route family.
