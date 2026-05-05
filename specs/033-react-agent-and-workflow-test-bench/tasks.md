# Tasks: React Agent And Workflow Test Bench

**Input**: Design documents from `specs/033-react-agent-and-workflow-test-bench/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Required. The feature specification mandates backend schema/service
coverage, generated TypeScript drift checks, local-principal and Auth0-shaped
route coverage, tenant isolation, redaction tests, frontend component tests,
Playwright suite/case/run/gate flows, QA docs, and full Spec QA evidence.

**Organization**: Tasks are grouped by user story so each story remains
independently testable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and has no
  dependency on an incomplete task.
- **[Story]**: User story label from `spec.md`.
- Every task includes an exact file path.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare backend, frontend, test, and QA folders for the React test
bench workspace.

- [X] T001 Add backend React test bench schema module in `src/multi_agent_platform/api/schemas/admin_test_bench.py`
- [X] T002 [P] Add React test bench aggregation/service module in `src/multi_agent_platform/testing/agent_bench/react_test_bench.py`
- [X] T003 [P] Add React test bench component directory in `frontend/admin/src/components/testBench/`
- [X] T004 [P] Add React test bench fixture file in `frontend/admin/src/test/testBenchTestData.ts`
- [X] T005 [P] Add React test bench performance test directory in `tests/performance/test_bench/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define shared contracts, authorization surfaces, generated types,
deterministic fixtures, safe mutations, and redaction guarantees.

**CRITICAL**: No user story implementation can proceed until these tasks are
done.

- [X] T006 Extend dashboard, scope, section, suite, case, assertion, target binding, safe mode, run, trace, artifact, gate, audit, action, form metadata, and mutation result models in `src/multi_agent_platform/api/schemas/admin_test_bench.py`
- [X] T007 Add raw secret, credential, authorization header, provider token, prompt, completion, private message, memory, connector payload, raw tool output, transcript, stack trace, local path, storage path, and unauthorized tenant label validators in `src/multi_agent_platform/api/schemas/admin_test_bench.py`
- [X] T008 Extend Spec 033 test bench contract and assertion helper generation in `scripts/frontend/generate_admin_react_types.py`
- [X] T009 Regenerate generated React API types in `frontend/admin/src/api/generated/reactAdminApi.ts`
- [X] T010 Add Spec 033 OpenAPI and generated-contract drift checks in `tests/contract/test_admin_react_contract.py`
- [X] T011 Add test bench schema redaction, safe problem, stale conflict, artifact reference, gate state, and mutation result tests in `tests/unit/api/test_admin_test_bench_schema.py`
- [X] T012 Add React client helpers for test bench bootstrap, suites, cases, runs, progress, run detail, gates, artifact metadata, and audit requests in `frontend/admin/src/api/client.ts`
- [X] T013 Register protected React test bench route and mutation surfaces in `src/multi_agent_platform/auth/policy.py`
- [X] T014 Add `/admin/app/test-bench` route constants, route wrapper, nav destination, and fallback links in `src/multi_agent_platform/api/routers/admin_react.py`

---

## Phase 3: User Story 1 - Author Reusable Test Suites (Priority: P1) MVP

**Goal**: Platform and tenant administrators can create and edit reusable
test suites and cases through guided forms without reading raw JSON or runtime
internals.

**Independent Test**: Acme tenant admin opens `/admin/app/test-bench`, creates
a workflow draft suite, adds a case with fixture metadata and assertions,
saves it, reloads suite detail, and verifies tenant scope and redaction.

### Tests for User Story 1

