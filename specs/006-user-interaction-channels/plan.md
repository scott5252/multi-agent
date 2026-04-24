# Implementation Plan: User Interaction Channels

**Branch**: `006-user-interaction-channels` | **Date**: 2026-04-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-user-interaction-channels/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See
`.specify/templates/commands/plan.md` for project-specific planning rules.

## Summary

Add a FastAPI channel layer that lets authenticated users start, monitor,
approve, resume, cancel, and retrieve workflow run outputs through Web UI,
Telegram, and user-facing REST APIs while preserving one shared runtime
invocation model. The design introduces request normalization, channel session
and identity mapping, user-visible run state mapping, trace correlation,
idempotency, rate-limit enforcement, notification subscriptions, short-lived
artifact access URLs, Web UI run details, Telegram webhook handling, and API
client callback delivery. Existing durable runtime, approval, artifact,
authorization, tenancy, audit, and observability primitives remain the source
of workflow behavior.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: FastAPI, Starlette `StreamingResponse` for SSE,
Pydantic v2, Pydantic Settings, SQLAlchemy 2.x, Alembic, PostgreSQL 16+,
psycopg 3, Auth0 JWT validation, existing local-principal auth mode,
LangChain 1.2.15, LangGraph 1.1.9, langgraph-checkpoint-postgres 3.0.5,
httpx for Telegram/API callback delivery, pytest, pytest-asyncio, Ruff,
mypy, uv  
**Storage**: PostgreSQL for channel sessions, Telegram identity links, request
normalization records, idempotency records, notification subscriptions,
notification delivery attempts, API callback registrations and attempts,
timeline event projections, interaction audit records, and references to
existing runtime run/result/artifact metadata; existing object storage remains
the source for artifact bytes and large payloads  
**Testing**: pytest unit tests for request normalization, state mapping,
idempotency, auth-aware routing, error categories, Telegram command parsing,
notification formatting, callback signing, artifact URL policy, and Pydantic
schemas; FastAPI contract tests for REST, Web UI, SSE/polling, Telegram webhook,
approval/resume, result, artifact, and callback registration endpoints;
integration tests for cross-channel recovery, linked Telegram identities,
rate limits, duplicate deliveries, callback retries, and notification
attempts; coverage enforcement at >=90 percent for channel-adapter and
user-interaction behavior  
**Target Platform**: Linux container deployment target for FastAPI API and
background delivery workers; local development on macOS/Linux with Telegram
webhooks simulated by HTTP fixtures; browser-based Web UI served by the
existing FastAPI app  
**Project Type**: Multi-tenant backend platform with FastAPI JSON APIs,
server-rendered/operator Web UI screens, Telegram webhook adapter, background
notification delivery, durable workflow runtime services, and operator-facing
documentation  
**Performance Goals**: Persist accepted channel invocations and return a run id
within 2 seconds; status lookup p95 <300ms and under 2 seconds for SC-003;
timeline polling p95 <300ms for latest 100 events; SSE event fan-out p95
<1 second after an observable lifecycle change while connected; callback and
Telegram terminal notification attempts scheduled within 30 seconds of terminal
state under normal load  
**Constraints**: All protected channel actions must resolve a platform identity
and tenant before touching runtime data; Telegram protected actions require
platform sign-in plus a one-time link token that expires within 10 minutes;
duplicate-prone actions require caller/channel idempotency keys; user-visible
run states are exactly `queued`, `running`, `waiting-for-input`, `completed`,
`failed`, and `canceled`; channels cannot add workflow decision logic; artifact
bytes are never sent directly by Telegram or REST responses; artifact URL TTL
defaults to 15 minutes with a configurable maximum of 60 minutes; large
result/artifact bodies stay in object storage; shared rate limits apply by
tenant, identity, and action type; provider/channel throttles may be stricter;
>=90 percent unit-test coverage, README update, PR review notes, and testing
instructions are required  
**Scale/Scope**: Initial scope supports Web UI, Telegram, and Web API channels;
hundreds of active or paused runs per tenant; thousands of historical runs;
low thousands of notification subscriptions and callback registrations per
tenant; timeline pages of 100 events by default with cursor pagination; one
authoritative channel facade over the durable runtime rather than separate
workflow execution paths

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Durable By Default | PASS | Accepted invocations, idempotency outcomes, channel sessions, Telegram links, status projections, notification subscriptions, delivery attempts, callback attempts, approvals/resumes, artifact access grants, and interaction audits are persisted before they become authoritative. |
| Immutable State And Memory | PASS | Runtime history remains append-only; channel-visible timeline events, delivery attempts, and audit records are append-only evidence rather than mutable chat/session state. |
| Contract-First Agent Coordination | PASS | REST, Telegram webhook, Web UI behavior, callback payloads, timeline events, run status, approval/resume, result, and artifact contracts are specified before implementation and mapped to existing runtime contracts. |
| Security With Practical Development Ergonomics | PASS | Auth0/local-principal dependencies are reused; Telegram access is locked behind one-time identity linking; local tests use deterministic principals while still exercising authorization and tenant checks. |
| Operability Is A Product Requirement | PASS | Plan defines trace correlation, structured logs, metrics, timelines, audits, delivery attempts, callback retries, Web UI run details, and operator troubleshooting docs. |
| Spec-Driven Delivery | PASS | Specification, plan, research, data model, contracts, quickstart, and future tasks trace directly to the user interaction channel requirements. |
| Test And Documentation Discipline | PASS | Plan requires >=90 percent unit coverage, contract/integration tests for each channel, quickstart validation, README updates, PR notes, and review instructions. |
| Clear Ownership And Small Safe Changes | PASS | Work is split across channel domain services, DB models/repositories, API schemas/routers, Telegram adapter, Web UI templates/assets, notification delivery, docs, and focused tests. |
| Tenant Isolation And Fair Scheduling | PASS | All channel records carry tenant and platform identity context; action rate limits and channel throttles apply by tenant, identity, channel, and action type; cross-tenant run ids fail closed. |
| Version-Pinned Execution | PASS | Channel invocations start the existing durable runtime, which pins execution bundles; channel contracts are versioned so in-flight runs remain understandable as UI/API payloads evolve. |
| Secret Hygiene And Controlled Tool Access | PASS | Channel messages, audits, traces, and notification payloads omit secrets and unauthorized result/artifact content; callback signing secrets and Telegram provider tokens are resolved from the configured production secret manager by reference only, with deterministic local test secrets allowed only when production mode is disabled. |
| Tiered Storage For Large Payloads | PASS | PostgreSQL stores metadata, status, audits, and signed URL grants; object storage remains responsible for large artifacts and payload bodies. |
| Human Approval Is Durable State | PASS | Approval and resume actions are normalized into durable runtime approval/input records and guarded against stale prompt responses; transient channel messages are not authoritative. |

