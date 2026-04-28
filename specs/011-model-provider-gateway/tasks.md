# Tasks: Model Provider Gateway

**Input**: Design documents from `/Users/scottcornell/src/my-projects/multi-agent/specs/011-model-provider-gateway/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `quickstart.md`, `contracts/`

**Tests**: Required. This feature is explicitly test-first and must keep provider connection and gateway code at >=90 percent coverage.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently after the shared foundation is complete.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches a different file or independent test surface
- **[Story]**: User story label from `spec.md`
- Every task includes an exact repository path
- **Execution order**: Phase order and dependency notes are authoritative; task IDs are stable identifiers and may not be numerically sorted after remediation additions.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare feature package boundaries, documentation stubs, and test locations without changing behavior.

- [X] T001 Create the model provider package initializer in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/__init__.py`
- [X] T002 [P] Create provider adapter module stubs in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/adapters.py`, `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/openai_adapter.py`, and `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/local_adapter.py`
- [X] T003 [P] Create provider domain module stubs in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/models.py`, `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/allowlist.py`, `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/validation.py`, `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/secrets.py`, `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/probes.py`, `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/catalog_sync.py`, `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/gateway.py`, `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/usage.py`, `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/redaction.py`, `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/health.py`, and `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/service.py`
- [X] T004 [P] Create admin API/UI stubs in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/routers/admin_model_providers.py`, `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/schemas/model_providers.py`, and `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/ui/model_providers.py`
- [X] T005 [P] Create model provider web asset stubs in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/static/model_providers.js` and `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/model_providers/index.html`
- [X] T006 [P] Create documentation stubs in `/Users/scottcornell/src/my-projects/multi-agent/docs/model-provider-gateway.md`, `/Users/scottcornell/src/my-projects/multi-agent/specs/011-model-provider-gateway/testing-instructions.md`, and `/Users/scottcornell/src/my-projects/multi-agent/specs/011-model-provider-gateway/pr-review-notes.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add persistent schema, shared domain contracts, settings, and dependency wiring required by every story.

**CRITICAL**: No user story work can begin until this phase is complete.

### Tests First

- [ ] T007 [P] Write migration tests for provider connection tables, constraints, indexes, catalog extension fields, and rollback safety in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/db/test_model_provider_gateway_migration.py`
- [ ] T008 [P] Write SQLAlchemy model tests for secret-free fields, enum constraints, model-id uniqueness, tenant visibility relationships, test result append-only behavior, health snapshots, catalog sync records, and gateway attempt metadata in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/db/test_model_provider_models.py`
- [ ] T009 [P] Write domain model tests for provider types, health states, timeout policy bounds, normalized error categories, safe audit summaries, and usage availability states in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/model_providers/test_models.py`
- [ ] T010 [P] Write configuration tests for local endpoint allowlist settings, timeout defaults, and fail-closed missing settings in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/config/test_model_provider_settings.py`
- [ ] T098 [P] Write durability/idempotency tests for probe attempts, catalog sync retries, and gateway invocation attempt recovery in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/runtime/test_model_provider_side_effect_recovery.py`
- [X] T100 [P] Write local endpoint allowlist normalization and rejection tests in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/model_providers/test_allowlist.py`

### Implementation

- [X] T011 Create the next Alembic migration for model provider gateway tables, constraints, indexes, and model_skill_config catalog extension fields in `/Users/scottcornell/src/my-projects/multi-agent/alembic/versions/0011_model_provider_gateway.py`
- [X] T012 Implement SQLAlchemy models for provider connections, model definitions, tenant visibility, test results, health snapshots, catalog sync records, and gateway attempts in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/db/models/model_providers.py`
- [X] T013 Register model provider SQLAlchemy metadata imports in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/db/models/__init__.py`
- [X] T014 Implement provider domain enums, dataclasses, Pydantic value objects, timeout policy, safe summaries, and normalized error objects in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/models.py`
- [X] T015 Add settings for local provider allowlisted schemes, hosts, ports, CIDRs, probe timeout defaults, and gateway timeout bounds in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/config/settings.py`
- [X] T016 Implement repository transaction methods for saving connections, listing visible connections, appending test results, deriving latest health, syncing catalog records, and recording gateway attempts in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/db/repositories/model_providers.py`
- [ ] T017 Wire repository and model provider service dependencies into the application container in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/bootstrap/container.py`
- [ ] T099 Implement persisted idempotency and recovery handling for provider probes, catalog sync, and gateway attempts in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/service.py`
- [X] T101 Implement local endpoint allowlist validation for schemes, hosts, ports, CIDRs, userinfo, secret-like query params, and redirect destinations in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/allowlist.py`

**Checkpoint**: Database, domain contracts, configuration, and service wiring are ready for user story work.

---

## Phase 3: User Story 1 - Configure Provider Connections (Priority: P1) MVP

**Goal**: Platform administrators can create, update, activate, deactivate, and view OpenAI/local model provider connections through APIs and the admin web UI, while tenant users only read visible safe metadata.

**Independent Test**: Sign in as a platform administrator, create OpenAI and local connections with model metadata, timeout policy, tenant visibility, and secret references, then confirm tenant-scoped users only see visible entries and cannot mutate them.

### Tests for User Story 1

> Write these tests first and confirm they fail before implementation.

- [ ] T018 [P] [US1] Write OpenAPI contract tests for connection list/create/get/update/activate/deactivate authorization and response shapes in `/Users/scottcornell/src/my-projects/multi-agent/tests/contract/test_model_provider_gateway_contract.py`
- [ ] T019 [P] [US1] Write API integration tests for platform-admin create/update/activate/deactivate and tenant read visibility in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_model_providers_api.py`
- [X] T020 [P] [US1] Write admin UI integration tests for list/create/edit/detail pages, disabled tenant mutation controls, shell navigation, validation states, and safe secret reference display in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_model_providers_ui.py`
- [X] T021 [P] [US1] Write schema tests for OpenAI/local provider payload validation, duplicate model ids, timeout bounds, tenant visibility, and safe redaction of secret-bearing fields in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/api/test_model_provider_schemas.py`
- [X] T022 [P] [US1] Write validation tests for local base URL allowlist rejection, malformed endpoint locations, unsupported provider types, invalid timeout policy, duplicate models, and unauthorized tenant visibility grants in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/model_providers/test_validation.py`
- [X] T023 [P] [US1] Write repository tests for create/update/list-visible/deactivate behavior and fail-closed unauthorized tenant access in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/db/test_model_provider_connection_repository.py`
- [ ] T024 [P] [US1] Write auth policy tests for platform-admin-only mutation and tenant-scoped read surfaces in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/auth/test_model_provider_policy.py`

### Implementation for User Story 1

- [X] T025 [US1] Implement Pydantic request/response schemas and safe error envelopes for provider connections in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/schemas/model_providers.py`
- [X] T026 [US1] Implement provider connection validation by coordinating local endpoint allowlist checks from `allowlist.py`, duplicate model detection, timeout validation, and tenant visibility validation in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/validation.py`
- [X] T027 [US1] Implement provider-safe redaction helpers for URLs, provider errors, secret references, headers, prompts, completions, and diagnostic summaries in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/redaction.py`
- [X] T028 [US1] Implement the provider connection service facade for create, update, activate, deactivate, list, and detail flows with safe audit calls in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/service.py`
- [X] T029 [US1] Implement admin JSON routes for `/admin/model-providers/api/connections` and connection mutation actions in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/routers/admin_model_providers.py`
- [X] T030 [US1] Register admin model provider routes in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/main.py`
- [X] T031 [US1] Add protected surface policy entries for model provider read, mutation, activation, deactivation, test, and catalog sync routes in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/auth/policy.py`
- [X] T032 [US1] Implement admin UI page models for list, create, edit, detail, tests, catalog, empty/error states, flash states, and safe field summaries in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/ui/model_providers.py`
- [X] T033 [US1] Implement shared-shell list page with filters, health columns, last-test outcome, model count, tenant visibility, catalog sync status, and no cross-tenant hints in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/model_providers/index.html`
- [X] T034 [US1] Implement create/edit form template with provider type fields, local base URL, model definitions, capability metadata, cost metadata, timeout policy, tenant visibility, active state, and secret reference ids in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/model_providers/edit.html`
- [X] T035 [US1] Implement detail template with safe connection metadata, model definitions, tenant visibility, latest health, last test, catalog entries, sync records, and audit/debug links in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/model_providers/detail.html`
- [X] T036 [US1] Implement progressive enhancement for dynamic model rows, metadata validation hints, and test/sync button states in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/static/model_providers.js`
- [X] T037 [US1] Add model provider navigation to the shared admin shell groups in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/ui/admin_console.py`
- [X] T038 [US1] Add model provider admin styling that fits the existing shared shell without nested card layouts in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/static/workflow_studio.css`

**Checkpoint**: User Story 1 is fully functional and testable independently.

---

## Phase 4: User Story 2 - Test Connections And Publish Catalog Entries (Priority: P2)

**Goal**: Platform administrators can run safe provider probes, inspect normalized test results and health, and publish only healthy active tenant-visible models into the routing catalog.

**Independent Test**: Run successful and failing probes for configured OpenAI and local connections, confirm last-test and health evidence is stored safely, then confirm catalog entries are created, updated, blocked, or marked unavailable according to health, activity, and tenant visibility.

### Tests for User Story 2

> Write these tests first and confirm they fail before implementation.

- [ ] T039 [P] [US2] Write OpenAI-compatible local provider contract tests for chat completion request/response shape, timeout handling, malformed responses, and no raw prompt persistence in `/Users/scottcornell/src/my-projects/multi-agent/tests/contract/test_local_openai_compatible_contract.py`
- [X] T040 [P] [US2] Write adapter interface tests for request mapping, safe response normalization, provider unavailable, rate limit, authorization failure, invalid model, and malformed provider response in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/model_providers/test_adapters.py`
- [X] T041 [P] [US2] Write probe tests for OpenAI success, OpenAI auth failure, local success without usage, local endpoint timeout, provider unavailable, invalid model, and safe persisted diagnostics in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/model_providers/test_probes.py`
- [X] T042 [P] [US2] Write secret reference tests for missing, inactive, expired, revoked, tenant-inappropriate, and unauthorized secret refs failing closed without values in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/model_providers/test_secret_references.py`
- [X] T043 [P] [US2] Write health derivation tests for disabled, untested, healthy, degraded, failing, unavailable, and selectable-only-when-healthy states in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/model_providers/test_health.py`
- [X] T044 [P] [US2] Write catalog synchronization tests for create, update, mark unavailable on inactive/deactivated state, block tenant-scope model collisions, and catalog inactive routing state in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/model_providers/test_catalog_sync.py`
- [ ] T045 [P] [US2] Write mocked provider integration tests for OpenAI and local provider success/failure probes in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/providers/test_mock_model_providers.py`
- [ ] T046 [P] [US2] Write admin API integration tests for test probe and sync-catalog actions, including denied tenant attempts and safe audit evidence in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_model_provider_tests_and_catalog.py`
- [ ] T104 [P] [US2] Write admin probe rate-limit and throttled-attempt audit tests in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_model_provider_probe_rate_limits.py`

### Implementation for User Story 2

- [X] T047 [US2] Implement provider adapter protocol, request/response objects, registry, timeout mapping, and normalized error categories in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/adapters.py`
- [X] T048 [US2] Implement OpenAI adapter over `httpx.AsyncClient` with chat completions, safe headers, timeout policy, response normalization, usage extraction hook, and error classification in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/openai_adapter.py`
- [X] T049 [US2] Implement local OpenAI-compatible adapter over `httpx.AsyncClient` with allowlist preflight, redirect rejection, chat completions contract enforcement, timeout policy, and error classification in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/local_adapter.py`
- [X] T050 [US2] Implement credential secret-reference resolution and fail-closed policy checks using existing secret providers in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/secrets.py`
- [X] T051 [US2] Implement safe provider probe construction, execution, result persistence, latency capture, and safe diagnostic summaries in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/probes.py`
- [X] T052 [US2] Implement health derivation and latest health snapshot persistence rules in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/health.py`
- [X] T053 [US2] Implement catalog entry synchronization into existing model_skill_config records with active/healthy/tenant-visible gating, collision blocking, and unavailable marking in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/catalog_sync.py`
- [X] T054 [US2] Extend model routing resolver to select only active, tenant-visible, healthy, gateway-governed provider catalog entries in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/config/resolver.py`
- [X] T055 [US2] Add test and sync-catalog actions to the provider connection service facade with audit-on-denial behavior in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/service.py`
- [X] T056 [US2] Add admin JSON and form routes for `/test`, `/sync-catalog`, `/tests`, and `/catalog` surfaces in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/routers/admin_model_providers.py`
- [ ] T105 [US2] Enforce existing operational rate limits for admin provider test probes and persist safe audit evidence for denied or throttled attempts in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/api/routers/admin_model_providers.py`
- [X] T057 [US2] Implement provider test results template with timestamp, actor/source, latency, tested model, outcome, normalized reason, and safe diagnostics in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/model_providers/test_results.html`
- [X] T058 [US2] Implement provider catalog template with tenant scope, provider type, model id, health state, availability, selectability, governing connection, and collision warnings in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/web_admin/templates/model_providers/catalog.html`
- [X] T059 [US2] Add model provider probe, health, catalog sync, and safe error metrics in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/observability/metrics.py`
- [X] T060 [US2] Add provider-safe structured logging fields and redaction enforcement for probes and catalog sync in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/observability/logging.py`

