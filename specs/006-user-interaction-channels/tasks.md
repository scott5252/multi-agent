# Tasks: User Interaction Channels

**Input**: Design documents from `/specs/006-user-interaction-channels/`
**Prerequisites**: `plan.md` (required), `spec.md` (required), `research.md`,
`data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Required. The specification requires at least 90 percent unit-test
coverage plus channel-level contract and integration tests for Web UI,
Telegram, Web API, status, timeline, streaming updates, terminal
notifications, final results, approval/resume flows, artifact downloads,
auth checks, and terminal-state behavior.

**Organization**: Tasks are grouped by user story so each story can be
implemented and validated as an independent increment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Used only for safely isolated adapter work in separate files.
- **[Story]**: Maps implementation work to the user stories in
  `specs/006-user-interaction-channels/spec.md`.
- Every task includes at least one concrete file path.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create channel package scaffolding, route placeholders, test
locations, and QA artifacts before shared implementation begins.

- [ ] T001 Create channel package exports and placeholder modules in `src/multi_agent_platform/channels/__init__.py`, `src/multi_agent_platform/channels/adapters.py`, `src/multi_agent_platform/channels/models.py`, `src/multi_agent_platform/channels/service.py`, `src/multi_agent_platform/channels/normalization.py`, `src/multi_agent_platform/channels/state_mapping.py`, `src/multi_agent_platform/channels/errors.py`, `src/multi_agent_platform/channels/idempotency.py`, `src/multi_agent_platform/channels/notifications.py`, `src/multi_agent_platform/channels/artifacts.py`, `src/multi_agent_platform/channels/callbacks.py`, and `src/multi_agent_platform/channels/telegram.py`
- [ ] T002 Create channel API and Web UI route placeholders in `src/multi_agent_platform/api/routers/channel_runs.py`, `src/multi_agent_platform/api/routers/telegram_webhook.py`, `src/multi_agent_platform/api/routers/web_run_ui.py`, `src/multi_agent_platform/api/schemas/channel_runs.py`, and `src/multi_agent_platform/api/ui/run_details.py`
- [ ] T003 Create channel persistence placeholders in `src/multi_agent_platform/db/models/channels.py`, `src/multi_agent_platform/db/repositories/channels.py`, and `alembic/versions/0006_user_interaction_channels.py`
- [ ] T004 Create Web UI asset and template placeholders in `src/multi_agent_platform/web_admin/static/run_details.js`, `src/multi_agent_platform/web_admin/templates/runs/index.html`, and `src/multi_agent_platform/web_admin/templates/runs/detail.html`
- [ ] T005 Create channel test scaffolding in `tests/unit/channels/__init__.py`, `tests/unit/api/test_channel_run_schemas.py`, `tests/contract/test_channel_layer_contract.py`, `tests/integration/api/test_channel_run_api.py`, `tests/integration/api/test_web_run_ui.py`, `tests/integration/api/test_telegram_webhook.py`, `tests/integration/channels/test_cross_channel_recovery.py`, `tests/integration/channels/test_notification_delivery.py`, and `tests/integration/channels/test_api_callbacks.py`
- [ ] T006 Create reviewer delivery placeholders in `docs/user-interaction-channels.md`, `specs/006-user-interaction-channels/pr-review-notes.md`, `specs/006-user-interaction-channels/testing-instructions.md`, `specs/006-user-interaction-channels/qa006.md`, and `specs/006-user-interaction-channels/.env.qa006`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared persistence, schemas, request envelopes, auth,
idempotency, rate limits, errors, state mapping, and service boundaries that
all channel stories depend on.

**Critical**: No user story work should begin until this phase is complete.

### Tests First

- [ ] T007 Add settings tests for Telegram secrets, Telegram link token TTL bounds, callback signing, artifact URL TTL default/max bounds, SSE heartbeat, channel rate limits, and local-principal defaults in `tests/unit/config/test_settings.py`
- [ ] T008 Add SQLAlchemy model and migration tests for channel sessions, Telegram links, normalized requests, idempotency records, timeline events, notification subscriptions, delivery attempts, callback registrations, callback delivery attempts, artifact grants, and interaction audits in `tests/unit/db/test_channel_models.py` and `tests/integration/db/test_migrations.py`
- [ ] T009 Add request envelope normalization tests for Web UI, Web API, Telegram, trace propagation, platform identity resolution, tenant resolution, idempotency-key requirements, and redacted source metadata in `tests/unit/channels/test_normalization.py`
- [ ] T010 Add state mapping tests for internal runtime states to exactly `queued`, `running`, `waiting-for-input`, `completed`, `failed`, and `canceled` in `tests/unit/channels/test_state_mapping.py`
- [ ] T011 Add channel error mapping tests for unauthorized, missing input, invalid run id, unavailable delivery, invalid lifecycle action, idempotency conflict, rate limited, artifact unavailable, callback delivery failed, and platform failure in `tests/unit/channels/test_errors.py`
- [ ] T012 Add idempotency tests for matching replay, conflicting replay, in-progress outcome, expiry, and per-tenant actor channel action uniqueness in `tests/unit/channels/test_idempotency.py`
- [ ] T013 Add auth integration tests for Web UI, Web API, Telegram linked identity, cross-tenant denial, permission mismatch, stale local principal, and action-specific authorization in `tests/integration/api/test_channel_auth.py`
- [ ] T013A Add Telegram link-token issuance integration tests for authenticated Web UI and Web API users, tenant scoping, 10-minute expiry, one-time consumption, expired/reused token denial, and unlinked Telegram protected-action denial in `tests/integration/api/test_channel_auth.py` and `tests/integration/api/test_web_run_ui.py`
- [ ] T014 Add shared channel facade tests for start, status, timeline, result, decision, cancel, subscription, callback registration, artifact grant, audit emission, and rate limit enforcement in `tests/unit/channels/test_service.py`

### Implementation

- [ ] T015 Add channel configuration settings and defaults in `src/multi_agent_platform/config/settings.py`
- [ ] T015A Implement secret-reference settings and production guardrails for Telegram provider tokens and callback signing secrets in `src/multi_agent_platform/config/settings.py`
- [ ] T016 Implement channel SQLAlchemy models and metadata registration in `src/multi_agent_platform/db/models/channels.py` and `src/multi_agent_platform/db/models/__init__.py`
- [ ] T017 Implement Alembic migration for channel sessions, Telegram identity links, normalized requests, idempotency records, timeline projections, notification subscriptions, delivery attempts, callback registrations, callback delivery attempts, artifact grants, and interaction audit records in `alembic/versions/0006_user_interaction_channels.py`
- [ ] T018 Implement channel repository operations with tenant predicates, idempotency locking, timeline pagination, delivery attempt storage, callback attempt storage, artifact grant storage, and audit insertion in `src/multi_agent_platform/db/repositories/channels.py`
- [ ] T019 Implement channel domain models, enums, and typed result objects in `src/multi_agent_platform/channels/models.py`
- [ ] T020 Implement canonical normalized request envelope creation for Web UI, Web API, Telegram, trace ids, source request ids, action metadata, and idempotency requirements in `src/multi_agent_platform/channels/normalization.py`
- [ ] T021 Implement user-visible state mapping and waiting prompt projection helpers in `src/multi_agent_platform/channels/state_mapping.py`
- [ ] T022 Implement shared channel error categories and presentation-safe error objects in `src/multi_agent_platform/channels/errors.py`
- [ ] T023 Implement channel idempotency policy and stored outcome handling in `src/multi_agent_platform/channels/idempotency.py`
- [ ] T024 Implement the channel service facade over runtime orchestration, approval/resume, authorization, rate limits, audit, timeline projection, notifications, callbacks, results, and artifact grants in `src/multi_agent_platform/channels/service.py`
- [ ] T025 Wire the channel repository and service into application dependencies in `src/multi_agent_platform/bootstrap/container.py` and `src/multi_agent_platform/api/deps.py`
- [ ] T025A Implement Telegram link-token issuance for authenticated Web UI and Web API users with tenant-aware authorization, durable one-time token storage, 10-minute expiry, safe reuse/expiry errors, and audit records in `src/multi_agent_platform/api/routers/channel_runs.py`, `src/multi_agent_platform/api/routers/web_run_ui.py`, `src/multi_agent_platform/channels/service.py`, and `src/multi_agent_platform/db/repositories/channels.py`

**Checkpoint**: Shared channel infrastructure is complete; user story phases
can begin.

---

## Phase 3: User Story 1 - Start Workflow Runs From Any Channel (Priority: P1) MVP

**Goal**: Authenticated users can start the same allowed workflow from Web UI,
Telegram, or Web API and receive the same canonical run identifier and
lifecycle semantics.

**Independent Test**: Invoke the same eligible workflow from Web UI, Telegram,
and Web API, then confirm equivalent authorization, normalized inputs,
idempotency behavior, initial state, audit evidence, and returned run id.

### Tests for User Story 1

> Write these tests first and confirm they fail before implementation.

- [ ] T026 [US1] Add contract tests for `POST /runs` accepted, missing input, unauthorized, forbidden, idempotency conflict, and rate-limited responses in `tests/contract/test_channel_layer_contract.py`
- [ ] T027 [US1] Add shared invocation service tests for workflow selection, input validation, authorization, runtime start delegation, automatic notification subscription, and audit outcome in `tests/unit/channels/test_service.py`
- [ ] T028 [US1] Add API route integration tests for Web API run starts, local-principal auth, tenant headers, idempotency replay, idempotency conflict, and missing workflow inputs in `tests/integration/api/test_channel_run_api.py`
- [ ] T029 [US1] Add Web UI invocation tests for list page, new-run form, POST handling, validation errors, successful redirect, and run id display in `tests/integration/api/test_web_run_ui.py`
- [ ] T030 [US1] Add Telegram webhook invocation tests for unlinked `/run` denial, linked `/run` success, duplicate `update_id` replay, missing input prompt, and safe authorization failures in `tests/integration/api/test_telegram_webhook.py`

### Implementation for User Story 1

- [ ] T031 [US1] Implement Web API run-start schemas for invocation request, invocation response, channel error, idempotency key validation, trace fields, and channel source validation in `src/multi_agent_platform/api/schemas/channel_runs.py`
- [ ] T032 [US1] Implement Web API `POST /runs` route with auth dependencies, normalized request creation, idempotency handling, shared service invocation, and 202/error responses in `src/multi_agent_platform/api/routers/channel_runs.py`
- [ ] T033 [P] [US1] Implement Web UI run list, new-run form, invocation POST, validation rendering, redirect behavior, and route registration in `src/multi_agent_platform/api/routers/web_run_ui.py`
- [ ] T034 [P] [US1] Implement Web UI run list and new-run templates in `src/multi_agent_platform/web_admin/templates/runs/index.html` and `src/multi_agent_platform/web_admin/templates/runs/detail.html`
- [ ] T035 [P] [US1] Implement Telegram `/start`, `/link`, `/run`, link-token consumption, duplicate update handling, and protected-command denial behavior in `src/multi_agent_platform/channels/telegram.py`
- [ ] T036 [P] [US1] Implement Telegram webhook route provider-secret validation, update parsing, generic retry-safe responses, and route registration in `src/multi_agent_platform/api/routers/telegram_webhook.py`
- [ ] T037 [US1] Register channel API, Web UI, and Telegram routers in `src/multi_agent_platform/api/main.py`
- [ ] T038 [US1] Add run-start audit events, metrics, and trace attributes for channel source, tenant, actor, workflow id, idempotency result, and run id without raw input leakage in `src/multi_agent_platform/channels/service.py`, `src/multi_agent_platform/observability/metrics.py`, and `src/multi_agent_platform/observability/tracing.py`

**Checkpoint**: User Story 1 is functional and independently testable as the
MVP.

---

## Phase 4: User Story 2 - Track Run Progress and Status (Priority: P2)

**Goal**: Users can retrieve durable status, timeline events, streaming
updates, terminal notifications, and final results by run identifier from any
authorized channel.

**Independent Test**: Start a run, observe live updates where available,
disconnect, retrieve persisted status and timeline by run id from another
channel, receive terminal notification attempts, and retrieve final result by
run id.

### Tests for User Story 2

> Write these tests first and confirm they fail before implementation.

- [ ] T039 [US2] Add contract tests for `GET /runs/{run_id}/status`, `GET /runs/{run_id}/timeline`, `GET /runs/{run_id}/events`, `GET /runs/{run_id}/result`, and `POST /runs/{run_id}/subscriptions` response shapes and error categories in `tests/contract/test_channel_layer_contract.py`
- [ ] T040 [US2] Add status and timeline service tests for latest state, progress summary, waiting prompt summary, terminal outcome, result availability, permitted actions, cursor pagination, redaction, and invalid run id handling in `tests/unit/channels/test_service.py`
- [ ] T041 [US2] Add SSE unit tests for event formatting, `Last-Event-ID`, heartbeat, disconnect cleanup, terminal stop behavior, and authorization denial in `tests/unit/channels/test_streaming.py`
- [ ] T042 [US2] Add notification service tests for automatic initiator subscription, explicit subscription, authorization re-check, terminal-only delivery, retry scheduling, suppression, and payload redaction in `tests/unit/channels/test_notifications.py`
- [ ] T042A [US2] Add notification acknowledgement tests for Web API/Web UI acknowledgement requests, idempotency-key replay, conflicting replay, unauthorized acknowledgement denial, and audit evidence in `tests/unit/channels/test_notifications.py` and `tests/integration/api/test_channel_run_api.py`
- [ ] T043 [US2] Add result retrieval tests for available, failed, canceled, unavailable, expired, unauthorized, and redacted structured-result cases in `tests/unit/channels/test_results.py`
- [ ] T044 [US2] Add API integration tests for status endpoints, timeline endpoints, result retrieval, subscription creation, terminal-state behavior, and cross-tenant safe not-found behavior in `tests/integration/api/test_channel_run_api.py`
- [ ] T045 [US2] Add Web UI run details tests for status rendering, timeline rendering, SSE connection markup, polling fallback state, result area, subscription state, terminal state behavior, and trace support details in `tests/integration/api/test_web_run_ui.py`
- [ ] T046 [US2] Add Telegram status, result, subscribe, bounded `/watch` and `/unwatch`, and terminal notification tests for linked users, unlinked users, duplicate updates, redacted payloads, throttled progress watches, and delivery-attempt evidence in `tests/integration/api/test_telegram_webhook.py` and `tests/integration/channels/test_notification_delivery.py`
- [ ] T047 [US2] Add API callback tests for registration, HTTPS validation, signed terminal payloads, signed waiting-prompt payloads, retry attempts, disabled callback behavior, and lifecycle non-mutation on delivery failure in `tests/integration/channels/test_api_callbacks.py`
- [ ] T048 [US2] Add cross-channel recovery tests for start in one channel, status in another, terminal notification delivery, final result retrieval, and persisted state after live connection loss in `tests/integration/channels/test_cross_channel_recovery.py`

### Implementation for User Story 2

- [ ] T049 [US2] Extend channel API schemas for run status, timeline page, timeline event, waiting prompt view, result response, subscription request/response, callback registration, and terminal notification payloads in `src/multi_agent_platform/api/schemas/channel_runs.py`
- [ ] T050 [US2] Implement status, timeline, SSE events, result retrieval, notification subscription, and callback registration routes in `src/multi_agent_platform/api/routers/channel_runs.py`
- [ ] T051 [US2] Implement timeline projection, status view construction, permitted action calculation, result view construction, and cross-channel read auditing in `src/multi_agent_platform/channels/service.py`
- [ ] T052 [US2] Implement SSE streaming helpers, heartbeat events, `Last-Event-ID` resume, and terminal stream completion in `src/multi_agent_platform/channels/streaming.py`
- [ ] T053 [US2] Implement terminal notification subscription, delivery scheduling, authorization re-check, retry policy, suppression, and redacted payload formatting in `src/multi_agent_platform/channels/notifications.py`
- [ ] T053A [US2] Implement notification acknowledgement handling with idempotency keys, authorization checks, stored acknowledgement outcome, and audit records in `src/multi_agent_platform/channels/notifications.py`, `src/multi_agent_platform/channels/service.py`, `src/multi_agent_platform/api/routers/channel_runs.py`, and `src/multi_agent_platform/db/repositories/channels.py`
- [ ] T054 [US2] Implement API callback registration, HMAC signing, delivery attempt storage, retry scheduling, HTTPS validation, and failure categorization in `src/multi_agent_platform/channels/callbacks.py`
- [ ] T055 [P] [US2] Implement Web UI run details view model for status, timeline, prompt summary, result, artifacts placeholder, subscription, callbacks, and support trace id in `src/multi_agent_platform/api/ui/run_details.py`
- [ ] T056 [P] [US2] Implement Web UI details route, result loading, subscription action, SSE endpoint delegation, and polling data responses in `src/multi_agent_platform/api/routers/web_run_ui.py`
- [ ] T057 [P] [US2] Implement Web UI live update JavaScript for SSE connection, `Last-Event-ID`, polling fallback, terminal stop behavior, result refresh, and stale connection display in `src/multi_agent_platform/web_admin/static/run_details.js`
- [ ] T058 [P] [US2] Implement Web UI run details template sections for state, run id, progress summary, timeline, terminal notification state, result, callbacks, and support trace id in `src/multi_agent_platform/web_admin/templates/runs/detail.html`
- [ ] T059 [P] [US2] Implement Telegram `/status`, `/result`, `/subscribe`, bounded `/watch` and `/unwatch`, and terminal notification rendering in `src/multi_agent_platform/channels/telegram.py`
- [ ] T060 [US2] Wire notification and callback delivery work into the worker bootstrap in `src/multi_agent_platform/workers/main.py`, `src/multi_agent_platform/workers/loops.py`, and `src/multi_agent_platform/bootstrap/worker.py`
- [ ] T060A [US2] Implement tenant-scoped delivery leases, lease expiry recovery, max-attempt handling, and dead-letter evidence for notification, callback, and Telegram progress-watch workers in `src/multi_agent_platform/workers/loops.py`, `src/multi_agent_platform/channels/notifications.py`, and `src/multi_agent_platform/channels/callbacks.py`
- [ ] T060B [US2] Add delivery lease and compensation tests for worker crash, duplicate lease acquisition, retry exhaustion, and observed-success reconciliation in `tests/integration/channels/test_notification_delivery.py` and `tests/integration/channels/test_api_callbacks.py`
- [ ] T061 [US2] Add metrics, logs, traces, and audits for status reads, timeline reads, SSE delivery, notification attempts, callback attempts, result reads, rate limits, and terminal-state behavior in `src/multi_agent_platform/observability/metrics.py`, `src/multi_agent_platform/observability/logging.py`, and `src/multi_agent_platform/observability/tracing.py`

**Checkpoint**: User Stories 1 and 2 are independently functional.

---

## Phase 5: User Story 3 - Approve, Reject, and Resume Waiting Runs (Priority: P3)

**Goal**: Authorized reviewers can inspect waiting prompts and approve, reject,
resume, or cancel runs from each supported channel without changing workflow
decision semantics.

**Independent Test**: Move a run into `waiting-for-input`, present the prompt
in each channel, submit approve/reject/resume/cancel decisions, and confirm
authorization, prompt freshness, idempotency, stale-response handling, and
latest-status behavior.

### Tests for User Story 3

> Write these tests first and confirm they fail before implementation.

- [ ] T062 [US3] Add contract tests for `POST /runs/{run_id}/approvals/{prompt_id}/decision` and `POST /runs/{run_id}/cancel` accepted, unauthorized, stale prompt, invalid action, idempotency replay, and latest status response shapes in `tests/contract/test_channel_layer_contract.py`
- [ ] T063 [US3] Add decision service tests for waiting prompt projection, eligible reviewer checks, prompt version matching, approve, reject, resume payload, cancel, stale prompt response, and unchanged run on rejected response in `tests/unit/channels/test_approvals.py`
- [ ] T064 [US3] Add API integration tests for approval, reject, resume, cancel, stale decision, duplicate key, conflicting key, terminal-state behavior, and unauthorized reviewer denial in `tests/integration/api/test_channel_run_api.py`
- [ ] T065 [US3] Add Web UI approval prompt tests for action visibility, disabled terminal controls, approve/reject/resume/cancel submissions, stale-button refresh, latest status rendering, and error banners in `tests/integration/api/test_web_run_ui.py`
- [ ] T066 [US3] Add Telegram approval tests for `/approve`, `/reject`, `/resume`, `/cancel`, protected-command linking, stale prompt behavior, duplicate `update_id`, concise errors, and updated status messages in `tests/integration/api/test_telegram_webhook.py`
- [ ] T067 [US3] Add cross-channel prompt tests for opening a prompt in Telegram, approving in Web UI, seeing stale Telegram response rejected, and retrieving latest status through Web API in `tests/integration/channels/test_cross_channel_recovery.py`

### Implementation for User Story 3

- [ ] T068 [US3] Extend channel API schemas for prompt decision request, prompt decision response, cancel request, latest status snapshot, stale prompt error, and decision audit fields in `src/multi_agent_platform/api/schemas/channel_runs.py`
- [ ] T069 [US3] Implement approval decision and cancel routes with auth dependencies, idempotency keys, prompt version validation, latest-status responses, and error mapping in `src/multi_agent_platform/api/routers/channel_runs.py`
- [ ] T070 [US3] Implement waiting prompt view, decision validation, runtime approval/resume delegation, cancel delegation, stale prompt detection, first-valid-decision preservation, and audit writes in `src/multi_agent_platform/channels/service.py`
- [ ] T071 [P] [US3] Implement Web UI waiting prompt controls, decision form handling, resume payload handling, stale refresh behavior, and disabled terminal controls in `src/multi_agent_platform/api/routers/web_run_ui.py` and `src/multi_agent_platform/api/ui/run_details.py`
- [ ] T072 [P] [US3] Implement Web UI prompt controls and client-side action state updates in `src/multi_agent_platform/web_admin/templates/runs/detail.html` and `src/multi_agent_platform/web_admin/static/run_details.js`
- [ ] T073 [P] [US3] Implement Telegram `/approve`, `/reject`, `/resume`, `/cancel`, prompt version handling, stale prompt messages, and updated status responses in `src/multi_agent_platform/channels/telegram.py`
- [ ] T074 [US3] Add decision, cancellation, stale prompt, unauthorized prompt, and terminal-control metrics and traces in `src/multi_agent_platform/observability/metrics.py` and `src/multi_agent_platform/observability/tracing.py`

**Checkpoint**: User Stories 1 through 3 are independently functional.

---

## Phase 6: User Story 4 - Retrieve Artifacts and Delivery Evidence (Priority: P4)

**Goal**: Authorized users can list run artifacts, request short-lived
platform-authenticated download URLs, and review delivery evidence,
documentation, testing instructions, README guidance, and PR notes.

**Independent Test**: Complete a run with artifacts, list artifact metadata,
request download URLs from each channel, verify expired/unauthorized URL
behavior, and inspect docs, QA instructions, README updates, coverage, and PR
review notes.

### Tests for User Story 4

> Write these tests first and confirm they fail before implementation.

- [ ] T075 [US4] Add contract tests for `GET /runs/{run_id}/artifacts` and `POST /runs/{run_id}/artifacts/{artifact_id}/download-url` metadata, download URL, unauthorized, expired, unavailable, and idempotency conflict response shapes in `tests/contract/test_channel_layer_contract.py`
- [ ] T076 [US4] Add artifact service tests for metadata listing, result-policy enforcement, short-lived grant creation, idempotent replay, expired grant denial, direct-byte suppression, and audit records in `tests/unit/channels/test_artifacts.py`
- [ ] T077 [US4] Add API integration tests for artifact listing, download URL creation, cross-tenant denial, unavailable artifact, expired grant, terminal-state behavior, and no artifact bytes in JSON responses in `tests/integration/api/test_channel_run_api.py`
- [ ] T078 [US4] Add Web UI artifact tests for artifact rows, status labels, download action creation, expired URL refresh, error banner categories, and no object-storage reference leakage in `tests/integration/api/test_web_run_ui.py`
- [ ] T079 [US4] Add Telegram artifact tests for `/artifacts`, protected linking, artifact metadata summaries, short-lived download actions, no direct bytes, duplicate updates, and unavailable artifact messages in `tests/integration/api/test_telegram_webhook.py`
- [ ] T080 [US4] Add terminal-state behavior tests for completed, failed, canceled, artifact-ready, result-unavailable, notification-attempt evidence, callback-attempt evidence, and subscription suppression in `tests/integration/channels/test_notification_delivery.py`
- [ ] T081 [US4] Add documentation validation tests for required QA guide, testing instructions, PR review notes, and README channel sections in `tests/docs/test_user_interaction_channels_docs.py`

### Implementation for User Story 4

- [ ] T082 [US4] Extend channel API schemas for artifact list response, artifact metadata item, artifact download URL response, grant expiry, and artifact error categories in `src/multi_agent_platform/api/schemas/channel_runs.py`
- [ ] T083 [US4] Implement artifact list and download URL routes with auth dependencies, idempotency keys, result-policy checks, grant creation, and no direct-byte responses in `src/multi_agent_platform/api/routers/channel_runs.py`
- [ ] T084 [US4] Implement artifact metadata lookup, short-lived platform-authenticated URL grant creation, grant expiry, authorization checks, and audit writes in `src/multi_agent_platform/channels/artifacts.py`
- [ ] T085 [US4] Integrate artifact listing and download URL grant creation into the channel service facade in `src/multi_agent_platform/channels/service.py`
- [ ] T086 [P] [US4] Implement Web UI artifact rows, download actions, expired URL refresh, and artifact error rendering in `src/multi_agent_platform/api/ui/run_details.py`, `src/multi_agent_platform/api/routers/web_run_ui.py`, `src/multi_agent_platform/web_admin/templates/runs/detail.html`, and `src/multi_agent_platform/web_admin/static/run_details.js`
- [ ] T087 [P] [US4] Implement Telegram `/artifacts` metadata rendering and fresh download action behavior in `src/multi_agent_platform/channels/telegram.py`
- [ ] T088 [US4] Write operator and reviewer documentation for channel concepts, lifecycle states, auth integration, Telegram linking, status/timeline/result flows, approvals/resumes, notifications, callbacks, artifact downloads, rate limits, audits, and troubleshooting in `docs/user-interaction-channels.md`
- [ ] T089 [US4] Write PR review notes covering shared invocation, lifecycle consistency, authorization, approval and resume flows, notifications, artifact access, cross-channel recovery, terminal-state behavior, known risks, and coverage evidence in `specs/006-user-interaction-channels/pr-review-notes.md`
- [ ] T090 [US4] Write reviewer testing instructions for Web UI, Telegram, Web API invocation, live progress, persisted status, terminal notifications, final results, approval, resume, cancellation, artifact downloads, auth denials, and rate limits in `specs/006-user-interaction-channels/testing-instructions.md`
- [ ] T091 [US4] Update the repository README with available channels, run lifecycle states, run id usage, approval and resume behavior, notifications, artifact downloads, auth setup, QA commands, and review verification steps in `README.md`

**Checkpoint**: All user stories are independently functional and reviewable.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Finish coverage, performance, security, docs consistency, QA
validation, and review evidence across all stories.

- [ ] T092 Add rate-limit regression tests for tenant, platform identity, action type, channel throttle, retry-after payload, and cross-channel bypass prevention in `tests/unit/channels/test_rate_limits.py` and `tests/integration/api/test_channel_auth.py`
- [ ] T092A Add fair-scheduling tests for per-tenant delivery concurrency, callback budget exhaustion, Telegram progress-watch throttling, SSE fan-out throttling, and tenant starvation prevention in `tests/unit/channels/test_rate_limits.py` and `tests/integration/channels/test_notification_delivery.py`
- [ ] T092B Implement per-tenant delivery concurrency budgets and fairness metrics in `src/multi_agent_platform/channels/notifications.py`, `src/multi_agent_platform/channels/callbacks.py`, `src/multi_agent_platform/workers/loops.py`, and `src/multi_agent_platform/observability/metrics.py`
- [ ] T093 Add security redaction tests for result summaries, artifact names, Telegram text, timeline events, logs, metrics, traces, audit records, callback payloads, and notification payloads in `tests/unit/channels/test_security_redaction.py`
- [ ] T094 Add channel performance tests for run start under 2 seconds, status lookup p95 under 300ms, timeline latest-100 p95 under 300ms, SSE fan-out under 1 second, and terminal notification scheduling under 30 seconds in `tests/performance/channels/test_channel_latency.py`
- [ ] T095 Update repository quickstart with channel API, Web UI, Telegram, callback, approval, result, and artifact examples in `docs/quickstart.md`
- [ ] T096 Validate `specs/006-user-interaction-channels/qa006.md` against the implemented API and update expected request/response examples in `specs/006-user-interaction-channels/qa006.md`
- [ ] T097 Validate `specs/006-user-interaction-channels/.env.qa006` is sufficient for a clean local QA run without depending on previous spec env files in `specs/006-user-interaction-channels/.env.qa006`
- [ ] T098 Run `uv run ruff check .` and record the result in `specs/006-user-interaction-channels/pr-review-notes.md`
- [ ] T099 Run `uv run ruff format --check .` and record the result in `specs/006-user-interaction-channels/pr-review-notes.md`
- [ ] T100 Run `uv run mypy src` and record the result in `specs/006-user-interaction-channels/pr-review-notes.md`
- [ ] T101 Run channel-focused tests and record the command output summary in `specs/006-user-interaction-channels/pr-review-notes.md`
- [ ] T102 Run `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90` and record coverage evidence in `specs/006-user-interaction-channels/pr-review-notes.md`
- [ ] T103 Review `specs/006-user-interaction-channels/tasks.md` for unchecked task format, story traceability, `[P]` usage limited to isolated adapters, and implementation follow-up notes before PR handoff in `specs/006-user-interaction-channels/tasks.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1: Setup**: No dependencies.
- **Phase 2: Foundational**: Depends on Setup and blocks all user stories.
- **Phase 3: US1**: Depends on Foundational and is the MVP.
- **Phase 4: US2**: Depends on US1 because status, timeline, streaming,
  notifications, callbacks, and result retrieval require accepted runs.