Post-Phase-1 re-check: design artifacts below keep every constitution gate in
`PASS` status with no exceptions required.

## Project Structure

### Documentation (this feature)

```text
specs/006-user-interaction-channels/
+-- plan.md
+-- research.md
+-- data-model.md
+-- quickstart.md
+-- contracts/
|   +-- channel-layer.openapi.yaml
|   +-- telegram-webhook.md
|   +-- web-ui-run-details.md
+-- tasks.md
```

### Source Code (repository root)

```text
src/
+-- multi_agent_platform/
    +-- api/
    |   +-- routers/
    |   |   +-- channel_runs.py             # user-facing REST run/status/result/artifact APIs
    |   |   +-- telegram_webhook.py         # Telegram webhook entrypoint
    |   |   +-- web_run_ui.py               # Web UI run list/details/approval screens
    |   +-- schemas/
    |   |   +-- channel_runs.py             # shared channel API schemas
    |   +-- ui/
    |       +-- run_details.py              # server-rendered view models
    +-- channels/
    |   +-- __init__.py
    |   +-- adapters.py                     # channel adapter protocols
    |   +-- artifacts.py                    # short-lived artifact URL facade
    |   +-- callbacks.py                    # API client callback registration/delivery
    |   +-- errors.py                       # channel error category mapping
    |   +-- idempotency.py                  # duplicate action policy
    |   +-- models.py                       # channel domain models
    |   +-- notifications.py                # terminal notification subscriptions
    |   +-- normalization.py                # normalized request/session/trace context
    |   +-- service.py                      # facade over runtime orchestration
    |   +-- state_mapping.py                # runtime -> user-visible lifecycle mapping
    |   +-- telegram.py                     # Telegram command and message behavior
    +-- db/
    |   +-- models/
    |   |   +-- channels.py                 # channel sessions, links, idempotency, delivery tables
    |   +-- repositories/
    |       +-- channels.py                 # transactional channel storage
    +-- web_admin/
    |   +-- static/
    |   |   +-- run_details.js              # polling/SSE behavior and action affordances
    |   +-- templates/
    |       +-- runs/
    |           +-- detail.html
    |           +-- index.html
    +-- bootstrap/
    |   +-- container.py                    # wire channel service and delivery workers
    +-- observability/
        +-- logging.py
        +-- metrics.py
        +-- tracing.py
alembic/versions/
+-- 0006_user_interaction_channels.py        # new migration
tests/
+-- contract/
|   +-- test_channel_layer_contract.py
+-- integration/
|   +-- api/
|   |   +-- test_channel_run_api.py
|   |   +-- test_web_run_ui.py
|   |   +-- test_telegram_webhook.py
|   +-- channels/
|       +-- test_cross_channel_recovery.py
|       +-- test_notification_delivery.py
|       +-- test_api_callbacks.py
+-- unit/
|   +-- api/
|   |   +-- test_channel_run_schemas.py
|   +-- channels/
|       +-- test_artifacts.py
|       +-- test_callbacks.py
|       +-- test_errors.py
|       +-- test_idempotency.py
|       +-- test_normalization.py
|       +-- test_notifications.py
|       +-- test_state_mapping.py
|       +-- test_telegram.py
README.md
docs/quickstart.md
docs/user-interaction-channels.md            # new operator/end-user guide
```