**Checkpoint**: User Stories 1 and 2 work independently and catalog publication is governed by safe probe health.

---

## Phase 5: User Story 3 - Invoke Models Through The Gateway (Priority: P3)

**Goal**: Runtime workers and test bench runs invoke every model through `ModelGateway`, capturing uniform latency, usage, normalized errors, retry and breaker inputs, traces, and safe audit summaries.

**Independent Test**: Run a workflow and a test bench execution requiring model calls, then verify both use the gateway path and persist safe invocation evidence without prompts, completions, credentials, tokens, or local endpoint secrets.

### Tests for User Story 3

> Write these tests first and confirm they fail before implementation.

- [ ] T061 [P] [US3] Write runtime gateway protocol contract tests for preflight, success, fail-closed visibility denial, invalid secret refs, catalog inactive state, and prohibited persisted metadata in `/Users/scottcornell/src/my-projects/multi-agent/tests/contract/test_runtime_model_gateway_protocol.py`
- [X] T062 [P] [US3] Write gateway unit tests for tenant visibility, healthy catalog lookup, secret resolution, local allowlist recheck, timeout, provider unavailable, retryable categories, and no raw prompt/completion persistence in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/model_providers/test_gateway.py`
- [X] T063 [P] [US3] Write usage metadata extraction tests for OpenAI usage, local usage, missing usage, malformed usage, and safe provider model id capture in `/Users/scottcornell/src/my-projects/multi-agent/tests/unit/model_providers/test_usage.py`
- [ ] T064 [P] [US3] Write audit trace tests for safe gateway summaries, model selection trace metadata, latency, normalized errors, retry inputs, breaker inputs, and redacted provider request ids in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/runtime/test_model_gateway_audit_traces.py`
- [ ] T065 [P] [US3] Write runtime worker integration tests proving workflow model calls use `ModelGateway` and record gateway attempts in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/runtime/test_model_gateway_runtime.py`
- [ ] T066 [P] [US3] Write test bench integration tests proving test bench model calls use `ModelGateway` and share production gateway metadata behavior in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/runtime/test_model_gateway_test_bench.py`
- [ ] T067 [P] [US3] Write static and behavioral guard tests that fail on direct provider SDK or direct provider HTTP calls from workers outside `ModelGateway` in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/workers/test_no_direct_provider_calls.py`
- [ ] T068 [P] [US3] Write gateway performance tests proving p95 wrapper overhead is <=25 ms excluding provider network time in `/Users/scottcornell/src/my-projects/multi-agent/tests/performance/model_providers/test_gateway_latency_overhead.py`

### Implementation for User Story 3

- [X] T069 [US3] Implement `ModelGateway` preflight, invocation lifecycle, adapter dispatch, attempt persistence, fail-closed errors, and safe in-memory response handling in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/gateway.py`
- [X] T070 [US3] Implement usage metadata normalization hooks for OpenAI and local OpenAI-compatible responses in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/model_providers/usage.py`
- [X] T071 [US3] Add gateway trace creation and safe audit summary emission helpers in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/audit/capture.py`
- [X] T072 [US3] Add provider gateway spans and safe trace attributes for selected catalog entry, connection, model, latency, usage availability, and normalized error in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/observability/tracing.py`
- [ ] T073 [US3] Integrate reliability retry classification and circuit breaker scope decisions for gateway invocation attempts in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/reliability/breakers.py`
- [ ] T074 [US3] Add gateway retry budget and retry decision integration using normalized provider error categories in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/reliability/retries.py`
- [ ] T075 [US3] Wire `ModelGateway`, adapter registry, secret resolver, repository, metrics, tracing, and breaker dependencies into runtime bootstrap in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/bootstrap/worker.py`
- [ ] T076 [US3] Replace runtime orchestration model call paths with `ModelGateway` invocation and preserve tenant/run/step trace context in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/runtime/orchestration/service.py`
- [X] T077 [US3] Add side-effect metadata and guardrails that classify model calls as gateway-governed side effects in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/runtime/orchestration/side_effects.py`
- [ ] T078 [US3] Update worker orchestration loops to inject and require the gateway for model-backed execution in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/workers/orchestration.py`
- [ ] T079 [US3] Add test bench gateway integration points and invocation context propagation in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/admin/workflow_registry/service.py`
- [X] T080 [US3] Register gateway invocation metrics for latency, outcome, retry category, breaker decision, and usage availability in `/Users/scottcornell/src/my-projects/multi-agent/src/multi_agent_platform/observability/metrics.py`

