# Tasks: Production Audit And Debugging

**Input**: Design documents from `/Users/scottcornell/src/my-projects/multi-agent/specs/008-production-audit-debugging/`
**Prerequisites**: `/Users/scottcornell/src/my-projects/multi-agent/specs/008-production-audit-debugging/plan.md`, `/Users/scottcornell/src/my-projects/multi-agent/specs/008-production-audit-debugging/spec.md`, `/Users/scottcornell/src/my-projects/multi-agent/specs/008-production-audit-debugging/research.md`, `/Users/scottcornell/src/my-projects/multi-agent/specs/008-production-audit-debugging/data-model.md`, `/Users/scottcornell/src/my-projects/multi-agent/specs/008-production-audit-debugging/contracts/`

**Tests**: Test tasks are included because the feature specification requires at least 90 percent unit-test coverage and the user explicitly requested coverage for event creation, trace correlation, timeline assembly, redaction behavior, version-bundle visibility, notification traceability, and admin-only debug access.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently after the shared foundation is complete.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and has no dependency on another incomplete task in the same phase
- **[Story]**: User story label from `/Users/scottcornell/src/my-projects/multi-agent/specs/008-production-audit-debugging/spec.md`
- Every task includes exact absolute file paths

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare the audit/debugging module, API surface, and test/documentation skeletons.

- [ ] T001 Create audit debugging package exports in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/audit/__init__.py`
- [ ] T002 [P] Create admin run inspection router skeleton in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/routers/admin_run_inspection.py`
- [ ] T003 [P] Create audit debugging API schema skeleton in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/schemas/audit_debugging.py`
- [ ] T004 [P] Create audit debugging database model skeleton in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/db/models/audit_debugging.py`
- [ ] T005 [P] Create audit debugging repository skeleton in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/db/repositories/audit_debugging.py`
- [ ] T006 [P] Create audit debugging Alembic migration skeleton in `/Users/scottcornell/src/my-projects/multi-agent/alembic/versions/0008_production_audit_debugging.py`
- [ ] T007 [P] Create audit debugging documentation placeholder in `/Users/scottcornell/src/my-projects/multi-agent/docs/production-audit-debugging.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build append-only storage, core domain models, classification/redaction, capture contracts, and dependency wiring that all user stories depend on.

**CRITICAL**: No user story work should begin until this phase is complete.

- [ ] T008 Define audit/debugging enums and domain value objects for timeline events, trace records, capture gaps, criticality, outcomes, lineage, version bundles, notifications, secret access, inspection audits, exports, and redaction records in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/audit/models.py`
- [ ] T009 Implement SQLAlchemy tables and constraints for `audit_timeline_events`, `audit_runtime_trace_records`, specialized trace tables, `audit_capture_gaps`, `audit_inspection_access_events`, `audit_debug_exports`, `audit_redaction_classification_records`, lineage projections, version-bundle snapshots, notification traces, and secret-access audits in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/db/models/audit_debugging.py`
- [ ] T010 Register audit debugging database models in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/db/models/__init__.py`
- [ ] T011 Implement Alembic upgrade/downgrade for audit debugging tables, append-only indexes, tenant/run/time search indexes, idempotency keys, and foreign keys in `/Users/scottcornell/src/my-projects/multi-agent/alembic/versions/0008_production_audit_debugging.py`
- [ ] T012 [P] Add migration tests for audit tables, append-only constraints, idempotency uniqueness, and required indexes in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/db/test_audit_debugging_migration.py`
- [ ] T013 Implement repository create/query methods for timeline events, trace records, capture gaps, inspection audits, exports, lineage, version bundles, notification state, and secret-access metadata in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/db/repositories/audit_debugging.py`
- [ ] T014 [P] Add repository tests for append-only writes, idempotent event creation, same-tenant trace linking, search filters, and denied cross-tenant queries in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/audit/test_repository.py`
- [ ] T015 Implement sensitivity classification labels, default-deny dynamic field behavior, safe summary builders, and viewer-aware redaction decisions in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/audit/classification.py`
- [ ] T016 [P] Add redaction/classification tests for raw secrets, credentials, prompt bodies, memory content, oversized payloads, unknown fields, and role-specific viewer output in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/audit/test_classification.py`
- [ ] T017 Implement audit capture facade with `record_event`, `record_trace`, fail-closed security/governance handling, diagnostic capture gaps, idempotent retries, structured logs, metrics, and trace propagation in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/audit/capture.py`
- [ ] T018 [P] Add capture facade tests for event creation, idempotency, fail-closed security events, diagnostic unavailable markers, and trace id propagation in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/audit/test_capture.py`
- [ ] T019 Implement audit debugging service facade for capture, inspection, export, denied-access audit, and query coordination in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/audit/service.py`
- [ ] T020 Wire `AuditDebuggingRepository` and `AuditDebuggingService` factories into the application container in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/bootstrap/container.py`
- [ ] T021 Add FastAPI dependency helpers for audit debugging services in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/deps.py`
- [ ] T022 [P] Extend observability logging helpers with run/trace/timeline safe context fields in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/observability/logging.py`
- [ ] T023 [P] Extend metrics helpers with capture, gap, denied-inspection, lookup, search, replay, export, and redaction metrics in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/observability/metrics.py`
- [ ] T024 [P] Extend tracing helpers with run trace id and correlation id propagation utilities in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/observability/tracing.py`