- **Phase 5: US3**: Depends on US1 and US2 because waiting prompts must appear
  in status/timeline views and decisions must return latest status snapshots.
- **Phase 6: US4**: Depends on US1 and US2 because artifact retrieval is tied
  to run result visibility and terminal-state behavior.
- **Phase 7: Polish**: Depends on all desired user stories.

### User Story Dependencies

- **US1 Start Workflow Runs From Any Channel**: Requires Phase 2 only.
- **US2 Track Run Progress and Status**: Requires accepted run creation from
  US1.
- **US3 Approve, Reject, and Resume Waiting Runs**: Requires US1 run creation
  and US2 status/timeline surfaces for waiting prompts and latest status.
- **US4 Retrieve Artifacts and Delivery Evidence**: Requires US1 run creation
  and US2 result/status behavior.

### Within Each User Story

- Tests must be written first and should fail before implementation.
- Shared schemas and service behavior come before route rendering.
- Channel-specific adapters stay thin and call the shared service facade.
- Auth, tenant, idempotency, rate-limit, audit, and redaction checks are part
  of every protected action.
- Story checkpoints should be validated before moving to the next priority.

## Parallel Opportunities

- After T031 and T032 exist for US1, isolated Web UI adapter tasks T033-T034
  and Telegram adapter tasks T035-T036 can proceed in parallel because they
  touch different adapter files.
