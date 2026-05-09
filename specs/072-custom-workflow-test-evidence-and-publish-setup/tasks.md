# Tasks: Custom Workflow Test Evidence And Publish Setup

**Input**: Design artifacts from `specs/072-custom-workflow-test-evidence-and-publish-setup/`  
**Prerequisites**: `spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/workflow-test-evidence-publish-setup.md`, `quickstart.md`

## Phase 1: Setup

- [x] T001 Update AGENTS.md latest Spec Kit plan pointer and verify `.specify/feature.json` references specs/072-custom-workflow-test-evidence-and-publish-setup
- [x] T002 [P] Review existing Test Bench schemas, service, and React adapters in src/multi_agent_platform/api/schemas/admin_test_bench.py, src/multi_agent_platform/testing/agent_bench/react_test_bench.py, src/multi_agent_platform/testing/agent_bench/service.py, and frontend/admin/src/components/testBench
- [x] T003 [P] Review workflow publish gate, workflow validation, and required test readiness behavior in src/multi_agent_platform/admin/workflow_registry/publish_gate.py, src/multi_agent_platform/admin/workflow_registry/validation.py, src/multi_agent_platform/admin/workflow_registry/reference_validation.py, and src/multi_agent_platform/admin/workflow_registry/service.py
- [x] T004 [P] Review workflow builder document editing and publish UI boundaries in frontend/admin/src/components/workflows/workflowDocumentEditor.ts, WorkflowBuilderPage.tsx, WorkflowPublishPanel.tsx, and WorkflowValidationPanel.tsx

## Phase 2: Foundational Evidence Contracts

- [x] T005 Add workflow test requirement editor types and normalization helpers in frontend/admin/src/components/workflows/workflowDocumentEditor.ts
- [x] T006 Add workflow evidence helper tests for requirement creation, freshness summaries, safe artifact labels, and redaction boundaries in frontend/admin/src/components/workflows/workflowTestEvidence.test.ts
- [x] T007 Implement workflow evidence helper module in frontend/admin/src/components/workflows/workflowTestEvidence.ts
- [x] T008 Add or extend backend tests for required test readiness, current revision matching, stale evidence, and publish blocker mapping in tests/unit/admin/test_workflow_registry_service.py and tests/unit/admin/test_workflow_builder_service.py
- [x] T009 Add or extend contract coverage for safe workflow publish evidence summaries in tests/contract/test_workflow_builder_contract.py and tests/contract/test_admin_react_contract.py

## Phase 3: User Story 1 - Create Required Evidence From Workflow Setup (Priority: P1) MVP

**Goal**: Authorized admins can create or select a required Test Bench suite and attach a workflow test requirement for the current draft revision without copying ids.

**Independent Test**: Create or select a required suite from the workflow setup evidence panel, add a deterministic requirement reference, save, reload, and verify the requirement remains attached to the current draft revision.

- [x] T010 [P] [US1] Add frontend tests for empty, existing, selected, and newly generated evidence requirement states in frontend/admin/src/components/workflows/WorkflowBuilderPage.test.tsx
- [x] T011 [P] [US1] Add backend integration coverage for contextual suite visibility, cross-tenant suite denial, and invalid target type rejection in tests/integration/test_admin_react_routes.py
- [x] T012 [US1] Build WorkflowTestEvidencePanel with required suite creation, existing suite selection, safe case template labels, and requirement attachment controls in frontend/admin/src/components/workflows/WorkflowTestEvidencePanel.tsx
- [x] T013 [US1] Wire WorkflowTestEvidencePanel into WorkflowBuilderPage draft state, dirty/save/revert flow, and tenant-aware Test Bench links in frontend/admin/src/components/workflows/WorkflowBuilderPage.tsx
- [x] T014 [US1] Add test requirement data to workflow builder fixtures without raw transcripts or local artifact paths in frontend/admin/src/test/workflowBuilderTestData.ts
- [x] T015 [US1] Ensure workflow create/save documents include normalized `test_requirements` and preserve idempotent full-document save behavior in frontend/admin/src/components/workflows/WorkflowBuilderPage.tsx

## Phase 4: User Story 2 - Run And Inspect Safe Evidence (Priority: P2)