**Checkpoint**: User Stories 1, 2, and 3 all work independently with runtime governance through `ModelGateway`.

---

## Phase 6: User Story 4 - Review Delivery Evidence And Safe Operations (Priority: P4)

**Goal**: Reviewers have clear docs, PR notes, testing instructions, coverage evidence, and safe-data verification guidance for release.

**Independent Test**: Follow the submitted docs and testing instructions to verify provider setup, safe probes, catalog updates, tenant visibility, gateway calls, normalized errors, usage metadata, breaker inputs, audit summaries, and secret hygiene without extra verbal guidance.

### Tests for User Story 4

> Write these tests first and confirm they fail before implementation.

- [X] T081 [P] [US4] Write documentation tests for model provider gateway docs, required reviewer flows, and safe-data search instructions in `/Users/scottcornell/src/my-projects/multi-agent/tests/docs/test_model_provider_gateway_docs.py`
- [X] T082 [P] [US4] Write README documentation tests for provider connection setup, admin UI path, gateway behavior, catalog visibility, health state, and sensitive-data protections in `/Users/scottcornell/src/my-projects/multi-agent/tests/docs/test_readme_model_provider_gateway.py`
- [ ] T083 [P] [US4] Write PR note and testing-instruction tests for OpenAI/local setup, success/failure probes, invalid secret refs, unauthorized access, timeout, provider unavailable, inactive catalog, safe redaction, usage capture, and no direct worker calls in `/Users/scottcornell/src/my-projects/multi-agent/tests/docs/test_model_provider_gateway_review_evidence.py`