**Structure Decision**: Keep channels inside the existing Python/FastAPI
backend. Add a focused `channels` package that normalizes all Web UI, Telegram,
and Web API actions into one service facade over `runtime/orchestration`.
Routers and templates stay thin: they authenticate, parse channel-specific
inputs, call the channel service, and render/serialize the same domain models.

## Request Normalization And Session Decisions

- **Canonical action envelope**: Every channel action is normalized into
  `NormalizedChannelRequest` before service handling. The envelope includes
  `tenant_id`, platform principal, channel type, channel session id, action
  type, normalized inputs, run id when known, idempotency key for duplicate
  prone actions, request timestamp, `trace_id`, and source metadata.
- **Session identifiers**: Web UI sessions use the existing authenticated web
  session id plus tenant and principal. Web API sessions use caller principal,
  client id when present, and request id. Telegram sessions use
  `(telegram_chat_id, telegram_user_id, linked_platform_identity_id)` after
  the one-time token link is complete. Session ids are opaque UUIDs in channel
  tables and never substitute for authorization.
- **Trace correlation**: Incoming `X-Request-ID` or W3C `traceparent` is
  accepted when valid; otherwise the channel layer creates a trace id. The
  same trace id is written to channel audit records, runtime start/status
  calls, timeline projections, notification attempts, callback attempts, and
  logs.
- **Auth-aware routing**: Web UI and REST use FastAPI dependencies that resolve
  platform identity and tenant before routing protected actions. Telegram
  webhook routes first verify provider authenticity, then resolve the linked
  platform identity; unlinked chats may only request linking help or submit a
  one-time token.