- [X] T015 [P] [US1] Add local-principal tenant bootstrap, suite list, suite save, case save, reload, and guided form route tests in `tests/integration/test_admin_react_routes.py`
- [X] T016 [P] [US1] Add Auth0-shaped tenant and platform suite authoring authorization tests in `tests/integration/test_admin_react_routes.py`
- [X] T017 [P] [US1] Add unauthenticated, non-admin, cross-tenant suite/case, stale revision, malformed assertion, and unsafe fixture denial tests in `tests/integration/test_admin_react_routes.py`
- [X] T018 [P] [US1] Add dashboard, suite list, target selection, suite save, case save, assertion metadata, revision token, and safe audit unit tests in `tests/unit/admin/test_test_bench_react_service.py`
- [X] T019 [P] [US1] Add suite, case, assertion, target binding, form metadata, field error, and unsafe text schema tests in `tests/unit/api/test_admin_test_bench_schema.py`
- [X] T020 [P] [US1] Add React test bench page shell, suite list, dashboard, empty state, and denied state tests in `frontend/admin/src/components/testBench/TestBenchPage.test.tsx`
- [X] T021 [P] [US1] Add React suite and case authoring form tests in `frontend/admin/src/components/testBench/SuiteAuthoringPanel.test.tsx`
- [X] T022 [P] [US1] Add React assertion builder and target selector tests in `frontend/admin/src/components/testBench/AssertionAndTargetPanel.test.tsx`

### Implementation for User Story 1

- [X] T023 [US1] Implement tenant and platform test bench bootstrap builders in `src/multi_agent_platform/testing/agent_bench/react_test_bench.py`
- [X] T024 [US1] Implement deterministic suite list, dashboard metrics, authorized target choices, and guided form metadata builders in `src/multi_agent_platform/testing/agent_bench/react_test_bench.py`
- [X] T025 [US1] Implement suite save, case save, assertion descriptor validation, revision token, stale-conflict, and safe audit mutation result builders in `src/multi_agent_platform/testing/agent_bench/react_test_bench.py`
- [X] T026 [US1] Add `/admin/app/test-bench`, `/admin/app/test-bench/bootstrap.json`, suite list, suite detail, suite save, and case save routes in `src/multi_agent_platform/api/routers/admin_react.py`
- [X] T027 [US1] Add frontend bootstrap, suite list, suite detail, suite save, and case save request helpers in `frontend/admin/src/api/client.ts`
- [X] T028 [US1] Implement `TestBenchPage` route shell in `frontend/admin/src/components/testBench/TestBenchPage.tsx`
- [X] T029 [US1] Implement `TestBenchSectionNav` in `frontend/admin/src/components/testBench/TestBenchSectionNav.tsx`
- [X] T030 [US1] Implement `TestBenchDashboardPanel` in `frontend/admin/src/components/testBench/TestBenchDashboardPanel.tsx`
- [X] T031 [US1] Implement `SuiteListPanel` with filters, latest run state, publish-gate state, and empty state in `frontend/admin/src/components/testBench/SuiteListPanel.tsx`
- [X] T032 [US1] Implement `SuiteAuthoringPanel` with guided suite and case forms in `frontend/admin/src/components/testBench/SuiteAuthoringPanel.tsx`
- [X] T033 [US1] Implement `AssertionAndTargetPanel` for target binding, structured assertions, thresholds, and field errors in `frontend/admin/src/components/testBench/AssertionAndTargetPanel.tsx`
- [X] T034 [US1] Route `/admin/app/test-bench` from `frontend/admin/src/App.tsx` and remove it from disabled fallback in `frontend/admin/src/routes.tsx`
- [X] T035 [US1] Add test bench shell, dashboard, suite list, forms, assertion builder, target selector, denied, empty, and validation styles in `frontend/admin/src/styles/admin.css`

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Launch Safe Test Runs (Priority: P1)

**Goal**: Administrators can launch durable test runs with safe execution
modes, backend-owned progress, idempotency, target revision binding, and
blocked side-effect evidence.

**Independent Test**: From a saved suite, launch one mock model/mock tools run
and one side-effect-disabled gateway-mode run, verify each run records safe
mode and target revision, and confirm local QA makes no live external calls.

### Tests for User Story 2