**Goal**: Authorized admins can launch deterministic evidence runs, refresh evidence, and inspect safe pass/fail diagnostics from workflow setup.

**Independent Test**: Launch a deterministic run from workflow setup, refresh evidence, inspect safe diagnostics and artifact references, and verify no raw transcript or local path renders.

- [x] T016 [P] [US2] Add frontend tests for deterministic run launch, evidence refresh, failed diagnostics, stale warning, and artifact redaction in frontend/admin/src/components/workflows/WorkflowBuilderPage.test.tsx
- [x] T017 [P] [US2] Add backend tests for unsupported live provider mode, artifact reference redaction, failed run summaries, and idempotent run launch in tests/integration/test_admin_react_routes.py
- [x] T018 [US2] Add deterministic run launch and refresh controls using existing Test Bench client helpers in frontend/admin/src/components/workflows/WorkflowTestEvidencePanel.tsx
- [x] T019 [US2] Add safe diagnostics, latest run status, case coverage, and opaque artifact reference rendering in frontend/admin/src/components/workflows/WorkflowTestEvidencePanel.tsx
- [x] T020 [US2] Add or update frontend API client helper coverage for Test Bench suite save, case save, run launch, and gate refresh error handling in frontend/admin/src/api/client.ts
- [x] T021 [US2] Ensure evidence panel displays loading, launching, refreshing, passed, failed, stale, denied, and blocked states without layout shifts in frontend/admin/src/styles/admin.css

## Phase 5: User Story 3 - Publish Only With Current Evidence (Priority: P3)

**Goal**: Publish readiness blocks missing, stale, failed, cross-tenant, synthetic, or unsupported evidence and passes only with current deterministic evidence.

**Independent Test**: Attempt publish with missing, stale, failed, and current passing evidence and verify backend-owned blockers or confirmation-ready state are shown with evidence-section links.

- [x] T022 [P] [US3] Add WorkflowPublishPanel tests for evidence-section links, current evidence, stale blockers, and confirmation readiness in frontend/admin/src/components/workflows/WorkflowPublishPanel.test.tsx
- [x] T023 [P] [US3] Add WorkflowValidationPanel tests for required evidence anchors and safe evidence references in frontend/admin/src/components/workflows/WorkflowValidationPanel.test.tsx
- [x] T024 [P] [US3] Add backend publish gate tests for missing, stale, failed, cross-tenant, synthetic, and current passing required evidence in tests/unit/admin/test_workflow_registry_service.py and tests/integration/test_admin_react_routes.py
- [x] T025 [US3] Update WorkflowPublishPanel to link required evidence blockers to `#workflow-test-evidence` while preserving backend-owned decision text in frontend/admin/src/components/workflows/WorkflowPublishPanel.tsx
- [x] T026 [US3] Update WorkflowValidationPanel recovery labels for `test_requirements` findings to target the evidence setup section in frontend/admin/src/components/workflows/WorkflowValidationPanel.tsx
- [x] T027 [US3] Ensure workflow builder and publish summaries never synthesize fake passing evidence or expose raw test transcripts in src/multi_agent_platform/admin/workflow_builder.py and frontend/admin/src/components/workflows

## Phase 6: Security, Tenancy, Redaction, And Curl Coverage

- [x] T028 [P] Add redaction tests proving raw transcripts, raw prompts, completions, provider/tool payloads, credentials, local paths, stack traces, and unauthorized tenant labels are absent from workflow evidence UI fixtures and backend summaries in frontend/admin/src/components/workflows/WorkflowBuilderPage.test.tsx and tests/unit/admin/test_workflow_builder_service.py
- [x] T029 [P] Add tenant-isolation tests for cross-tenant suites, runs, requirements, and publish attempts in tests/integration/test_admin_react_routes.py
- [x] T030 Ensure safe execution-mode denial remains backend-owned for unsupported live provider/tool modes in src/multi_agent_platform/testing/agent_bench/service.py and src/multi_agent_platform/api/routers/admin_react.py
- [x] T031 Review curl_testing.md and update route coverage if Test Bench, workflow setup, evidence, or publish route families changed
- [x] T032 Add deterministic QA seed data with workflow draft, prompt/profile bindings, required suite, passing run, stale run, and failed run states in scripts/qa/seed_workflow_test_evidence_qa072.py