**Checkpoint**: Foundation ready; user story phases can now proceed.

---

## Phase 3: User Story 1 - Inspect Run Timelines (Priority: P1) MVP

**Goal**: Administrators can inspect chronological run timelines, direct lookup, filtered search, replay, lineage summary, trace links, and failure context without database access.

**Independent Test**: Create successful and failed workflow run audit fixtures, call the admin inspection APIs as an authorized administrator and unauthorized user, and confirm timeline order, failure point, trace correlation, lineage summary, search filters, and denied-access auditing.

### Tests for User Story 1

- [ ] T025 [P] [US1] Add OpenAPI contract tests for debug search, timeline, replay, lineage, bundle, export, 403, and 404 response schemas in `/Users/scottcornell/src/my-projects/multi-agent/tests/contract/test_production_audit_debugging_contract.py`
- [ ] T026 [P] [US1] Add Pydantic schema tests for run summary, timeline events, trace records, replay events, lineage nodes, capture gaps, and inspection errors in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/api/test_audit_debugging_schemas.py`
- [ ] T027 [P] [US1] Add timeline assembly tests for lifecycle ordering, failed-stage summaries, capture gaps, trace correlation, and parent-child lineage summaries in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/audit/test_inspection.py`
- [ ] T028 [P] [US1] Add admin-only API integration tests for authorized timeline/search/replay/lineage access, unauthorized denial, cross-tenant fail-closed behavior, and denied inspection audit creation in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_run_inspection_api.py`
- [ ] T029 [P] [US1] Add lookup and filtered search latency tests for p95 direct lookup <= 2 seconds and p95 filtered search <= 5 seconds in `/Users/scottcornell/src/my-projects/multi-agent/tests/performance/audit/test_run_inspection_latency.py`
- [ ] T085 [P] [US1] Add audit capture overhead tests proving p95 in-process builder overhead <= 10 ms excluding database commit time in `/Users/scottcornell/src/my-projects/multi-agent/tests/performance/audit/test_audit_capture_overhead.py`

### Implementation for User Story 1

- [ ] T030 [US1] Implement inspection request/response Pydantic schemas matching `/Users/scottcornell/src/my-projects/multi-agent/specs/008-production-audit-debugging/contracts/production-audit-debugging.openapi.yaml` in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/schemas/audit_debugging.py`
- [ ] T031 [US1] Implement timeline, search, replay, lineage, bundle, notification, capture gap, and export query DTO assembly in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/audit/inspection.py`
- [ ] T032 [US1] Implement tenant-scoped direct lookup, debug-search filters, bounded pagination, and ordered event loading in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/db/repositories/audit_debugging.py`
- [ ] T033 [US1] Implement admin inspection authorization, role checks, denied-access audit writes, and safe not-found/forbidden behavior in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/audit/service.py`
- [ ] T034 [US1] Implement `/admin/runs/debug-search`, `/admin/runs/{workflow_run_id}/timeline`, `/admin/runs/{workflow_run_id}/replay`, `/admin/runs/{workflow_run_id}/lineage`, `/admin/runs/{workflow_run_id}/bundle`, and `/admin/runs/{workflow_run_id}/exports` endpoints in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/routers/admin_run_inspection.py`
- [ ] T035 [US1] Register the admin run inspection router in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/main.py`
- [ ] T036 [P] [US1] Implement minimal admin run search page consuming API schemas in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/runs/index.html`
- [ ] T037 [P] [US1] Implement minimal admin run timeline detail page consuming API schemas in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/runs/detail.html`
- [ ] T038 [P] [US1] Implement minimal admin replay page consuming API schemas in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/runs/replay.html`
- [ ] T039 [P] [US1] Implement admin run inspection JavaScript for pagination, replay stepping, lineage navigation, bundle links, and export actions in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/static/run_inspection.js`
- [ ] T040 [US1] Add admin UI route handlers for run search, timeline detail, replay, lineage, bundle, and export pages in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/routers/admin_run_inspection.py`