- [X] T036 [P] [US2] Add local-principal mock-mode run launch, gateway-mode launch, progress resume, idempotency, and terminal status route tests in `tests/integration/test_admin_react_routes.py`
- [X] T037 [P] [US2] Add Auth0-shaped run launch, safe-mode authorization, stale suite revision, stale target revision, duplicate idempotency, and no-active-cases route tests in `tests/integration/test_admin_react_routes.py`
- [X] T038 [P] [US2] Add real dependency probe denial, side-effect block, credential policy block, Telegram block, and live connector denial route tests in `tests/integration/test_admin_react_routes.py`
- [X] T039 [P] [US2] Add run launcher metadata, safe execution modes, mock default, run launch, progress snapshot, blocked side-effect, and audit unit tests in `tests/unit/admin/test_test_bench_react_service.py`
- [X] T040 [P] [US2] Add safe mode option, launch request, progress snapshot, run summary, side-effect block, and policy reason schema tests in `tests/unit/api/test_admin_test_bench_schema.py`
- [X] T041 [P] [US2] Add React safe execution selector, run launcher, queued/running state, idempotent submit, and policy rejection tests in `frontend/admin/src/components/testBench/RunLauncherPanel.test.tsx`
- [X] T042 [P] [US2] Add React run progress and run list tests in `frontend/admin/src/components/testBench/RunProgressPanel.test.tsx`

### Implementation for User Story 2

- [X] T043 [US2] Implement safe execution mode choices, mock default, side-effect-disabled gateway option, approved probe denial, and policy reason builders in `src/multi_agent_platform/testing/agent_bench/react_test_bench.py`
- [X] T044 [US2] Implement deterministic run launch, idempotency, target revision binding, queued/running/terminal progress snapshots, and audit references in `src/multi_agent_platform/testing/agent_bench/react_test_bench.py`
- [X] T045 [US2] Implement blocked model, tool, connector, credential, Telegram, external dependency, and side-effect summaries in `src/multi_agent_platform/testing/agent_bench/react_test_bench.py`
- [X] T046 [US2] Add run launch, run list, run progress, and cancellation-safe mutation routes in `src/multi_agent_platform/api/routers/admin_react.py`
- [X] T047 [US2] Add frontend run launch, run list, progress refresh, and cancel request helpers in `frontend/admin/src/api/client.ts`
- [X] T048 [US2] Implement `RunLauncherPanel` with safe execution selector, run reason choices, confirmation, and policy denial states in `frontend/admin/src/components/testBench/RunLauncherPanel.tsx`
- [X] T049 [US2] Implement `RunProgressPanel` for backend-owned queued, running, passed, failed, canceled, timed out, and unavailable status snapshots in `frontend/admin/src/components/testBench/RunProgressPanel.tsx`
- [X] T050 [US2] Implement `RunListPanel` for recent runs, safe modes, pass rates, actor summaries, and audit references in `frontend/admin/src/components/testBench/RunListPanel.tsx`
- [X] T051 [US2] Wire run launcher, progress, and run list panels into `frontend/admin/src/components/testBench/TestBenchPage.tsx`
- [X] T052 [US2] Add run launcher, safe mode, queued/running, blocked side-effect, confirmation, and policy denial styles in `frontend/admin/src/styles/admin.css`

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - Inspect Results And Diagnostics (Priority: P2)

**Goal**: Administrators can inspect pass/fail outcomes, case diagnostics,
assertion failures, contract findings, evaluator summaries, usage, latency,
redacted traces, and safe artifact metadata.

**Independent Test**: Open a deterministic failing run, identify the failing
assertion and contract path, review redacted step traces and artifact
references, and verify failure categories remain redaction-safe.

### Tests for User Story 3

- [X] T053 [P] [US3] Add local-principal passing run detail, failing run detail, assertion diagnostic, contract diagnostic, redacted trace, artifact metadata, and usage route tests in `tests/integration/test_admin_react_routes.py`
- [X] T054 [P] [US3] Add Auth0-shaped run detail authorization, artifact authorization, cross-tenant run denial, redaction-unavailable, and audit-unavailable route tests in `tests/integration/test_admin_react_routes.py`
- [X] T055 [P] [US3] Add prompt/completion/transcript/connector payload/stack trace/storage path redaction route tests in `tests/integration/test_admin_react_routes.py`
- [X] T056 [P] [US3] Add run detail, case outcome, diagnostic, trace step, artifact reference, redaction summary, usage, latency, and gateway decision unit tests in `tests/unit/admin/test_test_bench_react_service.py`
- [X] T057 [P] [US3] Add run detail, trace step, artifact reference, diagnostic category, redaction summary, and unavailable evidence schema tests in `tests/unit/api/test_admin_test_bench_schema.py`
- [X] T058 [P] [US3] Add React run detail, diagnostic category, failing assertion, contract path, gateway decision, and redaction summary tests in `frontend/admin/src/components/testBench/RunDetailPanel.test.tsx`
- [X] T059 [P] [US3] Add React trace and artifact metadata tests in `frontend/admin/src/components/testBench/TraceAndArtifactPanel.test.tsx`