## Phase 7: Documentation And QA Artifacts

- [x] T033 Add Spec 072 QA guide with deterministic setup, negative paths, evidence freshness, publish blockers, and automated evidence in specs/072-custom-workflow-test-evidence-and-publish-setup/qa072.md
- [x] T034 Add Spec 072 browser-first UI walkthrough in specs/072-custom-workflow-test-evidence-and-publish-setup/qa072_ui.md
- [x] T035 Add Spec 072 manual user guide in specs/072-custom-workflow-test-evidence-and-publish-setup/qa072_user_guide.md
- [x] T036 Add Spec 072 QA environment file in specs/072-custom-workflow-test-evidence-and-publish-setup/.env.qa072
- [x] T037 Add Spec 072 PR/reviewer notes and README.md/docs/quickstart.md impact review in specs/072-custom-workflow-test-evidence-and-publish-setup/pr_notes.md
- [x] T038 Update validation manifest with QA seed and desktop/mobile workflow evidence and publish journeys in specs/_autopilot/workflow-setup-roadmap/072-custom-workflow-test-evidence-and-publish-setup/validation.yml
- [x] T039 Update specs/_autopilot/workflow-setup-roadmap/072-custom-workflow-test-evidence-and-publish-setup/status.json with implementation artifact summary and curl coverage decision

## Phase 8: Validation

- [x] T040 Run focused backend tests for workflow builder, publish gates, Test Bench evidence, stale/cross-tenant blockers, and route contracts
- [x] T041 Run focused frontend workflow and Test Bench tests plus frontend typecheck
- [x] T042 Run uv run python scripts/frontend/generate_admin_react_types.py --check
- [x] T043 Run uv run ruff check .
- [x] T044 Run uv run ruff format --check .
- [x] T045 Run uv run mypy src
- [x] T046 Run cd frontend/admin && npm run build
- [x] T047 Run bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/072-custom-workflow-test-evidence-and-publish-setup
- [x] T048 Run uv run python scripts/qa/run_spec_qa.py specs/_autopilot/workflow-setup-roadmap/072-custom-workflow-test-evidence-and-publish-setup/validation.yml
- [x] T049 Run uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/workflow-setup-roadmap/072-custom-workflow-test-evidence-and-publish-setup/validation.yml --start-processes
- [x] T050 Run uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa072-after-spec
- [x] T051 Update specs/_autopilot/workflow-setup-roadmap/072-custom-workflow-test-evidence-and-publish-setup/status.json and specs/_autopilot/workflow-setup-roadmap/queue.json after all validation passes

## Dependencies

- Phase 1 must complete before implementation edits.
- Phase 2 helper and contract work blocks evidence UI wiring.
- User Story 1 is the MVP and must land before run launch and publish gating UI.
- User Story 2 depends on attached suite/requirement state from User Story 1.
- User Story 3 depends on evidence status from User Stories 1 and 2.
- Security/redaction and curl review must complete before QA screenshots and docs finalization.
- Validation must run only after QA docs, validation manifest, seed data, and curl coverage review are complete.

## Parallel Execution Examples

- T002, T003, and T004 can run in parallel during setup.
- T006, T008, and T009 can run in parallel after the implementation shape is confirmed.
- T010 and T011 can run in parallel before US1 implementation.
- T016 and T017 can run in parallel before US2 implementation.
- T022, T023, and T024 can run in parallel before US3 implementation.
- T033, T034, T035, T036, and T037 can be drafted in parallel once implementation behavior is stable.

## Implementation Strategy

1. Normalize workflow `test_requirements` in the editor document and add safe helper coverage.
2. Build a workflow evidence panel that attaches suite requirements and links to Agent Tests without copied ids.
3. Add deterministic run launch, evidence refresh, safe diagnostics, and redaction tests.
4. Connect publish and validation blockers to the evidence panel while preserving backend-owned readiness decisions.
5. Finish QA seed/docs, Playwright journeys, curl coverage review, and full validation before Spec 073.