- **Idempotency scope**: Invocation, approval, rejection, resume, cancel,
  notification acknowledgement, artifact URL grant, and callback registration
  require idempotency keys. Keys are unique per tenant, actor, action type, and
  channel. Replays return the first accepted outcome; conflicting payloads
  return `idempotency_conflict`.

## Run Lifecycle And Status API Decisions

- **User-visible state mapping**: Internal runtime states are mapped at the
  channel boundary: `pending`/`runnable` -> `queued`; `running`,
  `waiting_child`, `recoverable_failed`, and `cancelling` -> `running` unless a
  durable prompt is active; `paused` with approval/input prompt -> 
  `waiting-for-input`; `succeeded` -> `completed`; `failed` -> `failed`;
  `cancelled` -> `canceled`.
- **Status endpoint**: `GET /runs/{run_id}/status` returns the canonical run id,
  user-visible state, progress summary, latest timeline cursor, waiting prompt
  summary when allowed, terminal outcome, result availability, artifact
  availability, subscription state, and permitted actions for the caller.
- **Timeline events**: `GET /runs/{run_id}/timeline` returns ordered
  user-facing timeline events with stable sequence numbers, event categories,
  redacted summaries, trace ids, optional step/prompt/artifact references, and
  cursor pagination. Timeline payloads never expose unauthorized result or
  secret content.
- **Live updates**: Web UI uses SSE at `GET /runs/{run_id}/events` with
  `Last-Event-ID` support. If SSE is unavailable, the UI polls status and
  timeline every 2 to 10 seconds with backoff. Web API clients may poll status
  or register callbacks. Telegram receives terminal notifications, can fetch
  current status on demand, and may opt into bounded low-frequency progress
  watches for a single run. Watches coalesce updates and respect provider
  throttles; Telegram never receives high-frequency progress spam.
- **Result retrieval**: `GET /runs/{run_id}/result` distinguishes completed
  result, failed summary, canceled summary, unavailable, expired, and
  unauthorized outcomes through stable `availability` and error category
  fields.

## Approval, Resume, And Cancellation Decisions

- **Waiting prompt model**: The channel service derives a `WaitingPromptView`
  from durable runtime approval/input state. It includes prompt id, run id,
  prompt type, allowed actions, redacted context, eligible reviewer hints,
  deadline when present, and the latest prompt version.
- **Decision endpoints**: Approval, rejection, resume input, and cancellation
  use explicit endpoints with idempotency keys and prompt version checks. The
  channel layer validates current authorization and prompt freshness before
  forwarding to the runtime approval/resume service.
- **Stale action behavior**: If a prompt was answered, canceled, completed,
  failed, or superseded, the channel returns `invalid_lifecycle_action` plus
  the latest retrievable run status without mutating runtime state.
- **Cross-channel continuity**: A prompt opened from Telegram can be completed
  in the Web UI or REST API by the same authorized identity, and the next
  Telegram/Web UI action sees the updated status.

## Telegram Behavior Decisions

- **Webhook security**: Telegram webhook requests are accepted only on the
  configured secret path/header and are parsed into update ids with duplicate
  suppression. Provider verification failures return a generic success
  response where appropriate to avoid retry storms while recording a rejected
  delivery audit event.
- **Identity linking**: The Web UI/API creates a short-lived one-time link
  token that expires within 10 minutes for an authenticated platform user.
  Telegram `/link <token>` consumes it once and stores a durable link between
  Telegram user/chat and platform identity. Expired, reused, or
  tenant-mismatched tokens return a safe message with no protected details.
- **Commands**: Telegram supports `/start`, `/link`, `/run`, `/status`,
  `/watch`, `/unwatch`, `/approve`, `/reject`, `/resume`, `/cancel`, `/result`,
  `/artifacts`, and `/subscribe`. Commands requiring protected data fail with a
  linking prompt until identity is resolved.
