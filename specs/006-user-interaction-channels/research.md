# Research: User Interaction Channels

## Decision: Implement a channel facade over the durable runtime

**Rationale**: The spec requires Web UI, Telegram, and Web API actions to share
one workflow invocation model. A facade in `multi_agent_platform.channels`
keeps channel-specific parsing and presentation separate from runtime workflow
logic while preserving one authorization, idempotency, state mapping, audit,
and trace path.

**Alternatives considered**: Calling `runtime/orchestration` directly from each
router would duplicate permissions and state mapping. Creating separate
workflow handlers per channel would violate the spec by introducing separate
workflow behavior.

## Decision: Normalize every channel action into a canonical request envelope

**Rationale**: Web sessions, REST calls, and Telegram updates have different
input formats and identity hints. A `NormalizedChannelRequest` makes tenant,
identity, action type, run id, idempotency key, trace id, and source metadata
explicit before any runtime mutation occurs.

**Alternatives considered**: Passing raw FastAPI `Request` or Telegram update
objects into services would make test coverage and audit consistency brittle.

## Decision: Use opaque durable channel session identifiers

**Rationale**: Session ids support cross-channel recovery, delivery evidence,
and duplicate suppression without making chat ids, cookies, or API client ids
authoritative. Authorization still comes from platform identity and tenant
checks on every action.

**Alternatives considered**: Using channel-native ids directly would leak
provider details across service boundaries and make future channel additions
harder.

## Decision: Reuse Auth0/local-principal authorization and add Telegram linking

**Rationale**: Web UI and REST already have platform identity flows. Telegram
cannot safely access protected tenant data until a platform user signs in and
consumes a short-lived one-time linking token, giving Telegram an auditable
association with a platform identity.

**Alternatives considered**: Telegram-only passwords or trusting Telegram user
ids were rejected because they bypass the platform authorization model.

## Decision: Map internal runtime states to exactly six user-visible states

**Rationale**: Existing runtime states are useful for workers and operators but
the feature requires a stable user contract: `queued`, `running`,
`waiting-for-input`, `completed`, `failed`, and `canceled`. Mapping at the
channel boundary protects clients from internal runtime changes.

**Alternatives considered**: Exposing internal states such as `runnable`,
`paused`, or `recoverable_failed` would break the spec and make cross-channel
status inconsistent.

## Decision: Provide SSE for Web UI and polling/callbacks for clients

**Rationale**: SSE fits FastAPI and server-rendered Web UI run details without
adding a bidirectional protocol. Polling remains the durable fallback and Web
API callbacks cover integrations that need push behavior. Telegram receives
terminal messages plus on-demand status instead of high-frequency progress
updates.

**Alternatives considered**: WebSockets were unnecessary for the initial
read-only progress stream. Sending every progress event to Telegram would be
noisy and vulnerable to provider throttling.

## Decision: Treat timeline events as user-facing projections

**Rationale**: Runtime timeline and audit records can contain implementation
details. A channel timeline projection stores ordered, redacted, user-facing
events with trace ids and cursors, preserving observability without exposing
secrets or unauthorized content.

**Alternatives considered**: Returning raw runtime events would couple users to
internal event names and risk leaking hidden payloads.

## Decision: Require idempotency keys for duplicate-prone actions

**Rationale**: REST retries, double-clicks, Telegram webhook redelivery, and
callback acknowledgement retries can otherwise create duplicate runs or stale
decisions. Persisted idempotency outcomes keyed by tenant, actor, action, and
channel return the first accepted result or a conflict for mismatched replays.

**Alternatives considered**: Best-effort duplicate suppression by timestamp was
rejected because it cannot guarantee approval/resume correctness.

## Decision: Use short-lived platform-authenticated artifact URLs

**Rationale**: Artifacts may be large and sensitive. Returning metadata plus a
short-lived authenticated URL keeps bytes in object storage, reuses platform
authorization, supports Telegram/Web/API uniformly, and leaves auditable access
grants.

**Alternatives considered**: Sending files directly through Telegram or API
responses was rejected because it bypasses object-storage policy and makes
expiry, auditing, and large payload handling harder.

## Decision: Add signed API client callbacks for terminal and prompt events

**Rationale**: Polling is reliable but inefficient for integrations. Per-run
callback subscriptions with signed payloads, event ids, trace ids, retries,
and delivery status give API clients an optional push path without making
callbacks the source of truth.

**Alternatives considered**: Global webhooks for all tenant events were
deferred because this feature needs per-run subscriptions and explicit
authorization.

## Decision: Store delivery attempts and re-check authorization at send time

**Rationale**: A user may lose access, unlink Telegram, disable notifications,
or revoke preferences before a run finishes. Re-checking authorization before
terminal messages and artifact URL grants keeps notifications safe, while
delivery attempts preserve operator evidence.

**Alternatives considered**: Trusting the authorization decision from
subscription time was rejected because permissions can change while runs are
active.

## Decision: Use shared error categories across channels

**Rationale**: REST clients, Web UI, and Telegram need different presentation,
but operators and tests need consistent semantics. Stable categories such as
`unauthorized`, `invalid_lifecycle_action`, and `rate_limited` let adapters
render friendly messages without losing machine-readable meaning.

**Alternatives considered**: Returning channel-native free text only would make
cross-channel tests and support diagnostics weak.