### Implementation for User Story 3

- [X] T060 [US3] Implement deterministic passing and failing run detail builders with case outcomes, assertion diagnostics, contract diagnostics, evaluator summaries, usage, and latency in `src/multi_agent_platform/testing/agent_bench/react_test_bench.py`
- [X] T061 [US3] Implement redacted trace step summaries, gateway decisions, safe transcript excerpts, blocked side-effect references, and redaction unavailable states in `src/multi_agent_platform/testing/agent_bench/react_test_bench.py`
- [X] T062 [US3] Implement artifact metadata reference builders with checksum, size, content class, retention, redaction class, access status, authorized link state, and unavailable states in `src/multi_agent_platform/testing/agent_bench/react_test_bench.py`
- [X] T063 [US3] Add run detail and artifact metadata routes in `src/multi_agent_platform/api/routers/admin_react.py`
- [X] T064 [US3] Add frontend run detail and artifact metadata request helpers in `frontend/admin/src/api/client.ts`
- [X] T065 [US3] Implement `RunDetailPanel` for pass/fail status, case outcomes, diagnostics, usage, latency, and redaction summary in `frontend/admin/src/components/testBench/RunDetailPanel.tsx`
- [X] T066 [US3] Implement `TraceAndArtifactPanel` for trace steps, safe transcript excerpts, blocked side effects, artifact references, and access states in `frontend/admin/src/components/testBench/TraceAndArtifactPanel.tsx`
- [X] T067 [US3] Wire run detail, trace, and artifact panels into `frontend/admin/src/components/testBench/TestBenchPage.tsx`
- [X] T068 [US3] Add result summary, diagnostic, trace, artifact reference, unavailable evidence, and redaction warning styles in `frontend/admin/src/styles/admin.css`

**Checkpoint**: User Stories 1 through 3 work independently.

---

## Phase 6: User Story 4 - Review Publish-Gate Evidence (Priority: P2)

**Goal**: Administrators can see required suites, current target revision
evidence, missing/stale/running/failing/passing gate states, and authorized
links back to workflow publish flows.

**Independent Test**: Open a workflow draft with a required suite, verify stale
evidence blocks publication, launch a current run, confirm the gate becomes
ready, and open the linked run evidence.

### Tests for User Story 4

- [X] T069 [P] [US4] Add local-principal missing, stale, running, failing, passing, unavailable, current target revision, and authorized workflow link gate route tests in `tests/integration/test_admin_react_routes.py`
- [X] T070 [P] [US4] Add Auth0-shaped publish-gate evidence, stale evidence rejection, copied run rejection, audit-unavailable, and redaction-unavailable route tests in `tests/integration/test_admin_react_routes.py`
- [X] T071 [P] [US4] Add publish-gate status, current revision, remediation, authorized link, artifact evidence, audit evidence, stale rejection, and fail-closed unit tests in `tests/unit/admin/test_test_bench_react_service.py`
- [X] T072 [P] [US4] Add publish gate evidence, target revision binding, gate status enum, remediation, authorized action, and unavailable state schema tests in `tests/unit/api/test_admin_test_bench_schema.py`
- [X] T073 [P] [US4] Add React publish-gate evidence panel tests for missing, stale, running, failing, passing, unavailable, and authorized workflow links in `frontend/admin/src/components/testBench/PublishGateEvidencePanel.test.tsx`

### Implementation for User Story 4