### Implementation for User Story 4

- [X] T084 [US4] Document provider connection fields, OpenAI setup, local endpoint allowlist setup, safe probes, health states, tenant visibility, catalog publication, ModelGateway behavior, usage capture, breaker inputs, and secret hygiene in `/Users/scottcornell/src/my-projects/multi-agent/docs/model-provider-gateway.md`
- [X] T085 [US4] Add reviewer testing instructions covering admin UI, expected evidence for OpenAI/local provider setup, JSON APIs, mocked providers, safe probe success/failure, invalid secret refs, unauthorized tenant access, local timeout, provider unavailable, catalog inactive state, safe redaction, gateway usage capture, and no direct worker calls in `/Users/scottcornell/src/my-projects/multi-agent/specs/011-model-provider-gateway/testing-instructions.md`
- [X] T086 [US4] Add PR review notes covering setup boundaries, local endpoint safety, catalog sync, gateway-only invocation, trace metadata, usage extraction, retries, breakers, tenant visibility, authorization, audit summaries, tests, known risks, and rollback notes in `/Users/scottcornell/src/my-projects/multi-agent/specs/011-model-provider-gateway/pr-review-notes.md`
- [X] T087 [US4] Update project README with admin UI path, connection configuration guidance, safe testing flow, catalog visibility rules, gateway runtime contract, and sensitive-data verification commands in `/Users/scottcornell/src/my-projects/multi-agent/README.md`
- [X] T088 [US4] Update quickstart reviewer flow with exact commands and expected evidence for the completed implementation in `/Users/scottcornell/src/my-projects/multi-agent/specs/011-model-provider-gateway/quickstart.md`