- After T049-T054 exist for US2, isolated Web UI adapter tasks T055-T058 and
  Telegram adapter task T059 can proceed in parallel.
- After T068-T070 exist for US3, isolated Web UI adapter tasks T071-T072 and
  Telegram adapter task T073 can proceed in parallel.
- After T082-T085 exist for US4, isolated Web UI adapter task T086 and Telegram
  adapter task T087 can proceed in parallel.

## Parallel Example: User Story 1

```bash
Task: "Implement Web UI run list, new-run form, invocation POST, validation rendering, redirect behavior, and route registration in src/multi_agent_platform/api/routers/web_run_ui.py"
Task: "Implement Telegram /start, /link, /run, link-token consumption, duplicate update handling, and protected-command denial behavior in src/multi_agent_platform/channels/telegram.py"
```

## Parallel Example: User Story 2

```bash
Task: "Implement Web UI live update JavaScript for SSE connection, Last-Event-ID, polling fallback, terminal stop behavior, result refresh, and stale connection display in src/multi_agent_platform/web_admin/static/run_details.js"
Task: "Implement Telegram /status, /result, /subscribe, and terminal notification rendering in src/multi_agent_platform/channels/telegram.py"
```

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 for start-run parity across Web API, Web UI, and Telegram.
3. Validate US1 with contract, API, Web UI, Telegram, auth, idempotency, and
   audit tests before adding progress or result surfaces.

### Incremental Delivery

1. Add US1 for shared invocation and run id creation.
2. Add US2 for status, timeline, streaming updates, notifications, callbacks,
   and results.
3. Add US3 for approval, reject, resume, cancellation, and stale prompt
   handling.
4. Add US4 for artifacts, review evidence, docs, testing instructions, and
   README updates.
5. Finish Phase 7 quality gates and PR evidence.

### Review Discipline

- Keep channel adapters isolated from workflow decision logic.
- Route every protected action through the normalized request envelope and
  shared channel service.
- Verify terminal-state behavior for completed, failed, and canceled runs in
  each channel before review.
- Ensure `.env.qa006` and `qa006.md` can drive this spec without copying
  environment files or QA instructions from earlier specs.