- [X] T074 [US4] Implement required suite gate evidence, current target revision binding, missing/stale/running/failing/passing/unavailable states, and remediation builders in `src/multi_agent_platform/testing/agent_bench/react_test_bench.py`
- [X] T075 [US4] Implement gate evidence links to exact suite, run, artifact, audit reference, workflow builder, and publish flow only when authorized in `src/multi_agent_platform/testing/agent_bench/react_test_bench.py`
- [X] T076 [US4] Add publish-gate evidence route and current revision gate refresh mutation route in `src/multi_agent_platform/api/routers/admin_react.py`
- [X] T077 [US4] Add frontend publish-gate evidence and gate refresh request helpers in `frontend/admin/src/api/client.ts`
- [X] T078 [US4] Implement `PublishGateEvidencePanel` for gate states, target revisions, remediation, run links, artifact links, and workflow publish links in `frontend/admin/src/components/testBench/PublishGateEvidencePanel.tsx`
- [X] T079 [US4] Wire publish-gate evidence into suite detail, dashboard alerts, and run detail in `frontend/admin/src/components/testBench/TestBenchPage.tsx`
- [X] T080 [US4] Add publish-gate, stale evidence, current revision, remediation, and authorized link styles in `frontend/admin/src/styles/admin.css`

**Checkpoint**: User Stories 1 through 4 work independently.

---

## Phase 7: User Story 5 - Review Governance Evidence (Priority: P3)

**Goal**: Auditors and administrators can review safe audit timeline,
side-effect posture, redaction outcomes, artifact retention, usage summaries,
and denied access evidence.

**Independent Test**: As an auditor, open the Acme test bench evidence
timeline, review suite changes, run launches, side-effect decisions, result
finalization, and gate decisions, then verify Globex evidence is inaccessible.

### Tests for User Story 5

- [X] T081 [P] [US5] Add local-principal audit timeline, denied access evidence, artifact retention, side-effect posture, and redaction outcome route tests in `tests/integration/test_admin_react_routes.py`
- [X] T082 [P] [US5] Add Auth0-shaped auditor, tenant admin, platform admin, cross-tenant denial, and audit filter authorization tests in `tests/integration/test_admin_react_routes.py`
- [X] T083 [P] [US5] Add bounded audit timeline, safe diff, denied access summary, artifact retention, usage summary, side-effect posture, and tenant filter unit tests in `tests/unit/admin/test_test_bench_react_service.py`
- [X] T084 [P] [US5] Add audit record, safe diff, tenant scope label, denied access, retention state, and unauthorized label redaction schema tests in `tests/unit/api/test_admin_test_bench_schema.py`
- [X] T085 [P] [US5] Add bounded React test bench query performance tests in `tests/performance/test_bench/test_react_test_bench_queries.py`
- [X] T086 [P] [US5] Add React audit timeline and governance evidence tests in `frontend/admin/src/components/testBench/TestBenchAuditPanel.test.tsx`

### Implementation for User Story 5

- [X] T087 [US5] Implement bounded audit timeline, actor summary, tenant scope label, target summary, action, outcome, safe diff, redaction class, and audit reference builders in `src/multi_agent_platform/testing/agent_bench/react_test_bench.py`
- [X] T088 [US5] Implement denied access evidence, artifact retention state, side-effect posture, usage summary, and unavailable audit fallback builders in `src/multi_agent_platform/testing/agent_bench/react_test_bench.py`
- [X] T089 [US5] Add audit timeline route with bounded filters and safe denial behavior in `src/multi_agent_platform/api/routers/admin_react.py`
- [X] T090 [US5] Add frontend audit timeline and governance evidence request helpers in `frontend/admin/src/api/client.ts`
- [X] T091 [US5] Implement `TestBenchAuditPanel` for lifecycle events, safe diffs, denied access, retention, usage, side-effect posture, and audit-unavailable states in `frontend/admin/src/components/testBench/TestBenchAuditPanel.tsx`
- [X] T092 [US5] Wire audit timeline and governance evidence into `frontend/admin/src/components/testBench/TestBenchPage.tsx`
- [X] T093 [US5] Add audit timeline, safe diff, governance evidence, retention, denied access, and filter styles in `frontend/admin/src/styles/admin.css`

**Checkpoint**: All user stories are independently functional.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, validation manifest reconciliation, QA evidence,
and final quality gates.