**Checkpoint**: Review evidence is complete and executable by maintainers.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Validate coverage, quality gates, UI completeness, observability, and release readiness across all stories.

- [ ] T089 [P] Add fixture builders for provider connections, model definitions, tenant visibility, probe results, catalog entries, gateway attempts, and mocked provider transports in `/Users/scottcornell/src/my-projects/multi-agent/tests/fixtures/model_providers.py`
- [ ] T090 [P] Add safe-data regression tests that search connection rows, catalog rows, gateway attempts, logs, and audit summaries for raw API keys, provider tokens, prompts, completions, URL userinfo, Authorization headers, and endpoint secrets in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/runtime/test_model_gateway_secret_hygiene.py`
- [ ] T091 [P] Add admin browser-flow coverage for create/edit/test/sync/catalog pages and responsive shared-shell behavior in `/Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_model_providers_browser_flows.py`
- [ ] T102 [P] Write admin provider listing performance tests proving indexed tenant/status filters keep p95 <=200 ms in `/Users/scottcornell/src/my-projects/multi-agent/tests/performance/model_providers/test_admin_provider_listing_latency.py`
- [ ] T103 [P] Write catalog synchronization performance tests proving 100 configured models sync p95 <=1 second in `/Users/scottcornell/src/my-projects/multi-agent/tests/performance/model_providers/test_catalog_sync_latency.py`
- [X] T092 Run `uv run ruff check .` from `/Users/scottcornell/src/my-projects/multi-agent/` and record any required file-specific fixes as follow-up tasks before changing files
- [X] T093 Run `uv run ruff format --check .` from `/Users/scottcornell/src/my-projects/multi-agent/` and record any required file-specific fixes as follow-up tasks before changing files
- [X] T094 Run `uv run mypy src` from `/Users/scottcornell/src/my-projects/multi-agent/` and record any required file-specific fixes as follow-up tasks before changing files
- [X] T095 Run `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90` from `/Users/scottcornell/src/my-projects/multi-agent/` and record any required file-specific fixes as follow-up tasks before changing files
- [X] T096 Run and fix migration validation with `uv run alembic upgrade head` and rollback coverage in `/Users/scottcornell/src/my-projects/multi-agent/alembic/versions/0011_model_provider_gateway.py`
- [ ] T097 Verify admin web UI manually at `/admin/model-providers` and record any broken template, route, JavaScript, or CSS behavior as file-specific follow-up tasks before changing files

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; creates package, UI, and docs placeholders.
- **Foundational (Phase 2)**: Depends on Setup; blocks all user stories because schema, settings, repository, and domain contracts are shared.
- **User Story 1 (Phase 3)**: Depends on Foundational; produces the MVP provider connection admin lifecycle.
- **User Story 2 (Phase 4)**: Depends on Foundational and uses US1 connection records; independently testable through probe and catalog APIs/UI.
- **User Story 3 (Phase 5)**: Depends on Foundational and uses US2 healthy catalog entries for full acceptance; gateway fail-closed behavior can be tested independently with fixtures.
- **User Story 4 (Phase 6)**: Depends on implemented stories for accurate docs and reviewer evidence.
- **Polish (Phase 7)**: Depends on the selected story set and finalizes quality gates.

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2; MVP scope.
- **US2 (P2)**: Starts after Phase 2 but needs US1 data paths to run end-to-end.
- **US3 (P3)**: Starts after Phase 2 with fixtures; full runtime success path needs US2 catalog sync.
- **US4 (P4)**: Starts after story behavior is available for accurate evidence.

### Within Each User Story

- Tests must be written first and fail before implementation.
- Models and schemas precede services.
- Services precede routers, templates, runtime integration, and docs.
- Story checkpoints must pass before depending stories are treated as complete.

---

## Parallel Opportunities

- Setup tasks T002 through T006 can run in parallel after T001.
- Foundational test tasks T007 through T010 plus T098 and T100 can run in parallel.
- US1 test tasks T018 through T024 can run in parallel before implementation.
- US2 test tasks T039 through T046 plus T104 can run in parallel before implementation.
- US3 test tasks T061 through T068 can run in parallel before implementation.
- US4 test tasks T081 through T083 can run in parallel before documentation.
- Performance test tasks T102 and T103 can run in parallel with other polish validation after their target surfaces exist.
- After Phase 2, US1, US2 fixture-backed tests, and US3 fixture-backed tests can be drafted in parallel, but end-to-end acceptance should validate in story priority order.

## Parallel Example: User Story 1

```bash
Task: "Write API integration tests for platform-admin create/update/activate/deactivate and tenant read visibility in /Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_model_providers_api.py"
Task: "Write admin UI integration tests for list/create/edit/detail pages, disabled tenant mutation controls, shell navigation, validation states, and safe secret reference display in /Users/scottcornell/src/my-projects/multi-agent/tests/integration/api/test_admin_model_providers_ui.py"
Task: "Write validation tests for local base URL allowlist rejection, malformed endpoint locations, unsupported provider types, invalid timeout policy, duplicate models, and unauthorized tenant visibility grants in /Users/scottcornell/src/my-projects/multi-agent/tests/unit/model_providers/test_validation.py"
```

## Parallel Example: User Story 2

```bash
Task: "Write adapter interface tests for request mapping, safe response normalization, provider unavailable, rate limit, authorization failure, invalid model, and malformed provider response in /Users/scottcornell/src/my-projects/multi-agent/tests/unit/model_providers/test_adapters.py"
Task: "Write probe tests for OpenAI success, OpenAI auth failure, local success without usage, local endpoint timeout, provider unavailable, invalid model, and safe persisted diagnostics in /Users/scottcornell/src/my-projects/multi-agent/tests/unit/model_providers/test_probes.py"
Task: "Write catalog synchronization tests for create, update, mark unavailable on inactive/deactivated state, block tenant-scope model collisions, and catalog inactive routing state in /Users/scottcornell/src/my-projects/multi-agent/tests/unit/model_providers/test_catalog_sync.py"
```

## Parallel Example: User Story 3

```bash
Task: "Write runtime gateway protocol contract tests for preflight, success, fail-closed visibility denial, invalid secret refs, catalog inactive state, and prohibited persisted metadata in /Users/scottcornell/src/my-projects/multi-agent/tests/contract/test_runtime_model_gateway_protocol.py"
Task: "Write runtime worker integration tests proving workflow model calls use ModelGateway and record gateway attempts in /Users/scottcornell/src/my-projects/multi-agent/tests/integration/runtime/test_model_gateway_runtime.py"
Task: "Write static and behavioral guard tests that fail on direct provider SDK or direct provider HTTP calls from workers outside ModelGateway in /Users/scottcornell/src/my-projects/multi-agent/tests/integration/workers/test_no_direct_provider_calls.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup.
2. Complete Phase 2 foundation.
3. Complete Phase 3 tests and implementation.
4. Validate US1 independently with API and admin UI tests.
5. Demo provider connection lifecycle and tenant-safe read visibility.