**Checkpoint**: User Story 1 is independently testable through the admin inspection APIs and minimal admin views.

---

## Phase 4: User Story 2 - Debug Runtime Decisions And Handoffs (Priority: P2)

**Goal**: Operators can review agent handoffs, contract validation results, memory writes, tool usage, model selection, trace correlation, policy outcomes, and safe summaries linked to timeline events.

**Independent Test**: Run or fixture a workflow with handoffs, validation pass/fail outcomes, memory writes, tool allow/deny outcomes, model-backed steps, and capture gaps; confirm every runtime decision is safely visible and linked to the correct timeline event.

### Tests for User Story 2

- [ ] T041 [P] [US2] Add runtime event creation tests for lifecycle, handoff, contract validation, memory write, tool usage, model selection, and failure events in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/audit/test_event_builders.py`
- [ ] T042 [P] [US2] Add trace correlation tests proving every runtime trace links to the same-tenant timeline event, run step, trace id, and correlation id in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/audit/test_trace_correlation.py`
- [ ] T043 [P] [US2] Add redaction behavior tests for handoff payloads, contract errors, memory writes, tool inputs/outputs, model prompts, and unavailable diagnostic traces in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/audit/test_redaction.py`
- [ ] T044 [P] [US2] Add runtime capture integration tests for orchestration lifecycle, handoffs, validations, tool side effects, model selections, memory writes, fail-closed security events, and diagnostic capture gaps in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/runtime/test_audit_capture_runtime.py`
- [ ] T045 [P] [US2] Add timeline completeness integration tests linking runtime decisions to timeline events for successful, failed, waiting, resumed, retried, cancelled, and timed-out runs in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/runtime/test_timeline_completeness.py`

### Implementation for User Story 2

- [ ] T046 [US2] Implement event builder functions for lifecycle states, failed-stage summaries, recommended investigation categories, runtime decisions, and safe summaries in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/audit/capture.py`
- [ ] T047 [US2] Implement specialized trace builders for agent handoff, contract validation, memory write, tool usage, model selection, and capture gap records in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/audit/models.py`
- [ ] T048 [US2] Map orchestration lifecycle events to audit capture calls in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/runtime/orchestration/events.py`
- [ ] T049 [US2] Capture accepted, queued, started, waiting, resumed, retried, completed, cancelled, failed, and timed-out lifecycle events from orchestration service flows in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/runtime/orchestration/service.py`
- [ ] T050 [US2] Capture agent handoff source, destination, reason, outcome, contract reference, and safe payload metadata in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/runtime/orchestration/handoffs.py`
- [ ] T051 [US2] Capture contract validation pass/fail outcomes, prioritized safe error summaries, and related run step ids in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/runtime/orchestration/contracts.py`
- [ ] T052 [US2] Capture tool usage, policy decisions, execution outcomes, durations, and safe input/output summaries in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/runtime/orchestration/side_effects.py`
- [ ] T053 [US2] Capture model selection decisions, routing versions, prompt/config references, outcomes, and safe trace metadata in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/config/resolver.py`
- [ ] T054 [US2] Capture memory write attempts, requested/effective version references, projection references, outcomes, and safe summaries in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/memory/service.py`
- [ ] T055 [US2] Add structured logging, metrics, and trace id emission for runtime decision capture in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/audit/capture.py`

**Checkpoint**: User Story 2 is independently testable through runtime capture fixtures and linked admin timeline inspection.

---

## Phase 5: User Story 3 - Audit Governance And Delivery State (Priority: P3)

**Goal**: Auditors and administrators can inspect version-bundle visibility, notification delivery state, secret-access audit metadata, redacted exports, and governance evidence without exposing sensitive values.

**Independent Test**: Execute or fixture a run with a pinned execution bundle, notification attempts, secret-reference requests, export creation, and cross-tenant related runs; confirm only authorized reviewers see safe metadata and every governance action is auditable.

### Tests for User Story 3

- [ ] T056 [P] [US3] Add version-bundle visibility tests for pinned bundle identity, activation state at acceptance, workflow/contract/prompt/model/tool-policy refs, and historical migration refs in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/audit/test_version_bundle_visibility.py`
- [ ] T057 [P] [US3] Add notification traceability tests for destination category, delivery status, attempt count, latest attempt time, safe failure reason, provider correlation, and triggering timeline event in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/audit/test_notification_traceability.py`
- [ ] T058 [P] [US3] Add secret-access audit tests for requester metadata, secret reference version, policy outcome, denial reason, fail-closed capture, and zero raw secret leakage in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/audit/test_secret_access_audit.py`
- [ ] T059 [P] [US3] Add export tests for viewer-aware redaction, included/excluded sections, lineage scope, artifact metadata, expiration, and export audit events in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/audit/test_export.py`
- [ ] T060 [P] [US3] Add governance integration tests for bundle, notification, secret-access, lineage boundary nodes, and redacted export API responses in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_run_governance_api.py`