- [X] T094 [P] Update React test bench notes in `README.md`
- [X] T095 [P] Update local validation notes in `docs/quickstart.md`
- [X] T096 [P] Create implementation reviewer notes in `specs/033-react-agent-and-workflow-test-bench/pr_notes.md`
- [X] T097 Generate QA API/database guide in `specs/033-react-agent-and-workflow-test-bench/qa033.md`
- [X] T098 Generate QA UI walkthrough in `specs/033-react-agent-and-workflow-test-bench/qa033_ui.md`
- [X] T099 Generate QA environment file in `specs/033-react-agent-and-workflow-test-bench/.env.qa033`
- [X] T100 Generate detailed manual user guide in `specs/033-react-agent-and-workflow-test-bench/qa033_user_guide.md`
- [X] T101 Reconcile QA033 validation commands and Playwright test bench flows in `specs/_autopilot/react-ui-roadmap/033-react-agent-and-workflow-test-bench/validation.yml`
- [X] T102 Run frontend build/test commands and record outcomes in `specs/033-react-agent-and-workflow-test-bench/pr_notes.md`
- [X] T103 Run backend quality commands and record outcomes in `specs/033-react-agent-and-workflow-test-bench/pr_notes.md`
- [X] T104 Run QA docs, Spec QA, Playwright validation, screenshot redaction scan, and evidence paths in `specs/033-react-agent-and-workflow-test-bench/pr_notes.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup and blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational and provides the suite/case authoring MVP.
- **User Story 2 (Phase 4)**: Depends on Foundational and integrates with US1 while remaining testable through saved deterministic suites.
- **User Story 3 (Phase 5)**: Depends on Foundational and integrates with US2 while remaining testable through deterministic run details.
- **User Story 4 (Phase 6)**: Depends on Foundational and integrates with US1/US2 while remaining testable through current target revision evidence.
- **User Story 5 (Phase 7)**: Depends on Foundational and integrates with all stories while remaining testable through bounded audit evidence.
- **Polish (Phase 8)**: Depends on implemented stories.

### Parallel Opportunities

- T002-T005 can run in parallel after T001 is planned.
- T010-T013 can run in parallel after T006.
- T015-T022 can run in parallel after foundational contracts exist.
- T036-T042 can run in parallel after run launch contracts exist.
- T053-T059 can run in parallel after run detail contracts exist.
- T069-T073 can run in parallel after gate contracts exist.
- T081-T086 can run in parallel after audit contracts exist.
- T094-T096 can run in parallel with QA document drafting.

## Parallel Example: User Story 1

```bash
Task: "Add local-principal suite and case route tests in tests/integration/test_admin_react_routes.py"
Task: "Add suite authoring service tests in tests/unit/admin/test_test_bench_react_service.py"
Task: "Add suite/case schema redaction tests in tests/unit/api/test_admin_test_bench_schema.py"
Task: "Add React suite and case authoring tests in frontend/admin/src/components/testBench/SuiteAuthoringPanel.test.tsx"
```

## Implementation Strategy

1. Complete schemas, generated contracts, route protection, deterministic service builders, and client helpers.
2. Deliver User Story 1 as the MVP suite and case authoring workflow.
3. Add User Story 2 safe run launch, progress, idempotency, and side-effect evidence.
4. Add User Story 3 run detail, diagnostics, trace, and artifact references.
5. Add User Story 4 current-revision publish-gate evidence and workflow links.
6. Add User Story 5 governance timeline, denied access, retention, and audit evidence.
7. Finish QA docs, validation manifest, screenshots, and full quality evidence.

## Notes

- Do not retire or weaken existing Jinja agent/workflow test bench or workflow publish-gate routes.
- Do not call live Auth0, Telegram, model providers, credential stores, external connectors, direct connector SDKs, or real dependency probes in local or CI QA.
- Do not render raw secrets, credential values, authorization headers, provider tokens, raw prompts, raw completions, private channel messages, memory contents, connector payloads, raw tool outputs, raw transcripts, local paths, storage paths, stack traces, or unauthorized tenant labels.
- Stop if tenant scope, target revision binding, safe execution mode policy, stale evidence rejection, artifact access, audit persistence, side-effect blocking, real probe approval, or redaction becomes ambiguous.