- **Completion messages**: Terminal notifications include run id, state,
  redacted summary, and next action buttons/links. Completed runs offer
  "View result" and "Artifacts" actions when authorized; failed/canceled runs
  offer "View details". Messages do not include result bodies or artifact
  bytes.

## Web UI Decisions

- **Run details behavior**: The run details page shows run id, user-visible
  state, current progress summary, timeline, waiting prompt actions when
  allowed, final result availability, artifact list, notification subscription
  state, trace id for support, and callback status for API-originated runs.
- **Live state**: The page connects to SSE when possible and falls back to
  polling. If the connection drops, the UI keeps the last persisted state
  visible and shows retrying status without implying failure.
- **Operator/end-user UX**: Actions are disabled when the run is terminal or
  the prompt version is stale. Error banners use the shared error categories
  but user-facing language; support details are collapsible and redacted.

## Artifact And Callback Decisions

- **Artifact access**: `GET /runs/{run_id}/artifacts` lists metadata and a
  `download_url_available` flag. `POST /runs/{run_id}/artifacts/{artifact_id}/download-url`
  creates a short-lived platform-authenticated URL after authorization and
  idempotency checks. URL grants are audited, default to a 15-minute TTL, and
  may be configured up to a 60-minute maximum.
- **API callbacks**: Web API clients can register per-run callbacks for
  terminal, waiting prompt, and artifact-ready events. Callback payloads use
  the same status/result/timeline schema fragments, are signed with an HMAC
  secret reference, include event id and trace id, and require acknowledgement
  or idempotent receiver handling. Failed deliveries retry with exponential
  backoff and are visible in run details.
- **Notification subscriptions**: The initiating user is subscribed on
  invocation. Additional authorized users may subscribe per run. Delivery
  workers re-check authorization and user preferences before sending terminal
  notifications.

## Delivery Lease, Retry, And Compensation Decisions

- **Delivery leases**: Notification, callback, Telegram progress-watch, and
  artifact grant delivery workers acquire tenant-scoped leases before attempting
  external side effects. Leases include `leased_by`, `lease_expires_at`, attempt
  number, and trace id so interrupted work can be reclaimed safely.
- **Retry behavior**: Retryable Telegram and callback failures use bounded
  exponential backoff with max attempts and terminal `failed` evidence. Artifact
  URL grant creation is retried only before a grant is issued.
- **Compensation behavior**: If an external delivery succeeds but persistence of
  the attempt result fails, reconciliation jobs use provider/request ids and
  idempotency records to record the observed outcome without re-sending. Failed
  delivery never mutates workflow run state.

## Error Handling, Rate Limits, And Observability

- **Error categories**: Channel adapters map failures to stable categories:
  `unauthorized`, `missing_input`, `invalid_run_id`,
  `unavailable_channel_delivery`, `invalid_lifecycle_action`,
  `idempotency_conflict`, `rate_limited`, `artifact_unavailable`,
  `callback_delivery_failed`, and `platform_failure`.
- **HTTP behavior**: REST uses appropriate 4xx/5xx status codes with
  `error.category`, `trace_id`, and optional latest status. Web UI renders the
  same category as a human-friendly message. Telegram sends concise messages
  and avoids protected detail on authorization failures.
- **Rate limits**: Shared platform limits run before channel-specific
  throttles. Telegram send limits and callback delivery budgets may be
  stricter but cannot bypass tenant/identity/action limits.
- **Fair scheduling**: Shared delivery workers enforce per-tenant concurrency
  limits for notifications, callbacks, Telegram progress watches, and SSE
  fan-out. Callback and Telegram queues are drained round-robin by tenant so one
  tenant cannot starve another. Metrics expose queued, leased, retried, failed,
  and throttled work by tenant and action type.
- **Telemetry**: Emit structured logs, metrics, traces, and audit records for
  normalized action, auth decision, idempotency result, runtime call, timeline
  event projection, notification attempt, callback attempt, artifact URL grant,
  and user-visible outcome.

## Complexity Tracking

No constitution violations or complexity exceptions are required.