### Implementation for User Story 3

- [ ] T061 [US3] Implement pinned version-bundle snapshot creation, migration refs, activation state at acceptance, and safe bundle serialization in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/audit/inspection.py`
- [ ] T062 [US3] Capture workflow and execution bundle references when runtime accepts a run in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/runtime/versioning.py`
- [ ] T063 [US3] Capture notification delivery state, attempts, provider correlation refs, suppressed/retrying/failed outcomes, and triggering timeline event ids in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/channels/notifications.py`
- [ ] T064 [US3] Capture secret-access audit metadata before secret-backed protected actions proceed in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/secrets/base.py`
- [ ] T065 [US3] Capture delegated credential access and denial metadata without credential values in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/db/models/delegated_credential.py`
- [ ] T066 [US3] Implement authorized lineage graph assembly with redacted boundary nodes for unauthorized related runs in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/audit/inspection.py`
- [ ] T067 [US3] Implement redacted debug-evidence export generation, artifact storage metadata, export status transitions, and export audit events in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/audit/export.py`
- [ ] T068 [US3] Connect debug-evidence export creation to existing storage provider artifact handling in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/storage/base.py`
- [ ] T069 [US3] Add export creation, status, and safe failure responses to admin endpoints in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/routers/admin_run_inspection.py`
- [ ] T086 [US3] Implement idempotent export status transitions, bounded upload retry handling, and reconciliation for PostgreSQL metadata/object-storage divergence in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/audit/export.py`
- [ ] T087 [P] [US3] Add export durability tests for pending/available/failed transitions, upload retry, idempotent duplicate requests, partial artifact cleanup, and reconciliation in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/audit/test_export.py`
- [ ] T088 [US3] Enforce per-tenant and per-actor debug export rate limits with safe retry metadata in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/audit/service.py`
- [ ] T089 [P] [US3] Add export rate-limit and fairness tests for tenant quotas, actor quotas, rejected export audit events, and tenant-scoped metrics in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_run_governance_api.py`

**Checkpoint**: User Story 3 is independently testable through governance API responses and redacted exports.

---

## Phase 6: User Story 4 - Review Delivery Evidence (Priority: P4)

**Goal**: Maintainers can review coverage evidence, PR notes, testing instructions, README guidance, and operational documentation for the completed feature.

**Independent Test**: Review the submitted package and confirm coverage, PR review notes, testing instructions, README content, and quickstart commands cover all required audit/debugging behavior.

### Tests for User Story 4

- [ ] T070 [P] [US4] Add documentation tests that assert production audit debugging docs mention timelines, trace fields, lineage, version bundles, notifications, secret-access metadata, redaction, and escalation in `/Users/scottcornell/src/my-projects/multi-agent/tests/docs/test_production_audit_debugging_docs.py`
- [ ] T071 [P] [US4] Add README guidance tests that assert admin debugging instructions and required command references are present in `/Users/scottcornell/src/my-projects/multi-agent/tests/docs/test_readme_production_audit_debugging.py`

### Implementation for User Story 4

- [ ] T072 [US4] Write administrator/operator documentation for timeline inspection, trace interpretation, failed-run debugging, lineage, version bundles, notification delivery, secret-access metadata, redaction, exports, and escalation in `/Users/scottcornell/src/my-projects/multi-agent/docs/production-audit-debugging.md`
- [ ] T073 [US4] Update repository quickstart with audit/debugging setup, run examples, admin inspection API calls, export validation, and coverage commands in `/Users/scottcornell/src/my-projects/multi-agent/docs/quickstart.md`
- [ ] T074 [US4] Update README with administrator-facing audit/debugging guidance and links to detailed docs in `/Users/scottcornell/src/my-projects/multi-agent/README.md`
- [ ] T075 [US4] Add PR review notes covering timeline completeness, runtime decision capture, lineage, version-bundle visibility, notification state, secret handling, authorization, redaction, retention, operational risk, known limitations, and coverage evidence in `/Users/scottcornell/src/my-projects/multi-agent/specs/008-production-audit-debugging/pr-review-notes.md`
- [ ] T076 [US4] Add reviewer testing instructions for successful/failed runs, handoffs, validations, memory writes, tool usage, model selection, bundle visibility, lineage, notifications, secret access, authorization failures, redaction, exports, and README guidance in `/Users/scottcornell/src/my-projects/multi-agent/specs/008-production-audit-debugging/testing-instructions.md`

**Checkpoint**: User Story 4 is independently testable through documentation review and docs tests.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final quality, coverage, performance, contract alignment, and release readiness across all user stories.

- [ ] T077 [P] Add audit debugging fixture factories for tenants, principals, runs, timeline events, traces, bundles, lineage, notifications, secrets, and exports in `/Users/scottcornell/src/my-projects/multi-agent/tests/fixtures/audit_debugging.py`
- [ ] T078 [P] Add observability tests for structured log redaction, metric labels, trace id propagation, and capture failure metrics in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/observability/test_audit_observability.py`
- [ ] T079 [P] Add replay view assembly tests for ordered immutable replay events, checkpoints, unavailable markers, child-run inclusion, and no side effects in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/audit/test_replay.py`
- [ ] T080 [P] Add admin run inspection UI tests for search filters, timeline detail, replay stepping, lineage links, bundle view, export actions, and safe rendering in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_run_inspection_ui.py`
- [ ] T081 [P] Add contract drift checks comparing implemented routes and schemas to the OpenAPI contract in `/Users/scottcornell/src/my-projects/multi-agent/tests/contract/test_production_audit_debugging_contract.py`
- [ ] T082 Run and record full quality gates in `/Users/scottcornell/src/my-projects/multi-agent/specs/008-production-audit-debugging/testing-instructions.md`: `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy src`, and `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90`
- [ ] T083 Verify quickstart scenarios against implemented endpoints and update any mismatched commands or expected response fields in `/Users/scottcornell/src/my-projects/multi-agent/specs/008-production-audit-debugging/quickstart.md`
- [ ] T084 Review sensitive-data surfaces and document evidence that timelines, traces, exports, logs, metrics, README guidance, and PR notes contain no raw secrets, credentials, unauthorized prompt text, or unauthorized memory content in `/Users/scottcornell/src/my-projects/multi-agent/specs/008-production-audit-debugging/pr-review-notes.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately.
- **Foundational (Phase 2)**: Depends on Phase 1; blocks all user story implementation.
- **User Story 1 (Phase 3)**: Depends on Phase 2; MVP scope.
- **User Story 2 (Phase 4)**: Depends on Phase 2 and benefits from US1 inspection APIs for validation.
- **User Story 3 (Phase 5)**: Depends on Phase 2 and benefits from US1 inspection APIs for validation.
- **User Story 4 (Phase 6)**: Depends on the completed behavior it documents, especially US1-US3.
- **Polish (Phase 7)**: Depends on desired user stories being complete.

### User Story Dependencies

- **US1 - Inspect Run Timelines (P1)**: Can start after Foundational; delivers the MVP admin inspection surface.
- **US2 - Debug Runtime Decisions And Handoffs (P2)**: Can start after Foundational; can proceed in parallel with US1 implementation but final validation should use US1 APIs.
- **US3 - Audit Governance And Delivery State (P3)**: Can start after Foundational; can proceed in parallel with US2 once storage and service facades exist.
- **US4 - Review Delivery Evidence (P4)**: Should follow US1-US3 so docs and review notes describe implemented behavior.

### Within Each User Story

- Tests are written first and should fail before implementation.
- Storage/query tasks precede service assembly tasks.
- Service assembly tasks precede FastAPI/router tasks.
- Capture builders precede runtime integration hooks.
- Redaction/classification checks precede export and rendered view exposure.

---

## Parallel Opportunities

- Setup skeleton tasks T002-T007 can run in parallel after T001.
- Foundational tests T012, T014, T016, T018 and observability tasks T022-T024 can run in parallel with non-conflicting implementation tasks.
- US1 test tasks T025-T029 and T085 can run in parallel before implementation.
- US1 admin templates/static tasks T036-T039 can run in parallel after schemas in T030 stabilize.
- US2 test tasks T041-T045 can run in parallel before runtime implementation.
- US2 capture hook tasks T050-T054 can run in parallel once T046-T047 are complete.
- US3 test tasks T056-T060, T087, and T089 can run in parallel before governance implementation.
- US4 docs tests T070-T071 can run in parallel with documentation drafting T072-T076.
- Polish tests T077-T081 can run in parallel once feature code is available.

---

## Parallel Example: User Story 1

```bash
Task: "T025 [P] [US1] Add OpenAPI contract tests in /Users/scottcornell/src/my-projects/multi-agent/tests/contract/test_production_audit_debugging_contract.py"
Task: "T026 [P] [US1] Add Pydantic schema tests in /Users/scottcornell/src/my-projects/multi-agent/tests/unit/api/test_audit_debugging_schemas.py"
Task: "T027 [P] [US1] Add timeline assembly tests in /Users/scottcornell/src/my-projects/multi-agent/tests/unit/audit/test_inspection.py"
Task: "T028 [P] [US1] Add admin-only API integration tests in /Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_run_inspection_api.py"
Task: "T029 [P] [US1] Add lookup/search latency tests in /Users/scottcornell/src/my-projects/multi-agent/tests/performance/audit/test_run_inspection_latency.py"
```

## Parallel Example: User Story 2

```bash
Task: "T041 [P] [US2] Add runtime event creation tests in /Users/scottcornell/src/my-projects/multi-agent/tests/unit/audit/test_event_builders.py"
Task: "T042 [P] [US2] Add trace correlation tests in /Users/scottcornell/src/my-projects/multi-agent/tests/unit/audit/test_trace_correlation.py"
Task: "T043 [P] [US2] Add redaction behavior tests in /Users/scottcornell/src/my-projects/multi-agent/tests/unit/audit/test_redaction.py"
Task: "T044 [P] [US2] Add runtime capture integration tests in /Users/scottcornell/src/my-projects/multi-agent/tests/integration/runtime/test_audit_capture_runtime.py"
Task: "T045 [P] [US2] Add timeline completeness integration tests in /Users/scottcornell/src/my-projects/multi-agent/tests/integration/runtime/test_timeline_completeness.py"
```

## Parallel Example: User Story 3

```bash
Task: "T056 [P] [US3] Add version-bundle visibility tests in /Users/scottcornell/src/my-projects/multi-agent/tests/unit/audit/test_version_bundle_visibility.py"
Task: "T057 [P] [US3] Add notification traceability tests in /Users/scottcornell/src/my-projects/multi-agent/tests/unit/audit/test_notification_traceability.py"
Task: "T058 [P] [US3] Add secret-access audit tests in /Users/scottcornell/src/my-projects/multi-agent/tests/unit/audit/test_secret_access_audit.py"
Task: "T059 [P] [US3] Add export tests in /Users/scottcornell/src/my-projects/multi-agent/tests/unit/audit/test_export.py"
Task: "T060 [P] [US3] Add governance integration tests in /Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_run_governance_api.py"
```

## Parallel Example: User Story 4

```bash
Task: "T070 [P] [US4] Add documentation tests in /Users/scottcornell/src/my-projects/multi-agent/tests/docs/test_production_audit_debugging_docs.py"
Task: "T071 [P] [US4] Add README guidance tests in /Users/scottcornell/src/my-projects/multi-agent/tests/docs/test_readme_production_audit_debugging.py"
Task: "T072 [US4] Write administrator/operator documentation in /Users/scottcornell/src/my-projects/multi-agent/docs/production-audit-debugging.md"
Task: "T075 [US4] Add PR review notes in /Users/scottcornell/src/my-projects/multi-agent/specs/008-production-audit-debugging/pr-review-notes.md"
Task: "T076 [US4] Add reviewer testing instructions in /Users/scottcornell/src/my-projects/multi-agent/specs/008-production-audit-debugging/testing-instructions.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup.
2. Complete Phase 2 foundational storage, classification, capture facade, service wiring, and observability.
3. Complete Phase 3 User Story 1.
4. Stop and validate admin timeline/search/replay/lineage inspection with authorized and unauthorized principals.