### Incremental Delivery

1. Add US1 provider connection lifecycle and web UI support.
2. Add US2 safe probes, health, and catalog sync.
3. Add US3 gateway-only runtime invocation and operational evidence.
4. Add US4 reviewer docs, testing instructions, PR notes, and README updates.
5. Finish Phase 7 quality gates and coverage.

### Acceptance Coverage Map

- Success and failure probes: T041, T045, T046, T051
- Side-effect recovery/idempotency: T098, T099
- Invalid secret refs: T042, T050, T061, T062
- Unauthorized tenant access: T019, T023, T024, T031
- Local endpoint allowlist and timeout: T010, T022, T026, T039, T041, T049, T051, T100, T101
- Provider unavailable: T040, T041, T047, T048, T049
- Catalog inactive state: T044, T053, T054, T061
- Safe redaction: T021, T027, T060, T090
- Gateway usage capture: T063, T069, T070, T080
- Admin probe rate limiting and throttle audit: T104, T105
- Performance targets: T068, T102, T103
- No direct provider calls from workers outside gateway: T067, T075, T076, T078
- Web UI support for new features: T020, T032 through T038, T057, T058, T091, T097

## Extension Hooks

**Optional Pre-Hook**: git
Command: `/speckit.git.commit`
Description: Auto-commit before task generation

Prompt: Commit outstanding changes before task generation?
To execute: `/speckit.git.commit`

**Optional Hook**: git
Command: `/speckit.git.commit`
Description: Auto-commit after task generation

Prompt: Commit task changes?
To execute: `/speckit.git.commit`