### Incremental Delivery

1. Deliver US1 so operators can inspect timelines and failures without database access.
2. Add US2 so runtime decisions and handoffs are captured and correlated to timeline events.
3. Add US3 so governance evidence, version bundles, notification state, secret access, lineage boundaries, and exports are visible safely.
4. Add US4 docs, PR notes, testing instructions, README guidance, and coverage evidence.
5. Complete Phase 7 quality gates and sensitive-data review.

### Parallel Team Strategy

1. Team completes Phase 1 and Phase 2 together.
2. After Phase 2, one developer owns US1 API/inspection, one owns US2 runtime capture, one owns US3 governance/export evidence, and one owns US4 docs/review materials.
3. Coordinate shared-file edits in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/audit/service.py`, `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/audit/inspection.py`, and `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/routers/admin_run_inspection.py` to avoid conflicting changes.

---

## Validation Summary

- **Total tasks**: 89
- **Setup tasks**: 7
- **Foundational tasks**: 17
- **US1 tasks**: 17
- **US2 tasks**: 15
- **US3 tasks**: 18
- **US4 tasks**: 7
- **Polish tasks**: 8
- **Suggested MVP scope**: Phase 1, Phase 2, and User Story 1.
- **Format validation**: Every task uses `- [ ] T###`, optional `[P]`, required `[US#]` labels only for user-story phases, and exact absolute file paths.
